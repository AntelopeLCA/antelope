from .base import EntityRef
from synonym_dict import LowerDict


class NoUnitConversionTable(Exception):
    pass


def convert(quantity, from_unit=None, to=None):
    """
    Perform unit conversion within a quantity, using a 'UnitConversion' table stored in the object properties.
    For instance, if the quantity name was 'mass' and the reference unit was 'kg', then
    quantity.convert('lb') would[should] return 0.4536...
    quantity.convert('lb', to='ton') should return 0.0005

    This function requires that the quantity have a 'UnitConversion' property that works as a dict, with
    the unit names being keys.  The format of the dict is that all entries should equal the same amount as each other.
    For instance, if the quantity was mass, then the following would be equivalent:

    quantity['UnitConversion'] = { 'kg': 1, 'lb': 2.204622, 'ton': 0.0011023, 't': 0.001 }
    quantity['UnitConversion'] = { 'kg': 907.2, 'lb': 2000.0, 'ton': 1, 't': 0.9072 }

    If the quantity's reference unit is missing from the dict, it is set to 1, but it is not
    strictly required that the reference unit equals 1 in the dict.

    If the quantity is missing a unit conversion property, raises NoUnitConversionTable.  If the quantity does
    have such a table but one of the specified units is missing from it, raises KeyError

    :param quantity: something with a __getitem__ and a unit() function
    :param from_unit: unit to convert from (default is the reference unit)
    :param to: unit to convert to (default is the reference unit)
    :return: a float indicating how many to_units there are in one from_unit
    """

    if from_unit == to:
        return 1.0
    elif from_unit is None:
        if to.lower() == quantity.unit.lower():
            return 1.0
    elif to is None:
        if from_unit.lower() == quantity.unit.lower():
            return 1.0

    try:
        uc_table = quantity['UnitConversion']
        if quantity.unit not in uc_table:
            uc_table[quantity.unit] = 1.0
    except KeyError:
        raise NoUnitConversionTable

    if from_unit is None:
        if quantity.unit in uc_table:
            inbound = uc_table[quantity.unit]
        else:
            inbound = 1.0
    else:
        try:
            inbound = uc_table[from_unit]
        except KeyError:
            raise KeyError('Unknown unit %s for quantity %s' % (from_unit, quantity))

    if to is None:
        if quantity.unit in uc_table:
            outbound = uc_table[quantity.unit]
        else:
            outbound = 1.0

    else:
        try:
            outbound = uc_table[to]
        except KeyError:
            raise KeyError('Unknown unit %s for quantity %s' % (to, quantity))

    return round(outbound / inbound, 12)  # round off to curtail numerical / serialization issues


class QuantityRef(EntityRef):
    """
    Quantities can lookup:
    """
    _etype = 'quantity'
    _ref_field = 'referenceUnit'

    @property
    def unit(self):
        if isinstance(self.reference_entity, str):
            return self.reference_entity
        return self.reference_entity.unitstring

    @property
    def _addl(self):
        if self.is_lcia_method:
            return '%s] [LCIA' % self.unit
        return self.unit

    @property
    def name(self):
        return self._name

    def serialize(self, **kwargs):
        j = super(QuantityRef, self).serialize(**kwargs)
        j['referenceUnit'] = self.unit
        if self.is_lcia_method:
            j['Indicator'] = self.get_item('Indicator')
        return j

    @property
    def is_lcia_method(self):
        return 'Indicator' in self._d

    def convert(self, from_unit=None, to=None):
        if not self.has_property('UnitConversion'):
            uc = LowerDict()
            uc[self.unit] = 1.0
            self['UnitConversion'] = uc
        return convert(self, from_unit, to)

    def quantity_terms(self):
        """
        This is a little kludgey-- but requires agreement on what terms are considered synonymous.
        :return:
        """
        yield self['Name']
        yield self.name
        yield str(self)  # this is the same as above for entities, but includes origin for refs
        yield self.external_ref  # do we definitely want this?  will squash versions together
        if self.uuid is not None:
            yield self.uuid
        if self.origin is not None:
            yield self.link
        if self.has_property('Synonyms'):
            syns = self['Synonyms']
            if isinstance(syns, str):
                yield syns
            else:
                for syn in syns:
                    yield syn

    """
    Interface methods
    """
    def is_canonical(self, other):
        return self._query.get_canonical(other) is self

    def flowables(self, **kwargs):
        return self._query.flowables(quantity=self.external_ref, **kwargs)

    def factors(self, **kwargs):
        return self._query.factors(self.external_ref, **kwargs)

    def cf(self, flow, **kwargs):
        return self._query.cf(flow, self.external_ref, **kwargs)

    def characterize(self, flowable, ref_quantity, value, **kwargs):
        return self._query.characterize(flowable, ref_quantity, self, value, **kwargs)

    def do_lcia(self, inventory, **kwargs):
        return self._query.do_lcia(self, inventory, **kwargs)

    def quantity_relation(self, ref_quantity, flowable, context, locale='GLO', **kwargs):
        return self._query.quantity_relation(flowable, ref_quantity, self, context, locale=locale, **kwargs)

    def norm(self, **kwargs):
        return self._query.norm(self.external_ref, **kwargs)
