"""Modern animations and micro-interactions for Silicon Valley style UI."""

def get_animation_css() -> str:
    """Get CSS for modern animations and micro-interactions."""
    return """
    <style>
    /* Fade in animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Scale animations */
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Loading animations */
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -200px 0;
        }
        100% {
            background-position: calc(200px + 100%) 0;
        }
    }
    
    @keyframes bounce {
        0%, 20%, 53%, 80%, 100% {
            animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
            transform: translate3d(0, 0, 0);
        }
        40%, 43% {
            animation-timing-function: cubic-bezier(0.755, 0.05, 0.855, 0.06);
            transform: translate3d(0, -10px, 0);
        }
        70% {
            animation-timing-function: cubic-bezier(0.755, 0.05, 0.855, 0.06);
            transform: translate3d(0, -5px, 0);
        }
        90% {
            transform: translate3d(0, -2px, 0);
        }
    }
    
    /* Gradient animations */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Progress bar animation */
    @keyframes progressFill {
        from { width: 0%; }
        to { width: var(--progress-width, 100%); }
    }
    
    /* Floating animation */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Shake animation for errors */
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    /* Slide animations */
    @keyframes slideInFromTop {
        from { transform: translateY(-100%); }
        to { transform: translateY(0); }
    }
    
    @keyframes slideInFromBottom {
        from { transform: translateY(100%); }
        to { transform: translateY(0); }
    }
    
    @keyframes slideInFromLeft {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }
    
    @keyframes slideInFromRight {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    /* Animation utility classes */
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .animate-fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .animate-fade-in-down {
        animation: fadeInDown 0.6s ease-out;
    }
    
    .animate-fade-in-left {
        animation: fadeInLeft 0.6s ease-out;
    }
    
    .animate-fade-in-right {
        animation: fadeInRight 0.6s ease-out;
    }
    
    .animate-scale-in {
        animation: scaleIn 0.4s ease-out;
    }
    
    .animate-pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    .animate-spin {
        animation: spin 1s linear infinite;
    }
    
    .animate-bounce {
        animation: bounce 1s ease-in-out;
    }
    
    .animate-float {
        animation: float 3s ease-in-out infinite;
    }
    
    .animate-shake {
        animation: shake 0.5s ease-in-out;
    }
    
    .animate-slide-in-top {
        animation: slideInFromTop 0.5s ease-out;
    }
    
    .animate-slide-in-bottom {
        animation: slideInFromBottom 0.5s ease-out;
    }
    
    .animate-slide-in-left {
        animation: slideInFromLeft 0.5s ease-out;
    }
    
    .animate-slide-in-right {
        animation: slideInFromRight 0.5s ease-out;
    }
    
    /* Hover animations */
    .hover-lift {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .hover-lift:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
    }
    
    .hover-scale {
        transition: transform 0.2s ease;
    }
    
    .hover-scale:hover {
        transform: scale(1.05);
    }
    
    .hover-glow {
        transition: box-shadow 0.2s ease;
    }
    
    .hover-glow:hover {
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
    }
    
    /* Loading states */
    .loading-shimmer {
        background: linear-gradient(90deg, var(--gray-200) 25%, var(--gray-100) 50%, var(--gray-200) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
    }
    
    .loading-dots::after {
        content: '';
        animation: dots 1.5s steps(5, end) infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
    
    /* Gradient backgrounds */
    .gradient-bg {
        background: linear-gradient(-45deg, #6366f1, #8b5cf6, #06b6d4, #10b981);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    .gradient-text {
        background: linear-gradient(-45deg, #6366f1, #8b5cf6, #06b6d4);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 8s ease infinite;
    }
    
    /* Morphing shapes */
    .morphing-blob {
        border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
        animation: morph 8s ease-in-out infinite;
    }
    
    @keyframes morph {
        0% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
        50% { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
        100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
    }
    
    /* Stagger animations for lists */
    .stagger-children > * {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .stagger-children > *:nth-child(1) { animation-delay: 0.1s; }
    .stagger-children > *:nth-child(2) { animation-delay: 0.2s; }
    .stagger-children > *:nth-child(3) { animation-delay: 0.3s; }
    .stagger-children > *:nth-child(4) { animation-delay: 0.4s; }
    .stagger-children > *:nth-child(5) { animation-delay: 0.5s; }
    .stagger-children > *:nth-child(6) { animation-delay: 0.6s; }
    
    /* Progress ring animation */
    .progress-ring {
        transform: rotate(-90deg);
    }
    
    .progress-ring-circle {
        stroke-dasharray: 283;
        stroke-dashoffset: 283;
        animation: progressRing 2s ease-out forwards;
    }
    
    @keyframes progressRing {
        to {
            stroke-dashoffset: calc(283 - (283 * var(--progress, 0)) / 100);
        }
    }
    
    /* Glass morphism effects */
    .glass-effect {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .glass-effect:hover {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
    }
    
    /* Typewriter effect */
    .typewriter {
        overflow: hidden;
        border-right: 2px solid var(--primary);
        white-space: nowrap;
        animation: typing 3s steps(40, end), blink-caret 0.75s step-end infinite;
    }
    
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink-caret {
        from, to { border-color: transparent; }
        50% { border-color: var(--primary); }
    }
    
    /* Parallax scroll effect */
    .parallax {
        transition: transform 0.1s ease-out;
    }
    
    /* Smooth scroll behavior */
    html {
        scroll-behavior: smooth;
    }
    
    /* Reduce motion for accessibility */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """

