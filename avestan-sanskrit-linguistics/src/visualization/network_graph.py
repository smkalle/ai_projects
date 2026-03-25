"""
network_graph.py — Build and render PII root → language branch network graphs
using NetworkX + Plotly.

Produces directed graphs in which Proto-Indo-Iranian (PII) reconstructed roots
fan out to attested Avestan and Sanskrit reflexes.  Edge weights reflect
phonological similarity scores where available.  Rendering uses Plotly for
interactive HTML figures.
"""

from __future__ import annotations

import networkx as nx
import pandas as pd
import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# Colour / style constants
# ---------------------------------------------------------------------------

_NODE_COLOURS: dict[str, str] = {
    'root':     'gold',
    'avestan':  'royalblue',
    'sanskrit': 'crimson',
}

_DEFAULT_NODE_SIZE_BASE = 12  # minimum node marker size in px
_EDGE_COLOUR = 'rgba(150, 150, 150, 0.5)'


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_cognate_network(cognates_df: pd.DataFrame) -> nx.DiGraph:
    """Build a directed cognate network from a cognate-pair DataFrame.

    The graph has three node types:

    * **root** — PII reconstructed root, labelled ``*<root>`` (e.g. ``*daiva``).
    * **avestan** — Avestan reflex.
    * **sanskrit** — Sanskrit reflex.

    Directed edges run from each root node to its Avestan and Sanskrit
    daughter nodes.  Edge weight is taken from the ``ensemble_score`` column
    when present (default 1.0).

    Parameters
    ----------
    cognates_df:
        DataFrame containing cognate pair data.  Expected columns:

        * ``pii_root`` (str) — reconstructed PII root (without asterisk).
        * ``word_av`` (str) — Avestan word form.
        * ``word_sa`` (str) — Sanskrit word form.
        * ``ensemble_score`` (float, optional) — similarity score in [0, 1].
        * ``domain`` (str, optional) — semantic domain label.
        * ``meaning_av`` (str, optional) — Avestan gloss.
        * ``meaning_sa`` (str, optional) — Sanskrit gloss.

    Returns
    -------
    nx.DiGraph
        Directed graph with node attributes ``type`` and ``domain``, and
        edge attribute ``weight``.

    Raises
    ------
    ValueError
        If any of the mandatory columns (``pii_root``, ``word_av``,
        ``word_sa``) are absent.
    """
    required = {'pii_root', 'word_av', 'word_sa'}
    missing = required - set(cognates_df.columns)
    if missing:
        raise ValueError(f"cognates_df is missing required columns: {sorted(missing)}")

    G: nx.DiGraph = nx.DiGraph()

    has_score = 'ensemble_score' in cognates_df.columns
    has_domain = 'domain' in cognates_df.columns
    has_meaning_av = 'meaning_av' in cognates_df.columns
    has_meaning_sa = 'meaning_sa' in cognates_df.columns

    for _, row in cognates_df.iterrows():
        root_label = f"*{row['pii_root']}"
        av_label = str(row['word_av'])
        sa_label = str(row['word_sa'])
        weight = float(row['ensemble_score']) if has_score else 1.0
        domain = str(row['domain']) if has_domain else 'unknown'
        meaning_av = str(row['meaning_av']) if has_meaning_av else ''
        meaning_sa = str(row['meaning_sa']) if has_meaning_sa else ''

        # Add / update root node.
        if root_label not in G:
            G.add_node(root_label, type='root', domain=domain, meaning='')
        else:
            # A root may appear in multiple rows; keep domain consistent.
            if G.nodes[root_label].get('domain', 'unknown') == 'unknown':
                G.nodes[root_label]['domain'] = domain

        # Add Avestan node.
        G.add_node(
            av_label,
            type='avestan',
            domain=domain,
            meaning=meaning_av,
        )

        # Add Sanskrit node.
        G.add_node(
            sa_label,
            type='sanskrit',
            domain=domain,
            meaning=meaning_sa,
        )

        # Add directed edges: root → avestan, root → sanskrit.
        G.add_edge(root_label, av_label, weight=weight)
        G.add_edge(root_label, sa_label, weight=weight)

    return G


# ---------------------------------------------------------------------------
# Plotly rendering helpers
# ---------------------------------------------------------------------------

