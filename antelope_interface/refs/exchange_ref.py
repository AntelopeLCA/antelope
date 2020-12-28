from ..interfaces import check_direction
from .. import ExchangeRequired


class ExchangeRef(object):
    """
    Codifies the information required to define an exchange.  The supplied information could be either object or
    reference/link; it isn't specified.
    """
    is_reference = None
    entity_type = 'exchange'
    is_entity = False

    def __init__(self, process, flow, direction, value=0.0, unit=None, termination=None, is_reference=False, **kwargs):
        """
        Process, flow, must be entity refs; termination can be entity or external_ref

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
        if unit is None:
            if hasattr(self._flow, 'unit'):
                unit = self._flow.unit
            else:
                unit = ''
        self._unit = unit
        self._term = termination
        self.args = kwargs
        self.is_reference = bool(is_reference)

        self._hash = hash((process.origin, process.external_ref, flow.external_ref, direction, self.term_ref))

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
        if self.is_reference:
            try:
                return self.process.reference_value(self.flow)
            except (AttributeError, ExchangeRequired):
                if self._val != 0.0:
                    return self._val
                raise ExchangeRequired('Inoperable process ref %s' % self.process.link)
        return self._val

    @property
    def termination(self):
        return self._term

    @property
    def term_ref(self):
        if self._term is None:
            return None
        elif hasattr(self._term, 'external_ref'):
            return self._term.external_ref
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
            if self.termination == self.process.external_ref:
                return 'self'
            elif isinstance(self.termination, str):
                return 'node'
            else:
                return 'context'
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


class RxRef(ExchangeRef):
    """
    Class for process reference exchanges

    """
    def __init__(self, process, flow, direction, comment=None, **kwargs):
        if comment is not None:
            kwargs['comment'] = comment
        kwargs.pop('termination', None)
        super(RxRef, self).__init__(process, flow, direction, value=0.0, is_reference=True, **kwargs)

    '''
    def __str__(self):
        ref = '(*)'
        val = ' --- '
        return '%6.6s: %s [%s %s] %s' % (self.direction, ref, val, self.flow.unit, self.flow)
    '''
