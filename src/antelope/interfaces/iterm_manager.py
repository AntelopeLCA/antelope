"""
Abstract interface for term manager providers.

A term manager is the object stored in ``archive.tm``.  It handles synonym
resolution for flowables and contexts, and manages characterization factors.

The surface was derived by auditing every ``self._archive.tm.*`` access across
``antelope_core/implementations/*.py``.
"""

from abc import ABC, abstractmethod


class TermManagerInterface(ABC):
    """
    Minimal contract that a term manager object must satisfy to work with the
    standard ``*Implementation`` classes in ``antelope_core``.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def is_lcia_engine(self) -> bool:
        """
        True if this term manager operates as a full LCIA engine — i.e. it
        uses a standard canonical set of flowables and contexts and can match
        synonyms across data sources.  False for a provincial term manager
        that treats its own archive as the sole source of truth.
        """

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    @abstractmethod
    def __getitem__(self, term):
        """
        Look up *term* and return the matching ``Context`` (or flowable
        canonical name), or ``None`` if not found.  *term* may be a string
        synonym, a ``Context`` object, or ``None``.

        Used by ``BasicImplementation.get_context`` and
        ``QuantityImplementation._get_flowable_info``.
        """

    @abstractmethod
    def get_flowable(self, flow):
        """
        Return the canonical flowable name for *flow*.
        Raises ``KeyError`` if not recognised.

        Used by ``IndexImplementation.unmatched_flows``.
        """

    @abstractmethod
    def get_canonical(self, quantity):
        """
        Return the canonical quantity entity for *quantity* (which may be a
        string external_ref or a quantity object).
        Raises ``EntityNotFound`` if not recognised.

        Used by ``QuantityImplementation.get_canonical`` and related helpers.
        """

    # ------------------------------------------------------------------
    # Enumeration
    # ------------------------------------------------------------------

    @abstractmethod
    def synonyms(self, item):
        """
        Generate synonym strings for the given flowable or context *item*.

        Used by ``BasicImplementation.synonyms``.
        """

    @abstractmethod
    def flowables(self, **kwargs):
        """
        Generate canonical flowable name strings, optionally filtered by
        keyword arguments.

        Used by ``IndexImplementation.flowables``.
        """

    @abstractmethod
    def contexts(self, **kwargs):
        """
        Generate ``Context`` objects known to this term manager, optionally
        filtered by keyword arguments.

        Used by ``IndexImplementation.contexts``.
        """

    # ------------------------------------------------------------------
    # Characterization factors
    # ------------------------------------------------------------------

    @abstractmethod
    def factors_for_quantity(self, quantity, flowable=None, context=None, dist=0):
        """
        Generate ``Characterization`` objects for the given canonical
        *quantity*, optionally filtered by *flowable* and *context*.

        *dist* controls context-matching strictness:
          0 = exact match, 1 = child contexts, 2 = parent context,
          3 = any ancestor including NullContext.

        Used by ``QuantityImplementation.factors``.
        """

    @abstractmethod
    def factors_for_flowable(self, flowable, quantity=None, context=None, **kwargs):
        """
        Generate ``Characterization`` objects for the given canonical
        *flowable* string, optionally filtered by *quantity* and *context*.

        Used by ``QuantityImplementation._quantity_engine`` and
        ``_ref_qty_conversion``.
        """

    @abstractmethod
    def add_characterization(self, flowable, ref_quantity, query_quantity,
                             value, context=None, location='GLO', origin=None,
                             **kwargs):
        """
        Store a characterization factor: 1 unit of *ref_quantity* of
        *flowable* in *context* equals *value* units of *query_quantity*.

        *location* defaults to ``'GLO'``; *origin* defaults to the archive's
        own ``ref`` string when called from ``ConfigureImplementation``.

        Used by ``QuantityImplementation.characterize`` and
        ``ConfigureImplementation.characterize_flow``.
        """
