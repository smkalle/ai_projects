"""Dark/Light theme system with Silicon Valley aesthetics."""

def get_theme_css() -> str:
    """Get CSS for dark/light theme system."""
    return """
    <style>
    /* CSS Variables for theming */
    :root {
        /* Light theme colors */
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-elevated: #ffffff;
        --bg-overlay: rgba(0, 0, 0, 0.5);
        
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --text-tertiary: #9ca3af;
        --text-inverse: #ffffff;
        
        --border-primary: #e5e7eb;
        --border-secondary: #d1d5db;
        --border-focus: #6366f1;
        
        --surface-primary: #ffffff;
        --surface-secondary: #f9fafb;
        --surface-elevated: #ffffff;
        
        /* Brand colors (same for both themes) */
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        
        /* Shadows for light theme */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }
    
    /* Dark theme */
    [data-theme="dark"] {
        --bg-primary: #0f0f23;
        --bg-secondary: #1a1a2e;
        --bg-elevated: #252545;
        --bg-overlay: rgba(0, 0, 0, 0.8);
        
        --text-primary: #e2e8f0;
        --text-secondary: #94a3b8;
        --text-tertiary: #64748b;
        --text-inverse: #1f2937;
        
        --border-primary: #2d3748;
        --border-secondary: #4a5568;
        --border-focus: #818cf8;
        
        --surface-primary: #1a1a2e;
        --surface-secondary: #252545;
        --surface-elevated: #2d2d4a;
        
        /* Dark theme shadows */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
        --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.4), 0 1px 2px -1px rgb(0 0 0 / 0.4);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.4);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.4);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.4);
    }
    
    /* Auto theme based on system preference */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-elevated: #252545;
            --bg-overlay: rgba(0, 0, 0, 0.8);
            
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-tertiary: #64748b;
            --text-inverse: #1f2937;
            
            --border-primary: #2d3748;
            --border-secondary: #4a5568;
            --border-focus: #818cf8;
            
            --surface-primary: #1a1a2e;
            --surface-secondary: #252545;
            --surface-elevated: #2d2d4a;
            
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
            --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.4), 0 1px 2px -1px rgb(0 0 0 / 0.4);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.4);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.4);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.4);
        }
    }
    
    /* Override auto theme when explicitly set */
    [data-theme="light"] {
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-elevated: #ffffff;
        --bg-overlay: rgba(0, 0, 0, 0.5);
        
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --text-tertiary: #9ca3af;
        --text-inverse: #ffffff;
        
        --border-primary: #e5e7eb;
        --border-secondary: #d1d5db;
        --border-focus: #6366f1;
        
        --surface-primary: #ffffff;
        --surface-secondary: #f9fafb;
        --surface-elevated: #ffffff;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }
    
    /* Base element styling with theme variables */
    body {
        background: var(--bg-primary);
        color: var(--text-primary);
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    
    /* Theme toggle button */
    .theme-toggle {
        position: fixed;
        top: var(--space-4);
        right: var(--space-4);
        z-index: 1000;
        background: var(--surface-elevated);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-full);
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
    }
    
    .theme-toggle:hover {
        background: var(--surface-secondary);
        transform: scale(1.05);
        box-shadow: var(--shadow-lg);
    }
    
    .theme-toggle-icon {
        font-size: 1.25rem;
        transition: transform 0.3s ease;
    }
    
    .theme-toggle:hover .theme-toggle-icon {
        transform: rotate(180deg);
    }
    
    /* Sun icon for light theme */
    .theme-toggle .sun-icon {
        display: block;
        color: #f59e0b;
    }
    
    .theme-toggle .moon-icon {
        display: none;
        color: #6366f1;
    }
    
    /* Moon icon for dark theme */
    [data-theme="dark"] .theme-toggle .sun-icon {
        display: none;
    }
    
    [data-theme="dark"] .theme-toggle .moon-icon {
        display: block;
    }
    
    /* Themed components */
    .card {
        background: var(--surface-elevated);
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-lg);
    }
    
    .input {
        background: var(--surface-primary);
        border: 1px solid var(--border-primary);
        color: var(--text-primary);
        transition: all 0.3s ease;
    }
    
    .input:focus {
        border-color: var(--border-focus);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    .button-secondary {
        background: var(--surface-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-primary);
        transition: all 0.3s ease;
    }
    
    .button-secondary:hover {
        background: var(--surface-elevated);
        border-color: var(--border-secondary);
    }
    
    /* Navigation theming */
    .sidebar {
        background: var(--surface-elevated);
        border-color: var(--border-primary);
    }
    
    .nav-item {
        color: var(--text-secondary);
        transition: all 0.3s ease;
    }
    
    .nav-item:hover,
    .nav-item.active {
        color: var(--text-primary);
        background: var(--surface-secondary);
    }
    
    /* Table theming */
    .table {
        background: var(--surface-elevated);
        border: 1px solid var(--border-primary);
    }
    
    .table th {
        background: var(--surface-secondary);
        color: var(--text-secondary);
        border-color: var(--border-primary);
    }
    
    .table td {
        border-color: var(--border-primary);
        color: var(--text-primary);
    }
    
    .table tr:hover {
        background: var(--surface-secondary);
    }
    
    /* Modal theming */
    .modal-overlay {
        background: var(--bg-overlay);
    }
    
    .modal {
        background: var(--surface-elevated);
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-xl);
    }
    
    /* Toast notifications theming */
    .toast {
        background: var(--surface-elevated);
        border: 1px solid var(--border-primary);
        color: var(--text-primary);
        box-shadow: var(--shadow-lg);
    }
    
    /* Code blocks theming */
    .code-block {
        background: var(--surface-secondary);
        border: 1px solid var(--border-primary);
        color: var(--text-primary);
    }
    
    /* Scrollbar theming */
    ::-webkit-scrollbar-track {
        background: var(--surface-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-secondary);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-tertiary);
    }
    
    /* Selection theming */
    ::selection {
        background: rgba(99, 102, 241, 0.2);
        color: var(--text-primary);
    }
    
    /* Glassmorphism effect for dark theme */
    [data-theme="dark"] .glass-effect {
        background: rgba(37, 37, 69, 0.3);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-theme="dark"] .glass-effect:hover {
        background: rgba(37, 37, 69, 0.4);
        backdrop-filter: blur(16px);
    }
    
    /* Light theme glassmorphism */
    [data-theme="light"] .glass-effect {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    [data-theme="light"] .glass-effect:hover {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(16px);
    }
    
    /* Smooth theme transitions */
    * {
        transition: background-color 0.3s ease, 
                    border-color 0.3s ease, 
                    color 0.3s ease,
                    box-shadow 0.3s ease;
    }
    
    /* Override transitions for animations */
    .animate-fade-in,
    .animate-scale-in,
    .animate-bounce {
        transition: none;
    }
    </style>
    """

