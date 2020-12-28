from setuptools import setup, find_packages
from antelope_interface import ANTELOPE_VERSION

requires = [
    "synonym_dict"
]

"""
Version History:
0.1.2 2020/12/28 - Background interface- re-specify cutoffs to be process-specific; create sys_lci;

0.1.1 2020/11/12 - Bug fixes and boundary setting
                   add synonyms() route and grant a ref access to synonyms from its origin
                   terminate() is now called targets()
                   remove most of the foreground interface spec
                   
0.1.0 2020/07/31 - Initial release - JIE paper 
"""

setup(
    name="antelope_interface",
    version=ANTELOPE_VERSION,
    author="Brandon Kuczenski",
    author_email="bkuczenski@ucsb.edu",
    license=open('LICENSE').read(),
    install_requires=requires,
    url="https://github.com/AntelopeLCA/antelope",
    summary="An interface specification for accessing LCA data",
    long_description=open('README.md').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering"
    ],
    python_requires='>=3.6',
    packages=find_packages()
)
