# antelope
Standard Interface and reference framework for LCA

The `antelope` package is an interface specification for accessing LCA data resources, as described in [JIE submitted].  It should be subclassed by implementations that wish to expose data using this uniform interface.  A reference implementation, including a stand-alone LCA computing tool, exists...

## Documentation

See the following articles:

 * [Antelope Design Principles](principles.md) for documentation of this repository.
 * [Entity Specification](entities.md) and nomenclature.
 * [Return Types](types.md) which are *references* to entities.

### See Also

 * [antelope_core](https://github.com/AntelopeLCA/core) The reference implementation including local data source management.
 * [antelope_background](https://github.com/AntelopeLCA/background) Used for partial ordering of databases and construction and inversion of matrices
 * [antelope_foreground](https://github.com/AntelopeLCA/foreground) Used for building foreground models
