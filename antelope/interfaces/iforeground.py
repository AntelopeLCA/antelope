from antelope.interfaces.abstract_query import AbstractQuery


class ForegroundRequired(Exception):
    pass


_interface = 'foreground'


class ForegroundInterface(AbstractQuery):
    """
    The bare minimum foreground interface allows a foreground to create new flows and quantities, lookup terminations,
     and to save anything it creates.
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
    candidates
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
