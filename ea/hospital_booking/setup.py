"""
Setup script for Hospital Booking System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hospital-booking-system",
    version="1.0.0",
    author="Hospital Booking System Contributors",
    author_email="contributors@hospital-booking.dev",
    description="A comprehensive hospital management system with appointment scheduling and analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hospital-booking-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: Streamlit",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hospital-booking=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yaml", "*.yml"],
        "templates": ["email/*.html", "email/*.txt"],
        "static": ["*.css", "*.js", "*.png", "*.jpg"],
    },
    keywords="hospital healthcare booking appointment scheduling medical management",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/hospital-booking-system/issues",
        "Source": "https://github.com/yourusername/hospital-booking-system",
        "Documentation": "https://hospital-booking-system.readthedocs.io/",
        "Changelog": "https://github.com/yourusername/hospital-booking-system/blob/main/CHANGELOG.md",
    },
)