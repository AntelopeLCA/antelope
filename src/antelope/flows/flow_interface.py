from abc import ABC


class BaseEntity(object):
    """
    The very most basic characteristics of entities and entity refs
    """
    @property
    def entity_type(self):
        return NotImplemented

    @property
    def reference_entity(self):
        """
        Must have a .unit property that returns a string,
        should have .entity_type property that returns 'quantity'
        :return:
        """
        return NotImplemented

    @property
    def origin(self):
        """
        Must return a resolvable unique ID, nominally 'origin/external_ref'
        :return:
        """
        return NotImplemented

    @property
    def external_ref(self):
        """
        Must return a resolvable unique ID, nominally 'origin/external_ref'
        :return:
        """
        return NotImplemented

    @property
    def link(self):
        return '%s/%s' % (self.origin, self.external_ref)

    def properties(self):
        raise NotImplementedError

    def get(self, item):
        return NotImplemented

    @property
    def is_entity(self):
        """
        Used to distinguish between entities and catalog refs (which answer False)
        :return: True for LcEntity subclasses
        """
        return False

    def make_ref(self, query):
        """
        if is_entity is true, entity must return a ref made from the provided query
        :param query:
        :return:
        """
        return NotImplemented


class NullEntity(BaseEntity):
    entity_type = 'null'
    external_ref = 'null'
    reference_entity = None

    def __init__(self, origin):
        self._origin = origin

    @property
    def origin(self):
        return self._origin

    def properties(self):
        for i in ():
            yield i

    def get(self, item):
        raise KeyError

    def make_ref(self, query):
        return NotImplemented


class FlowInterface(BaseEntity, ABC):
    """
    An abstract class that establishes common functionality for OBSERVATIONS OF FLOWS.  A Flow consists of:
     - a reference quantity with a fixed unit
     - a flowable (a list of synonyms for the flowable substnce being described)
     - a context (a hierarchical list of strings designating the flows 'compartment' or category)

    Must be implemented (properties):
     - name - string
     - link - string
     - synonyms - iterable
    """
    @property
    def unit(self):
        if hasattr(self.reference_entity, 'unit'):
            return self.reference_entity.unit
        return ''

    @property
    def name(self):
        return NotImplemented

    @property
    def synonyms(self):
        return NotImplemented

    def _add_synonym(self, synonym):
        raise NotImplementedError

    @property
    def context(self):
        """
        A flow's context is any hierarchical tuple of strings (generic, intermediate, ..., specific)
        0-length default for flows with no specific context
        :return:
        """
        return NotImplemented

    @property
    def locale(self):
        """
        A flow can have a locale
        :return:
        """
        return NotImplemented

    def get_context(self):
        raise NotImplementedError

    def match(self, other):
        """
        match if any synonyms match
        :param other:
        :return:
        """
        raise NotImplementedError

    def lookup_cf(self, quantity, context, locale, refresh=False, **kwargs):
        """
        Look for cached characterizations, and retrieve one from the provided quantity if none is found.
        :param quantity: a QuantityRef
        :param context:
        :param locale:
        :param refresh: [False] if True, discard cached CF
        :param kwargs: passed to quantity relation
        :return:
        """
        raise NotImplementedError

    def pop_char(self, quantity, context, locale):
        raise NotImplementedError
