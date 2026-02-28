"""
Design System — ui-design-brain applied to CellType Research Workbench.

Implements core principles from github.com/carmahhawwari/ui-design-brain:
  1. Restraint over decoration — fewer elements, white space is a feature
  2. Typography hierarchy — distinctive display + clean body fonts
  3. One strong color moment — neutral palette, one confident accent
  4. 8px grid spacing — tighter gaps group, generous gaps breathe
  5. Accessibility — WCAG AA contrast, focus indicators, keyboard nav

Design direction: Data Dashboard + Modern SaaS
"""

import streamlit as st
from typing import Optional

# ---------------------------------------------------------------------------
# Design Tokens
# ---------------------------------------------------------------------------

COLORS = {
    # The one strong accent — teal (confident, scientific, not generic AI purple)
    "accent": "#00d4aa",
    "accent_hover": "#00e6b8",
    "accent_muted": "rgba(0, 212, 170, 0.12)",
    "accent_border": "rgba(0, 212, 170, 0.25)",
    # Dark neutral palette
    "bg": "#0f1117",
    "surface": "#161b22",
    "elevated": "#1c2333",
    "overlay": "#232b3a",
    # Borders — subtle, never heavy
    "border": "rgba(255, 255, 255, 0.06)",
    "border_hover": "rgba(255, 255, 255, 0.12)",
    "border_focus": "rgba(0, 212, 170, 0.5)",
    # Text — warm off-whites, not pure white
    "text": "#e6edf3",
    "text_secondary": "#8b949e",
    "text_tertiary": "#6e7681",
    "text_on_accent": "#0f1117",
    # Semantic — muted, not rainbow
    "success": "#3fb950",
    "success_bg": "rgba(63, 185, 80, 0.10)",
    "warning": "#d29922",
    "warning_bg": "rgba(210, 153, 34, 0.10)",
    "error": "#f85149",
    "error_bg": "rgba(248, 81, 73, 0.10)",
    "info": "#58a6ff",
    "info_bg": "rgba(88, 166, 255, 0.10)",
}

# 8px grid spacing scale
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "12px",
    "base": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
    "3xl": "64px",
}

RADIUS = {
    "sm": "4px",
    "md": "6px",
    "lg": "8px",
    "xl": "12px",
    "pill": "9999px",
}

# Typography — distinctive display + clean body (not Inter/Roboto defaults)
FONTS = {
    "display": "'Space Grotesk', system-ui, sans-serif",
    "body": "'DM Sans', system-ui, sans-serif",
    "mono": "'JetBrains Mono', 'Fira Code', monospace",
}


# ---------------------------------------------------------------------------
# Plotly chart theme — consistent with design system
# ---------------------------------------------------------------------------

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=COLORS["surface"],
    font=dict(family="DM Sans, system-ui, sans-serif", color=COLORS["text_secondary"], size=13),
    title=dict(font=dict(family="Space Grotesk, system-ui, sans-serif", size=16, color=COLORS["text"]), x=0),
    xaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
    yaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
    colorway=[
        COLORS["accent"], "#58a6ff", "#f0883e", "#a371f7",
        "#3fb950", "#d29922", "#f85149", "#79c0ff",
    ],
    margin=dict(l=48, r=16, t=48, b=40),
    hoverlabel=dict(bgcolor=COLORS["elevated"], font_color=COLORS["text"], bordercolor=COLORS["border"]),
)


def apply_plotly_theme(fig):
    """Apply the design system theme to any Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ---------------------------------------------------------------------------
# Global CSS — injected once via app.py
# ---------------------------------------------------------------------------

def get_global_css() -> str:
    """Return comprehensive CSS implementing ui-design-brain principles."""
    return f"""
<style>
/* ================================================================
   FONTS — distinctive display + clean body (not Inter/Roboto)
   ================================================================ */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ================================================================
   ROOT VARIABLES — single source of truth
   ================================================================ */
