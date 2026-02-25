"""Workflow: Molecular Biology Design — primers, codon optimization, assemblies."""

import streamlit as st
import pandas as pd
import numpy as np

from utils.config import WorkbenchConfig
from utils.celltype_agent import run_celltype_query
from utils.state import save_report
from utils.examples import MOLECULAR_EXAMPLES


def render_molecular_design():
    """Render the molecular design workflow page."""
    st.title("🧬 Molecular Biology Design")
    st.caption(
        "Design primers, codon-optimize ORFs, plan Golden Gate / Gibson assemblies, "
        "and design CRISPR guide RNAs — all through natural language."
    )

    tab_primer, tab_codon, tab_assembly, tab_crispr, tab_agent = st.tabs([
        "🔬 Primer Design", "🧬 Codon Optimization", "🔧 Assembly Planning",
        "✂️ CRISPR Guide Design", "🤖 Free-Form Agent",
    ])

    with tab_primer:
        _render_primer_design()

    with tab_codon:
        _render_codon_optimization()

    with tab_assembly:
        _render_assembly_planning()

    with tab_crispr:
        _render_crispr_design()

    with tab_agent:
        _render_freeform_agent()


def _render_primer_design():
    """Primer design interface."""
    st.subheader("PCR Primer Design")

    col1, col2 = st.columns(2)
    with col1:
        gene = st.text_input("Target Gene / Region", value="IKZF1 exon 5-7")
        organism = st.selectbox("Organism", ["Human (Homo sapiens)", "Mouse (Mus musculus)",
                                              "E. coli", "Yeast (S. cerevisiae)", "Custom"])
        purpose = st.selectbox("Purpose", [
            "RT-qPCR", "Cloning (restriction sites)", "Mutagenesis (site-directed)",
            "Sequencing", "Colony PCR", "Golden Gate (BsaI)", "Gibson Assembly",
        ])

    with col2:
        tm_range = st.slider("Target Tm (°C)", 55, 72, (60, 65))
        gc_range = st.slider("GC Content (%)", 30, 70, (40, 60))
        product_size = st.slider("Product Size (bp)", 100, 5000, (200, 500), step=50)
        amplicon_length = st.number_input("Max Primer Length (nt)", 18, 40, 25)

    additional = st.text_area(
        "Additional Requirements",
        placeholder="e.g., add 5' His-tag, avoid secondary structures, include Kozak sequence",
        height=60,
    )

    if st.button("🧬 Design Primers", type="primary", use_container_width=True):
        query = (
            f"Design PCR primers for {gene} in {organism} for {purpose}. "
            f"Target Tm: {tm_range[0]}-{tm_range[1]}°C, GC: {gc_range[0]}-{gc_range[1]}%, "
            f"product size: {product_size[0]}-{product_size[1]} bp, max primer length: {amplicon_length} nt. "
            f"{('Additional: ' + additional) if additional else ''}"
            f"Provide forward and reverse primers with Tm, GC%, and any adaptor sequences."
        )
        _run_and_display(query)

    # Example output
    with st.expander("💡 Example Primer Output"):
        example_primers = pd.DataFrame({
            "Primer": ["Forward", "Reverse"],
            "Sequence (5'→3')": ["ATGGATCCTGGACAGCACAG", "TCAGAATTCGCTGATCTGCC"],
            "Length (nt)": [20, 20],
            "Tm (°C)": [62.3, 61.8],
            "GC (%)": [55.0, 55.0],
            "Notes": ["Includes BamHI site", "Includes EcoRI site"],
        })
        st.dataframe(example_primers, use_container_width=True, hide_index=True)


def _render_codon_optimization():
    """Codon optimization interface."""
    st.subheader("Codon Optimization")

    col1, col2 = st.columns(2)
    with col1:
        protein_input = st.text_area(
            "Protein Sequence or Gene Name",
            value="IKZF1 degradation domain (aa 1-150)",
            height=100,
            help="Enter an amino acid sequence (FASTA), gene name + region, or UniProt ID.",
        )
        expression_host = st.selectbox("Expression Host", [
            "E. coli (BL21)", "E. coli (K-12)", "CHO cells", "HEK293",
            "Pichia pastoris", "S. cerevisiae", "Insect cells (Sf9)",
        ])

    with col2:
        optimization_goals = st.multiselect(
            "Optimization Goals",
            ["Maximize expression", "Avoid rare codons", "Reduce mRNA secondary structure",
             "Add restriction site avoidance", "Harmonize codon usage", "GC content normalization"],
            default=["Maximize expression", "Avoid rare codons"],
        )
        add_tags = st.multiselect(
            "Add Tags/Elements",
            ["N-terminal His6", "C-terminal His6", "GST tag", "MBP tag",
             "TEV cleavage site", "Kozak sequence", "Start/Stop codons"],
        )

    if st.button("🧬 Optimize Codons", type="primary", use_container_width=True):
        query = (
            f"Codon-optimize the following for expression in {expression_host}: {protein_input}. "
            f"Goals: {', '.join(optimization_goals)}. "
            f"{'Add: ' + ', '.join(add_tags) + '. ' if add_tags else ''}"
            f"Provide the optimized DNA sequence, CAI score, GC content, and any restriction sites to avoid."
        )
        _run_and_display(query)


