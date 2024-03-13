from ..interfaces import check_direction
# from .. import ExchangeRequired


class UnallocatedExchangeError(Exception):
    pass


class InaccessibleExchangeValue(Exception):
    """
    The exchange ref is somehow unable to lookup the exchange value
    """
    pass


EXCHANGE_TYPES = ('reference', 'self', 'node', 'context', 'cutoff')


class ExchangeRef(object):
    """
    Codifies the information required to define an exchange.  The supplied information could be either object or
    reference/link; it isn't specified.
    """
    is_reference = None
    entity_type = 'exchange'
    is_entity = False
    _term = None

    def __init__(self, process, flow, direction, value=None, unit=None, termination=None, is_reference=False, **kwargs):
        """
        Process, flow, must be entity refs; termination can be process or fragment entity or external_ref,
        context, or None (cutoff).  Any str will be interpreted as an external_ref.  Any non-None, non-str will be
        interpreted as a context (but you're better off supplying an authentic context than a tuple)

        :param process:
        :param flow:
        :param direction:
        :param value:
        :param unit:
        :param termination:
        :param is_reference:
        """
        self._node = process
        self._flow = flow
        self._dir = check_direction(direction)
        self._val = value
        if unit is None:  # this should rather be used to convert numeric values to the flow's reference unit ??
            if hasattr(self._flow, 'unit'):
                unit = self._flow.unit
            else:
                unit = ''
        self._unit = unit
        self.termination = termination
        self.args = kwargs
        self.is_reference = bool(is_reference)

        self._hash = hash((process.origin, process.external_ref, flow.external_ref, direction, self.term_ref))

    @property
    def origin(self):
        return self._node.origin

    @property
    def process(self):
        return self._node

    @property
    def flow(self):
        return self._flow

    @property
    def direction(self):
        return self._dir

    @property
    def value(self):
        if isinstance(self._val, dict):
            try:
                return self._val[None]
            except KeyError:
                raise UnallocatedExchangeError
        else:
            if self._val is not None:  # need to accept 0.0
                return self._val
            else:
                try:
                    if self.is_reference:
                        return self.process.reference_value(self.flow)
                    return self.process.exchange_relation(None, self.flow, self.direction, termination=self.termination)
                except AttributeError:
                    raise InaccessibleExchangeValue

    @property
    def values(self):
        if isinstance(self._val, dict):
            return self._val
        return {None: self._val}

    @property
    def termination(self):
        """
        This can be an entity, str, or None.
        Note that term_ref replicates the characteristics of Exchange.termination (either None, context, or str).

        :return:
        """
        return self._term

    @termination.setter
    def termination(self, term):
        """
        the termination is always one of the following:
         - None
         - a str
         - a tuple (corresponding to a context)
         - an object with the 'entity_type' property with the value 'context', 'process', or 'fragment'
        :param term:
        :return:
        """
        if term is None or isinstance(term, str) or isinstance(term, tuple):
            self._term = term
        elif hasattr(term, 'entity_type'):
            if term.entity_type in ('context', 'process', 'fragment'):
                self._term = term
            else:
                raise TypeError('%s: Invalid termination type: %s' % (term, term.entity_type))
        else:
            raise ValueError('Unintelligible termination %s' % term)

    @property
    def is_elementary(self):
        if hasattr(self.termination, 'elementary'):
            return bool(self.termination.elementary)
        return False

    @property
    def term_ref(self):
        """
        returns either None, a str external_ref, or a tuple.
        Equivalent to native Exchange.lkey for hashing purposes
        :return:
        """
        if hasattr(self._term, 'entity_type'):
            if self._term.entity_type in ('process', 'fragment'):
                return self._term.external_ref
            elif self._term.entity_type == 'context':
                return tuple(self._term)
        return self._term

    @property
    def unit(self):
        return self._unit

    def __getitem__(self, item):
        return self.args[item]

    @property
    def type(self):
        if self.is_reference:
            return 'reference'
        elif self.termination is not None:
            if self.term_ref == self.process.external_ref:
                return 'self'
            elif isinstance(self.term_ref, str):
                return 'node'
            else:
                # resolved: 'elementary' is not an exchange type- the type is 'context'
                return 'context'
                # also resolved: any non-None, non-str term_ref indicates a context
                # it is an ERROR to supply a context NAME as a termination- it will be interpreted as a process ref
            # 'elementary' is a property of a context, but not an exchange_ref
        return 'cutoff'

    def __str__(self):
        """

        :return:
        """
        '''
        old RxRef:
        ref = '(*)'
        return '%6.6s: %s [%s %s] %s' % (self.direction, ref, self._value_string, self.flow.unit, self.flow)
        (value string was ' --- ')
        '''

        ds = {'Input': '<--',
              'Output': '==>'}[self._dir]
        s = d = ' '
        tt = ''
        if self.type == 'reference':
            s = '*'
        elif self.type == 'self':
            d = 'o'
        elif self.type == 'node':
            d = '#'
        elif self.type == 'context':
            tt = ' (%s)' % self._term
        else:
            tt = ' (cutoff)'

        if isinstance(self._val, dict):
            v = '{ #%d# }' % len(self._val)
        elif self._val is None:
            v = '   '
        else:
            v = '%.3g' % self.value
        return '[ %s ]%s%s%s %s (%s) %s %s' % (self.process.name, s, ds, d, v, self.unit, self.flow.name, tt)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if other is None:
            return False
        '''
        if not hasattr(other, 'entity_type'):
            return False
        if other.entity_type != 'exchange':
            return False
        # if self.key == other.key and self.lkey != other.lkey:
        #     raise DuplicateExchangeError('Hash collision!')
        return self.key == other.key
        '''
        try:
            return self.key == other.key
        except AttributeError:
            return False

    @property
    def key(self):
        return self._hash

    @property
    def lkey(self):
        """
        Used for local comparisons
        :return:
        """
        return self.flow.external_ref, self.direction, self.term_ref

    @property
    def comment(self):
        try:
            return self.args['comment']
        except KeyError:
            return ''

    @property
    def locale(self):
        try:
            return self.args['locale']
        except KeyError:
            return self.flow.locale


class RxRef(ExchangeRef):
    """
    Class for process reference exchanges

    """
    @property
    def external_ref(self):
        """
        Reference exchanges can be used as flows w/l/o/g
        :return:
        """
        return self._flow.external_ref

    def __init__(self, process, flow, direction, comment=None, value=0.0, **kwargs):
        if comment is not None:
            kwargs['comment'] = comment
        kwargs.pop('termination', None)
        kwargs.pop('is_reference', None)
        super(RxRef, self).__init__(process, flow, direction, value=value, is_reference=True, **kwargs)

    '''
    def __str__(self):
        ref = '(*)'
        val = ' --- '
        return '%6.6s: %s [%s %s] %s' % (self.direction, ref, val, self.flow.unit, self.flow)
    '''