:root {{
    --accent: {COLORS["accent"]};
    --accent-hover: {COLORS["accent_hover"]};
    --accent-muted: {COLORS["accent_muted"]};
    --accent-border: {COLORS["accent_border"]};
    --bg: {COLORS["bg"]};
    --surface: {COLORS["surface"]};
    --elevated: {COLORS["elevated"]};
    --overlay: {COLORS["overlay"]};
    --border: {COLORS["border"]};
    --border-hover: {COLORS["border_hover"]};
    --border-focus: {COLORS["border_focus"]};
    --text: {COLORS["text"]};
    --text-secondary: {COLORS["text_secondary"]};
    --text-tertiary: {COLORS["text_tertiary"]};
    --text-on-accent: {COLORS["text_on_accent"]};
    --success: {COLORS["success"]};
    --warning: {COLORS["warning"]};
    --error: {COLORS["error"]};
    --info: {COLORS["info"]};
    --font-display: {FONTS["display"]};
    --font-body: {FONTS["body"]};
    --font-mono: {FONTS["mono"]};
    --radius-sm: {RADIUS["sm"]};
    --radius-md: {RADIUS["md"]};
    --radius-lg: {RADIUS["lg"]};
    --radius-xl: {RADIUS["xl"]};
    --radius-pill: {RADIUS["pill"]};
    --space-xs: {SPACING["xs"]};
    --space-sm: {SPACING["sm"]};
    --space-md: {SPACING["md"]};
    --space-base: {SPACING["base"]};
    --space-lg: {SPACING["lg"]};
    --space-xl: {SPACING["xl"]};
    --space-2xl: {SPACING["2xl"]};
    --transition: 200ms ease-out;
}}

/* ================================================================
   BASE — font smoothing, body font
   ================================================================ */
html, body, [data-testid="stAppViewContainer"] {{
    font-family: var(--font-body) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* ================================================================
   TYPOGRAPHY — heading hierarchy (Space Grotesk display)
   ================================================================ */
h1, h2, h3, .stTitle, [data-testid="stHeading"] {{
    font-family: var(--font-display) !important;
    letter-spacing: -0.02em;
}}

h1 {{ font-weight: 700 !important; }}
h2 {{ font-weight: 600 !important; }}
h3, h4, h5 {{ font-weight: 500 !important; }}

/* Body text: minimum 14px (brain: no tiny text <12px, prefer 16px) */
p, li, span, label, .stMarkdown {{
    font-size: 14px;
}}

/* Code blocks */
code, pre, .stCode, [data-testid="stCode"] {{
    font-family: var(--font-mono) !important;
    font-size: 13px !important;
}}

/* ================================================================
   HEADER — transparent, minimal
   ================================================================ */
.stApp header {{
    background-color: transparent !important;
}}

/* ================================================================
   SIDEBAR — darker surface, grouped navigation
   ================================================================ */
[data-testid="stSidebar"] {{
    background-color: #0a0e14 !important;
    border-right: 1px solid var(--border) !important;
}}

[data-testid="stSidebar"] [data-testid="stMarkdown"] h2 {{
    font-size: 1.25rem !important;
}}

/* Sidebar nav section headers */
.nav-section-header {{
    font-family: var(--font-display);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-tertiary);
    padding: 12px 0 4px 0;
    margin: 0;
}}

/* ================================================================
   METRIC CARDS — clean, border only (not both shadow AND border)
   ================================================================ */
[data-testid="stMetric"] {{
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 16px;
    transition: border-color var(--transition);
}}
[data-testid="stMetric"]:hover {{
    border-color: var(--border-hover);
}}
[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
    font-family: var(--font-body);
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    font-family: var(--font-display);
    font-weight: 700;
    color: var(--text);
}}

/* ================================================================
   CONTAINERS & CARDS — border only, no shadow
   ================================================================ */
[data-testid="stExpander"] {{
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    transition: border-color var(--transition);
}}
[data-testid="stExpander"]:hover {{
    border-color: var(--border-hover) !important;
}}

/* Bordered containers (st.container(border=True)) */
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    background-color: var(--surface) !important;
    transition: border-color var(--transition);
}}
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: var(--border-hover) !important;
}}

