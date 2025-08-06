"""Setup script for the Legal Document Analyzer Pipeline."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="legal-document-analyzer",
    version="1.0.0",
    author="Legal AI Engineer",
    description="AI-powered Indian legal document reader and analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pdfplumber>=0.9.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "google-generativeai>=0.3.0",
        "openai>=1.0.0",
        "accelerate>=0.20.0",
        "sentencepiece>=0.1.99",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "legal-analyzer=pipeline.main:main",
        ],
    },
)