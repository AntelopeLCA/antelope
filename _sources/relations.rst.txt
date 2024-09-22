Quantitative Information
------------------------
The numerical data required to perform LCA computations can be described entirely with the
following two *ratiometric* relations:

1. **Exchange relation**: for a given process, the amount of an *exchange flow* that is
exchanged in proportion to a unit amount of a *reference flow*

  Example: for a machine that produces widgets, the process requires 0.435 kWh of electricity
  for every 1,000 widgets it produces.

2. **Characterization relation**: for a given flow, the measure of a *query quantity*
that is equivalent to a unit measure of the *reference quantity*

  Example: A fuel's primary reference is its higher heating value, and the fuel flow is found
  to have a mass of 22.4 grams per MJ (HHV)

Each relation represents the ratio of two extensive measurements.  The exchange relation is
used to construct the technology and environment matrices (A, B) in the LCA computation,
often with flow characterizations as supporting information.  The characterization relation
alone is used to construct the characterization matrix C.

Semi-Quantitative Information
-----------------------------
Omitting the numerical data from the above relations, they still express precise information:
the presence or absence of an entry in the sparse A, B, and C matrices.  The inventory of
a unit process, reporting exchanges but not exchange values, still discloses information,
namely the set of flows associated with the operation of the process.  This information
describes the structure of the process-flow graph that makes up the product system model.
