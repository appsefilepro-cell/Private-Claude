"""
Setup configuration for Private-Claude AGENTX5 Trading System
"""
from setuptools import setup, find_packages

setup(
    name="private-claude-agentx5",
    version="1.0.0",
    description="AGENTX5 Trading System with 750 Diamond Agent Activation",
    author="appsefilepro-cell",
    packages=find_packages(),
    install_requires=[
        "urllib3<2.0.0",
        "requests==2.31.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "python-docx>=0.8.11",
        "python-dotenv>=0.19.0",
        "yfinance>=0.1.70",
    ],
    python_requires=">=3.8",
    package_dir={"": "."},
    include_package_data=True,
)
