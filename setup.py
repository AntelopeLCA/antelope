from setuptools import setup, find_packages

requires = [
    "synonym_dict"
]

"""
Version History:
0.1.1 2020/11/12 - Bug fixes and boundary setting
                   add synonyms() route and grant a ref access to synonyms from its origin
                   terminate() is now called targets()
                   remove most of the foreground interface spec
                   
0.1.0 2020/07/31 - Initial release - JIE paper 
"""

VERSION = "0.1.1"

setup(
    name="antelope",
    version=VERSION,
    author="Brandon Kuczenski",
    author_email="bkuczenski@ucsb.edu",
    license=open('LICENSE').read(),
    install_requires=requires,
    url="https://github.com/AntelopeLCA/antelope",
    summary="An interface specification for accessing LCA data",
    long_description=open('README.md').read(),
    packages=find_packages()
)