def _render_assembly_planning():
    """DNA assembly planning interface."""
    st.subheader("DNA Assembly Planning")

    assembly_type = st.selectbox("Assembly Method", [
        "Golden Gate (BsaI/BpiI)", "Gibson Assembly", "In-Fusion Cloning",
        "Restriction/Ligation", "SLIC/CPEC", "Gateway Cloning",
    ])

    col1, col2 = st.columns(2)
    with col1:
        n_fragments = st.number_input("Number of DNA Fragments", 2, 12, 3)
        vector = st.text_input("Destination Vector", value="pET-28a(+)")
        insert_desc = st.text_area(
            "Insert Description",
            value="IKZF1 degradation domain ORF with N-terminal His-tag",
            height=80,
        )

    with col2:
        for i in range(n_fragments):
            st.text_input(f"Fragment {i+1} Description", key=f"frag_{i}",
                          value=f"Fragment {i+1}" if i > 0 else "Vector backbone")

    if st.button("🔧 Plan Assembly", type="primary", use_container_width=True):
        fragments = [st.session_state.get(f"frag_{i}", f"Fragment {i+1}") for i in range(n_fragments)]
        query = (
            f"Design a {assembly_type} strategy to assemble {n_fragments} fragments "
            f"into {vector}. Insert: {insert_desc}. Fragments: {', '.join(fragments)}. "
            f"Provide primer sequences with overhangs, assembly order, expected sizes, "
            f"and a verification strategy (colony PCR primers, diagnostic digest)."
        )
        _run_and_display(query)


def _render_crispr_design():
    """CRISPR guide RNA design interface."""
    st.subheader("CRISPR Guide RNA Design")

    col1, col2 = st.columns(2)
    with col1:
        target_gene = st.text_input("Target Gene", value="BRD4")
        organism = st.selectbox("Organism", ["Human", "Mouse", "Rat", "Zebrafish", "Drosophila"],
                                key="crispr_organism")
        cas_system = st.selectbox("Cas System", [
            "SpCas9 (NGG PAM)", "SaCas9 (NNGRRT PAM)", "Cas12a/Cpf1 (TTTV PAM)",
            "CasX", "Base Editor (CBE)", "Base Editor (ABE)", "Prime Editor",
        ])

    with col2:
        edit_type = st.selectbox("Edit Type", [
            "Knockout (frameshift)", "Knock-in (HDR)", "CRISPRi (repression)",
            "CRISPRa (activation)", "Base edit", "Prime edit",
        ])
        target_region = st.selectbox("Target Region", [
            "Early exon (exon 2-4)", "Functional domain", "Promoter region",
            "Splice site", "Custom locus",
        ])
        n_guides = st.slider("Number of guides", 1, 10, 3)

    if st.button("✂️ Design Guides", type="primary", use_container_width=True):
        query = (
            f"Design {n_guides} CRISPR guide RNAs for {edit_type} of {target_gene} "
            f"in {organism} using {cas_system}. Target {target_region}. "
            f"Provide guide sequences, PAM sites, on-target scores, off-target analysis, "
            f"and recommended delivery method."
        )
        _run_and_display(query)

    with st.expander("💡 Example Guide Design Output"):
        guide_df = pd.DataFrame({
            "Guide #": [1, 2, 3],
            "Sequence (20-mer)": ["AGCTGATCGTACCGATCGTA", "TGCATCGATCGTACGATCGA", "GCATCGATCGTAGCTAGCTA"],
            "PAM": ["AGG", "TGG", "CGG"],
            "Position": ["Exon 2", "Exon 3", "Exon 3"],
            "On-Target Score": [0.85, 0.79, 0.91],
            "Off-Targets (0-3 mm)": [2, 5, 1],
            "Recommendation": ["Primary", "Backup", "Highest specificity"],
        })
        st.dataframe(guide_df, use_container_width=True, hide_index=True)


def _render_freeform_agent():
    """Free-form molecular design agent."""
    st.subheader("Free-Form Molecular Design Agent")
    st.markdown("Ask any molecular biology design question in natural language.")

    # Pre-built examples from gallery
    with st.expander("📦 Load a pre-built example", expanded=False):
        for ex_name, ex in MOLECULAR_EXAMPLES.items():
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{ex_name}**")
                st.caption(ex["description"])
            with col_btn:
                if st.button("Load", key=f"mol_load_{ex_name}", use_container_width=True):
                    st.session_state["_molecular_example_query"] = ex["query"]
                    st.rerun()

    # Additional inline examples
    examples = {
        "Mutagenesis Library": "Design a site-saturation mutagenesis library for BRD4 bromodomain residues 80-85 using NNK codons. Include primer design and expected library size.",
        "Reporter Assay": "Design a luciferase reporter construct for measuring CRBN-dependent degradation. Include CRE element, minimal promoter, and control constructs.",
    }

    with st.expander("💡 More example queries"):
        for name, q in examples.items():
            st.markdown(f"**{name}:** {q}")

    # Use pre-loaded example query if available
    default_query = st.session_state.pop("_molecular_example_query", "")

    query = st.text_area(
        "Your molecular design question",
        value=default_query,
        height=120,
        placeholder="Ask anything about primer design, codon optimization, assembly planning, CRISPR design...",
    )

    if st.button("🚀 Run Agent", type="primary", use_container_width=True) and query:
        _run_and_display(query)


def _run_and_display(query: str):
    """Common function to run agent and display results."""
    wb_config = WorkbenchConfig.load()
    with st.spinner("🧬 Agent is working on your molecular design..."):
        response = run_celltype_query(query, wb_config)

    st.markdown("---")
    st.markdown(response.content)

    if response.tools_used:
        with st.expander("🔧 Tools Used"):
            for t in response.tools_used:
                st.markdown(f"- {t}")

    st.caption(f"⏱ {response.duration:.1f}s | 💰 ${response.cost:.4f}")

    report_path = save_report("molecular_design", f"# Molecular Design\n\n**Query:** {query}\n\n{response.content}")
    st.success(f"Report saved: {report_path}")
