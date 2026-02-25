"""Data Management page — dataset downloads, paths, and status."""

import streamlit as st
import subprocess

from utils.config import WorkbenchConfig, DATASETS, ensure_dirs
from utils.celltype_agent import check_celltype_installed


def render_data_management():
    """Render the data management page."""
    st.title("📁 Data Management")
    st.caption("Download, configure, and manage local datasets for offline analysis.")

    tab_status, tab_download, tab_config = st.tabs([
        "📊 Dataset Status", "📥 Download Datasets", "⚙️ Path Configuration",
    ])

    with tab_status:
        _render_status()

    with tab_download:
        _render_download()

    with tab_config:
        _render_path_config()


def _render_status():
    """Show dataset availability status."""
    st.subheader("Dataset Availability")

    config = WorkbenchConfig.load()

    path_map = {
        "depmap": config.depmap_path,
        "prism": config.prism_path,
        "msigdb": config.msigdb_path,
        "alphafold": "",
    }

    for key, ds in DATASETS.items():
        path = path_map.get(key, "")
        status = "🟢 Configured" if path else "🔴 Not configured"

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{ds['name']}** — {status}")
                st.caption(ds["description"])
                if path:
                    st.code(path, language=None)
                else:
                    st.caption(f"Size: {ds['size']} | Command: `{ds['command']}`")
            with col2:
                st.markdown(f"**{ds['size']}**")

    st.divider()
    st.markdown("#### Without Local Data")
    st.info(
        "Without local datasets, the agent falls back to 30+ public APIs "
        "(PubMed, ChEMBL, UniProt, etc.). This is slower but fully functional "
        "for most queries."
    )


def _render_download():
    """Dataset download interface."""
    st.subheader("Download Datasets")

    ct = check_celltype_installed()
    if not ct["installed"]:
        st.warning(
            "celltype-cli is not installed. Install it first:\n\n"
            "```bash\npip install celltype-cli\n```"
        )
        st.markdown("After installation, come back here to download datasets.")
        return

    st.markdown(
        "Click below to generate terminal commands for dataset downloads. "
        "These commands should be run in your terminal (not in the browser)."
    )

    for key, ds in DATASETS.items():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{ds['name']}**")
                st.caption(f"{ds['description']}")
            with col2:
                st.code(ds["command"], language="bash")

    st.divider()

    st.markdown("#### Quick Download Script")
    script = """#!/bin/bash
# Download all celltype-cli datasets
echo "Starting dataset downloads..."

ct data pull depmap     # ~15 GB
ct data pull prism      # ~5 GB
ct data pull msigdb     # ~500 MB
ct data pull alphafold  # On-demand

echo "Done! Configure paths with: ct config set data.<name> /path/"
"""
    st.code(script, language="bash")
    st.download_button(
        "📥 Download Script",
        script,
        "download_datasets.sh",
        "text/plain",
    )


def _render_path_config():
    """Configure dataset paths."""
    st.subheader("Dataset Path Configuration")

    config = WorkbenchConfig.load()

    st.markdown("Point to your locally downloaded datasets:")

    config.data_dir = st.text_input(
        "Base Data Directory",
        value=config.data_dir,
    )

    config.depmap_path = st.text_input(
        "DepMap Data Path",
        value=config.depmap_path,
        placeholder="e.g., /data/depmap/2024Q4/",
    )

    config.prism_path = st.text_input(
        "PRISM Data Path",
        value=config.prism_path,
        placeholder="e.g., /data/prism/",
    )

    config.msigdb_path = st.text_input(
        "MSigDB Data Path",
        value=config.msigdb_path,
        placeholder="e.g., /data/msigdb/",
    )

    if st.button("💾 Save Paths", type="primary"):
        config.save()
        st.success("Dataset paths saved!")

    st.divider()

    st.markdown("#### CLI Path Configuration")
    st.markdown("You can also set paths via the command line:")
    st.code("""ct config set data.depmap /path/to/depmap/
ct config set data.prism /path/to/prism/
ct config set data.msigdb /path/to/msigdb/""", language="bash")
