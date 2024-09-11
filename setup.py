from setuptools import setup

setup()


"""
Version History:
0.2.7   2024/09/10 - synchronization release for background / LCI changes 
                     add make_ref() machinery to a few interface routes
                     alter extend_process to use dependencies instead of inventory
                     make deep_lcia() biogenic-aware
                     (note: folding observations directly into lci() / abandoning sys_lcia() still to come)

0.2.6.3 2024/08/15 - cutoff_flows and remote traversal compatibility
                   - modify FlowInterface and FlowEntity to not die on missing reference_entity

0.2.6.2 2024/06/11 - get_context into basic interface
0.2.6.1 2024/06/06 - ItemNotFound

0.2.6 2024/05/29 - split_subfragment and fragments_with_flow into fg interface
                   contrib_lcia is an exchange method
                   un-resolved CatalogRefs can now return their replacement, if provided a query at instantiation 
                   
0.2.5 2024/05/06 - bg_lcia() becomes a basic interface route; sys_lcia() is the fully-featured background route

0.2.4 2024/04/17 - split out BasicInterface from AbstractQuery. 
                   abandon setup.py except for this changelog.
                   Redesign ExteriorFlow to have maybe a little bit more logic
                   First pass at API documentation

0.2.3.2 2024/03/26 move to src layout

0.2.3.1 2024/03/22 LciaDetail objects now return DirectedFlow instead of FlowSpec (as exchange proxy)

0.2.3 2024/01/05 - 'lcia' index route; exclude LCIA metadata from quantity manager synonyms
                   Versions >= 0.2.3 to support 0.3-branch development code (but this package is not branched)

0.2.2 2023/11/30 - oryx debug release
 
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