def _build_plotly_traces(
    G: nx.DiGraph,
    pos: dict[str, tuple[float, float]],
) -> tuple[go.Scatter, go.Scatter]:
    """Return (edge_trace, node_trace) for a Plotly figure."""
    # --- Edge trace ---
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=1, color=_EDGE_COLOUR),
        hoverinfo='none',
        showlegend=False,
        name='edges',
    )

    # --- Node trace ---
    node_x: list[float] = []
    node_y: list[float] = []
    node_colours: list[str] = []
    node_sizes: list[int] = []
    node_text: list[str] = []
    node_hover: list[str] = []

    degrees = dict(G.degree())

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        ntype = G.nodes[node].get('type', 'root')
        meaning = G.nodes[node].get('meaning', '')
        domain = G.nodes[node].get('domain', '')

        node_colours.append(_NODE_COLOURS.get(ntype, 'grey'))
        node_sizes.append(_DEFAULT_NODE_SIZE_BASE + degrees.get(node, 0) * 4)
        node_text.append(node)
        node_hover.append(
            f"<b>{node}</b><br>"
            f"Type: {ntype}<br>"
            f"Domain: {domain}<br>"
            f"Meaning: {meaning or '—'}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            color=node_colours,
            size=node_sizes,
            line=dict(width=1, color='white'),
        ),
        text=node_text,
        textposition='top center',
        hovertext=node_hover,
        hoverinfo='text',
        showlegend=False,
        name='nodes',
    )

    return edge_trace, node_trace


def _legend_traces() -> list[go.Scatter]:
    """Return invisible scatter traces used solely as legend entries."""
    entries = []
    for label, colour in _NODE_COLOURS.items():
        entries.append(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(color=colour, size=10),
                name=label.capitalize(),
                showlegend=True,
            )
        )
    return entries


def render_network_plotly(
    G: nx.DiGraph,
    title: str = "PII Root Cognate Network",
) -> go.Figure:
    """Render the full cognate network as an interactive Plotly figure.

    Uses the Kamada–Kawai force-directed layout for node positioning.

    Parameters
    ----------
    G:
        Directed graph produced by :func:`build_cognate_network`.
    title:
        Figure title string.

    Returns
    -------
    go.Figure
        Plotly figure.  Call ``fig.show()`` or ``fig.write_html(path)`` to
        display or save.
    """
    if len(G) == 0:
        return go.Figure(layout=go.Layout(title=title))

    pos = nx.kamada_kawai_layout(G)
    edge_trace, node_trace = _build_plotly_traces(G, pos)

    fig = go.Figure(
        data=[edge_trace, node_trace, *_legend_traces()],
        layout=go.Layout(
            title=dict(text=title, font=dict(size=18)),
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#1a1a2e',
            paper_bgcolor='#1a1a2e',
            font=dict(color='white'),
            margin=dict(l=20, r=20, t=60, b=20),
        ),
    )
    return fig


def render_domain_subnetwork(G: nx.DiGraph, domain: str) -> go.Figure:
    """Render the subgraph restricted to a single semantic domain.

    Root nodes that connect exclusively to nodes of *domain* are included.
    Avestan and Sanskrit nodes are included only when their ``domain``
    attribute matches *domain*.  Root nodes are included when at least one
    of their neighbours belongs to *domain*.

    Parameters
    ----------
    G:
        Full cognate network.
    domain:
        Semantic domain label (e.g. ``'divine'``, ``'military'``).

    Returns
    -------
    go.Figure
        Interactive Plotly figure for the domain subgraph.
    """
    # Collect nodes belonging to the target domain or connected to them.
    domain_nodes: set[str] = set()
    for node, attrs in G.nodes(data=True):
        if attrs.get('domain') == domain:
            domain_nodes.add(node)

    # Also include root nodes that have at least one neighbour in domain_nodes.
    for node, attrs in G.nodes(data=True):
        if attrs.get('type') == 'root':
            neighbours = set(G.successors(node))
            if neighbours & domain_nodes:
                domain_nodes.add(node)

    sub: nx.DiGraph = G.subgraph(domain_nodes).copy()
    title = f"PII Cognate Network — Domain: {domain.capitalize()}"
    return render_network_plotly(sub, title=title)
