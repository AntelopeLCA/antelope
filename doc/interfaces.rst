Organizing LCA Data in Antelope
-------------------------------



Interfaces
==========

The problem of LCA computation can be broken up into several distinct pieces, each of which
utilizes different *kinds* of information and requires different levels of access to sensitive
data. The Antelope API is divided up into the following seven distinct interfaces:

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   interfaces/basic
   interfaces/index
   interfaces/exchange
   interfaces/quantity
   interfaces/background
   interfaces/configure
   interfaces/foreground


The

.. list-table::
   :header-rows: 1

   * - Interface
     - Description
     - Values?
     - Writable?
   * - :doc:`basic <interfaces/basic>`
     - Retrieve documentary information about a data object
     - -
     - -
   * - :doc:`index <interfaces/index>`
     - Information about the contents of different data sources, including quantities, flows, processes, reference flows, and contexts
     - -
     - -
   * - :doc:`exchange <interfaces/exchange>`
     - The exchange relation, i.e. flows exchanged by processes
     - exchange values
     - -
   * - :doc:`quantity <interfaces/quantity>`
     - The characterization relation, i.e. different quantities of measure for flows
     - characterization values
     - in foreground
   * - :doc:`background <interfaces/background>`
     - The construction and inversion of technology matrix, multiplied by environment matrix
     - LCI results
     - -
   * - :doc:`configure <interfaces/configure>`
     - Information about how flows are characterized and processes are allocated and linked during background computation
     - -
     - for own resources
   * - :doc:`foreground <interfaces/foreground>`
     - Working environment for constructing models through reference to the other interfaces
     - -
     - for own foregrounds

Each interface is handled by a separate Antelope subclass. Click on the links to read about them.

Implementation
^^^^^^^^^^^^^^

The Antelope interfaces are all subclasses of an :class:`abstract query <AbstractQuery>` class.
Each antelope interface can be implemented by creating a subclass and implementing the abstract
methods.