def create_theme_toggle() -> str:
    """Create a theme toggle button."""
    return """
    <div class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">
        <div class="theme-toggle-icon">
            <span class="sun-icon">☀️</span>
            <span class="moon-icon">🌙</span>
        </div>
    </div>
    
    <script>
    // Theme management
    function getStoredTheme() {
        return localStorage.getItem('theme') || 'auto';
    }
    
    function setStoredTheme(theme) {
        localStorage.setItem('theme', theme);
    }
    
    function getPreferredTheme() {
        const storedTheme = getStoredTheme();
        if (storedTheme !== 'auto') {
            return storedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    function setTheme(theme) {
        if (theme === 'auto') {
            document.documentElement.removeAttribute('data-theme');
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }
    }
    
    function toggleTheme() {
        const currentTheme = getStoredTheme();
        let newTheme;
        
        if (currentTheme === 'light') {
            newTheme = 'dark';
        } else if (currentTheme === 'dark') {
            newTheme = 'auto';
        } else {
            newTheme = 'light';
        }
        
        setStoredTheme(newTheme);
        setTheme(getPreferredTheme());
        
        // Optional: Show theme change notification
        showThemeNotification(newTheme);
    }
    
    function showThemeNotification(theme) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--surface-elevated);
            color: var(--text-primary);
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            transition: all 0.3s ease;
            border: 1px solid var(--border-primary);
        `;
        
        const themeNames = {
            'light': 'Light theme',
            'dark': 'Dark theme', 
            'auto': 'Auto theme'
        };
        
        notification.textContent = `Switched to ${themeNames[theme]}`;
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateY(0)';
            notification.style.opacity = '1';
        }, 10);
        
        // Remove after 2 seconds
        setTimeout(() => {
            notification.style.transform = 'translateY(-20px)';
            notification.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 2000);
    }
    
    // Initialize theme on page load
    function initializeTheme() {
        setTheme(getPreferredTheme());
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            if (getStoredTheme() === 'auto') {
                setTheme(getPreferredTheme());
            }
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeTheme);
    } else {
        initializeTheme();
    }
    </script>
    """

def create_theme_aware_gradient(light_colors: list, dark_colors: list) -> str:
    """Create a gradient that changes based on theme."""
    light_gradient = f"linear-gradient(135deg, {', '.join(light_colors)})"
    dark_gradient = f"linear-gradient(135deg, {', '.join(dark_colors)})"
    
    return f"""
    <style>
    .theme-aware-gradient {{
        background: {light_gradient};
        transition: background 0.5s ease;
    }}
    
    [data-theme="dark"] .theme-aware-gradient {{
        background: {dark_gradient};
    }}
    
    @media (prefers-color-scheme: dark) {{
        .theme-aware-gradient {{
            background: {dark_gradient};
        }}
    }}
    
    [data-theme="light"] .theme-aware-gradient {{
        background: {light_gradient};
    }}
    </style>
    """

def create_theme_aware_card(content: str, glass_effect: bool = False) -> str:
    """Create a card that adapts to the current theme."""
    
    glass_class = "glass-effect" if glass_effect else ""
    
    return f"""
    <div class="card {glass_class}" style="
        background: var(--surface-elevated);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    ">
        {content}
    </div>
    """