What is a Fragment?
====

Life cycle inventory data are made up principally of "processes" and "flows," where
the processes are industrial
activities that occur, and the flows are the inputs and outputs to the processes.
The unit process is commonly regarded as the "smallest unit" of information in LCA.

However, In Antelope, we regard the *exchange* as the smallest unit of information, and
a "fragment" is what we call an "observed exchange".  An exchange is a single flow coming
into or out of a process (they all have to flow in a set for the process to work). When
the process "runs", the flow comes from (or goes to) *somewhere*, a "terminus" or a "provider",
and it comes in a certain *amount*.

These five pieces of information define a fragment or an observed exchange:
 - The activity being observed (this is called the parent node. This where the
observation occurred)
 - the identity and characteristics of the flow
 - the flow's direction (input or output)
 - the amount of the flow
 - the "anchor" (provider, sink, terminus) of the flow,

A fragment is a flow exchanged between two nodes. The nodes can be different process steps,
different facilities, different supply chain partners, etc.  A node can even be an entire
industry sector.

Individual fragments can be thought of like tinker toys that can be put together.  In order
to describe an actual industrial process, a number of different flows must be observed and
recorded in concert to achieve the measurement.  So a "fragment" colloquially also means a
*tree* of individual fragment branches that has been put together for the purposes of modeling.




Nested Fragments
----

The most useful aspect of fragments is that they can be *nested*

Observation
----



but an
exchange can be directly *observed*.  One can *look* at an injection molding machine and
measure the amount of plastic that goes in, as well as the number of products that come out.


[image]

A fragment is the smallest piece of an LCA model. It

represents the *act of flow* of a modeling element,
