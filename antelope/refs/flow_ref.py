from .base import EntityRef, InvalidQuery

from ..flows import Flow


'''
FlowRef could conceivably be used to store characterizations (as opposed to LcFlows, where they're useless)  

Think about this for future.
'''


class FlowRef(EntityRef, Flow):
    """
    Flows can lookup:
    """
    _etype = 'flow'
    _ref_field = 'referenceQuantity'

    def __init__(self, *args, **kwargs):
        super(FlowRef, self).__init__(*args, **kwargs)
        '''
        try:
            self._add_synonym(self._localitem('name'), set_name=True)
        except (KeyError, AttributeError):
            pass
        if self._localitem('casnumber'):
            self._add_synonym(self._localitem('casnumber'))
        '''
        self._flowable.add_term(self.link)

    @property
    def context(self):
        return self._query.get_context(self._context)

    @context.setter
    def context(self, value):
        self._catch_context('Context', value)

    @property
    def _addl(self):
        return self.unit

    def _show_hook(self):
        print('Context: %s' % (self.context, ))
        print(' Locale: %s' % self.locale)
        super(FlowRef, self)._show_hook()

    '''
    def has_characterization(self, quantity, location='GLO'):
        """
        A flow ref keeps track of characterizations by link
        :param quantity:
        :param location:
        :return:
        """
        if quantity.uuid in self._characterizations.keys():
            if location == 'GLO' or location is None:
                return True
            if location in self._characterizations[quantity.uuid].locations():
                return True
        return False

    def add_characterization(self, quantity, value=None, **kwargs):
        q = quantity.uuid
        if q in self._characterizations.keys():
            if value is None:
                return
            c = self._characterizations[q]
        else:
            c = Characterization(self, quantity)
            self._characterizations[q] = c
        if value is not None:
            if isinstance(value, dict):
                c.update_values(**value)
            else:
                kwargs['overwrite'] = kwargs.pop('overwrite', False)
                c.add_value(value=value, **kwargs)
        return c

    def characterizations(self):
        for i in self._characterizations.values():
            yield i
    '''
    def __setitem__(self, key, value):
        """
        trade one DRY for another... this is not too bad though.
        :param key:
        :param value:
        :return:
        """
        if key == 'locale':
            self._locale = value
        else:
            self._catch_context(key, value)
            self._catch_flowable(key.lower(), value)
        super(FlowRef, self).__setitem__(key, value)

    def serialize(self, characterizations=False, domesticate=False, **kwargs):
        j = super(FlowRef, self).serialize(domesticate=domesticate)
        j['referenceQuantity'] = self.reference_entity.external_ref

        return j

    '''
    Interface methods
    '''
    def get_context(self):
        try:
            return self._query.get_context(self._context)
        except InvalidQuery:
            return self._the_query.get_context(self._context)  # this one can bypass -- by talking directly to the catalog

    def targets(self, direction=None, **kwargs):
        return self._query.targets(self.external_ref, direction, **kwargs)

    def emitters(self, direction=None, context=None, **kwargs):
        if context is None:
            context = self.context
        return self._query.emitters(self.external_ref, direction=direction, context=context, **kwargs)

    def terminate(self, **kwargs):
        return self.targets(**kwargs)

    def originate(self, direction=None, **kwargs):
        return self._query.originate(self.external_ref, direction, **kwargs)

    def profile(self, **kwargs):
        return self._query.profile(self.external_ref, **kwargs)

    def characterize(self, quantity, value, context=None, location='GLO', origin=None, **kwargs):
        if context is None:
            context = self.context
        flowable = self.name
        if origin is None:
            origin = self.origin
        self.pop_char(quantity, context, location)
        return self._query.characterize(flowable, self.reference_entity, quantity, value, context=context,
                                        origin=origin, location=location, **kwargs)

    def cf(self, quantity, context=None, locale=None, **kwargs):
        if context is None:
            context = self.context
        if locale is None:
            locale = self.locale

        return self._query.cf(self.external_ref, quantity, ref_quantity=self.reference_entity, context=context,
                              locale=locale, **kwargs)

    '''
    Characterization caching
    this is now builtin to the flow interface
    def see_char(self, qq, cx, loc, qrr):
        self._chars_seen[qq, cx, loc] = qrr

    def chk_char(self, qq, cx, loc):
        return self._chars_seen[qq, cx, loc]

    def pop_char(self, qq, cx, loc):
        return self._chars_seen.pop((qq, cx, loc), None)
    '''