def create_loading_spinner(size: str = "40px", color: str = "var(--primary)") -> str:
    """Create a modern loading spinner."""
    return f"""
    <div style="
        width: {size};
        height: {size};
        border: 3px solid var(--gray-200);
        border-top: 3px solid {color};
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    "></div>
    """

def create_progress_circle(progress: float, size: str = "100px", 
                          stroke_width: str = "8", color: str = "var(--primary)") -> str:
    """Create an animated circular progress indicator."""
    radius = 45
    circumference = 2 * 3.14159 * radius
    offset = circumference - (progress / 100) * circumference
    
    return f"""
    <div style="position: relative; width: {size}; height: {size};">
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <circle
                cx="50"
                cy="50"
                r="{radius}"
                stroke="var(--gray-200)"
                stroke-width="{stroke_width}"
                fill="none"
            />
            <circle
                cx="50"
                cy="50"
                r="{radius}"
                stroke="{color}"
                stroke-width="{stroke_width}"
                fill="none"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{offset}"
                stroke-linecap="round"
                style="transition: stroke-dashoffset 1s ease-in-out;"
            />
        </svg>
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: 600;
            font-size: 1.25rem;
            color: var(--gray-700);
        ">
            {progress:.0f}%
        </div>
    </div>
    """

def create_morphing_button(text: str, loading_text: str = "Loading", 
                          success_text: str = "Success!", 
                          button_id: str = "morph-btn") -> str:
    """Create a button that morphs through different states."""
    return f"""
    <style>
    .morphing-button {{
        background: var(--primary);
        color: white;
        border: none;
        border-radius: var(--radius-lg);
        padding: var(--space-3) var(--space-6);
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .morphing-button:hover {{
        background: var(--primary-dark);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }}
    
    .morphing-button.loading {{
        background: var(--warning);
        cursor: not-allowed;
        animation: pulse 1.5s ease-in-out infinite;
    }}
    
    .morphing-button.success {{
        background: var(--success);
        animation: bounce 0.6s ease-out;
    }}
    
    .morphing-button .button-text {{
        transition: opacity 0.2s ease;
    }}
    
    .morphing-button.loading .button-text,
    .morphing-button.success .button-text {{
        opacity: 0;
    }}
    
    .morphing-button::after {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        opacity: 0;
        transition: opacity 0.2s ease;
    }}
    
    .morphing-button.loading::after {{
        content: '{loading_text}';
        opacity: 1;
    }}
    
    .morphing-button.success::after {{
        content: '{success_text}';
        opacity: 1;
    }}
    </style>
    
    <button class="morphing-button" id="{button_id}" onclick="morphButton('{button_id}')">
        <span class="button-text">{text}</span>
    </button>
    
    <script>
    function morphButton(buttonId) {{
        const button = document.getElementById(buttonId);
        
        // Loading state
        button.classList.add('loading');
        button.disabled = true;
        
        // Simulate async operation
        setTimeout(() => {{
            // Success state
            button.classList.remove('loading');
            button.classList.add('success');
            
            // Reset after 2 seconds
            setTimeout(() => {{
                button.classList.remove('success');
                button.disabled = false;
            }}, 2000);
        }}, 2000);
    }}
    </script>
    """