/* ================================================================
   TABS — clear active indicator, proper spacing
   ================================================================ */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    border-bottom: 1px solid var(--border);
}}

.stTabs [data-baseweb="tab"] {{
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 0.875rem;
    padding: 10px 20px;
    border-radius: 0;
    color: var(--text-secondary);
    border-bottom: 2px solid transparent;
    transition: color var(--transition), border-color var(--transition);
    min-height: 44px; /* touch target */
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: var(--text);
}}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    font-weight: 600;
}}

/* ================================================================
   BUTTONS — verb-first, primary/secondary hierarchy
   ================================================================ */
.stButton > button {{
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    border-radius: var(--radius-lg) !important;
    padding: 8px 20px !important;
    min-height: 44px !important; /* 44px touch targets */
    transition: all var(--transition) !important;
    letter-spacing: 0.01em;
}}

/* Primary button — accent color */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {{
    background-color: var(--accent) !important;
    color: var(--text-on-accent) !important;
    border: none !important;
    font-weight: 700 !important;
}}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {{
    background-color: var(--accent-hover) !important;
    box-shadow: 0 0 0 3px var(--accent-muted) !important;
}}

/* Secondary button — subtle, ghost-like */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="stBaseButton-secondary"] {{
    background-color: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
}}
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="stBaseButton-secondary"]:hover {{
    border-color: var(--border-hover) !important;
    color: var(--text) !important;
    background-color: var(--surface) !important;
}}

/* Download button */
.stDownloadButton > button {{
    font-family: var(--font-body) !important;
    font-weight: 500 !important;
    font-size: 0.8125rem !important;
    border-radius: var(--radius-lg) !important;
    padding: 8px 16px !important;
    min-height: 40px !important;
    background-color: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    transition: all var(--transition) !important;
}}
.stDownloadButton > button:hover {{
    border-color: var(--accent-border) !important;
    color: var(--accent) !important;
}}

/* ================================================================
   FORM INPUTS — labels above, clean borders
   ================================================================ */
.stTextInput > label, .stTextArea > label, .stSelectbox > label,
.stMultiSelect > label, .stSlider > label, .stNumberInput > label,
.stCheckbox > label, .stRadio > label {{
    font-family: var(--font-body) !important;
    font-weight: 500 !important;
    font-size: 0.8125rem !important;
    color: var(--text-secondary) !important;
}}

.stTextInput input, .stTextArea textarea {{
    font-family: var(--font-body) !important;
    border-radius: var(--radius-md) !important;
    border-color: var(--border) !important;
    transition: border-color var(--transition) !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-muted) !important;
}}

/* Placeholder as format hint, never label replacement */
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{
    color: var(--text-tertiary) !important;
    font-style: italic;
}}

/* ================================================================
   CHAT — clean message bubbles
   ================================================================ */
.stChatMessage {{
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border);
    padding: 16px !important;
}}

[data-testid="stChatInput"] {{
    border-radius: var(--radius-lg) !important;
}}

[data-testid="stChatInput"] textarea {{
    font-family: var(--font-body) !important;
}}

/* ================================================================
   DATA TABLES — clean borders, right-aligned numbers
   ================================================================ */
.stDataFrame {{
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border) !important;
}}

/* Table headers */
.stDataFrame th {{
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.8125rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-secondary) !important;
}}

/* ================================================================
   ALERTS & STATUS — semantic colors, not rainbow
   ================================================================ */
[data-testid="stAlert"] {{
    border-radius: var(--radius-lg) !important;
    font-family: var(--font-body) !important;
    font-size: 0.875rem !important;
    border-left-width: 3px !important;
}}

/* ================================================================
   DIVIDERS — subtle
   ================================================================ */
hr, [data-testid="stDivider"] {{
    border-color: var(--border) !important;
    margin: 24px 0 !important;
}}

/* ================================================================
   PROGRESS BAR
   ================================================================ */
.stProgress > div > div {{
    background-color: var(--accent) !important;
    border-radius: var(--radius-pill) !important;
}}

