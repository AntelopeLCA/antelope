"""
Abstract interface for archive providers.

An archive is the object stored in ``BasicImplementation._archive`` (and all
subclass implementations).  Any object that satisfies this interface can be
used as a provider for the standard implementation classes.

The surface was derived by auditing every ``self._archive.*`` access across
``antelope_core/implementations/*.py``.
"""

from abc import ABC, abstractmethod


class ArchiveInterface(ABC):
    """
    Minimal contract that a provider object must satisfy to work with the
    standard ``*Implementation`` classes in ``antelope_core``.

    Read-only requirements are marked with ``@property``; methods that may
    mutate the store are marked accordingly in their docstrings.
    """

    # ------------------------------------------------------------------
    # Identity / metadata
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def ref(self) -> str:
        """Semantic reference string used as the archive's origin identifier."""

    @property
    @abstractmethod
    def source(self) -> str:
        """Physical data source (file path, URL, etc.) — used for display."""

    # ------------------------------------------------------------------
    # Entity access
    # ------------------------------------------------------------------

    @abstractmethod
    def __getitem__(self, key):
        """
        Return the already-loaded entity for *key*, or ``None`` if not present.
        Must never raise on a cache miss — return ``None`` instead.
        """

    @abstractmethod
    def _fetch(self, key, **kwargs):
        """
        Obtain the entity for *key* in a provider-specific way.  Raise ``EntityNotFound`` on failure
        """

    # ------------------------------------------------------------------
    # Interface factory
    # ------------------------------------------------------------------

    @abstractmethod
    def make_interface(self, itype: str):
        """
        Return an implementation object for the named interface type string
        (``'basic'``, ``'index'``, ``'exchange'``, ``'quantity'``,
        ``'background'``, ``'configure'``).
        """
