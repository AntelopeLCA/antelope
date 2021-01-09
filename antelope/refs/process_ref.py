from .base import EntityRef
from .exchange_ref import ExchangeRef


class MultipleReferences(Exception):
    pass


class NoReference(Exception):
    pass


class ProcessRef(EntityRef):
    """
    Processes can lookup:
    """
    _etype = 'process'
    _ref_field = 'referenceExchange'

    @property
    def _addl(self):
        return self.__getitem__('SpatialScope')

    def __init__(self, external_ref, query, **kwargs):
        self._default_rx = None
        self._lci = dict()
        super(ProcessRef, self).__init__(external_ref, query, **kwargs)

    @property
    def reference_entity(self):
        if self._reference_entity is None:
            self._reference_entity = self._query.get_reference(self.external_ref)
            if len(self._reference_entity) == 1:
                self._default_rx = self._reference_entity[0].flow.external_ref
        return self._reference_entity

    def _show_ref(self):
        for i in self.references():
            print('reference: %s' % i)

    @property
    def name(self):
        return self._name

    @property
    def default_rx(self):
        """
        The 'primary' reference exchange of a process CatalogRef.  This is an external_ref for a flow.
        This can be set by a user for convenience for multi-reference processes.

        (- which is req. unique among references)
        :return:
        """
        return self._default_rx

    @default_rx.setter
    def default_rx(self, value):
        if not isinstance(value, str) and not isinstance(value, int):
            if hasattr(value, 'external_ref'):
                value = value.external_ref
            elif hasattr(value, 'entity_type'):
                if value.entity_type == 'exchange':
                    value = value.flow.external_ref
        if value in [rx.flow.external_ref for rx in self.references()]:
            self._default_rx = value
        else:
            print('Not a valid reference exchange specification')

    def reference(self, flow=None):
        """
        This used to fallback to regular exchanges; no longer.
        :param flow:
        :return:
        """
        if len(self.reference_entity) == 0:
            raise NoReference
        if flow is None:
            if len(self.reference_entity) > 1:
                raise MultipleReferences('%s: You must specify a reference flow' % self.link)
            return self.reference_entity[0]
        if hasattr(flow, 'entity_type'):
            if flow.entity_type == 'exchange':
                flow = flow.flow
        try:
            return next(x for x in self.reference_entity if x.flow == flow or x.flow.external_ref == flow)
        except StopIteration:
            try:
                return next(x for x in self.reference_entity if x.flow.match(flow))
            except StopIteration:
                print('%s: references:' % self.link)
                self._show_ref()
                raise KeyError(flow)

    def references(self):
        for x in self.reference_entity:
            yield x

    '''
    def is_allocated(self, rx):
        """
        For process refs, assume
        :param rx:
        :return:
        """
        for _rx in self.reference_entity:
            if _rx.key == rx.key:
                return _rx.is_alloc
        return False
    '''

    def _use_ref_exch(self, ref_flow):
        """
        returns a string which is the external_ref of a flow; default_rx if none was specified and the process has one.
        :param ref_flow:
        :return:
        """
        if ref_flow is None:
            if self._default_rx is not None:
                ref_flow = self._default_rx
        elif hasattr(ref_flow, 'entity_type'):
            if ref_flow.entity_type == 'exchange':
                return ref_flow.flow.external_ref
            elif ref_flow.entity_type == 'flow':
                return ref_flow.external_ref
            raise TypeError('Invalid reference exchange: %s' % ref_flow)
        return ref_flow

    '''
    Inventory queries
    '''
    def exchanges(self, **kwargs):
        for x in self._query.exchanges(self.external_ref, **kwargs):
            yield ExchangeRef(self, self._query.make_ref(x.flow), x.direction, value=None, termination=x.termination,
                              comment=x.comment)

    def exchange_values(self, flow, direction=None, termination=None, reference=None, **kwargs):
        """
        This should get replaced by ev()
        :param flow:
        :param direction:
        :param termination:
        :param reference:
        :param kwargs:
        :return:
        """
        if hasattr(flow, 'entity_type'):
            if flow.entity_type == 'exchange':
                flow = flow.flow.external_ref
            elif flow.entity_type == 'flow':
                flow = flow.external_ref
        for x in  self._query.exchange_values(self.external_ref, flow, direction,
                                              termination=termination, reference=reference, **kwargs):
            yield ExchangeRef(self, self._query.make_ref(x.flow), x.direction, value=x.value, termination=x.termination,
                              comment=x.comment)

    def inventory(self, ref_flow=None, **kwargs):
        # ref_flow = self._use_ref_exch(ref_flow)  # ref_flow=None returns unallocated inventory
        for x in sorted(self._query.inventory(self.external_ref, ref_flow=ref_flow, **kwargs),
                        key=lambda t: (not t.is_reference, t.type == 'elementary', t.type == 'context', t.type == 'cutoff', t.direction)):
            yield ExchangeRef(self, self._query.make_ref(x.flow), x.direction, value=x.value, termination=x.termination,
                              comment=x.comment, is_reference=x.is_reference)

    def exchange_relation(self, ref_flow, exch_flow, direction, termination=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        if hasattr(exch_flow, 'external_ref'):
            exch_flow = exch_flow.external_ref
        return self._query.exchange_relation(self.external_ref, ref_flow,
                                             exch_flow, direction,
                                             termination=termination, **kwargs)

    def fg_lcia(self, lcia_qty, ref_flow=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.lcia(self.external_ref, ref_flow, lcia_qty, **kwargs)

    '''
    support process
    '''
    def reference_value(self, flow=None):
        if flow is None:
            flow = self.reference().flow
        return sum(x.value for x in self.exchange_values(flow, reference=True))

    def get_exchange(self, key):
        try:
            return next(x for x in self.reference_entity if x.key == key)
        except StopIteration:
            raise KeyError

    @property
    def alloc_qty(self):
        """
        This is hugely kludgely. What should be the expected behavior of a process ref asked to perform allocation?
        :return:
        """
        return None

    '''
    Background queries
    '''
    def foreground(self, ref_flow=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.foreground(self.external_ref, ref_flow=ref_flow, **kwargs)

    def consumers(self, ref_flow=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.consumers(self.external_ref, ref_flow=ref_flow, **kwargs)

    def dependencies(self, ref_flow=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.dependencies(self.external_ref, ref_flow=ref_flow, **kwargs)

    def emissions(self, ref_flow=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.emissions(self.external_ref, ref_flow=ref_flow, **kwargs)

    def cutoffs(self, ref_flow=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.cutoffs(self.external_ref, ref_flow=ref_flow, **kwargs)

    def is_in_background(self, termination=None, ref_flow=None, **kwargs):
        if termination is None:
            termination = self.external_ref
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.is_in_background(termination, ref_flow=ref_flow, **kwargs)

    def ad(self, ref_flow=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.ad(self.external_ref, ref_flow, **kwargs)

    def bf(self, ref_flow=None, **kwargs):
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.bf(self.external_ref, ref_flow, **kwargs)

    def lci(self, ref_flow=None, refresh=False, **kwargs):
        """
        Caches LCI results
        :param ref_flow:
        :param refresh:
        :param kwargs:
        :return:
        """
        ref_flow = self._use_ref_exch(ref_flow)
        if refresh:
            self._lci.pop(ref_flow, None)
        if ref_flow not in self._lci:

            self._lci[ref_flow] = list(self._query.lci(self.external_ref, ref_flow, **kwargs))
        for i in self._lci[ref_flow]:
            yield i

    def unobserved_lci(self, observed, ref_flow=None, **kwargs):
        """
        Performs a sys_lci of the process's unobserved exchanges. derived by excluding observed exchanges from the
        process's inventory and passing the result to sys_lci.  Note that terminations are ignored-- if a process
        has an observed Electricity flow, all the process's electricity exchanges are assumed to be accounted for
        by the observation.  (flow.external_ref, direction) is the filter.

        :param observed: iterable of exchanges or child flows, having a flow (with external_ref) and direction
        :param ref_flow:
        :param kwargs:
        :return:
        """
        excl = set((k.flow.external_ref, k.direction) for k in observed)
        ref_flow = self._use_ref_exch(ref_flow)
        incl = (k for k in self.inventory(ref_flow) if (k.flow.external_ref, k.direction) not in excl)
        return self._query.sys_lci(self, incl, **kwargs)

    def bg_lcia(self, lcia_qty, ref_flow=None, **kwargs):
        """
        :param lcia_qty: should be a quantity ref (or qty), not an external ID
        :param ref_flow:
        :param kwargs:
        :return:
        """
        ref_flow = self._use_ref_exch(ref_flow)
        return self._query.bg_lcia(self.external_ref, lcia_qty, ref_flow=ref_flow, **kwargs)
