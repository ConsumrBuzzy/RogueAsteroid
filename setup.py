from setuptools import setup, find_packages

setup(
    name="rogueasteroid",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.2",
        "numpy>=1.24.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "coverage>=7.3.2",
        ],
    },
    python_requires=">=3.8",
) 