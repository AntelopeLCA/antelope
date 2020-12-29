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
    Not-qute-abstract base class for executing queries

    Query implementation must provide:
     - origin (property)
     - _iface (generator: itype)
     - _tm (property) a TermManager
    """
    _dbg = False
    _validated = None

    def on_debug(self):
        self._dbg = True

    def off_debug(self):
        self._dbg = False

    def _debug(self, *args):
        if self._dbg:
            print(*args)

    '''
    Overridde these methods
    '''
    @property
    def origin(self):
        return NotImplemented

    def make_ref(self, entity):
        """
        Query subclasses can return abstracted versions of query results.
        :param entity:
        :return: an entity that could have a reference to a grounded query
        """
        if entity is None:
            return None
        if entity.is_entity:
            return entity.make_ref(self)
        else:
            return entity  # already a ref

    def _iface(self, itype, **kwargs):
        """
        Pseudo-abstract method to generate interfaces of the specified type upon demand.  Must be implemented
        :param itype: 'basic', 'index', 'exchange' (nee 'inventory'), 'quantity', 'background', 'foreground'
        :param kwargs: for use by subclasses
        :return: generate interfaces of the given type
        """
        return NotImplemented

    '''
    Internal workings
    '''
    def _perform_query(self, itype, attrname, exc, *args, strict=False, **kwargs):
        self._debug('Performing %s query, iface %s' % (attrname, itype))
        try:
            for iface in self._iface(itype, strict=strict):
                try:
                    self._debug('Attempting %s query on iface %s' % (attrname, iface))
                    result = getattr(iface, attrname)(*args, **kwargs)
                except exc:  # allow nonimplementations to pass silently
                    continue
                if result is not None:  #successful query must return something
                    return result
        except NotImplementedError:
            pass

        raise exc('itype %s required for attribute %s | %s' % (itype, attrname, args))

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
                self._validated = False
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
        return self._perform_query(None, 'properties', EntityNotFound, external_ref, **kwargs)

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
        return self._perform_query(None, 'get_reference', EntityNotFound,
                                   external_ref)

    def synonyms(self, item, **kwargs):
        """
        Return a list of synonyms for the object -- quantity, flowable, or compartment
        :param item:
        :return: list of strings
        """
        return self._perform_query(None, 'synonyms', EntityNotFound, item,
                                   **kwargs)
