"""
Reusable Streamlit components for Energy Document AI
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import pandas as pd

def create_metrics_dashboard(stats: Dict[str, Any]) -> None:
    """Create a metrics dashboard"""
    if not stats:
        st.warning("No statistics available")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Documents", 
            stats.get('total_documents', 0),
            help="Number of unique documents processed"
        )

    with col2:
        st.metric(
            "Total Chunks", 
            stats.get('total_points', 0),
            help="Number of text chunks in vector database"
        )

    with col3:
        avg_chunks = stats.get('total_points', 0) / max(stats.get('total_documents', 1), 1)
        st.metric(
            "Avg Chunks/Doc", 
            f"{avg_chunks:.1f}",
            help="Average chunks per document"
        )

def create_document_type_chart(doc_types: Dict[str, int]) -> None:
    """Create document type distribution chart"""
    if not doc_types:
        st.info("No document type data available")
        return

    fig = px.pie(
        values=list(doc_types.values()),
        names=list(doc_types.keys()),
        title="Document Type Distribution"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_relevance_chart(chat_history: List[Dict]) -> None:
    """Create relevance score trend chart"""
    if not chat_history:
        st.info("No query history available")
        return

    scores = [entry['response']['relevance_score'] for entry in chat_history]
    queries = [f"Query {i+1}" for i in range(len(scores))]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=queries,
        y=scores,
        mode='lines+markers',
        name='Relevance Score',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8)
    ))

    fig.add_hline(y=0.75, line_dash="dash", line_color="green", 
                  annotation_text="High Relevance Threshold")
    fig.add_hline(y=0.5, line_dash="dash", line_color="orange", 
                  annotation_text="Medium Relevance Threshold")

    fig.update_layout(
        title="Query Relevance Score Trend",
        xaxis_title="Query",
        yaxis_title="Relevance Score",
        yaxis=dict(range=[0, 1]),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

def create_processing_status(status: str, progress: float = 0) -> None:
    """Create processing status display"""
    if status == "processing":
        st.info(f"🔄 Processing document... {progress:.0%}")
        st.progress(progress)
    elif status == "complete":
        st.success("✅ Document processing complete!")
    elif status == "error":
        st.error("❌ Document processing failed")
    else:
        st.info("Ready to process documents")

def create_query_suggestions(document_types: List[str]) -> List[str]:
    """Generate query suggestions based on document types"""
    suggestions = {
        "regulatory": [
            "What are the NERC compliance requirements?",
            "Explain the regulatory framework for grid operations",
            "What are the environmental compliance standards?"
        ],
        "technical": [
            "What are the equipment specifications?",
            "Describe the installation procedures",
            "What are the performance metrics?"
        ],
        "safety": [
            "What are the safety protocols?",
            "Describe the emergency procedures",
            "What are the hazard mitigation strategies?"
        ],
        "grid": [
            "Explain the grid interconnection requirements",
            "What are the transmission standards?",
            "Describe the load balancing procedures"
        ]
    }

    all_suggestions = []
    for doc_type in document_types:
        if doc_type in suggestions:
            all_suggestions.extend(suggestions[doc_type])

    return all_suggestions[:5]  # Return top 5 suggestions

def display_search_results(results: List[Dict], max_results: int = 10) -> None:
    """Display formatted search results"""
    if not results:
        st.info("No results found")
        return

    for i, result in enumerate(results[:max_results]):
        with st.expander(f"📄 {result['document_name']} (Score: {result['score']:.3f})"):
            st.markdown(f"**Document Type:** {result['document_type']}")
            st.markdown(f"**Content Preview:**")
            st.markdown(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])

            if 'metadata' in result and result['metadata']:
                st.markdown("**Metadata:**")
                metadata_df = pd.DataFrame([result['metadata']])
                st.dataframe(metadata_df, use_container_width=True)

def create_cost_estimator(num_pages: int, dpi: int = 300) -> None:
    """Create cost estimation display"""
    base_cost = 0.02  # Approximate cost per page
    dpi_multiplier = dpi / 300
    estimated_cost = num_pages * base_cost * dpi_multiplier

    st.info(f"""
    📊 **Processing Cost Estimate**
    - Pages: {num_pages}
    - DPI: {dpi}
    - Estimated Cost: ${estimated_cost:.2f}

    *Note: This is an approximation based on OpenAI API pricing*
    """)

def create_system_status() -> None:
    """Create system status indicator"""
    col1, col2 = st.columns(2)

    with col1:
        st.success("🟢 OpenAI API: Connected")

    with col2:
        try:
            # This would need actual Qdrant connection check
            st.success("🟢 Qdrant: Connected")
        except:
            st.error("🔴 Qdrant: Disconnected")
