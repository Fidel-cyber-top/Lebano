#!/usr/bin/env python3
"""
FidelinvestigatorAI - Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fidelinvestigator",
    version="1.0.0",
    author="FidelinvestigatorAI",
    author_email="info@fidelinvestigator.ai",
    description="Agente Investigativo OSINT di Elite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fidelinvestigator/fidelinvestigator-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Internet",
    ],
    python_requires=">=3.8",
    install_requires=[
        "beautifulsoup4>=4.12.0",
        "reportlab>=4.0.0",
        "lxml>=4.9.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fidelinvestigator=fidelinvestigator.agent:main",
        ],
    },
    include_package_data=True,
    keywords=[
        "osint",
        "intelligence",
        "investigation",
        "security",
        "analysis",
        "profiling",
        "pdf-report"
    ],
)
