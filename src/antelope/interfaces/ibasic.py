from .abstract_query import AbstractQuery


class BasicRequired(Exception):
    """
    Default exception to indicate that the requested method cannot be invoked without an implementation of the
    basic interface (and none could be found).
    """
    pass


class ValidationError(Exception):
    """
    :meta private:
    """
    pass


class EntityNotFound(Exception):
    """
    An exception of generic usefulness.
    """
    pass


class NoAccessToEntity(Exception):
    """
    Used when the actual entity is not accessible, i.e. when a ref cannot dereference itself
    """
    pass


class ItemNotFound(Exception):
    """
    not a KeyError
    """
    pass


class BasicInterface(AbstractQuery):
    """
    BasicInterface core methods.

    These are methods for retrieving objects and accessing documentary information about them. The basic interface
    should provide access to the most authoritative source of information about a data resource.


    """
    """
    Basic "Documentary" interface implementation
    From JIE submitted:
     - get(id)
     - properties(id)
     - get item(id, item)
     - get reference(id)
     - synonyms(id-or-string)
    provided but not spec'd:
     - validate
     - get_uuid
    """

    def validate(self):
        """
        This method should return `True` whenever the implementation is attached to a valid data source that is
        capable of answering questions.  The existence of a basic implementation is necessary and sufficient for a
        query to be valid.

        :return: bool
        """
        if self._validated is None:
            try:
                self._perform_query('basic', 'validate', ValidationError)
                self._validated = True
            except ValidationError:
                return False
        return self._validated

    def get(self, eid, **kwargs):
        """
        Basic entity retrieval-- should be supported by all implementations
        :param eid:
        :param kwargs:
        :return:
        """
        return self._perform_query('basic', 'get', EntityNotFound, eid,
                                   **kwargs)

    def properties(self, external_ref, **kwargs):
        """
        Get an entity's list of properties
        :param external_ref:
        :param kwargs:
        :return:
        """
        return self._perform_query('basic', 'properties', EntityNotFound, external_ref, **kwargs)

    def get_item(self, external_ref, item):
        """
        access an entity's properties.  This requires de-referencing the query to the true entity.  This method
        is used to access essentially all documentary information about an object.
        :param external_ref: the entity's identifier
        :param item: the desired property
        :return:
        """
        return self._perform_query('basic', 'get_item', ItemNotFound,
                                   external_ref, item)

    def get_uuid(self, external_ref):
        return self._perform_query('basic', 'get_uuid', EntityNotFound,
                                   external_ref)

    def get_context(self, term, **kwargs):
        """
        Return the context matching the specified term
        :param term:
        :param kwargs:
        :return:
        """
        return self._perform_query('basic', 'get_context', BasicRequired,
                                   term, ** kwargs)

    def get_reference(self, external_ref):
        return self._perform_query('basic', 'get_reference', EntityNotFound,
                                   external_ref)

    def synonyms(self, item, **kwargs):
        """
        Return a list of synonyms for the object -- quantity, flowable, or compartment
        :param item:
        :return: list of strings
        """
        return self._perform_query('basic', 'synonyms', KeyError, item,
                                   **kwargs)

    def is_lcia_engine(self, **kwargs):
        """
        A key question in the quantity interface is the way terms are managed.
        An archive's Term Manager determines how input terms are interpreted and how characterizations are looked up.
        There are two main footings:

         - the terms specified by the source are authentic / canonical and should be reproduced
         - terms from different data sources refer to the same concept, and the *concept* should be returned.

        A *provincial* term manager considers the local archive (to which it is attached) to be the source of all
        truth. It will return flowables and contexts exactly as they are defined in the native data source.  In
        this case, `is_lcia_engine()` returns `False`.

        if the term manager is an LciaEngine, it uses a standard set of contexts and flowables, and provides routes
        to add new synonyms for flowables/contexts and to report new flowables or contexts.  Ultimately the objective
        is to manage characterization + knowledge of both elementary and intermediate flows.
        In this case, `is_lcia_engine()` returns `True`.

        :param kwargs:
        :return: bool
        """

        try:
            return self._perform_query('basic', 'is_lcia_engine', TypeError, **kwargs)
        except TypeError:
            return False

    def bg_lcia(self, process, query_qty=None, ref_flow=None, **kwargs):
        """
        Basic interface permits cumulative LCIA scores to be retrieved, but only if values=True

        :param process:
        :param query_qty: if omitted, a catalog may select a default LCIA method
        :param ref_flow:
        :param kwargs:
        :return:
        """
        return self._perform_query('basic', 'bg_lcia', BasicRequired,
                                   process, query_qty, ref_flow=ref_flow, **kwargs)


