from setuptools import setup, find_packages

setup(
    name="csvdoctor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "pyarrow",
        "chardet",
    ],
    entry_points={
        "console_scripts": [
            "csvdoctor=csvdoctor.cli:main",
        ]
    },
)
