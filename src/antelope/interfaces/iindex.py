from .abstract_query import AbstractQuery


class IndexRequired(Exception):
    pass


directions = ('Input', 'Output')


class InvalidDirection(Exception):
    pass


def check_direction(dirn):
    _dir = dirn  # needed only in case of exception
    if isinstance(dirn, str):
        dirn = dirn[0].lower()
    try:
        return {0: 'Input',
                1: 'Output',
                'i': 'Input',
                'o': 'Output'}[dirn]
    except KeyError:
        raise InvalidDirection(_dir)


class InvalidSense(Exception):
    pass


def valid_sense(sense):
    if sense is None:
        return None
    try:
        v = {'source': 'Source',
             'sink': 'Sink'}[sense.lower()]
    except KeyError:
        raise InvalidSense(sense)
    return v


def comp_dir(direction):
    """
    Returns the complementary direction to the provided direction ('input' or 'output'), case-insensitive but
    unfortunately localized.

    (Obviously this whole concept is essentially i18n of a boolean value)

    comp_dir also accepts inputs of sense, e.g. 'source' and 'sink'  The implicit direction of a 'source' is 'output',
    and so comp_dir('Source') returns 'Input', and comp_dir('Sink') returns 'Output'.
    :param direction:
    :return:
    """
    if direction is None:
        return None
    try:
        _dirn = check_direction(direction)
    except InvalidDirection:
        try:
            return {'Source': 'Input',
                    'Sink': 'Output'}[valid_sense(direction)]
        except InvalidSense:
            raise InvalidDirection('%s' % direction)
    return next(k for k in directions if k != _dirn)


def comp_sense(direction):
    """
    This inverts the conversion of sense to complementary direction in comp_dir
    comp_sense('Input') returns 'Source' and comp_sense('Output') returns 'Sink'
    :param direction:
    :return:
    """
    return {
        'Input': 'Source',
        'Output': 'Sink'
    }[check_direction(direction)]


def num_dir(direction):
    """
    Converts a direction input to a number, in which Input = 0 and Output = 1.
    :param direction:
    :return:
    """
    return {'Input': 0,
            'Output': 1,
            'input': 0,
            'output': 1,
            0: 0,
            1: 1,
            '0': 0,
            '1': 1}[direction]


_interface = 'index'


class IndexInterface(AbstractQuery):
    """
    CatalogInterface core methods
    These are the main tools for describing information about the contents of the archive
    """
    def count(self, entity_type, **kwargs):
        """
        Return a count of the number of entities of the named type
        :param entity_type:
        :param kwargs:
        :return: int
        """
        return self._perform_query(_interface, 'count', IndexRequired, entity_type, **kwargs)

    def processes(self, **kwargs):
        """
        Generate process entities (reference exchanges only)
        :param kwargs: keyword search
        :return:
        """
        for i in self._perform_query(_interface, 'processes', IndexRequired, **kwargs):
            yield self.make_ref(i)

    def flows(self, **kwargs):
        """
        Generate flow entities (reference quantity only)
        :param kwargs: keyword search
        :return:
        """
        for i in self._perform_query(_interface, 'flows', IndexRequired, **kwargs):
            yield self.make_ref(i)

    def flowables(self, search=None, **kwargs):
        """
        Generate known flowables by their canonical name
        :param search: [None] if provided, filter results (implementation dependent)
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'flowables', IndexRequired,
                                   search=search, **kwargs)

    def contexts(self, **kwargs):
        """
        Generate known contexts as tuples of canonical names
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'contexts', IndexRequired,
                                   ** kwargs)

    '''    
    def get_context(self, term, **kwargs):
        """
        Return the context matching the specified term
        :param term:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'get_context', IndexRequired,
                                   term, ** kwargs)
    '''
    def quantities(self, **kwargs):
        """
        Generate quantities
        :param kwargs: keyword search
        :return:
        """
        for i in self._perform_query(_interface, 'quantities', IndexRequired, **kwargs):
            yield self.make_ref(i)

    def lcia(self, **kwargs):
        """
        Generate LCIA methodologies or collections of LCIA indicators.  type not yet specified
        :param kwargs: keyword search
        :return:
        """
        for i in self._perform_query(_interface, 'lcia', IndexRequired, **kwargs):
            yield self.make_ref(i)

    def lcia_methods(self, **kwargs):
        """
        Generate LCIA methods (nominally, quantities with an 'Indicator' property)
        :param kwargs: keyword search
        :return:
        """
        for i in self._perform_query(_interface, 'lcia_methods', IndexRequired, **kwargs):
            yield self.make_ref(i)

    """
    API functions- entity-specific -- get accessed by catalog ref
    index interface
    """
    def unmatched_flows(self, flows, **kwargs):
        """
        Takes in a list of flowable terms and generates a sublist of flows that were not recognized as synonyms to any
        local flows.
        :param flows: iterable
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'unmatched_flows', IndexRequired,
                                   flows, **kwargs)

    def targets(self, flow, direction=None, **kwargs):
        """
        Find processes that match the given flow and have a complementary direction
        :param flow:
        :param direction: if omitted, return all processes having the given flow as reference, regardless of direction
        :return:
        """
        for i in self._perform_query(_interface, 'targets', IndexRequired,
                                     flow, direction=direction, **kwargs):
            yield self.make_ref(i)

    def originate(self, flow, direction=None, **kwargs):
        """
        Find processes that match the given flow and have the same direction
        :param flow:
        :param direction: if omitted, return all processes having the given flow as reference, regardless of direction
        :return:
        """
        '''
        for i in self._perform_query(_interface, 'originate', IndexRequired('Index access required'),
                                     flow, direction=direction, **kwargs):
            yield self.make_ref(i)
        '''
        for i in self.targets(flow, comp_dir(direction), **kwargs):  # just gets flipped back again in terminate()
            yield i
    '''
    def mix(self, flow, direction, **kwargs):
        """
        Create a mixer process whose inputs are all processes that terminate the given flow and direction
        :param flow:
        :param direction:
        :return:
        """
        return self._perform_query(_interface, 'mix', IndexRequired('Index access required'),
                                   flow, direction, **kwargs)
    '''
