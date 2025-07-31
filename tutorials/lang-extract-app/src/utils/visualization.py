"""Visualization utilities for extraction results."""

import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import json


logger = logging.getLogger(__name__)


def create_extraction_chart(results: List[Any]) -> go.Figure:
    """Create overview chart of extraction results."""
    try:
        # Prepare data
        data = []
        for result in results:
            data.append({
                "Source": result.source_file[:30] + "..." if len(result.source_file) > 30 else result.source_file,
                "Template": result.template_used,
                "Extractions": len(result.extractions),
                "Processing Time": result.processing_time
            })
        
        df = pd.DataFrame(data)
        
        # Create subplots
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Extractions by Source", "Processing Time by Source",
                          "Template Distribution", "Extraction Efficiency"),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "scatter"}]]
        )
        
        # Bar chart - Extractions by source
        fig.add_trace(
            go.Bar(
                x=df["Source"],
                y=df["Extractions"],
                name="Extractions",
                marker_color="#0066CC"
            ),
            row=1, col=1
        )
        
        # Bar chart - Processing time by source
        fig.add_trace(
            go.Bar(
                x=df["Source"],
                y=df["Processing Time"],
                name="Processing Time (s)",
                marker_color="#00A86B"
            ),
            row=1, col=2
        )
        
        # Pie chart - Template distribution
        template_counts = df["Template"].value_counts()
        fig.add_trace(
            go.Pie(
                labels=template_counts.index,
                values=template_counts.values,
                name="Templates"
            ),
            row=2, col=1
        )
        
        # Scatter plot - Efficiency (extractions vs time)
        fig.add_trace(
            go.Scatter(
                x=df["Processing Time"],
                y=df["Extractions"],
                mode="markers+text",
                text=df["Source"].str[:10],
                textposition="top center",
                marker=dict(size=10, color="#FF6B35"),
                name="Efficiency"
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Extraction Analysis Dashboard",
            title_font_size=20
        )
        
        # Update axes
        fig.update_xaxes(tickangle=-45, row=1, col=1)
        fig.update_xaxes(tickangle=-45, row=1, col=2)
        fig.update_xaxes(title_text="Processing Time (s)", row=2, col=2)
        fig.update_yaxes(title_text="Number of Extractions", row=2, col=2)
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to create extraction chart: {e}")
        # Return empty figure on error
        return go.Figure()


def create_word_cloud(extraction_data: List[Dict[str, Any]]) -> plt.Figure:
    """Create word cloud from extracted text data."""
    try:
        # Collect all text
        all_text = []
        
        for item in extraction_data:
            for key, value in item.items():
                if isinstance(value, str) and len(value) > 10:
                    all_text.append(value)
                elif isinstance(value, list):
                    for v in value:
                        if isinstance(v, str):
                            all_text.append(v)
        
        # Join all text
        combined_text = " ".join(all_text)
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='Blues',
            max_words=100,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(combined_text)
        
        # Create figure
        fig = plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title("Key Terms from Extractions", fontsize=16, pad=20)
        plt.tight_layout()
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to create word cloud: {e}")
        # Return empty figure on error
        fig = plt.figure(figsize=(10, 5))
        plt.text(0.5, 0.5, "Word cloud generation failed", 
                ha='center', va='center', fontsize=14)
        plt.axis('off')
        return fig


def create_entity_network(extraction_data: List[Dict[str, Any]]) -> go.Figure:
    """Create network graph of relationships between extracted entities."""
    try:
        # Extract relationships
        edges = []
        nodes = set()
        
        for item in extraction_data:
            # Look for relationship fields
            if "character" in item and "relationship" in item:
                source = item["character"]
                if isinstance(item["relationship"], str) and " " in item["relationship"]:
                    # Try to extract target from relationship text
                    words = item["relationship"].split()
                    for word in words:
                        if word.istitle() and word != source:
                            edges.append((source, word))
                            nodes.add(source)
                            nodes.add(word)
        
        if not edges:
            # Return empty figure if no relationships found
            fig = go.Figure()
            fig.add_annotation(
                text="No entity relationships found",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Create network layout
        import networkx as nx
        G = nx.Graph()
        G.add_edges_from(edges)
        
        # Generate positions
        pos = nx.spring_layout(G)
        
        # Create edge traces
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=1, color='#888'),
                    hoverinfo='none'
                )
            )
        
        # Create node trace
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode='markers+text',
            text=list(G.nodes()),
            textposition="top center",
            marker=dict(
                size=20,
                color='#0066CC',
                line=dict(width=2, color='white')
            ),
            hoverinfo='text'
        )
        
        # Create figure
        fig = go.Figure(
            data=edge_trace + [node_trace],
            layout=go.Layout(
                title="Entity Relationship Network",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to create entity network: {e}")
        return go.Figure()


def create_timeline_visualization(extraction_data: List[Dict[str, Any]]) -> go.Figure:
    """Create timeline visualization for temporal data."""
    try:
        # Extract temporal data
        timeline_data = []
        
        for item in extraction_data:
            # Look for date/time fields
            if "date" in item or "year" in item or "timestamp" in item:
                date_value = item.get("date") or item.get("year") or item.get("timestamp")
                event = item.get("event") or item.get("finding") or "Event"
                
                timeline_data.append({
                    "Date": date_value,
                    "Event": event[:50] + "..." if len(str(event)) > 50 else event,
                    "Source": item.get("Source", "Unknown")
                })
        
        if not timeline_data:
            # Return empty figure if no temporal data
            fig = go.Figure()
            fig.add_annotation(
                text="No temporal data found",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Create timeline
        df = pd.DataFrame(timeline_data)
        
        fig = px.timeline(
            df,
            x_start="Date",
            x_end="Date",
            y="Event",
            color="Source",
            title="Temporal Event Timeline"
        )
        
        fig.update_layout(height=400)
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to create timeline: {e}")
        return go.Figure()


def create_statistical_summary(extraction_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate statistical summary of extractions."""
    try:
        summary = {
            "total_extractions": len(extraction_data),
            "field_frequency": {},
            "value_distributions": {},
            "common_patterns": []
        }
        
        # Count field frequency
        field_counter = Counter()
        for item in extraction_data:
            if isinstance(item, dict):
                field_counter.update(item.keys())
        
        summary["field_frequency"] = dict(field_counter.most_common(10))
        
        # Analyze value distributions for common fields
        for field in ["diagnosis", "drug_name", "outcome", "finding"]:
            values = []
            for item in extraction_data:
                if field in item:
                    value = item[field]
                    if isinstance(value, str):
                        values.append(value)
                    elif isinstance(value, list):
                        values.extend(value)
            
            if values:
                value_counter = Counter(values)
                summary["value_distributions"][field] = dict(value_counter.most_common(5))
        
        # Identify common patterns
        text_lengths = [len(str(item)) for item in extraction_data]
        if text_lengths:
            summary["common_patterns"] = {
                "avg_extraction_length": sum(text_lengths) / len(text_lengths),
                "min_length": min(text_lengths),
                "max_length": max(text_lengths)
            }
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to create statistical summary: {e}")
        return {}