"""
The Background interface is a hybrid interface that can be produced from the combination of  a complete index and
exchange interface for a self-contained database (terminate() and inventory() are required, and the resulting matrix
must be invertible)

The default implementation is a dumb proxy, for use when archives provide LCI information over an inventory interface.
 Here the proxy just 'masquerades' the contents to answer background instead of inventory queries.  Though it does not
 thrown an error, it is a conceptual violation for one data source to supply both inventory and background interfaces
 using the proxy implementation.

The LcBackground class, added with the antelope_lcbackground plugin, provides an engine that partially orders the
datasets in an ecoinvent-style unit process database and stores the results in a static set of scipy sparse arrays, in
a manner consistent with the JIE disclosure paper (augmented with the full LCIDB).

The (as yet hypothetical) antelope_brightway2 plugin can provide index, inventory, and background data for a bw2
database.

More plugins are yet imagined.
"""

from .abstract_query import AbstractQuery
from ..refs import ExchangeRef


class BackgroundRequired(Exception):
    pass


_interface = 'background'

BACKGROUND_VALUES_REQUIRED = {'dependencies', 'emissions', 'cutoffs', 'lci', 'sys_lci', 'foreground', 'ad', 'bf'}


class BackgroundInterface(AbstractQuery):
    """
    BackgroundInterface core methods
    """
    def check_bg(self, reset=False, **kwargs):
        """
        Trivial method to force creation of background / check if it exists.  Also provides a way to reset / pass
        keyword arguments to the background engine.
        :param reset: [False] whether to re-create the matrix
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'check_bg', BackgroundRequired,
                                   reset=reset, **kwargs)

    def setup_bm(self, query):
        """
        Utility hook for configuring a background from an index + exchange query
        :param query:
        :return:
        """
        return False

    def exterior_flows(self, direction=None, search=None, **kwargs):
        """
        Yield a list of ExteriorFlows or cutoff flows, which serialize to flow, direction
        Ultimately this will be origin, flow ref, direction, context. Context=None are cutoffs.

        :param direction:
        :param search:
        :return: ExteriorFlows
        """
        return self._perform_query(_interface, 'exterior_flows', BackgroundRequired,
                                   search=search, **kwargs)

    def consumers(self, process, ref_flow=None, **kwargs):
        """
        Generate Reference Exchanges which consume the query process, i.e. columns in Af / Ad having nonzero entries
        in the row corresponding to the query process.
        :param process:
        :param ref_flow:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'consumers', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def emitters(self, flow, direction=None, context=None, **kwargs):
        """
        Generate Reference exchanges which include the designated exterior flow in their inventories, optionally
        filtering by context
        :param flow:
        :param direction:
        :param context:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'emitters', BackgroundRequired,
                                   flow, direction=direction, context=context, **kwargs)

    def dependencies(self, process, ref_flow=None, **kwargs):
        """
        Interior exchanges for a given node

        :param process:
        :param ref_flow:
        :return:
        """
        return self._perform_query(_interface, 'dependencies', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def emissions(self, process, ref_flow=None, **kwargs):
        """
        Exterior exchanges for a given node that are terminated to elementary context

        :param process:
        :param ref_flow:
        :return:
        """
        return self._perform_query(_interface, 'emissions', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def cutoffs(self, process, ref_flow=None, **kwargs):
        """
        Exterior Intermediate Flows- exchanges with null termination or terminated to non-elementary context

        :param process:
        :param ref_flow:
        :return:
        """
        return self._perform_query(_interface, 'cutoffs', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def lci(self, process, ref_flow=None, **kwargs):
        """
        returns aggregated LCI as a list of exchanges (privacy permitting)
        :param process:
        :param ref_flow:
        :return:
        """
        return self._perform_query(_interface, 'lci', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def _make_sys_lci_exchange(self, x):
        return ExchangeRef(self.make_ref(x.process), self.make_ref(x.flow), x.direction, value=x.value,
                           termination=x.termination, comment='SYS LCI', is_reference=False)

    def sys_lci(self, demand, **kwargs):
        """
        Perform LCI on an arbitrary demand vector, which should be supplied as an iterable of UnallocatedExchange
        models whose terminations can be found in the background database.

        Terminations to foreground and background are allowed. Exterior flows are just passed through but contexts
        may be transformed in the process and thus should be excluded.  See bg_lcia() for recommended implementation.

        sys_lci(process_ref.dependencies()) + process_ref.emissions() should equal process_ref.lci()
        although the sum of iterables would not be straightforward to compute... the correct approach is:
        sys_lci(itertools.chain(process_ref.dependencies(), process_ref.emissions(), process_ref.cutoffs()))

        sys_lci(process_ref.inventory()) should equal process_ref.lci() directly, up to a normalization, assuming
        the individual exchanges are properly terminated.
        :param demand: an iterable of exchanges with terminations that can be found in the background database.
        :param kwargs:
        :return:
        """
        for i in self._perform_query(_interface, 'sys_lci', BackgroundRequired, demand, **kwargs):
            yield self._make_sys_lci_exchange(i)

    def sys_lcia(self, process, query_qty, observed=None, ref_flow=None, **kwargs):
        """

        :param process:
        :param query_qty:
        :param observed:
        :param ref_flow:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'sys_lcia', BackgroundRequired,
                                   process, query_qty, observed=observed, ref_flow=ref_flow, **kwargs)

    '''
    Methods requiring a partial ordering (implemented by antelope_background)
    '''
    def foreground_flows(self, search=None, **kwargs):
        """
        Yield a list of Reference Exchanges that make up the foreground (e.g. rows/columns of Af).
        Serialization should include origin, process external ref, flow external ref, direction.

        :param search:
        :return: ProductFlows (should be ref-ized somehow)
        """
        return self._perform_query(_interface, 'foreground_flows', BackgroundRequired,
                                   search=search, **kwargs)

    def background_flows(self, search=None, **kwargs):
        """
        Yield a list of Reference Exchanges that make up the background (e.g. rows/columns of Ad)
        Serialization should include origin, process external ref, flow external ref, direction.

        :param search:
        :return: ProductFlows (should be ref-ized somehow)
        """
        return self._perform_query(_interface, 'background_flows', BackgroundRequired,
                                   search=search, **kwargs)

    def foreground(self, process, ref_flow=None, **kwargs):
        """
        Returns an ordered list of exchanges for the foreground matrix Af for the given process and reference flow-
        the first being the named process + reference flow, and every successive one having a named termination, so
        that the exchanges could be linked into a fragment tree.

        This technically should require exchange interface as well as values
        :param process:
        :param ref_flow:
        :return:
        """
        return self._perform_query(_interface, 'foreground', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def is_in_scc(self, process, ref_flow=None, **kwargs):
        """
        Returns True if the identified productflow is part of a strongly connected component (including the background)
        :param process:
        :param ref_flow:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'is_in_scc', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def is_in_background(self, process, ref_flow=None, **kwargs):
        """

        :param process:
        :param ref_flow:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'is_in_background', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def ad(self, process, ref_flow=None, **kwargs):
        """
        returns foreground-aggregated dependencies on the background as a list of exchanges
        :param process:
        :param ref_flow:
        :return:
        """
        return self._perform_query(_interface, 'ad', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def bf(self, process, ref_flow=None, **kwargs):
        """
        returns foreground-aggregated emissions as a list of exchanges
        :param process:
        :param ref_flow:
        :return:
        """
        return self._perform_query(_interface, 'bf', BackgroundRequired,
                                   process, ref_flow=ref_flow, **kwargs)

    def deep_lcia(self, process, quantity_ref, ref_flow=None, **kwargs):
        """
        Performs LCIA at the A-matrix level
        :param process:
        :param quantity_ref: quantity's factors must be accessible to the background's index query
        :param ref_flow:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'deep_lcia', BackgroundRequired,
                                   process, quantity_ref, ref_flow=ref_flow, **kwargs)
