from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-ai-agent-tutorial",
    version="1.0.0",
    author="AI Engineering Team",
    author_email="team@example.com",
    description="Complete tutorial for building AI agents with MCP, Streamlit, and FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/mcp-ai-agent-tutorial",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=[
        "mcp-use>=1.0.0",
        "fastapi>=0.104.0",
        "streamlit>=1.28.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "full": [
            "sqlalchemy>=2.0.0",
            "redis>=4.5.0",
            "prometheus-client>=0.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-agent=mcp_agent.cli:main",
        ],
    },
)
