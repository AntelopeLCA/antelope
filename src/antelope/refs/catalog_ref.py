"""
The main import.
"""


from .base import BaseRef, InvalidQuery, NoCatalog
from .flow_ref import FlowRef
# from .fragment_ref import FragmentRef
from .process_ref import ProcessRef
from .quantity_ref import QuantityRef


class UnknownOrigin(Exception):
    pass


class CatalogRef(BaseRef):
    """
    user-facing entity ref generator

    CatalogRef.from_json(j, catalog=None)

    A catalog ref is defined by an entity's origin and external reference, which are all that is necessary to
    identify and/or recreate the entity.  A ref can be "grounded" by being provided with a query that can
    resolve the reference and access the entity.

    :param origin: semantic reference to data source (catalog must resolve to a physical data source)
    :param ref: external reference of entity in semantic data source
    :param _query: if a query is already on hand, set it and skip the catalog lookup
    :param catalog: semantic resolver. Must provide the interfaces that can be used to answer queries
    """

    @classmethod
    def from_json(cls, j, catalog=None):
        external_ref = j.pop('externalId')
        if 'entityType' in j:
            etype = j.pop('entityType', None)
            if etype == 'unknown':
                etype = None
        else:
            etype = None
        if 'origin' in j:
            origin = j.pop('origin')
        elif 'source' in j:
            origin = j['source']
        else:
            origin = 'foreground'  # generic fallback origin
        if catalog is not None:
            try:
                query = catalog.query(origin)
                ref = cls.from_query(external_ref, query, etype, **j)
            except UnknownOrigin:
                ref = cls(origin, external_ref, entity_type=etype, **j)
        else:
            ref = cls(origin, external_ref, entity_type=etype, **j)
        return ref

    @classmethod
    def from_query(cls, external_ref, query, etype, **kwargs):
        if query is not None:
            if etype == 'process':
                return ProcessRef(external_ref, query, **kwargs)
            elif etype == 'flow':
                return FlowRef(external_ref, query, **kwargs)
            elif etype == 'quantity':
                return QuantityRef(external_ref, query, **kwargs)
        # elif etype == 'fragment':
        #     return FragmentRef(external_ref, query, reference_entity, **kwargs)
        return cls(query.origin, external_ref, entity_type=etype, query=query, **kwargs)

    def __init__(self, origin, external_ref, entity_type=None, reference_entity=None, **kwargs):
        """
        A CatalogRef that is created from scratch will not be active
        :param origin:
        :param external_ref:
        :param entity_type:
        :param kwargs:
        """
        super(CatalogRef, self).__init__(origin, external_ref, **kwargs)

        if 'Name' not in self._d:
            self['Name'] = self.link

        self._asgn_etype = entity_type
        self._reference_entity = reference_entity

    @property
    def reference_entity(self):
        return self._reference_entity

    @property
    def name(self):
        return self._name

    def quantity_terms(self):
        """
        Code repetition! for subclass purity
        :return:
        """
        if not self.is_lcia_method:
            yield self.name
            yield str(self)  # this is the same as above for entities, but includes origin for refs
            yield self.external_ref  # do we definitely want this?  will squash versions together
        if self.uuid is not None:
            yield self.uuid
        if self.origin is not None:
            yield self.link

    def validate(self):
        """
        Always returns true in order to add to an archive. this should probably be fixed.
        :return:
        """
        return False

    @property
    def entity_type(self):
        if self._asgn_etype is not None:
            return self._asgn_etype
        return super(CatalogRef, self).entity_type

    @property
    def unit(self):
        if self.entity_type == 'quantity':
            if self.has_property('Indicator'):
                return self['Indicator']
            return self.reference_entity
        elif self.entity_type == 'flow':
            if self.reference_entity is not None:
                return self.reference_entity.unit
            return None
        raise AttributeError('This entity does not have a unit')

    @property
    def is_lcia_method(self):
        if self.entity_type == 'quantity':
            if self.has_property('Indicator'):
                return True
        return False

    def has_lcia_engine(self):
        return False

    def cf(self, *args, **kwargs):
        return 0.0

    def resolve(self):
        if self.has_property('query'):
            try:
                return self['query'].get(self.external_ref)
            except InvalidQuery:
                return self
        else:
            raise NoCatalog(self.origin)
