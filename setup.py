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
    ],
    entry_points={
        "console_scripts": [
            "stockr=stockr.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A command line tool for stock analysis",
    keywords="stocks, finance, options, analysis",
    python_requires=">=3.6",
)
