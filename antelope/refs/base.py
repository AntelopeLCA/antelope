"""
Motivation:
The main idea is that one can manipulate entities by reference without possessing the actual source data.
Each entity is identified as a string 'origin/external_ref', where an origin is a hierarchical specification
with semantic significance (e.g. ecoinvent.3.4.cutoff) and the 'external_ref' is the unique id of the entity
in that source.

A catalog can resolve a catalog reference by locating the appropriate source and retrieving the entity, or asking
other questions about it.  To that end, the origins and their mapping to source data must be curated.

Design principles:
1. References should be lightweight and should not require importing anything. Of course, references are useless
without access to a query object that can implement the various methods.

2. Un-grounded references are useless except for collecting metadata about entities.

3. Grounded references should behave equivalently to the entities themselves. (except the remote catalogs can act
as gatekeepers to decide what information can be disclosed)

The inheritance pattern is:

BaseRef
|    |
|    EntityRef (grounded by a catalog query)
|      | \ \
|    ProcessRef, FlowRef, QuantityRef [...]
|
CatalogRef (un-grounded)

The CatalogRef can instantiate a grounded reference if supplied with a query object that implements the interface.

"""
from synonym_dict import LowerDict

from ..flows import BaseEntity
from ..interfaces.abstract_query import NoAccessToEntity


class NoCatalog(Exception):
    pass


class InvalidQuery(Exception):
    pass


class EntityRefMergeError(Exception):
    pass


class BaseRef(BaseEntity):
    """
    A base class for defining entity references.  The base class can also store information, such as properties
    """
    _etype = None

    def __init__(self, origin, external_ref, uuid=None, **kwargs):
        """

        :param origin:
        :param external_ref:
        :param kwargs:
        """
        self._origin = origin
        self._ref = external_ref
        self._uuid = uuid

        self._d = LowerDict()
        self._d.update({k: v for k, v in filter(lambda x: x[1] is not None, kwargs.items())})

    @property
    def origin(self):
        return self._origin

    @property
    def external_ref(self):
        return self._ref

    @property
    def uuid(self):
        return self._uuid or self._ref

    @property
    def entity_type(self):
        if self._etype is None:
            return 'unknown'
        return self._etype

    def _localitem(self, item):
        if item in self._d:
            return self._d[item]
        if 'local_%s' % item in self._d:
            return self._d['local_%s' % item]

    def __getitem__(self, item):
        """
        should be overridden
        :param item:
        :return:
        """
        return self._localitem(item)

    def properties(self):
        for k in self._d.keys():
            yield k

    def get(self, item, default=None):
        try:
            return self.__getitem__(item)
        except KeyError:
            return default

    def has_property(self, item):
        return self._localitem(item) is not None

    def __setitem__(self, key, value):
        if not key.lower().startswith('local_'):
            key = 'local_%s' % key
        self._d[key] = value

    @property
    def _name(self):
        """
        This should be the same as .name for entities; whereas str(ref) prepends origin
        :return:
        """
        if self.has_property('Name'):
            addl = self._addl
            name = self['Name'].replace('\n', '|')
            if len(addl) > 0:
                name += ' [%s]' % addl
            return name
        return self.external_ref

    @property
    def _addl(self):
        return ''

    def __eq__(self, other):
        """
        Catalog refs are equal if their external_refs are equal and their origins start with each other
        :param other:
        :return:
        """
        if other is None:
            return False
        try:
            return (#(other.entity_type == 'unknown' or self.entity_type == other.entity_type) and
                    self.external_ref == other.external_ref and
                    (self.origin.startswith(other.origin) or other.origin.startswith(self.origin)))
        except AttributeError:
            return False

    def __str__(self):
        return '[%s] %s' % (self.origin, self._name)

    def __hash__(self):
        return hash(self.link)

    def _show_hook(self):
        """
        Place for subclass-dependent specialization of show()
        :return:
        """
        print(' ** UNRESOLVED **')

    @property
    def resolved(self):
        return False

    def merge(self, other):
        if self.entity_type != other.entity_type:
            raise EntityRefMergeError('Type mismatch %s vs %s' % (self.entity_type, other.entity_type))
        if self.link != other.link:
            if self.external_ref == other.external_ref:
                pass  # we're going to consider origin mismatches allowable for entity refs
                '''
                if not (self.origin.startswith(other.origin) or other.origin.startswith(self.origin)):
                    raise EntityRefMergeError('Origin mismatch %s vs %s' % (self.origin, other.origin))
                '''
            else:
                raise EntityRefMergeError('external_ref mismatch: %s vs %s' % (self.external_ref, other.external_ref))
        # otherwise fine-- left argument is dominant
        self._d.update(other._d)

    def show(self):
        """
        should be finessed in subclasses
        :return:
        """
        print('%s catalog reference (%s)' % (self.__class__.__name__, self.external_ref))
        print('origin: %s' % self.origin)
        self._show_hook()
        if len(self._d) > 0:
            _notprint = True  # only print '==Local Fields==' if there are any
            ml = len(max(self._d.keys(), key=len))
            named = {'comment', 'name'}
            for k, v in self._d.items():
                if k.lower() in named or 'local' + k.lower() in named:
                    continue
                named.add(k.lower())
                if _notprint:
                    print('==Local Fields==')
                    _notprint = False
                print('%*s: %s' % (ml, k, v))

    def serialize(self, **kwargs):
        """

        :param kwargs: 'domesticate' has no effect- refs can't be domesticated
        :return:
        """
        j = {
            'origin': self.origin,
            'externalId': self.external_ref
        }
        if self._etype is not None:
            j['entityType'] = self._etype
        # j.update(self._d)  ## don't want this
        if 'Name' in self._d:
            j['Name'] = self._d['Name']
        return j


