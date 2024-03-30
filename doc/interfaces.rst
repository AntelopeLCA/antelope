Organizing LCA Data in Antelope
===============================



Interfaces
==========

The problem of LCA computation can be broken up into several distinct pieces, each of which
utilizes different *kinds* of information and requires different levels of access to sensitive
data. The Antelope API is divided up into the following seven distinct interfaces:

- **basic**: Retrieve documentary information about a data object
- **index**: Information about the contents of different data sources, including quantities, flows,
  processes, reference flows, and contexts
- **exchange**: The exchange relation, i.e. flows exchanged by processes
  (*numerical*: exchange values)
- **quantity**: The characterization relation, i.e. different quantities of measure for flows
  (*numerical*: characterization values)
- **background**: The construction and inversion of technology matrix, multiplied by environment matrix
- **configure**: Information about how flows are characterized and processes are allocated and
  linked during background computation
- **foreground**: Working environment for constructing models through reference to the other interfaces

Each interface is handled by a separate subclass in the Antelope interface.