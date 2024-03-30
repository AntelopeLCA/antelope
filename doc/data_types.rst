Basic Data Types
----------------

The data types in Antelope are similar to conventional LCA, with one extension.

1. **quantities** are dimensions of measurement. They can be either directly measurable,
such as mass, price, volume, or energetic content; or "analytic", derived from a mathematical
model.
  - In Antelope, all quantities are **extensive**. Intensive measures like pressure and
    temperature are not available.
  - All quantities have a ``referencue unit``, typically abbreviated as ``unit``, which is
    the quantitative extent of 1.0 of the quantity.
  - All analytic quantites have an ``Indicator`` property, which describes what they measure.
  - LCIA Indicators are analytic quantities. They often also have a ``Method`` property that
    names the family of indicators they are a part of.

2. **flows** are "anything that can be measured or observed." Flows are one of the two key
data types established in `ISO 14048`_. A flow can include a physical object (e.g. with mass
and volume), an amount of energy, a discrete item, a form of service, a currency, or anything
else that can be assigned a measurable extent.
  - Every flow is assigned a ``reference quantity`` which gives the principal dimension in
    which it can be measured.
  - A flow's ``unit`` is the same as its reference quantity's unit.
  - A flow can optionally be given a ``locale`` and / or a ``context`` (see below)

3. **processes** are the counterpart to flows. In other words, a process is defined by the
set of flows that are *exchanged* by it with other processes or environmental compartments.
  - A process is something that has "activity" and can be *operated*.  When a process is
    operated, all of its
    flows are exchanged in concert with one another, and typically in fixed proportion to
    one another.
  - Processes have a spatial boundary and a temporal extent.

4. **contexts** are analogous to processes in that they are counterparts to flows. However,
contexts are more like "stocks" or reservoirs than processes.  A context has no notion of
activity or operation, and instead simply acts as a reservoir.
  - Contexts can be either "elementary" (part of nature) or intermediate (part of the human
    system or the "technosphere")
  - A flow that is exchanged between a process and an elementary context can have an
    environmental effect or impact.
  - A flow that is exchanged between a process and an intermediate context cannot have an
    environmental effect.

.. _`ISO 14048`: https://www.iso.org/standard/29872.html


