"""
Streamlit Web UI for the Code Eval Workbench.

Run:  streamlit run app.py
"""
import json
import time
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dataset import DATASET, generate_examples, get_categories, get_difficulties, get_dataset
from scorer import composite_score
from task import fix_code_bug
from utils import EvalResult, RunSummary, ScoreBreakdown, load_all_runs, save_run

# ─── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Code Eval Workbench",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.score-card {
    background: #1e1e2e;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.score-high { color: #a6e3a1; }
.score-med  { color: #f9e2af; }
.score-low  { color: #f38ba8; }
.metric-big { font-size: 2.4rem; font-weight: 700; }
.metric-label { font-size: 0.85rem; color: #6c7086; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def score_color_class(s: float) -> str:
    if s >= 0.75:
        return "score-high"
    elif s >= 0.50:
        return "score-med"
    return "score-low"


def score_badge(s: float | None) -> str:
    if s is None:
        return "—"
    cls = score_color_class(s)
    return f'<span class="{cls}"><b>{s:.3f}</b></span>'


def color_score(s: float | None) -> str:
    """Return a colored string for display."""
    if s is None:
        return "N/A"
    if s >= 0.75:
        return f"🟢 {s:.3f}"
    elif s >= 0.50:
        return f"🟡 {s:.3f}"
    return f"🔴 {s:.3f}"


# ─── Session state init ────────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = []
if "run_summary" not in st.session_state:
    st.session_state.run_summary = None
if "generated_examples" not in st.session_state:
    st.session_state.generated_examples = []


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🔬 Eval Workbench")
    st.caption("Claude-powered Code Bug Fix Evaluator")
    st.divider()

    st.subheader("Dataset Filters")
    all_categories = get_categories()
    all_difficulties = get_difficulties()

    selected_categories = st.multiselect(
        "Categories",
        options=all_categories,
        default=all_categories,
        help="Bug categories to include",
    )
    selected_difficulties = st.multiselect(
        "Difficulty",
        options=all_difficulties,
        default=all_difficulties,
    )

    st.divider()
    st.subheader("Scorers")
    use_llm = st.checkbox("LLM-as-Judge (Claude)", value=True, help="Claude grades correctness, quality, explanation")
    use_prog = st.checkbox("Programmatic (pytest)", value=True, help="Run actual tests against fixed code")
    use_lev = st.checkbox("Levenshtein Similarity", value=True, help="Character-level similarity to reference")

    st.divider()
    st.subheader("CI/CD Gate")
    threshold = st.slider(
        "Pass threshold", 0.0, 1.0, 0.70, 0.01,
        help="CLI exits with code 1 if composite < threshold",
    )
    st.caption(f"`python run_eval.py --threshold {threshold:.2f}`")

    st.divider()
    st.caption("Model: `claude-opus-4-6`")
    st.caption("Thinking: adaptive")


# ─── Tabs ──────────────────────────────────────────────────────────────────────

tab_eval, tab_analysis, tab_dataset, tab_history = st.tabs([
    "🔬 Evaluation",
    "📊 Analysis",
    "🗂️ Dataset Studio",
    "📜 History",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Evaluation
# ════════════════════════════════════════════════════════════════════════════

with tab_eval:
    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        st.header("Run Evaluation")
    with col_btn:
        st.write("")
        run_btn = st.button("▶ Run Eval", type="primary", use_container_width=True)

    # Build working dataset (curated + any generated)
    working_dataset = get_dataset(
        categories=selected_categories if selected_categories else None,
        difficulties=selected_difficulties if selected_difficulties else None,
    )
    if st.session_state.generated_examples:
        extra = [
            e for e in st.session_state.generated_examples
            if (not selected_categories or e.get("category") in selected_categories)
            and (not selected_difficulties or e.get("difficulty") in selected_difficulties)
        ]
        working_dataset = working_dataset + extra

    st.info(
        f"**{len(working_dataset)} examples** selected  |  "
        f"Scorers: {'LLM-judge ' if use_llm else ''}{'Programmatic ' if use_prog else ''}{'Levenshtein' if use_lev else ''}",
        icon="ℹ️",
    )

    if run_btn and working_dataset:
        results: list[EvalResult] = []
        progress_bar = st.progress(0, text="Starting evaluation...")
        status_area = st.empty()
        live_table = st.empty()
        table_rows = []

        for i, item in enumerate(working_dataset):
            progress_pct = i / len(working_dataset)
            progress_bar.progress(progress_pct, text=f"🔧 Fixing bug: **{item['id']}** ({i+1}/{len(working_dataset)})")

            with status_area.container():
                st.caption(f"Processing `{item['id']}` — category: *{item['category']}* — difficulty: *{item['difficulty']}*")

            # Run task
            try:
                output = fix_code_bug(item["input"])
            except Exception as e:
                st.error(f"Task error on {item['id']}: {e}")
                output = ""

            progress_bar.progress(progress_pct + 0.5 / len(working_dataset), text=f"📊 Scoring: **{item['id']}**")

            # Score
            score_dict = composite_score(
                output=output,
                input_dict=item["input"],
                reference=item["reference_output"],
                test_code=item.get("test_code", ""),
                use_llm_judge=use_llm,
                use_programmatic=use_prog,
                use_levenshtein=use_lev,
            )

            result = EvalResult(
                id=item["id"],
                category=item["category"],
                difficulty=item["difficulty"],
                output=output,
                scores=ScoreBreakdown(
                    llm_judge=score_dict.get("llm_judge"),
                    programmatic=score_dict.get("programmatic"),
                    levenshtein=score_dict.get("levenshtein"),
                    composite=score_dict["composite"],
                ),
                reasoning=score_dict.get("reasoning", ""),
                passed_tests=score_dict.get("passed_tests"),
                total_tests=score_dict.get("total_tests"),
            )
            results.append(result)

            # Live table row
            row = {
                "ID": item["id"],
                "Category": item["category"],
                "Difficulty": item["difficulty"],
                "Composite": color_score(score_dict["composite"]),
            }
            if use_llm:
                row["LLM Judge"] = color_score(score_dict.get("llm_judge"))
            if use_prog:
                tests_label = ""
                if score_dict.get("passed_tests") is not None:
                    tests_label = f" ({score_dict['passed_tests']}/{score_dict['total_tests']})"
                row["Prog Tests"] = color_score(score_dict.get("programmatic")) + tests_label
            if use_lev:
                row["Similarity"] = color_score(score_dict.get("levenshtein"))
            table_rows.append(row)

            live_table.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        progress_bar.progress(1.0, text="✅ Evaluation complete!")
        status_area.empty()

        # Save run
        composites = [r.scores.composite for r in results]
        avg_composite = sum(composites) / len(composites)

        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        scorers_used = (
            (["LLM-as-judge"] if use_llm else [])
            + (["Programmatic"] if use_prog else [])
            + (["Levenshtein"] if use_lev else [])
        )
        run_summary = RunSummary(
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            avg_composite=round(avg_composite, 4),
            avg_llm_judge=round(
                sum(r.scores.llm_judge for r in results if r.scores.llm_judge is not None)
                / max(1, sum(1 for r in results if r.scores.llm_judge is not None)), 4,
            ),
            avg_programmatic=round(
                sum(r.scores.programmatic for r in results if r.scores.programmatic is not None)
                / max(1, sum(1 for r in results if r.scores.programmatic is not None)), 4,
            ),
            avg_levenshtein=round(
                sum(r.scores.levenshtein for r in results if r.scores.levenshtein is not None)
                / max(1, sum(1 for r in results if r.scores.levenshtein is not None)), 4,
            ),
            n_examples=len(results),
            scorers_used=scorers_used,
            results=results,
        )
        save_run(run_summary)
        st.session_state.results = results
        st.session_state.run_summary = run_summary

    # ── Show results if available ────────────────────────────────────────────
    if st.session_state.run_summary:
        rs = st.session_state.run_summary

        st.divider()
        st.subheader("Results")

        # Score cards
        cols = st.columns(4)
        metrics = [
            ("Composite", rs.avg_composite),
            ("LLM Judge", rs.avg_llm_judge),
            ("Prog Tests", rs.avg_programmatic),
            ("Similarity", rs.avg_levenshtein),
        ]
        for col, (label, val) in zip(cols, metrics):
            cls = score_color_class(val)
            col.markdown(
                f'<div class="score-card">'
                f'<div class="metric-big {cls}">{val:.3f}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Pass/fail gate
        st.write("")
        if rs.avg_composite >= threshold:
            st.success(f"✅ PASS — Composite {rs.avg_composite:.3f} ≥ threshold {threshold:.2f}", icon="✅")
        else:
            st.error(f"❌ FAIL — Composite {rs.avg_composite:.3f} < threshold {threshold:.2f}", icon="❌")

        # Per-example details
        st.write("")
        st.subheader("Per-Example Details")
        for r in st.session_state.results:
            comp = r.scores.composite
            icon = "🟢" if comp >= 0.75 else "🟡" if comp >= 0.50 else "🔴"
            with st.expander(f"{icon} `{r.id}` — {r.category} ({r.difficulty}) — composite: **{comp:.3f}**"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Buggy Code**")
                    item = next((d for d in working_dataset if d["id"] == r.id), None)
                    if item:
                        st.code(item["input"]["buggy_code"], language="python")
                        st.caption(f"Bug: {item['input']['bug_description']}")
                with c2:
                    st.markdown("**Claude's Fix**")
                    from utils import extract_code_block
                    fixed = extract_code_block(r.output)
                    st.code(fixed, language="python")
                    from utils import extract_explanation
                    expl = extract_explanation(r.output)
                    if expl:
                        st.caption(f"Explanation: {expl}")

                score_cols = st.columns(4)
                score_cols[0].metric("Composite", f"{r.scores.composite:.3f}")
                score_cols[1].metric("LLM Judge", f"{r.scores.llm_judge:.3f}" if r.scores.llm_judge is not None else "N/A")
                score_cols[2].metric(
                    "Prog Tests",
                    f"{r.scores.programmatic:.3f}" if r.scores.programmatic is not None else "N/A",
                    delta=f"{r.passed_tests}/{r.total_tests} tests" if r.passed_tests is not None else None,
                )
                score_cols[3].metric("Similarity", f"{r.scores.levenshtein:.3f}" if r.scores.levenshtein is not None else "N/A")

                if r.reasoning:
                    st.info(f"**Judge reasoning:** {r.reasoning}", icon="🧑‍⚖️")

        # Download button
        st.write("")
        if st.session_state.run_summary:
            json_str = st.session_state.run_summary.model_dump_json(indent=2)
            st.download_button(
                "⬇️ Download Results (JSON)",
                data=json_str,
                file_name=f"eval_run_{rs.run_id}.json",
                mime="application/json",
            )


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Analysis
# ════════════════════════════════════════════════════════════════════════════

with tab_analysis:
    st.header("Score Analysis")

    results = st.session_state.results
    if not results:
        st.info("Run an evaluation first to see analysis.", icon="ℹ️")
    else:
        df = pd.DataFrame([
            {
                "id": r.id,
                "category": r.category,
                "difficulty": r.difficulty,
                "composite": r.scores.composite,
                "llm_judge": r.scores.llm_judge,
                "programmatic": r.scores.programmatic,
                "levenshtein": r.scores.levenshtein,
            }
            for r in results
        ])

        col1, col2 = st.columns(2)

        with col1:
            # Score distribution histogram
            fig = px.histogram(
                df,
                x="composite",
                nbins=10,
                title="Composite Score Distribution",
                color_discrete_sequence=["#89b4fa"],
                labels={"composite": "Composite Score", "count": "Count"},
            )
            fig.update_layout(
                plot_bgcolor="#1e1e2e",
                paper_bgcolor="#1e1e2e",
                font_color="#cdd6f4",
                showlegend=False,
            )
            fig.add_vline(x=threshold, line_dash="dash", line_color="#f38ba8",
                          annotation_text=f"Threshold {threshold:.2f}")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Per-category bar chart
            cat_avg = df.groupby("category")["composite"].mean().reset_index()
            fig2 = px.bar(
                cat_avg,
                x="composite",
                y="category",
                orientation="h",
                title="Average Score by Category",
                color="composite",
                color_continuous_scale="RdYlGn",
                range_color=[0, 1],
                labels={"composite": "Avg Composite", "category": "Category"},
            )
            fig2.update_layout(
                plot_bgcolor="#1e1e2e",
                paper_bgcolor="#1e1e2e",
                font_color="#cdd6f4",
                showlegend=False,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            # Scorer comparison radar / grouped bar
            score_cols = []
            if df["llm_judge"].notna().any():
                score_cols.append("llm_judge")
            if df["programmatic"].notna().any():
                score_cols.append("programmatic")
            if df["levenshtein"].notna().any():
                score_cols.append("levenshtein")

            if score_cols:
                melted = df[["id"] + score_cols].melt(id_vars="id", var_name="scorer", value_name="score")
                fig3 = px.bar(
                    melted,
                    x="id",
                    y="score",
                    color="scorer",
                    barmode="group",
                    title="Scorer Comparison per Example",
                    labels={"id": "Example", "score": "Score"},
                )
                fig3.update_layout(
                    plot_bgcolor="#1e1e2e",
                    paper_bgcolor="#1e1e2e",
                    font_color="#cdd6f4",
                    xaxis_tickangle=-45,
                )
                st.plotly_chart(fig3, use_container_width=True)

        with col4:
            # Difficulty breakdown
            diff_avg = df.groupby("difficulty")["composite"].mean().reset_index()
            fig4 = px.bar(
                diff_avg,
                x="difficulty",
                y="composite",
                title="Score by Difficulty",
                color="difficulty",
                color_discrete_map={"easy": "#a6e3a1", "medium": "#f9e2af", "hard": "#f38ba8"},
                labels={"composite": "Avg Composite", "difficulty": "Difficulty"},
            )
            fig4.update_layout(
                plot_bgcolor="#1e1e2e",
                paper_bgcolor="#1e1e2e",
                font_color="#cdd6f4",
                showlegend=False,
                yaxis_range=[0, 1],
            )
            st.plotly_chart(fig4, use_container_width=True)

        # Raw data table
        st.subheader("Raw Scores")
        st.dataframe(
            df.style.background_gradient(subset=["composite", "llm_judge", "programmatic", "levenshtein"],
                                          cmap="RdYlGn", vmin=0, vmax=1),
            use_container_width=True,
            hide_index=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Dataset Studio
# ════════════════════════════════════════════════════════════════════════════

with tab_dataset:
    st.header("Dataset Studio")

    sub1, sub2 = st.tabs(["📋 Browse", "✨ Generate"])

    with sub1:
        st.subheader(f"Curated Dataset ({len(DATASET)} examples)")
        for item in DATASET:
            with st.expander(f"`{item['id']}` — {item['category']} ({item['difficulty']})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Buggy Code**")
                    st.code(item["input"]["buggy_code"], language="python")
                    st.caption(f"*Bug:* {item['input']['bug_description']}")
                with c2:
                    st.markdown("**Reference Fix**")
                    st.code(item["reference_output"], language="python")
                st.markdown("**Test Code**")
                st.code(item.get("test_code", "# No tests"), language="python")

        if st.session_state.generated_examples:
            st.divider()
            st.subheader(f"Generated Examples ({len(st.session_state.generated_examples)})")
            for item in st.session_state.generated_examples:
                with st.expander(f"`{item.get('id', 'gen')}` — {item.get('category','?')} ({item.get('difficulty','?')}) ✨"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Buggy Code**")
                        st.code(item["input"]["buggy_code"], language="python")
                        st.caption(f"*Bug:* {item['input']['bug_description']}")
                    with c2:
                        st.markdown("**Reference Fix**")
                        st.code(item["reference_output"], language="python")
                    if item.get("test_code"):
                        st.markdown("**Test Code**")
                        st.code(item["test_code"], language="python")

    with sub2:
        st.subheader("Generate New Examples with Claude")
        st.caption("Claude synthesizes new bug-fix pairs in the same format as the curated dataset.")

        g1, g2, g3 = st.columns(3)
        n_gen = g1.number_input("Number to generate", 1, 10, 3)
        gen_cat = g2.selectbox("Category", ["any"] + all_categories)
        gen_diff = g3.selectbox("Difficulty", ["easy", "medium", "hard"])

        if st.button("✨ Generate Examples", type="primary"):
            with st.spinner(f"Generating {n_gen} new examples with Claude..."):
                try:
                    new_examples = generate_examples(n=int(n_gen), category=gen_cat, difficulty=gen_diff)
                    st.session_state.generated_examples.extend(new_examples)
                    st.success(f"Generated {len(new_examples)} new examples! They're now included in evaluations.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation failed: {e}")

        if st.session_state.generated_examples:
            if st.button("🗑️ Clear Generated Examples", type="secondary"):
                st.session_state.generated_examples = []
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — History
# ════════════════════════════════════════════════════════════════════════════

with tab_history:
    st.header("Run History")

    all_runs = load_all_runs()

    if not all_runs:
        st.info("No saved runs yet. Run an evaluation to see history.", icon="📜")
    else:
        # Summary table
        summary_rows = []
        for run in all_runs:
            summary_rows.append({
                "Run ID": run.run_id,
                "Timestamp": run.timestamp[:19].replace("T", " "),
                "Examples": run.n_examples,
                "Composite": f"{run.avg_composite:.3f}",
                "LLM Judge": f"{run.avg_llm_judge:.3f}",
                "Prog Tests": f"{run.avg_programmatic:.3f}",
                "Similarity": f"{run.avg_levenshtein:.3f}",
                "Scorers": ", ".join(run.scorers_used),
            })

        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        # Trend chart (composite over time)
        if len(all_runs) > 1:
            trend_df = pd.DataFrame([
                {"Run": r.run_id[-6:], "Composite": r.avg_composite, "Timestamp": r.timestamp}
                for r in reversed(all_runs)
            ])
            fig = px.line(
                trend_df,
                x="Run",
                y="Composite",
                title="Composite Score Trend",
                markers=True,
                labels={"Composite": "Avg Composite Score"},
            )
            fig.update_layout(
                plot_bgcolor="#1e1e2e",
                paper_bgcolor="#1e1e2e",
                font_color="#cdd6f4",
                yaxis_range=[0, 1],
            )
            fig.add_hline(y=threshold, line_dash="dash", line_color="#f38ba8",
                          annotation_text=f"Threshold {threshold:.2f}")
            st.plotly_chart(fig, use_container_width=True)

        # Drill into a run
        st.subheader("Drill Into a Run")
        run_ids = [r.run_id for r in all_runs]
        selected_run_id = st.selectbox("Select run", run_ids)
        selected_run = next((r for r in all_runs if r.run_id == selected_run_id), None)

        if selected_run:
            st.json({
                "run_id": selected_run.run_id,
                "avg_composite": selected_run.avg_composite,
                "avg_llm_judge": selected_run.avg_llm_judge,
                "avg_programmatic": selected_run.avg_programmatic,
                "avg_levenshtein": selected_run.avg_levenshtein,
                "n_examples": selected_run.n_examples,
                "scorers_used": selected_run.scorers_used,
            })

            json_str = selected_run.model_dump_json(indent=2)
            st.download_button(
                f"⬇️ Download run_{selected_run.run_id}.json",
                data=json_str,
                file_name=f"run_{selected_run.run_id}.json",
                mime="application/json",
            )
