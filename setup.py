from setuptools import setup, find_packages

setup(
    name="stockr",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yfinance",
        "pandas",
        "numpy",
        "scipy",
        "rich",
        "prompt_toolkit",
    ],
    entry_points={
        "console_scripts": [
            "stockr=stockr.cli:main",
        ],
    },
    author="Michael McDuffee",
    author_email="your.email@example.com",
    description="A command line tool for stock analysis",
    keywords="stocks, finance, options, analysis",
    python_requires=">=3.6",
    # In setup.py
    extras_require={
        "dev": [
            "ruff",
            "pytest",
        ],
        "polygon": [
            "requests",
        ],
    },
)
