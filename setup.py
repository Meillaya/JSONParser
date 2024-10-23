from setuptools import setup, find_packages

setup(
    name="JSONParser",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'jsonparse=src:main',
        ],
    },
    python_requires='>=3.7',
    description="A CLI tool for parsing JSON files.",
    author="Nathan Agbomedarho",
    author_email="your.email@example.com"
)
