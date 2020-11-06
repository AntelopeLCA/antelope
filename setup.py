from setuptools import setup, find_packages

requires = [
    "synonym_dict"
]

setup(
    name="antelope",
    version="0.1.0",
    author="Brandon Kuczenski",
    author_email="bkuczenski@ucsb.edu",
    license=open('LICENSE').read(),
    install_requires=requires,
    url="https://github.com/AntelopeLCA/antelope",
    summary="An interface specification for accessing LCA data",
    long_description=open('README.md').read(),
    packages=find_packages()
)
