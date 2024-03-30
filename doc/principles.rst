Key principles of operation
---------------------------

 *Data-free Models*

The structure of product system models that are used in LCA can be described without disclosing
data considered to be confidential.  The *data-free product model* is a description of an LCA
study from which all non-disclosed information has been removed.

One key feature the Antelope framework provides is the ability to share and distribute data-free
product models to various users according to the specifications of the model owner.  A model
can be "viewed" online, and a viewer may fill in the missing values using information
available to them, or by making their own assumptions.  They can then run the models and
generate and inspect the results.

Data-free models may or may not be copied or shared depending on the restrictions placed
by the owner.

 *Data owners are in control*

The primary function of the Antelope framework is to enable data owners and LCA modelers to
build and manage life cycle models.  The purpose of the *vault.lc service* is to support
the generalized access and use of Antelope models, and to provide capabilities for data sharing
and shared computation.

 *Strict privacy is the goal*

Although the pilot software does not support this, it is the intention of the platform to
provide strict mechanistic privacy to data owners through segregation of resources, including
distributed hosting.  Data owners (as hosts) will have discretion over whether to respond to
any request for data.  In the strict-privacy case, computational results will be prepared
by ephemeral *secure enclaves*, which will prepare and perform the shared computations
by submitting data requests to all involved parties and aggregating the results.  The results
are reported to the party that directed (and funded) the computation, though canonically
it is good practice to disclose the net result ("bottom line") to all parties who provided
data. Parties may negotiate to disclose or conceal information from one another.

In principle, vault.lc staff and employees should not have access to any computation elements
or results unless disclosure of that information is part of the computation terms.


 *All primary data are extensive*

The flow measurements that are relevant to LCA practice are all *extensive* -- i.e. they have
"extent."  The definitive characteristic of a flow is that there can be *more* of it.  Whatever
units are used to describe flows in LCA, they are all extensive: mass, volume, price, calorific
value, freight transport, land transformation and occupation.   Anything with extent can be
measured.

In contrast, unit processes are described entirely with *intensive* values: amounts of energy,
supplies, or materials used *per unit* of production.  None of these values can be measured;
they can only be inferred as the *ratio* of two (extensive) measurements of *flows*.

When considering the precision and accuracy of LCA results, it is important to remember what
extensive measurements underlie them.  Sometimes this distinction is trivial-- a well-made unit
process inventory for a factory will report "kWh/widget" as the ratio of the two extensive
measurements: kWh consumed and widgets produced, over a fixed time period.  However, the use
of a secondary dataset as a proxy will obfuscate the extensive measurements that are being
used to represent the activity being modeled.

An implication of this principle is that measurements of *intensive physical quantities*,
such as temperature or pressure, are not material to LCA computation.
