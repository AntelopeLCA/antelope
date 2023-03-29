from .flow_interface import FlowInterface
from ..interfaces.iquantity import ConversionReferenceMismatch, NoFactorsFound

import os
import re
import json

from synonym_dict import SynonymSet
from synonym_dict.flowables.cas_number import CasNumber, InvalidCasNumber


# the weak link in our biogenic CO2 accounting: flow name MUST be caught by this regex in order to be quelled
# our hacky-hack: rename flows when they are CO2 and any term matches the regex. do this in the LciaEngine.
biogenic = re.compile('(biotic|biogenic|non-fossil|in air)', flags=re.IGNORECASE)


def flowname_is_biogenic(flowname):
    return bool(biogenic.search(flowname))


class QuelledCO2(object):
    def __init__(self, flowable, context):
        self.flowable = flowable
        self.context = context

    @property
    def value(self):
        return 0.0

"""
openlca_locales.json file created from: antelope_olca package, gen_locales('openlca_locales.json') 
"""

with open(os.path.join(os.path.dirname(__file__), 'openlca_locales.json')) as fp:
    olca_locales = json.load(fp)


class Flow(FlowInterface):
    """
    A partly-abstract class that implements the flow specification but not the entity specification.

    Included in this specification is a *detection of biogenic CO2 by regex*
    Each flow has a quell_co2 property which is True if:
     - the flow is a synonym for CO2 and
     - the flow's name matches the biogenic regex: '(biotic|biogenic|non-fossil|in air)' (case insensitive)
    There are 3 ways for a flow to be identified as a synonym for CO2:
     1. pass is_co2=True at instantiation
     2. set flow.is_co2 = True
     3. assign a CasNumber equivalent to '124-38-9'

    Item #2 can be used in general by downstream implementations.

    For the time being, the flow name matching the regex is the *only* way to identify a flow as biogenic.
    """

    _is_co2 = False
    _context = ()
    _context_set_level = 0
    _locale = None

    _filt = str.maketrans('\u00b4\u00a0\u2032\xa0', "' ' ", '')  # filter name strings to pull out problematic unicode

    def _catch_context(self, key, value):
        """
        Add a hook to set context in __getitem__ or wherever is appropriate, to capture and automatically set context
        according to the following precedence:
         context > compartment > category > class | classification > cutoff (default)
        :param key:
        :param value:
        :return:
        """
        try:
            level = {'none': 0,
                     'class': 1,
                     'classification': 1,
                     'classifications': 1,
                     'category': 2,
                     'categories': 2,
                     'compartment': 3,
                     'compartments': 3,
                     'context': 4}[key.lower()]
        except KeyError:
            return
        if isinstance(value, str):
            value = (value, )
        if level > self._context_set_level:
            self._context_set_level = min([level, 3])  # always allow context spec to override
            self._context = tuple(filter(None, value))

    def _add_synonym(self, term, set_name=False):
        if set_name:
            tm = term.translate(self._filt).strip()  # have to put strip after because \u00a0 turns to space
            self._flowable.add_term(tm)
            self._flowable.set_name(tm)
            self._check_locale(tm)
        self._flowable.add_term(term.strip())

    def _check_locale(self, term):
        """
        If the term matches the pattern ^[text], [locale]$, where 'locale' is found in a canonical set of locale
         specs (olca_locales), then add the locale-free term as a synonym and set the locale as the flow's locale.
        :param term:
        :return:
        """
        if self._locale is None:
            parts = term.split(', ')
            cand = parts[-1]
            if cand in olca_locales:
                self._locale = cand
                self._flowable.add_term(', '.join(parts[:-1]))

    @property
    def locale(self):
        if self._locale is None:
            return 'GLO'
        return self._locale

    @property
    def is_co2(self):
        return self._is_co2

    @is_co2.setter
    def is_co2(self, value):
        self._is_co2 = bool(value)

    def _catch_flowable(self, key, value):
        """
        Returns True or None- allow to chain to avoid redundant _catch_context
        :param key:
        :param value:
        :return:
        """
        if key == 'name':
            self._add_synonym(value, set_name=True)
            return True
        elif key == 'casnumber':
            try:
                c = CasNumber(value)
                for t in c.terms:
                    self._add_synonym(t)
                if c.name == '124-38-9':
                    self._is_co2 = True
            except InvalidCasNumber:
                pass
            return True
        elif key == 'synonyms':
            if isinstance(value, str):
                self._add_synonym(value)
                return True
            else:
                for v in value:
                    self._add_synonym(v)
                return True
        elif key in ('locale', 'location'):
            self._locale = value
            return True

    __flowable = None

    @property
    def _flowable(self):
        if self.__flowable is None:
            self.__flowable = SynonymSet()
        return self.__flowable

    @property
    def name(self):
        return self._flowable.name

    @name.setter
    def name(self, name):
        """

        :param name:
        :return:
        """
        if name is None:
            raise TypeError('None is not a valid name')
        elif name in self.synonyms:
            self._flowable.set_name(name)
        else:
            raise ValueError('name %s not a recognized synonym for %s' % (name, self.name))

    @property
    def synonyms(self):
        for t in self._flowable.terms:
            yield t

    @property
    def context(self):
        """
        A flow's context is any hierarchical tuple of strings (generic, intermediate, ..., specific).
        :return:
        """
        return self._context

    @context.setter
    def context(self, value):
        self._catch_context('Context', value)

    def match(self, other):
        """
        match if any synonyms match
        :param other:
        :return:
        """
        '''
        return (self.uuid == other.uuid or
                self['Name'].lower() == other['Name'].lower() or
                (trim_cas(self['CasNumber']) == trim_cas(other['CasNumber']) and len(self['CasNumber']) > 4) or
                self.external_ref == other.external_ref)  # not sure about this last one! we should check origin too
        '''
        if hasattr(other, 'flow'):
            other = other.flow
        if isinstance(other, str):
            if other == self.external_ref:
                return True
            return other in self._flowable
        if hasattr(other, 'synonyms'):
            return any([t in self._flowable for t in other.synonyms])
        return False

    __chars_seen = None

    @property
    def _chars_seen(self):
        if self.__chars_seen is None:
            self.__chars_seen = dict()
        return self.__chars_seen

    @property
    def quell_co2(self):
        if self._is_co2:
            if flowname_is_biogenic(self.name):
                return True
        return False

    def lookup_cf(self, quantity, context, locale, refresh=False, quell_biogenic_co2=False, **kwargs):
        """
        Cache characterization factors obtained from quantity relation queries
        :param quantity:
        :param context:
        :param locale:
        :param refresh:
        :param quell_biogenic_co2:
        :param kwargs:
        :return: a QRResult which is not even known to the interface
        """
        locale = locale or self.locale
        key = (quantity, context, locale)

        if quell_biogenic_co2:
            if self.quell_co2:
                return QuelledCO2(self._flowable, context)

        if refresh:
            self._chars_seen.pop(key, None)
        try:
            return self._chars_seen.__getitem__(key)
        except KeyError:
            try:
                qr = quantity.quantity_relation(self.name, self.reference_entity, context, locale=locale, **kwargs)
            except ConversionReferenceMismatch as e:
                qr = e.args[0]
            except NoFactorsFound:
                qr = None
        self._chars_seen[key] = qr
        return qr

    def pop_char(self, qq, cx, loc):
        return self._chars_seen.pop((qq, cx, loc), None)
