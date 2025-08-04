"""Design system and UI components for Contract Intelligence Platform."""

import streamlit as st
from typing import Optional, List, Dict, Any

class DesignSystem:
    """Silicon Valley style design system."""
    
    # Color palette inspired by modern SaaS apps
    COLORS = {
        # Primary brand colors
        'primary': '#6366f1',      # Indigo
        'primary_light': '#818cf8',
        'primary_dark': '#4f46e5',
        
        # Secondary colors
        'secondary': '#8b5cf6',    # Purple
        'accent': '#06b6d4',       # Cyan
        'success': '#10b981',      # Emerald
        'warning': '#f59e0b',      # Amber
        'error': '#ef4444',        # Red
        
        # Neutral grays
        'gray_50': '#f9fafb',
        'gray_100': '#f3f4f6', 
        'gray_200': '#e5e7eb',
        'gray_300': '#d1d5db',
        'gray_400': '#9ca3af',
        'gray_500': '#6b7280',
        'gray_600': '#4b5563',
        'gray_700': '#374151',
        'gray_800': '#1f2937',
        'gray_900': '#111827',
        
        # Dark theme colors
        'dark_bg': '#0f0f23',
        'dark_surface': '#1a1a2e',
        'dark_elevated': '#252545',
        'dark_text': '#e2e8f0',
        'dark_text_secondary': '#94a3b8',
    }
    
    # Typography scale
    TYPOGRAPHY = {
        'font_family': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        'font_mono': '"JetBrains Mono", "Fira Code", "Consolas", monospace',
        'sizes': {
            'xs': '0.75rem',    # 12px
            'sm': '0.875rem',   # 14px  
            'base': '1rem',     # 16px
            'lg': '1.125rem',   # 18px
            'xl': '1.25rem',    # 20px
            '2xl': '1.5rem',    # 24px
            '3xl': '1.875rem',  # 30px
            '4xl': '2.25rem',   # 36px
            '5xl': '3rem',      # 48px
            '6xl': '3.75rem',   # 60px
        }
    }
    
    # Spacing scale (Tailwind-inspired)
    SPACING = {
        'px': '1px',
        '0': '0',
        '1': '0.25rem',  # 4px
        '2': '0.5rem',   # 8px
        '3': '0.75rem',  # 12px
        '4': '1rem',     # 16px
        '5': '1.25rem',  # 20px
        '6': '1.5rem',   # 24px
        '8': '2rem',     # 32px
        '10': '2.5rem',  # 40px
        '12': '3rem',    # 48px
        '16': '4rem',    # 64px
        '20': '5rem',    # 80px
        '24': '6rem',    # 96px
    }
    
    # Border radius scale
    RADIUS = {
        'none': '0',
        'sm': '0.125rem',   # 2px
        'base': '0.25rem',  # 4px
        'md': '0.375rem',   # 6px
        'lg': '0.5rem',     # 8px
        'xl': '0.75rem',    # 12px
        '2xl': '1rem',      # 16px
        '3xl': '1.5rem',    # 24px
        'full': '9999px',
    }
    
    # Shadows (elevated design)
    SHADOWS = {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'base': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        'inner': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
    }

    @classmethod
    def get_base_css(cls) -> str:
        """Get base CSS for the design system."""
        return f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        :root {{
            /* Colors */
            --primary: {cls.COLORS['primary']};
            --primary-light: {cls.COLORS['primary_light']};
            --primary-dark: {cls.COLORS['primary_dark']};
            --secondary: {cls.COLORS['secondary']};
            --accent: {cls.COLORS['accent']};
            --success: {cls.COLORS['success']};
            --warning: {cls.COLORS['warning']};
            --error: {cls.COLORS['error']};
            
            /* Grays */
            --gray-50: {cls.COLORS['gray_50']};
            --gray-100: {cls.COLORS['gray_100']};
            --gray-200: {cls.COLORS['gray_200']};
            --gray-300: {cls.COLORS['gray_300']};
            --gray-400: {cls.COLORS['gray_400']};
            --gray-500: {cls.COLORS['gray_500']};
            --gray-600: {cls.COLORS['gray_600']};
            --gray-700: {cls.COLORS['gray_700']};
            --gray-800: {cls.COLORS['gray_800']};
            --gray-900: {cls.COLORS['gray_900']};
            
            /* Typography */
            --font-family: {cls.TYPOGRAPHY['font_family']};
            --font-mono: {cls.TYPOGRAPHY['font_mono']};
            
            /* Spacing */
            --space-1: {cls.SPACING['1']};
            --space-2: {cls.SPACING['2']};
            --space-3: {cls.SPACING['3']};
            --space-4: {cls.SPACING['4']};
            --space-5: {cls.SPACING['5']};
            --space-6: {cls.SPACING['6']};
            --space-8: {cls.SPACING['8']};
            --space-10: {cls.SPACING['10']};
            --space-12: {cls.SPACING['12']};
            --space-16: {cls.SPACING['16']};
            --space-20: {cls.SPACING['20']};
            --space-24: {cls.SPACING['24']};
            
            /* Border radius */
            --radius-sm: {cls.RADIUS['sm']};
            --radius-base: {cls.RADIUS['base']};
            --radius-md: {cls.RADIUS['md']};
            --radius-lg: {cls.RADIUS['lg']};
            --radius-xl: {cls.RADIUS['xl']};
            --radius-2xl: {cls.RADIUS['2xl']};
            --radius-3xl: {cls.RADIUS['3xl']};
            
            /* Shadows */
            --shadow-sm: {cls.SHADOWS['sm']};
            --shadow-base: {cls.SHADOWS['base']};
            --shadow-md: {cls.SHADOWS['md']};
            --shadow-lg: {cls.SHADOWS['lg']};
            --shadow-xl: {cls.SHADOWS['xl']};
            --shadow-2xl: {cls.SHADOWS['2xl']};
        }}
        
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: var(--font-family);
            line-height: 1.6;
            color: var(--gray-800);
            background: var(--gray-50);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* Hide Streamlit default elements */
        .css-1d391kg, .css-1lcbmhc, .css-1lucf3a {{
            display: none !important;
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--gray-100);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--gray-300);
            border-radius: var(--radius-full);
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--gray-400);
        }}
        
        /* Responsive breakpoints */
        @media (max-width: 640px) {{
            .hide-mobile {{ display: none !important; }}
            .show-mobile {{ display: block !important; }}
        }}
        
        @media (min-width: 641px) and (max-width: 1024px) {{
            .hide-tablet {{ display: none !important; }}
            .show-tablet {{ display: block !important; }}
        }}
        
        @media (min-width: 1025px) {{
            .hide-desktop {{ display: none !important; }}
            .show-desktop {{ display: block !important; }}
        }}
        </style>
        """

def apply_design_system():
    """Apply the design system to the Streamlit app."""
    st.markdown(DesignSystem.get_base_css(), unsafe_allow_html=True)

def create_card(content: str, padding: str = "var(--space-6)", 
                shadow: str = "var(--shadow-md)", 
                border_radius: str = "var(--radius-xl)",
                background: str = "white") -> str:
    """Create a modern card component."""
    return f"""
    <div style="
        background: {background};
        padding: {padding};
        border-radius: {border_radius};
        box-shadow: {shadow};
        border: 1px solid var(--gray-200);
        transition: all 0.2s ease;
    " class="card">
        {content}
    </div>
    """

def create_button(text: str, variant: str = "primary", size: str = "md", 
                 icon: Optional[str] = None, disabled: bool = False) -> str:
    """Create a modern button component."""
    
    size_styles = {
        'sm': 'padding: var(--space-2) var(--space-3); font-size: 0.875rem;',
        'md': 'padding: var(--space-3) var(--space-6); font-size: 1rem;',
        'lg': 'padding: var(--space-4) var(--space-8); font-size: 1.125rem;',
    }
    
    variant_styles = {
        'primary': f'background: var(--primary); color: white; border: none;',
        'secondary': f'background: var(--gray-100); color: var(--gray-800); border: 1px solid var(--gray-300);',
        'success': f'background: var(--success); color: white; border: none;',
        'warning': f'background: var(--warning); color: white; border: none;',
        'error': f'background: var(--error); color: white; border: none;',
        'ghost': f'background: transparent; color: var(--primary); border: 1px solid var(--primary);',
    }
    
    disabled_style = 'opacity: 0.5; cursor: not-allowed;' if disabled else ''
    icon_html = f'<span style="margin-right: var(--space-2);">{icon}</span>' if icon else ''
    
    return f"""
    <button style="
        {size_styles[size]}
        {variant_styles[variant]}
        border-radius: var(--radius-lg);
        font-weight: 600;
        font-family: var(--font-family);
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        text-decoration: none;
        {disabled_style}
    " class="btn btn-{variant}" {'disabled' if disabled else ''}>
        {icon_html}{text}
    </button>
    """

def create_badge(text: str, variant: str = "primary", size: str = "md") -> str:
    """Create a modern badge component."""
    
    size_styles = {
        'sm': 'padding: var(--space-1) var(--space-2); font-size: 0.75rem;',
        'md': 'padding: var(--space-2) var(--space-3); font-size: 0.875rem;',
        'lg': 'padding: var(--space-3) var(--space-4); font-size: 1rem;',
    }
    
    variant_styles = {
        'primary': f'background: var(--primary); color: white;',
        'secondary': f'background: var(--gray-200); color: var(--gray-800);',
        'success': f'background: var(--success); color: white;',
        'warning': f'background: var(--warning); color: white;',
        'error': f'background: var(--error); color: white;',
    }
    
    return f"""
    <span style="
        {size_styles[size]}
        {variant_styles[variant]}
        border-radius: var(--radius-full);
        font-weight: 500;
        font-family: var(--font-family);
        display: inline-block;
    " class="badge badge-{variant}">
        {text}
    </span>
    """

def create_progress_bar(progress: float, height: str = "8px", 
                       color: str = "var(--primary)") -> str:
    """Create a modern progress bar."""
    return f"""
    <div style="
        width: 100%;
        height: {height};
        background: var(--gray-200);
        border-radius: var(--radius-full);
        overflow: hidden;
    ">
        <div style="
            width: {progress}%;
            height: 100%;
            background: {color};
            border-radius: var(--radius-full);
            transition: width 0.3s ease;
        "></div>
    </div>
    """

def create_metric_card(title: str, value: str, change: Optional[str] = None,
                      change_type: str = "positive", icon: Optional[str] = None) -> str:
    """Create a modern metric card."""
    
    change_color = "var(--success)" if change_type == "positive" else "var(--error)"
    icon_html = f'<div style="font-size: 1.5rem; margin-bottom: var(--space-2);">{icon}</div>' if icon else ''
    change_html = f'<div style="color: {change_color}; font-size: 0.875rem; font-weight: 500;">{change}</div>' if change else ''
    
    return create_card(f"""
        {icon_html}
        <div style="font-size: 0.875rem; color: var(--gray-600); margin-bottom: var(--space-1);">
            {title}
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--gray-900); margin-bottom: var(--space-1);">
            {value}
        </div>
        {change_html}
    """)

def create_loading_skeleton(height: str = "20px", width: str = "100%") -> str:
    """Create a loading skeleton."""
    return f"""
    <div style="
        width: {width};
        height: {height};
        background: linear-gradient(90deg, var(--gray-200) 25%, var(--gray-100) 50%, var(--gray-200) 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: var(--radius-md);
    "></div>
    
    <style>
    @keyframes loading {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    </style>
    """

def create_glassmorphism_card(content: str, blur: str = "10px") -> str:
    """Create a glassmorphism card effect."""
    return f"""
    <div style="
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur({blur});
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--radius-2xl);
        padding: var(--space-6);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    " class="glass-card">
        {content}
    </div>
    """