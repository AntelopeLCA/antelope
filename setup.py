from setuptools import setup, find_packages

ANTELOPE_VERSION = '0.2.1'

requires = [
    "synonym_dict>=0.2.0",
    "pydantic>=1.8.2"
]

"""
Version History:
0.2.1-virtualize - 2023/04/10 xdb passes benchmarks.
                   pydantic models moved into interface
                   sys_lci and bg_lcia operational, both locally and remotely

0.2.0-virtualize - in progress, with xdb
                   minimal complete foreground spec
                   add xdb token spec
                   
0.1.8 2022/04/08 - Minor changes, to go along with 0.1.8 core release
 - support None in exchanges_from_spreadsheet (this will still not work until xls_tools is out)
 - add comp_sense function to relate Sink-Output and Source-Input
 - add emitters() function
 - add positional search argument for flowables()
 - allow refs to operate with invalid queries

0.1.7 2021/08/05 - merge configuration changes developed in virtualize branch

0.1.6 2021/03/16 - get_context() into flow interface spec- returns an implementation-specific context entity

0.1.5 2021/03/09 - remove unnecessary dependence on Py>=3.7 in namedtuple use

0.1.4 2021/01/29 - unobserved_lci; fix result caching on flow refs and process refs

0.1.3 2020/12/30 - upstream change in synonym_dict- bump requirements

0.1.2b 2020/12/29 - fix last edit
0.1.2a 2020/12/29 - fix last edit

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
    license="BSD 3-Clause",
    install_requires=requires,
    url="https://github.com/AntelopeLCA/antelope",
    summary="An interface specification for accessing LCA data",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    include_package_data=True,
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