/* ================================================================
   SCROLLBAR — slim, unobtrusive
   ================================================================ */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: var(--text-tertiary);
    border-radius: var(--radius-pill);
}}
::-webkit-scrollbar-thumb:hover {{
    background: var(--text-secondary);
}}

/* ================================================================
   FOCUS INDICATORS — accessibility required
   ================================================================ */
*:focus-visible {{
    outline: 2px solid var(--accent) !important;
    outline-offset: 2px !important;
    border-radius: var(--radius-sm);
}}

/* ================================================================
   CAPTIONS — consistent muted styling
   ================================================================ */
.stCaption, [data-testid="stCaption"] {{
    color: var(--text-tertiary) !important;
    font-size: 0.8125rem !important;
}}

/* ================================================================
   FOOTER — minimal, centered
   ================================================================ */
.workbench-footer {{
    text-align: center;
    padding: 32px 0 16px 0;
    color: var(--text-tertiary);
    font-size: 0.75rem;
    font-family: var(--font-body);
    border-top: 1px solid var(--border);
    margin-top: 48px;
}}
.workbench-footer a {{
    color: var(--text-secondary);
    text-decoration: none;
    transition: color var(--transition);
}}
.workbench-footer a:hover {{
    color: var(--accent);
}}

/* ================================================================
   RESPONSIVE — hide/show at breakpoints
   ================================================================ */
@media (max-width: 768px) {{
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.75rem;
        padding: 8px 12px;
    }}
}}
</style>
"""


# ---------------------------------------------------------------------------
# UI Helper Components
# ---------------------------------------------------------------------------

def render_section_header(label: str):
    """Render a nav section header (uppercase, small, muted)."""
    st.markdown(f'<p class="nav-section-header">{label}</p>', unsafe_allow_html=True)


def render_empty_state(
    headline: str,
    description: str,
    icon: str = "",
    cta_label: Optional[str] = None,
):
    """Render a proper empty state: icon + headline + description + optional CTA.

    Brain rule: Empty states need illustration + helpful headline + primary CTA.
    """
    html = f"""
    <div style="
        text-align: center;
        padding: 48px 24px;
        color: var(--text-secondary);
    ">
        <div style="font-size: 2.5rem; margin-bottom: 12px; opacity: 0.6;">{icon}</div>
        <h3 style="
            font-family: var(--font-display);
            font-weight: 600;
            color: var(--text);
            margin: 0 0 8px 0;
            font-size: 1.125rem;
        ">{headline}</h3>
        <p style="
            font-family: var(--font-body);
            color: var(--text-secondary);
            margin: 0;
            font-size: 0.875rem;
            max-width: 400px;
            margin: 0 auto;
            line-height: 1.5;
        ">{description}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_status_badge(label: str, variant: str = "default"):
    """Render a small status badge.

    Brain rule: 1-2 words, pill shape, limited color palette (no rainbow).
    """
    colors = {
        "success": (COLORS["success"], COLORS["success_bg"]),
        "warning": (COLORS["warning"], COLORS["warning_bg"]),
        "error": (COLORS["error"], COLORS["error_bg"]),
        "info": (COLORS["info"], COLORS["info_bg"]),
        "accent": (COLORS["accent"], COLORS["accent_muted"]),
        "default": (COLORS["text_secondary"], "rgba(139, 148, 158, 0.1)"),
    }
    fg, bg = colors.get(variant, colors["default"])
    return f"""<span style="
        display: inline-block;
        padding: 2px 10px;
        border-radius: {RADIUS["pill"]};
        font-size: 0.75rem;
        font-weight: 500;
        font-family: var(--font-body);
        color: {fg};
        background: {bg};
    ">{label}</span>"""


def render_kpi_row(metrics: list[tuple[str, str, Optional[str]]]):
    """Render a row of KPI metrics with clear hierarchy.

    Brain rule: KPI → trend → detail. Clear metric hierarchy.
    metrics: list of (label, value, detail) tuples
    """
    cols = st.columns(len(metrics))
    for col, (label, value, detail) in zip(cols, metrics):
        with col:
            st.metric(label, value, help=detail)
