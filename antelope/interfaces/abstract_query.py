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

    def _perform_query(self, itype, attrname, exc, *args, strict=False, **kwargs):
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
