from setuptools import setup, find_packages

setup(
    name="json-parser-cli",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'jsonparse=src.cli:main',
        ],
    },
    python_requires='>=3.7',
    description="A CLI tool for parsing JSON",
    author="Your Name",
    author_email="your.email@example.com"
)
