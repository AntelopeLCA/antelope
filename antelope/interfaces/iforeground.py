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
        """
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
        return self._perform_query(_interface, 'new_quantity', ForegroundRequired,
                                   name, ref_unit=ref_unit, **kwargs)

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
        :param kwargs: uuid=None, parent=None, comment=None, value=None, balance=False; **kwargs passed to LcFragment
        :return: the fragment? or a fragment ref? <== should only be used in the event of a non-local foreground
        """
        return self._perform_query(_interface, 'new_fragment', ForegroundRequired,
                                   flow, direction, **kwargs)

    def observe(self, fragment, exchange_value=None, termination=None, name=None, scenario=None, **kwargs):
        """
        Observe a fragment's exchange value with respect to its parent activity level.  Only applicable for
        non-balancing fragments whose parents are processes or foreground nodes (child flows of subfragments have
        their exchange values determined at traversal, as do balancing flows).

        A fragment should be named when it is observed.  This should replace name_fragment. In a completed model, all
        observable fragments should have names.

        Also use to define scenario exchange values (or to make replicate observations..).

        scenario and name should be mutually exclusive; if both are supplied, name is ignored.

        :param fragment:
        :param exchange_value: [this must be the second positional argument for legacy reasons, but can still be None]
        :param termination:
        :param name:
        :param scenario:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'observe', ForegroundRequired,
                                   fragment, exchange_value=exchange_value, termination=termination, name=name,
                                   scenario=scenario, **kwargs)

    def observe_unit_score(self, fragment, quantity, score, scenario=None, **kwargs):
        return self._perform_query(_interface, 'observe_unit_score', ForegroundRequired,
                                   fragment, quantity, score, scenario=scenario, **kwargs)

    def tree(self, fragment, **kwargs):
        """
        Return the fragment tree structure with all child flows in depth-first order
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


