"""Responsive layout components for mobile-first design."""

import streamlit as st
from typing import List, Optional, Dict, Any

def create_responsive_grid(columns: List[Dict[str, Any]], gap: str = "var(--space-6)") -> str:
    """Create a responsive grid layout."""
    
    # Generate grid template columns based on breakpoints
    grid_cols = []
    for col in columns:
        desktop = col.get('desktop', 1)
        tablet = col.get('tablet', desktop)
        mobile = col.get('mobile', 1)
        
        grid_cols.append(f"repeat({desktop}, 1fr)")
    
    return f"""
    <style>
    .responsive-grid {{
        display: grid;
        grid-template-columns: {' '.join(grid_cols)};
        gap: {gap};
        width: 100%;
    }}
    
    @media (max-width: 1024px) {{
        .responsive-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
    
    @media (max-width: 640px) {{
        .responsive-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    
    <div class="responsive-grid">
    """

def create_mobile_navigation() -> str:
    """Create mobile-friendly navigation."""
    return """
    <style>
    .mobile-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid var(--gray-200);
        padding: var(--space-3);
        display: none;
        z-index: 1000;
        box-shadow: 0 -4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .mobile-nav-items {
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
    
    .mobile-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-decoration: none;
        color: var(--gray-600);
        font-size: 0.75rem;
        font-weight: 500;
        padding: var(--space-2);
        border-radius: var(--radius-md);
        transition: all 0.2s ease;
    }
    
    .mobile-nav-item:hover,
    .mobile-nav-item.active {
        color: var(--primary);
        background: var(--gray-50);
    }
    
    .mobile-nav-icon {
        font-size: 1.25rem;
        margin-bottom: var(--space-1);
    }
    
    @media (max-width: 768px) {
        .mobile-nav {
            display: block;
        }
        
        .desktop-sidebar {
            display: none;
        }
        
        .main-content {
            padding-bottom: 80px;
        }
    }
    </style>
    
    <div class="mobile-nav">
        <div class="mobile-nav-items">
            <a href="#" class="mobile-nav-item active">
                <div class="mobile-nav-icon">🏠</div>
                <span>Home</span>
            </a>
            <a href="#" class="mobile-nav-item">
                <div class="mobile-nav-icon">📄</div>
                <span>Upload</span>
            </a>
            <a href="#" class="mobile-nav-item">
                <div class="mobile-nav-icon">📊</div>
                <span>Dashboard</span>
            </a>
            <a href="#" class="mobile-nav-item">
                <div class="mobile-nav-icon">⚖️</div>
                <span>Compliance</span>
            </a>
            <a href="#" class="mobile-nav-item">
                <div class="mobile-nav-icon">📝</div>
                <span>Reports</span>
            </a>
        </div>
    </div>
    """

def create_responsive_sidebar(content: str, width: str = "300px") -> str:
    """Create responsive sidebar that collapses on mobile."""
    return f"""
    <style>
    .responsive-sidebar {{
        width: {width};
        height: 100vh;
        background: white;
        border-right: 1px solid var(--gray-200);
        padding: var(--space-6);
        overflow-y: auto;
        position: fixed;
        left: 0;
        top: 0;
        z-index: 100;
        transition: transform 0.3s ease;
    }}
    
    .sidebar-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 99;
        display: none;
    }}
    
    .main-container {{
        margin-left: {width};
        min-height: 100vh;
        transition: margin-left 0.3s ease;
    }}
    
    .sidebar-toggle {{
        display: none;
        position: fixed;
        top: var(--space-4);
        left: var(--space-4);
        z-index: 101;
        background: white;
        border: 1px solid var(--gray-300);
        border-radius: var(--radius-md);
        padding: var(--space-2);
        box-shadow: var(--shadow-md);
        cursor: pointer;
    }}
    
    @media (max-width: 768px) {{
        .responsive-sidebar {{
            transform: translateX(-100%);
        }}
        
        .responsive-sidebar.open {{
            transform: translateX(0);
        }}
        
        .sidebar-overlay.open {{
            display: block;
        }}
        
        .main-container {{
            margin-left: 0;
        }}
        
        .sidebar-toggle {{
            display: block;
        }}
    }}
    </style>
    
    <button class="sidebar-toggle" onclick="toggleSidebar()">
        <span style="font-size: 1.25rem;">☰</span>
    </button>
    
    <div class="sidebar-overlay" onclick="closeSidebar()"></div>
    
    <div class="responsive-sidebar" id="sidebar">
        {content}
    </div>
    
    <script>
    function toggleSidebar() {{
        const sidebar = document.getElementById('sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }}
    
    function closeSidebar() {{
        const sidebar = document.getElementById('sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
    }}
    </script>
    """