def create_floating_action_button(icon: str, tooltip: str = "", 
                                position: str = "bottom-right") -> str:
    """Create a floating action button with modern styling."""
    
    position_styles = {
        'bottom-right': 'bottom: var(--space-6); right: var(--space-6);',
        'bottom-left': 'bottom: var(--space-6); left: var(--space-6);',
        'top-right': 'top: var(--space-6); right: var(--space-6);',
        'top-left': 'top: var(--space-6); left: var(--space-6);',
    }
    
    return f"""
    <style>
    .floating-action-button {{
        position: fixed;
        {position_styles[position]}
        width: 56px;
        height: 56px;
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        transition: all 0.3s ease;
        z-index: 1000;
    }}
    
    .floating-action-button:hover {{
        background: var(--primary-dark);
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
    }}
    
    .floating-action-button:active {{
        transform: scale(0.95);
    }}
    
    .fab-tooltip {{
        position: absolute;
        right: 70px;
        top: 50%;
        transform: translateY(-50%);
        background: var(--gray-800);
        color: white;
        padding: var(--space-2) var(--space-3);
        border-radius: var(--radius-md);
        font-size: 0.875rem;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
    }}
    
    .floating-action-button:hover .fab-tooltip {{
        opacity: 1;
        visibility: visible;
    }}
    
    @media (max-width: 768px) {{
        .floating-action-button {{
            bottom: 90px; /* Above mobile nav */
        }}
    }}
    </style>
    
    <button class="floating-action-button" title="{tooltip}">
        <span>{icon}</span>
        {f'<div class="fab-tooltip">{tooltip}</div>' if tooltip else ''}
    </button>
    """

def create_particle_background(count: int = 50) -> str:
    """Create animated particle background effect."""
    return f"""
    <style>
    .particle-background {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        overflow: hidden;
    }}
    
    .particle {{
        position: absolute;
        background: var(--primary);
        border-radius: 50%;
        opacity: 0.1;
        animation: float 20s infinite linear;
    }}
    
    @keyframes particleFloat {{
        0% {{
            transform: translateY(100vh) rotate(0deg);
            opacity: 0;
        }}
        10% {{
            opacity: 0.1;
        }}
        90% {{
            opacity: 0.1;
        }}
        100% {{
            transform: translateY(-100px) rotate(360deg);
            opacity: 0;
        }}
    }}
    </style>
    
    <div class="particle-background" id="particle-bg"></div>
    
    <script>
    function createParticles() {{
        const bg = document.getElementById('particle-bg');
        const particleCount = {count};
        
        for (let i = 0; i < particleCount; i++) {{
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            const size = Math.random() * 5 + 2;
            const duration = Math.random() * 15 + 10;
            const delay = Math.random() * 20;
            
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDuration = duration + 's';
            particle.style.animationDelay = delay + 's';
            particle.style.animationName = 'particleFloat';
            
            bg.appendChild(particle);
        }}
    }}
    
    // Create particles when page loads
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', createParticles);
    }} else {{
        createParticles();
    }}
    </script>
    """