class EntityRef(BaseRef):
    """
    An EntityRef is a CatalogRef that has been provided a valid catalog query.  the EntityRef is still semi-abstract
    since there is no meaningful reference to an entity that is not typed.
    """
    _ref_field = 'referenceEntity'

    @property
    def reference_field(self):
        return self._ref_field

    def make_ref(self, *args):
        return self

    def __init__(self, external_ref, query, reference_entity=None, masquerade=None, **kwargs):
        """

        :param external_ref:
        :param query:
        :param kwargs: masquerade: self-described origin is different from the query origin
        """
        origin = masquerade or query.origin
        super(EntityRef, self).__init__(origin, external_ref, **kwargs)
        if not query.validate():
            raise InvalidQuery('Query failed validation')
        self._reference_entity = reference_entity

        self._query = query

    @property
    def uuid(self):
        if self._uuid is None:
            self._uuid = self._query.get_uuid(self.external_ref)
        return self._uuid

    def query_synonyms(self, term):
        """
        Provide access to root archive's synonyms
        :param term:
        :return:
        """
        return self._query.synonyms(term)

    def get_reference(self):
        return self.reference_entity

    def _check_query(self, message=''):
        if self._query is None:
            print(self)
            raise NoCatalog(message)

    @property
    def reference_entity(self):
        if self._reference_entity is None:
            self._reference_entity = self._query.get_reference(self.external_ref)
        return self._reference_entity

    @property
    def resolved(self):
        return True

    def signature_fields(self):
        yield self._ref_field

    def _show_ref(self):
        print('reference: %s' % self.reference_entity)

    def _show_hook(self):
        if self._uuid:
            print('UUID: %s' % self.uuid)
        for i in ('Name', 'Comment'):
            try:
                print('%7s: %s' % (i, self.get_item(i)))
            except NoAccessToEntity:
                print('%7s: NoAccessToEntity' % i)
            except KeyError:
                pass

    def validate(self):
        """
        This is required by certain implementations to be added to archives (born legacy...)
        There should be no way to get through the instantiation without a valid query, so this should probably just
        return True (or be made more useful)
        :return:
        """
        if self._query is None:
            return False
        return True

    def properties(self):
        try:
            for k in self._query.properties(self.external_ref):
                yield k
        except NoAccessToEntity:
            for k in self._d.keys():
                yield k

    def get_item(self, item, force_query=True):
        """

        This keeps generating recursion errors. Let's think it through.
         - first checks locally. If known, great.
         - if not, need to check remotely by running the query.
         - the query retrieves the entity and asks has_property
           -- which causes recursion error if the query actually gets the entity_ref
           --- attempted solution with NoAccessToEntity exception in BasicImplementation
         - fine. So when do we raise a key error?
        :param item:
        :param force_query:
        :return:
        """
        # check local first.  return Localitem if present.
        loc = self._localitem(item)
        if loc is not None:
            return loc
        if force_query:
            self._check_query('getitem %s' % item)
            val = self._query.get_item(self, item)
            if val is not None and val != '':
                self._d[item] = val
                return val
        raise KeyError(item)

    def __getitem__(self, item):
        if item == self._ref_field:
            return self._reference_entity
        val = self.get_item(item)
        if val is None:
            raise KeyError(item)
        return val

    def has_property(self, item):
        """
        let's deal with the recursion issue head-on
        :param item:
        :return:
        """
        try:
            self.get_item(item)
        except (KeyError, NoAccessToEntity):
            return False
        return True

    def serialize(self, **kwargs):
        j = super(EntityRef, self).serialize(**kwargs)
        if self._uuid:
            j['uuid'] = self.uuid
        return j
