"""
Antelope Interface Definitions

The abstract classes in this sub-package define what information is made available via a stateless query to an Antelope
resource of some kind.  The interfaces must be instantiated in order to be used.  In the core package
"""

from .interfaces import ANTELOPE_INTERFACES

from .interfaces.ibasic import BasicInterface, EntityNotFound, NoAccessToEntity, ItemNotFound
from .interfaces.iconfigure import ConfigureInterface
from .interfaces.iexchange import ExchangeInterface, ExchangeRequired
from .interfaces.iindex import IndexInterface, IndexRequired, directions, comp_dir, num_dir, check_direction, valid_sense, comp_sense
from .interfaces.ibackground import BackgroundInterface, BackgroundRequired
from .interfaces.iquantity import QuantityInterface, QuantityRequired, NoFactorsFound, ConversionReferenceMismatch, FlowableMismatch
from .interfaces.iforeground import ForegroundInterface

from .flows import BaseEntity, NullEntity, FlowInterface, Flow

from .refs.process_ref import MultipleReferences, NoReference
from .refs.catalog_ref import CatalogRef, QuantityRef, UnknownOrigin
from .refs.quantity_ref import convert, ConversionError, RefQuantityRequired

from .refs.base import NoCatalog, EntityRefMergeError, InvalidQuery, PropertyExists
from .refs.exchange_ref import ExchangeRef, RxRef, EXCHANGE_TYPES


import re

from os.path import splitext


class ValuesAccessRequired(Exception):
    """
    The requested route requires a grant that has values=True
    """
    pass


class UpdateAccessRequired(Exception):
    """
    The requested route requires a grant that has updates=True
    """
    pass


'''
Query classes
'''


class BasicQuery(BasicInterface, IndexInterface, ExchangeInterface, QuantityInterface):
    """
    A basic query depends on an archive-- which has the following API:

     - archive.make_interface(interface): returns an implementation of the designated interface
     - archive.ref: returns the archive's semantic reference
     - archive.source: returns the physical source (or URI) for the archive's content

    """
    def __init__(self, archive, debug=False):
        self._archive = archive
        self._dbg = debug

    def _perform_query(self, itype, attrname, exc, *args, **kwargs):
        if itype is None:
            itype = 'basic'
        iface = self._archive.make_interface(itype)
        result = getattr(iface, attrname)(*args, **kwargs)
        if result is not None:  # successful query must return something
            return result
        raise exc(itype, attrname, *args)

    @property
    def origin(self):
        return self._archive.ref

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

    def __str__(self):
        return '%s(%s:%s:%s)' % (self.__class__.__name__, self.origin,
                                 self._archive.__class__.__name__,
                                 self._archive.source)

    def __repr__(self):
        return self.__str__()

    '''
    I think that's all I need to do!
    '''


class LcQuery(BasicQuery, BackgroundInterface, ConfigureInterface):
    pass


class FgQuery(LcQuery, ForegroundInterface):
    pass


'''
Utilities

'''


def local_ref(source, prefix=None):
    """
    Create a semantic ref for a local filename.  Just uses basename.  what kind of monster would access multiple
    different files with the same basename without specifying ref?

    alternative is splitext(source)[0].translate(maketrans('/\\','..'), ':~') but ugghh...

    Okay, FINE.  I'll use the full path.  WITH leading '.' removed.

    Anyway, to be clear, local semantic references are not supposed to be distributed.
    :param source:
    :param prefix: [None] default 'local'
    :return:
    """
    if prefix is None:
        prefix = 'local'
    xf = source.translate(str.maketrans('/\\', '..', ':~'))
    while splitext(xf)[1] in {'.gz', '.json', '.zip', '.txt', '.spold', '.7z'}:
        xf = splitext(xf)[0]
    while xf[0] == '.':
        xf = xf[1:]
    while xf[-1] == '.':
        xf = xf[:-1]
    return '.'.join([prefix, xf])


def q_node_activity(fg):
    """
    A reference quantity for dimensionless node activity. This should be part of Qdb reference quantities (but isn't)
    :param fg:
    :return:
    """
    try:
        return fg.get_canonical('node activity')
    except EntityNotFound:
        fg.new_quantity('Node Activity', ref_unit='activity', external_ref='node activity', comment='MFA metric')
        return fg.get_canonical('node activity')


def enum(iterable, filt=None, invert=True):
    """
    Enumerate an iterable for interactive use. return it as a list. Optional negative filter supplied as regex.

    :param iterable:
    :param filt: regex to filter out entries from return and enumeration.
    :param invert: [True] sense of filter. note default is negative i.e. to screen *out* matches
     (the thinking is that the input is already positive-filtered)
    :return:
    """
    ret = []
    if filt is not None:
        if invert:
            _iter = filter(lambda x: not bool(re.search(filt, str(x), flags=re.I)), iterable)
        else:
            _iter = filter(lambda x: bool(re.search(filt, str(x), flags=re.I)), iterable)
    else:
        _iter = iterable
    for k, v in enumerate(_iter):
        print(' [%02d] %s' % (k, v))
        ret.append(v)
    return ret


"""
In most LCA software, a 'flow' is a composite entity that is made up of a 'flowable' (substance, product, 
intervention, or service) and a 'context', which is synonymous with an environmental compartment.

The US EPA review of elementary flows recommended managing the names of flowables and contexts separately, and that
is the approach that is done here.  

The exchange model consists of : parent | flow(able), direction | [exch value] | [terminal node]

If the terminal node is a context, the exchange is elementary. if it's a process, then intermediate. 
If none, then cutoff.

The new Flat Background already implements context-as-termination, but the main code has had to transition and we are 
still technically debugging the CalRecycle project. So we introduce this flag CONTEXT_STATUS_ to express to client code 
which one to do. It should take either of the two values: 'compat' means "old style" (flows have Compartments) and 
'new' means use the new data model (exchange terminations are contexts) 
"""
CONTEXT_STATUS_ = 'new'  # 'compat': context = flow['Compartment']; 'new': context = exch.termination


# Exterior exchanges- with contexts outside the db.  Direction is given with respect to the Interior (e.g. "Output" "to air")
# LciaResults should negate values when an exchange direction and a context are not complementary (i.e. "Input" "to air")
# ExteriorFlow = namedtuple('ExteriorFlow', ('origin', 'flow', 'direction', 'termination'))

# EntitySpec = namedtuple('EntitySpec', ('link', 'ref', 'name', 'group'))

# packages that contain 'providers'
antelope_herd = [
    'antelope_background',
    'antelope_foreground'
]
