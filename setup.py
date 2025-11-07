from setuptools import setup, find_packages

setup(
    name="sources-media",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "redis>=7.0.0",
    ],
)