# Antelope Design Principles

Data sources used in life cycle assessment provide a variety of different types of information, and different use cases require different subsets of information.  The purpose of the Antelope framework is twofold:

 1. To identify separate types of data according to a consistent specification;
 2. To develop tools that make use of that specification to simplify the tasks of publishing and accessing data.

This package `antelope` contains the minimal interface specification.  It is accompanied by a separate, reference implementation ([antelope core](https://github.com/AntelopeLCA/antelope_core)) that can be used for research purposes.

# Contents of this repository

The repository contains three main elements.

## Entity Specification

### Activity versus Process

The contents of a data resource in Life Cycle Assessment are typically described as a collection of relationships among **activities** and **flows** [1][2], where activities accomplish some task through the exchange of flows with other activities.  The field has never fully engaged with the difference between conceptual "activities and flows," and actual instances of activities and flows that make up data resources.

In Antelope, the two distinct terms of "activity" and "process" are used differently.  An "activity" has a conceptual definition *only*, and is not directly used in modeling. In contrast, a `process` is considered to be a precise description of an activity over a specific spatial and temporal scope.  Think of a `process` as an "inventoried activity."  There is no `activity` data type in Antelope, and the documentation of activities themselves, as well as the relationship among different processes that may represent the same activity, is not considered here.

### Three Fundamental Entity Classes

This schema recognizes three fundamental entity classes.  Each entity class has a shared set of characteristics, defined by the `EntityInterface` (see below).  

 * **Quantities** are used to measure extensive values.  Different quantities are generally not commensurable with one another.  A quantity's defining characteristic is its fixed unit of measure.

 * **Flows** are the defining concept of life cycle assessment.  A flow can represent any accountable element of a product model, including a physical substance, an economic payment, a service delivery, an event such as transformation of area or occupation of space, or a record of a conceptual occurrence.  Flows are the "swiss army knife" of LCA, and they are used in every LCA-related data publication.

 * **Processes** are concrete descriptions of the inter-relationships of several flows within a specific activity.  A process is characterized by one or more *reference exchanges* and zero or more *dependent exchanges*.  As is consistent with ISO 14040-44-48, A process must have a designated quantitative reference.


Each entity can be described programmatically in terms of the `EntityInterface`:

 * `type`, a string describing the type of entity
 * `reference_entity` - a type-specific object that defines a reference
 * `origin` - A semantic origin where the entity is authentically defined
 * `external_ref` - a reference string used to identify the entity with respect to the origin
 * `link` that identifies an entity uniquely. Nominally <origin>/<external_ref>
 * `properties()` - generates a list of properties the entity possesses
 * `get(property)` - retrieves the value of a given property
 * `is_entity` flag that indicates whether it is a true entity or a reference to an entity. By default, anything returned by the interface is a reference (`False`), whereas anything created in an implementation could be a true entity (`True`).
 * `make_ref()` - true entities must implement a method which generate references to themselves.

### Quantity Interface

A Quantity is an `entity` whose reference entity must be a unit in some form.  The entity inherits the `EntityInterface` plus adds the following:

 * `unit`: a unit string that is derived from the reference_entity

### Flow Interface

First, a flow is an `entity`. The `FlowInterface` is a subclass of entity interface.  Its reference entity must be a quantity of measure (i.e. an entity whose `entity_type == 'quantity'`), such as mass or volume.  It specifies:

 * `unit` string unit of measure for the flow's reference quantity.
 * `name`, human-readable string to describe the flow
 * `synonyms`, a generator of strings that are synonymous to the name
 * `_add_synonym(term)`, private method to add synonyms
 * `context` (optional), a tuple of strings in hierarchical sequence
 * `match(other)` - method that can be used to compare a flow to another flow to determine whether they are the same.

An object satisfying this interface is easy to work with in an LCA setting.

### Flow

The Antelope interface provides a [flow implementation](antelope/flows/flow.py).  The implementation uses a [synonym set](https://pypi.org/project/synonym-dict/) to implement the flow name, synonyms, and matching.  This is the package's only dependency.


[1] - Janowicz et al 2015
[2] - BONSAI ontology
