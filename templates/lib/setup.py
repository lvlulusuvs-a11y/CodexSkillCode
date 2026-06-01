from setuptools import setup, find_packages

setup(
    name="mylib",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=8.0", "pytest-cov>=5.0", "ruff>=0.3.0"],
    },
)
