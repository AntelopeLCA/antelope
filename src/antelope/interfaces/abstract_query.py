"""
Root-level catalog interface
"""


#: The interfaces that exist in the Antelope framework
ANTELOPE_INTERFACES = ('basic', 'exchange', 'index', 'quantity', 'background', 'configure', 'foreground')


class PrivateArchive(Exception):
    """
    :meta exclude:
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
        The workhorse of the abstract query.  The implementation uses this to perform whatever query is requested.

        :param itype: type of query being performed (which interface is being invoked). Must be in ANTELOPE_INTERFACES
        :param attrname: query name
        :param exc: "fallback exception": ignore it if an implementation raises it; then raise it if no implementation
         succeeds
        :param args: to pass to the query
        :param kwargs: to pass to the query or subclass
        :return:
        """
        raise NotImplementedError

    def _grounded_query(self, origin):
        """
        Pseudo-abstract method used to construct entity references from a query that is anchored to a metaresource.
        must be overriden by user-facing subclasses if resources beyond self are required to answer
        the queries (e.g. a catalog).
        Can be overridden.

        :param origin:
        :return:
        """
        return self