def create_responsive_header(title: str, subtitle: Optional[str] = None, 
                           actions: Optional[List[str]] = None) -> str:
    """Create responsive page header."""
    
    subtitle_html = f'<p style="color: var(--gray-600); margin-top: var(--space-2); font-size: 1.125rem;">{subtitle}</p>' if subtitle else ''
    
    actions_html = ""
    if actions:
        actions_html = f"""
        <div class="header-actions" style="
            display: flex;
            gap: var(--space-3);
            align-items: center;
            flex-wrap: wrap;
        ">
            {''.join(actions)}
        </div>
        """
    
    return f"""
    <style>
    .responsive-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: var(--space-8);
        padding: var(--space-6) 0;
        border-bottom: 1px solid var(--gray-200);
    }}
    
    .header-content {{
        flex: 1;
    }}
    
    .header-title {{
        font-size: 2.25rem;
        font-weight: 800;
        color: var(--gray-900);
        margin: 0;
        line-height: 1.2;
    }}
    
    @media (max-width: 768px) {{
        .responsive-header {{
            flex-direction: column;
            gap: var(--space-4);
        }}
        
        .header-title {{
            font-size: 1.875rem;
        }}
        
        .header-actions {{
            width: 100%;
            justify-content: flex-start;
        }}
    }}
    </style>
    
    <div class="responsive-header">
        <div class="header-content">
            <h1 class="header-title">{title}</h1>
            {subtitle_html}
        </div>
        {actions_html}
    </div>
    """

def create_responsive_card_grid(cards: List[str], columns: Dict[str, int] = None) -> str:
    """Create responsive card grid."""
    
    if columns is None:
        columns = {'desktop': 3, 'tablet': 2, 'mobile': 1}
    
    cards_html = ''.join(f'<div class="grid-item">{card}</div>' for card in cards)
    
    return f"""
    <style>
    .responsive-card-grid {{
        display: grid;
        grid-template-columns: repeat({columns['desktop']}, 1fr);
        gap: var(--space-6);
        width: 100%;
    }}
    
    @media (max-width: 1024px) {{
        .responsive-card-grid {{
            grid-template-columns: repeat({columns['tablet']}, 1fr);
        }}
    }}
    
    @media (max-width: 640px) {{
        .responsive-card-grid {{
            grid-template-columns: repeat({columns['mobile']}, 1fr);
            gap: var(--space-4);
        }}
    }}
    
    .grid-item {{
        transition: transform 0.2s ease;
    }}
    
    .grid-item:hover {{
        transform: translateY(-2px);
    }}
    </style>
    
    <div class="responsive-card-grid">
        {cards_html}
    </div>
    """

def create_responsive_table(headers: List[str], rows: List[List[str]], 
                          mobile_labels: Optional[List[str]] = None) -> str:
    """Create responsive table that stacks on mobile."""
    
    if mobile_labels is None:
        mobile_labels = headers
    
    # Generate table headers
    headers_html = ''.join(f'<th>{header}</th>' for header in headers)
    
    # Generate table rows
    rows_html = ""
    for row in rows:
        cells_html = ""
        for i, cell in enumerate(row):
            cells_html += f'<td data-label="{mobile_labels[i]}">{cell}</td>'
        rows_html += f'<tr>{cells_html}</tr>'
    
    return f"""
    <style>
    .responsive-table {{
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }}
    
    .responsive-table th {{
        background: var(--gray-50);
        padding: var(--space-4);
        text-align: left;
        font-weight: 600;
        color: var(--gray-700);
        border-bottom: 1px solid var(--gray-200);
    }}
    
    .responsive-table td {{
        padding: var(--space-4);
        border-bottom: 1px solid var(--gray-100);
    }}
    
    .responsive-table tr:hover {{
        background: var(--gray-50);
    }}
    
    @media (max-width: 768px) {{
        .responsive-table,
        .responsive-table thead,
        .responsive-table tbody,
        .responsive-table th,
        .responsive-table td,
        .responsive-table tr {{
            display: block;
        }}
        
        .responsive-table thead tr {{
            position: absolute;
            top: -9999px;
            left: -9999px;
        }}
        
        .responsive-table tr {{
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-lg);
            margin-bottom: var(--space-4);
            padding: var(--space-4);
            background: white;
        }}
        
        .responsive-table td {{
            border: none;
            position: relative;
            padding-left: 30%;
            padding-top: var(--space-2);
            padding-bottom: var(--space-2);
        }}
        
        .responsive-table td:before {{
            content: attr(data-label) ": ";
            position: absolute;
            left: var(--space-3);
            width: 25%;
            padding-right: var(--space-2);
            white-space: nowrap;
            font-weight: 600;
            color: var(--gray-700);
        }}
    }}
    </style>
    
    <table class="responsive-table">
        <thead>
            <tr>{headers_html}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """

def create_responsive_container(content: str, max_width: str = "1200px") -> str:
    """Create responsive container with proper padding."""
    return f"""
    <style>
    .responsive-container {{
        max-width: {max_width};
        margin: 0 auto;
        padding: 0 var(--space-6);
    }}
    
    @media (max-width: 640px) {{
        .responsive-container {{
            padding: 0 var(--space-4);
        }}
    }}
    </style>
    
    <div class="responsive-container">
        {content}
    </div>
    """