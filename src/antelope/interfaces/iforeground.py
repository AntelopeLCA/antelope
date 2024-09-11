from antelope.interfaces.abstract_query import AbstractQuery


class ForegroundRequired(Exception):
    pass


_interface = 'foreground'


class ForegroundInterface(AbstractQuery):
    """
    The bare minimum foreground interface allows a foreground to create new flows and quantities, lookup terminations,
    observe exchanges, and to save anything it creates.
    """
    '''
    minimal
    '''
    def save(self, **kwargs):
        """
        Save the foreground to local storage.  Revert is not supported for now
        :param kwargs: save_unit_scores [False]: whether to save cached LCIA results (for background fragments only)
        :return:
        """
        return self._perform_query(_interface, 'save', ForegroundRequired, **kwargs)

    def find_term(self, term_ref, origin=None, **kwargs):
        """ # DEPRECATED
        Find a termination for the given reference.  Essentially do type and validity checking and return something
        that can be used as a valid termination.
        :param term_ref: either an entity, entity ref, or string
        :param origin: if provided, interpret term_ref as external_ref
        :param kwargs:
        :return: either a context, or a process_ref, or a flow_ref, or a fragment or fragment_ref, or None
        """
        return self._perform_query(_interface, 'find_term', ForegroundRequired,
                                   term_ref, origin=origin, **kwargs)

    '''
    core required functionality
    NOTE: a foreground interface must have access to a qdb to run get_canonical
    '''
    def new_quantity(self, name, ref_unit=None, **kwargs):
        """
        Creates a new quantity entity and adds it to the foreground
        :param name:
        :param ref_unit:
        :param kwargs:
        :return:
        """
        return self.make_ref(self._perform_query(_interface, 'new_quantity', ForegroundRequired,
                                                 name, ref_unit=ref_unit, **kwargs))

    def new_flow(self, name, ref_quantity=None, context=None, **kwargs):
        """
        Creates a new flow entity and adds it to the foreground
        :param name: required flow name
        :param ref_quantity: [None] implementation must handle None / specify a default
        :param context: [None] Required if flow is strictly elementary. Should be a tuple
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'new_flow', ForegroundRequired,
                                   name, ref_quantity=ref_quantity, context=context,
                                   **kwargs)

    def new_fragment(self, flow, direction, **kwargs):
        """
        Create a fragment and add it to the foreground.

        If creating a child flow ('parent' kwarg is non-None), then supply the direction with respect to the parent
        fragment. Otherwise, supply the direction with respect to the newly created fragment.  Example: for a fragment
        for electricity production:

        >>> fg = ForegroundInterface(...)
        >>> elec = fg.new_flow('Electricity supply fragment', 'kWh')
        >>> my_frag = fg.new_fragment(elec, 'Output')  # flow is an output from my_frag
        >>> child = fg.new_fragment(elec, 'Input', parent=my_frag, balance=True)  # flow is an input to my_frag
        >>> child.terminate(elec_production_process)

        :param flow: a flow entity/ref, or an external_ref known to the foreground
        :param direction:
        :param kwargs: uuid=None, parent=None, comment=None, value=None, balance=False; kwargs passed to LcFragment
        :return: the fragment? or a fragment ref? <== should only be used in the event of a non-local foreground
        """
        return self._perform_query(_interface, 'new_fragment', ForegroundRequired,
                                   flow, direction, **kwargs)

    def child_flows(self, fragment, **kwargs):
        """

        :param fragment:
        :param kwargs:
        :return:
        """
        return self.make_ref(self._perform_query(_interface, 'child_flows', ForegroundRequired, fragment, **kwargs))

    def fragments_with_flow(self, flow, direction=None,**kwargs):
        """
        Generates fragments made with the specified flow, optionally filtering by direction, reference status, and
        background status.  For all three filters, the default None is to generate all fragments.
        :param flow:
        :param direction: [None | 'Input' | 'Output']
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'fragments_with_flow', ForegroundRequired,
                                   flow, direction=direction, **kwargs)

    def split_subfragment(self, fragment, replacement=None, **kwargs):
        """
                Given a non-reference fragment, split it off into a new reference fragment, and create a surrogate child
        that terminates to it.

        without replacement:
        Old:   ...parent-->fragment
        New:   ...parent-->surrogate#fragment;   (fragment)

        with replacement:
        Old:   ...parent-->fragment;  (replacement)
        New:   ...parent-->surrogate#replacement;  (fragment);  (replacement)

        :param fragment:
        :param replacement:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'split_subfragment', ForegroundRequired,
                                   fragment, replacement=replacement, **kwargs)

    def anchors(self, fragment, **kwargs):
        """
        List observed anchors for a fragment

        :param fragment:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'anchors', ForegroundRequired, fragment, **kwargs)

    def parameters(self, fragment=None, **kwargs):
        """
        Return a list of observable fragments in the foreground.
        :param fragment: optionally filter to a specific fragment and its child flows
        :param kwargs:
        :return:
        """

    def observe(self, fragment, exchange_value=None, anchor=None, name=None, scenario=None, **kwargs):
        """
        Observe quantitative aspects of a fragment, and assign it a name.

        Two different elements can be observed: its exchange value and its anchor. Either or both can be observed
        with respect to some scenario or scope specification that really needs to be ironed out.  For now a
        'scenario' is just a tidy string, typically: brief, non-whitespace containing, ','-parseable

        If no scenario name is given, the fragment's default observed state is set.  A fragment should be named
        when it is observed.  In a completed model, all observable fragments should "have names" (i.e. be QC'able).

        Exchange value is given with respect to a unit of the parent node's activity level and the fragment's flow
        reference quantity, optionally including a unit of measure.

        Exchange values may only be observed for observable fragments, i.e. non-balancing fragments whose parents are
        processes or foreground nodes (child flows of subfragments have their exchange values determined at traversal,
        as do balancing flows, so not "observable" in the model building sense).

        Scenario names e.g. as natural numbers could be used to store replicate observations.

        Fragments should not be named during scenario observations.  If a scenario is supplied, name is ignored.

        :param fragment:
        :param exchange_value: [this must be the second positional argument for legacy reasons, but can still be None]
        :param anchor: type-agnostic; left to implementation
        :param name:
        :param scenario:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'observe', ForegroundRequired,
                                   fragment, exchange_value=exchange_value, anchor=anchor, name=name,
                                   scenario=scenario, **kwargs)

    def observe_unit_score(self, fragment, quantity, score, scenario=None, **kwargs):
        return self._perform_query(_interface, 'observe_unit_score', ForegroundRequired,
                                   fragment, quantity, score, scenario=scenario, **kwargs)

    def tree(self, fragment, **kwargs):
        """
        Return the fragment tree structure with all child flows in depth-first semi-order
        :param fragment:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'tree', ForegroundRequired, fragment, **kwargs)

    def traverse(self, fragment, scenario=None, **kwargs):
        """
        Traverse the fragment (observed) according to the scenario specification and return a list of FragmentFlows
        :param fragment:
        :param scenario:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'traverse', ForegroundRequired,
                                   fragment, scenario, **kwargs)

    def cutoff_flows(self, fragment, scenario=None, **kwargs):
        """
        Report cut-off flows (inputs and outputs to the fragment) grouped as exchanges
        :param fragment:
        :param scenario:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'cutoff_flows', ForegroundRequired,
                                   fragment, scenario, **kwargs)

    def activity(self, fragment, scenario=None, **kwargs):
        """
        Traverse the fragment, returning direct-descendent nodes only. This must be run on an authentic entity and
        not on a ref
        :param fragment:
        :param scenario:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'activity', ForegroundRequired,
                                   fragment, scenario, **kwargs)

    def fragment_lcia(self, fragment, quantity_ref, scenario=None, **kwargs):
        """
        Perform fragment LCIA by first traversing the fragment to determine node weights, and then combining with
        unit scores.
        Not sure whether this belongs in Quantity or Foreground. but probably foreground.
        :param fragment:
        :param quantity_ref:
        :param scenario:
        :param kwargs:
        :return: an LciaResult whose components are FragmentFlows
        """
        return self._perform_query(_interface, 'fragment_lcia', ForegroundRequired,
                                   fragment, quantity_ref, scenario, **kwargs)
