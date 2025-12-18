"""
LVL-CODES: 2026 Sales Target Management System
Setup Configuration for Package Installation

This setup.py allows the project to be installed as a package, making imports cleaner
and enabling easy distribution and deployment.

Installation:
    Development mode (editable): pip install -e .
    Production mode: pip install .

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements from requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

# Development dependencies (for testing, linting, etc.)
dev_requirements = [
    "pytest>=7.4.3",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "black>=23.11.0",
    "flake8>=6.1.0",
    "mypy>=1.7.0",
    "isort>=5.12.0",
    "pylint>=3.0.2",
    "pre-commit>=3.5.0",
]

# Documentation dependencies
docs_requirements = [
    "mkdocs>=1.5.3",
    "mkdocs-material>=9.4.14",
    "pdoc3>=0.10.0",
]

# Setup configuration
setup(
    # ============================================================================
    # PACKAGE METADATA
    # ============================================================================
    name="lvl-codes",
    version="1.0.0",
    author="LVL-CODES Analytics Team",
    author_email="analytics@lvl-codes.com",
    description="Comprehensive sales target management system for pet food retail & distribution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/banddanalytics/LVL-CODES",

    # ============================================================================
    # PACKAGE DISCOVERY
    # ============================================================================
    packages=find_packages(exclude=["tests", "tests.*", "notebooks", "docs"]),

    # Include non-Python files specified in MANIFEST.in
    include_package_data=True,

    # ============================================================================
    # PYTHON VERSION REQUIREMENT
    # ============================================================================
    python_requires=">=3.9",

    # ============================================================================
    # DEPENDENCIES
    # ============================================================================
    install_requires=requirements,

    # Extra dependencies for different use cases
    extras_require={
        "dev": dev_requirements,
        "docs": docs_requirements,
        "all": dev_requirements + docs_requirements,
    },

    # ============================================================================
    # ENTRY POINTS (Command-line scripts)
    # ============================================================================
    entry_points={
        "console_scripts": [
            # Main application launcher
            "lvl-codes=src.main:main",

            # Dashboard launcher
            "lvl-dashboard=src.dashboard.app:main",

            # ETL pipeline runner
            "lvl-etl=src.data.etl.run_etl:main",

            # Model training script
            "lvl-train=src.models.train_models:main",

            # Target allocation script
            "lvl-targets=src.targets.allocation.run_allocation:main",

            # Report generator
            "lvl-report=src.reporting.generate_reports:main",
        ],
    },

    # ============================================================================
    # CLASSIFIERS (for PyPI categorization)
    # ============================================================================
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],

    # ============================================================================
    # KEYWORDS
    # ============================================================================
    keywords=[
        "sales",
        "forecasting",
        "targets",
        "retail",
        "distribution",
        "time-series",
        "machine-learning",
        "inventory",
        "analytics",
        "dashboard",
    ],

    # ============================================================================
    # PROJECT URLS
    # ============================================================================
    project_urls={
        "Bug Reports": "https://github.com/banddanalytics/LVL-CODES/issues",
        "Source": "https://github.com/banddanalytics/LVL-CODES",
        "Documentation": "https://github.com/banddanalytics/LVL-CODES/docs",
    },

    # ============================================================================
    # ZIP SAFE
    # ============================================================================
    # Set to False to allow access to package data files
    zip_safe=False,
)
