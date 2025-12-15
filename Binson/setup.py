# setup.py
from setuptools import setup, find_packages

setup(
    name="binjson",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "msgpack>=1.0.0",
        "zstandard>=0.15.0",
        "pycryptodome>=3.10.0",
        "jsonschema>=4.0.0",
    ],
    python_requires=">=3.7",
)
