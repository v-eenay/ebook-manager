#!/usr/bin/env python3
"""
Setup script for Modern EBook Reader
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="modern-ebook-reader",
    version="2.0.0",
    description="A clean, minimal ebook reader supporting PDF, EPUB, and MOBI formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Modern EBook Reader Team",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ebook-reader=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Topic :: Office/Business",
    ],
    keywords="ebook reader pdf epub mobi qt pyqt",
    project_urls={
        "Source": "https://github.com/v-eenay/ebook-manager",
        "Bug Reports": "https://github.com/v-eenay/ebook-manager/issues",
    },
)
