# antelope
Standard Interface and reference framework for LCA

The `antelope` package is an interface specification for accessing LCA data resources. 
The goal of the Antelope project is to reduce the complexity of LCA along three central 
fronts:

 1. Reduce complexity of *modeling* by providing a simple, recursive data structure (the
fragment) that can effectively describe complex, dynamic LCA models;
 2. Reduce complexity of *software* by liberating users from costly and cumbersome desktop
LCA software applications and relocating reference data to the cloud, without compromising
computational sophistication;
 3. Reduce complexity of *communication* by providing online tools for describing and sharing
LCA models that conceal or omit confidential and proprietary information.


## Principles

The Antelope framework is *distributed by design*, intended to allow data owners to independently
create and manage their own intellectual property, allowing access by others while regulating
what can be seen and concealed.

Antelope provides a *hosting platform* for working online and sharing information within a
trust network.  User-owned data is managed by owners, while reference data is curated by
the user community.

Antelope uses *separation of concerns* to help organize different computational facets of
the LCA problem into separate services. 

## Documentation

Coming to github.io

### See Also

 * [vault.lc](https://vault.lc/) Home to the Antelope authentication service
 * [antelope_core](https://github.com/AntelopeLCA/core) The reference implementation including local data source management.
 * [antelope_background](https://github.com/AntelopeLCA/background) Used for partial ordering of databases and construction and inversion of matrices
 * [antelope_foreground](https://github.com/AntelopeLCA/foreground) Used for building foreground models
