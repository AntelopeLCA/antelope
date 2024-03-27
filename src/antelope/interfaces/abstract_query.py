"""
Root-level catalog interface
"""


class ValidationError(Exception):
    pass


class PrivateArchive(Exception):
    pass


class EntityNotFound(Exception):
    pass


class NoAccessToEntity(Exception):
    """
    Used when the actual entity is not accessible, i.e. when a ref cannot dereference itself
    """
    pass


class AbstractQuery(object):
    """
    Not-quite-abstract base class for executing queries

    Query implementation must provide:
     - origin (property)
     - _iface (generator: itype)
     - _tm (property) a TermManager
    """
    _validated = None

    '''
    Overridde these methods
    '''
    @property
    def origin(self):
        return NotImplemented

    def make_ref(self, entity):
        raise NotImplementedError

    def _perform_query(self, itype, attrname, exc, *args, **kwargs):
        """

        :param itype: type of query being performed (which interface is being invoked)
        :param attrname: query name
        :param exc: "fallback exception": ignore it if an implementation raises it; then raise it if no implementation
         succeeds
        :param args: to pass to the query
        :param kwargs: to pass to the query or subclass
        :return:
        """
        raise NotImplementedError

    '''
    Internal workings
    '''
    '''
    Can be overridden
    '''
    def _grounded_query(self, origin):
        """
        Pseudo-abstract method used to construct entity references from a query that is anchored to a metaresource.
        must be overriden by user-facing subclasses if resources beyond self are required to answer
        the queries (e.g. a catalog).
        :param origin:
        :return:
        """
        return self

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
        access an entity's dictionary items
        :param external_ref:
        :param item:
        :return:
        """
        '''
        if hasattr(external_ref, 'external_ref'):  # debounce
            err_str = external_ref.external_ref
        else:
            err_str = external_ref
        '''
        return self._perform_query('basic', 'get_item', EntityNotFound,
                                   external_ref, item)

    def get_uuid(self, external_ref):
        return self._perform_query('basic', 'get_uuid', EntityNotFound,
                                   external_ref)

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
        A key question in the quantity interface is the way terms are managed.  There are two main footings:
         - the terms specified by the source are authentic / canonical and should be reproduced
         - terms from different data sources refer to the same concept.
        An archive's Term Manager determines how input terms are interpreted and how characterizations are looked up.

        if the term manager is an LciaEngine, it uses a standard set of contexts and flowables, and provides routes
        to add new synonyms for flowables/contexts and to report new flowables or contexts.  Ultimately the objective
        is to manage characterization + knowledge of intermediate flows.

        This routine reports whether an origin implements the LciaEngine [protocol?] for dealing with flows.

        :param kwargs:
        :return: True/False - could also provide more structured information as needed.
        """

        try:
            return self._perform_query('basic', 'is_lcia_engine', TypeError, **kwargs)
        except TypeError:
            return False

