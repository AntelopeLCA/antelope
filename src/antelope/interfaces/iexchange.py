from .abstract_query import AbstractQuery
# from .iindex import check_direction


class ExchangeRequired(Exception):
    pass


_interface = 'exchange'

EXCHANGE_VALUES_REQUIRED = {'ev', 'exchange_values', 'inventory', 'exchange_relation'}


class ExchangeInterface(AbstractQuery):
    """
    InventoryInterface core methods: individual processes, quantitative data.

    Need to do some thinking here-- the list of methods is very short. In particular there is no way to do any of
    the following:
     * retrieve reference exchanges
     * retrieve cutoff exchanges or only terminated exchanges
     * retrieve only intermediate or only elementary exchanges [[ pending context refactor :(:( ]]
       = this is frankly not possible to do, even after the context refactor, because there is no bulletproof way to
         determine whether a termination is a context or a process or some non-elementary compartment, until you
         introduce the Lcia Engine with its reference set of contexts, UNLESS you include the reference elementary set
         in ALL context managers.  Which is feasible- since it's a short list- but still, not done as yet.
    There's also no access to information from the original source that is not part of the data model, e.g. uncertainty
    information, arbitrary XML queries, etc.
    """
    def exchanges(self, process, **kwargs):
        """
        Retrieve process's full exchange list, without values
        :param process:
        :return: list of exchanges without values
        """
        return self._perform_query(_interface, 'exchanges',
                                   ExchangeRequired, process, **kwargs)

    def ev(self, process, flow, direction=None, termination=None, ref_flow=None, **kwargs):
        """
        Return a float.  Symmetric to quantity.cf
        :param process:
        :param flow:
        :param direction: [None] if none, if flows exist with both directions, raise an error
        :param termination: [None] if none, return sum of flows across all terminations
        :param ref_flow: [None] if none, return unallocated value. Otherwise, return value allocated to a unit of the
         specified reference
        :return: a float
        """
        return self._perform_query(_interface, 'ev', ExchangeRequired,
                                   process, flow, direction=direction, termination=termination, ref_flow=ref_flow,
                                   **kwargs)

    def exchange_values(self, process, flow, direction=None, termination=None, reference=None, **kwargs):
        """
        Leftover from earlier implementation; deprecated.
        2022-12-27: is this really deprecated? it's used in computing reference_value and I don't see any other way...
        perhaps we should add reference_value() to the API but for now let's keep this around

        Return a list of exchanges with values matching the specification
        :param process:
        :param flow:
        :param direction: [None] if none,
        :param termination: [None] if none, return all terminations
        :param reference: [None] if True, only find reference exchanges. If false- maybe omit reference exchanges?
        :return: list of exchanges with values matching the specification
        """
        return self._perform_query(_interface, 'exchange_values',
                                   ExchangeRequired,
                                   process, flow, direction=direction, termination=termination, reference=reference,
                                   **kwargs)

    def inventory(self, process, ref_flow=None, scenario=None, **kwargs):
        """
        Return a list of exchanges with values. If no reference is supplied, return all unallocated exchanges, including
        reference exchanges.

        If a reference flow is supplied, expected behavior depends on a number of factors.
         - If the supplied reference flow is part of the process's reference entity, the inventory should return all
         non-reference exchanges, appropriately allocated to the specified flow, and normalized to a unit of the
         specified flow.
         - If the supplied reference flow is not part of the reference entity, NO allocation should be performed.
         Instead, the inventory should return ALL exchanges except for the specified flow, un-allocated, normalized to
         a unit of the specified flow.  This query is only valid if the specified flow is a cut-off (i.e. un-terminated)
         exchange (i.e. it could be treated as a "silent reference" or effective co-product)
         - If the supplied reference flow is a non-reference, non-cutoff flow (i.e. it is a terminated exchange), then
         the appropriate behavior is undefined. The default implementation raises an ExchangeError.

        Note: if this is called on a fragment, the signature is the same but the 'ref_flow' argument is ignored and
        the alternative 'scenario' kwarg is accepted
        :param process:
        :param ref_flow: used only for processes
        :param scenario: used only for fragments (antelope_foreground)
        :return: a list of unallocated or allocated exchange refs
        """
        return self._perform_query(_interface, 'inventory', ExchangeRequired,
                                   process, ref_flow=ref_flow, scenario=scenario, **kwargs)

    def exchange_relation(self, process, ref_flow, exch_flow, direction, termination=None, **kwargs):
        """
        should return some sort of exchange relation result, analogous to quantity.quantity_relation

        :param process:
        :param ref_flow:
        :param exch_flow:
        :param direction:
        :param termination:
        :return:
        """
        return self._perform_query(_interface, 'exchange_relation', ExchangeRequired,
                                   process, ref_flow, exch_flow, direction, termination=termination, **kwargs)
