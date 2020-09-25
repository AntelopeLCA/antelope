# Antelope Design Principles

Data sources used in life cycle assessment provide a variety of different types of information, and different use cases require different subsets of information.  The purpose of the Antelope framework is twofold:

 1. To identify separate types of data according to a consistent specification;
 2. To develop tools that make use of that specification to simplify the tasks of publishing and accessing data.

This package `antelope` contains the minimal interface specification.  It is accompanied by a separate, reference implementation ([antelope core](https://github.com/AntelopeLCA/antelope_core)) that can be used for research purposes.

# Contents of this repository

The repository contains three main elements.

## Flow Specification

A `flow` is the defining concept of life cycle assessment.  A flow can represent any accountable element of a product model, including a physical substance, an economic payment, a service delivery, an event such as transformation of area or occupation of space, or a record of a conceptual occurrence.  Flows are the "swiss army knife" of LCA, and they are used in every LCA-related data publication.

For that reason, this interface must assume a [core definition of a flow](antelope/flows/flow_interface.py).

### Flow Interface

First, a flow is an `entity`. The `EntityInterface` defines:

 * `type`, a string describing the type of entity
 * `reference entity`
 * `link` that identifies an entity uniquely
 * `is_entity` flag that indicates whether it is a true entity or a reference to an entity. By default, anything returned by the interface is a reference (`False`), whereas anything created in an implementation could be a true entity (`True`).
 * `make_ref()` - true entities must implement a method which generate references to themselves.

The `FlowInterface` is a subclass of entity interface.  Its reference entity must be a quantity of measure, such as mass or volume.  It specifies:

 * `unit` string unit of measure for the flow's reference quantity.
 * `name`, human-readable string to describe the flow
 * `synonyms`, a generator of strings that are synonymous to the name
 * `_add_synonym(term)`, private method to add synonyms
 * `context` (optional), a tuple of strings in hierarchical sequence
 * `match(other)` - method that can be used to compare a flow to another flow to determine whether they are the same.

An object satisfying this interface is easy to work with in an LCA setting.

### Flow

The Antelope interface provides a [flow implementation](antelope/flows/flow.py).  The implementation uses a [synonym set](https://pypi.org/project/synonym-dict/) to implement the flow name, synonyms, and matching.  This is the package's only dependency.


