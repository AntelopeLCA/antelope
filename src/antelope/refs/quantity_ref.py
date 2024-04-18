"""
Quantity Reference

A couple things really bother me about this spec:

1- the routine for doing LCIA (antelope_core.implementations.quantity.do_lcia()) seems like it should be generic,
but it depends on the LciaResult implementation, which is irretrievably part of the core and NOT part of the spec.

1a- That means the interface currently lacks a specification for LCIA Results, which seems important

2- The signatures for these methods are delicate:
  quantity_ref.cf(flow, context=?, locale=?) --> float
  quantity_ref.quantity_relation(flowable, ref_quantity, context=?, locale=?) --> QuantityConversion
  quantity_ref.characterize(flowable, ref_quantity, value, context=?, locale=?) --> CF

"""

from ..flows import FlowInterface
from .base import EntityRef
from synonym_dict import LowerDict


class RefQuantityRequired(Exception):
    pass


class ConversionError(Exception):
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
        if to == quantity.unit:
            return 1.0
    elif to is None:
        if from_unit == quantity.unit:
            return 1.0

    try:
        uc_table = quantity['UnitConversion']
        if quantity.unit is not None:
            if quantity.unit not in uc_table:
                uc_table[quantity.unit] = 1.0
    except KeyError:
        raise ConversionError('%s: No Unit Conversion Table' % quantity)

    if from_unit is None:
        if quantity.unit in uc_table:
            inbound = uc_table[quantity.unit]
        else:
            inbound = 1.0
    else:
        try:
            inbound = uc_table[from_unit]
        except KeyError:
            raise ConversionError('%s: Unknown from_unit %s' % (quantity, from_unit))

    if to is None:
        if quantity.unit in uc_table:
            outbound = uc_table[quantity.unit]
        else:
            outbound = 1.0

    else:
        try:
            outbound = uc_table[to]
        except KeyError:
            raise ConversionError('%s: Unknown to_unit %s' % (quantity, to))

    return round(outbound / inbound, 12)  # round off to curtail numerical / serialization issues


class QuantityRef(EntityRef):
    """
    Quantities can lookup:
    """
    _etype = 'quantity'
    _ref_field = 'referenceUnit'

    @property
    def unit(self):
        ref = self.reference_entity
        if isinstance(ref, str):
            return ref
        elif hasattr(ref, 'unitstring'):
            return ref.unitstring
        return ref

    @property
    def _addl(self):
        u = self.unit or ''
        if self.is_lcia_method:
            m = self.get('Method', 'LCIA')
            return '%s] [%s' % (u, m)
        return u

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
        is_ind = self._d.get('Indicator', '')
        if isinstance(is_ind, str) and len(is_ind) > 0:
            return True
        return False

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
        if not self.is_lcia_method:
            yield self['Name']
            yield self.name
            yield str(self)  # this is the same as above for entities, but includes origin for refs
        yield self.external_ref  # do we definitely want this?  version-less name will return earliest version
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
    def has_lcia_engine(self):
        return self._query.is_lcia_engine()

    @property
    def is_local(self):
        return self._query.origin == 'local.qdb'

    def is_canonical(self, other):
        return self._query.get_canonical(other) is self

    def flowables(self, **kwargs):
        return self._query.flowables(quantity=self.external_ref, **kwargs)

    def factors(self, **kwargs):
        return self._query.factors(self.external_ref, **kwargs)

    def cf(self, flow, ref_quantity=None, **kwargs):
        if ref_quantity is None:
            try:
                ref_quantity = flow.reference_entity
            except AttributeError:
                raise RefQuantityRequired
        if self.is_canonical(ref_quantity):
            return 1.0
        return self._query.cf(flow, self.external_ref, ref_quantity=ref_quantity, **kwargs)

    def characterize(self, flowable, ref_quantity, value, **kwargs):
        """
        Enter a characterization factor for the current object (query quantity) w.r.t. the specified reference quantity.
        The characterization value should report the amount of the query quantity (quantity being characterized) that
        equals a unit of the reference quantity (used to measure the flow). The following is correct,
        for mass in kg and volume in m3:

        >>> mass.characterize('water', 'volume', 1000.0)
        "I {characterize} the [mass] of [water] in a unit [volume] to be 1000.0".

        The thing being measured is mass.
        The flow's reference quantity is volume. a unit reference quantity of water is characterized as 1000.0 kg.

        The following is NOT correct, but it may SEEM more semantically natural:

        >>> mass.characterize('water', 'volume', 0.001)
        "I {characterize} the unit [mass] of [water] to have a [volume] of 0.001"

        The unit of the flow is measured in terms of the query quantity.  But we don't yet know the size of a unit
        of the query quantity because that is what is in fact being characterized.

        To see this borne out, imagine using characterize() in its most natural way, for LCIA:

        >>> gwp.characterize('methane', 'mass', 25)
        "I characterize the GWP of methane in a unit mass to be 25" <<--- CORRECT
        {I characterize the unit GWP of methane to have a mass of 0.04} <<--- plainly wrong

        REALLY, the MOST natural way to characterize is to use `FlowRef.characterize()`:

        >>> m = q.get('methane')
        >>> m.unit
        'kg'
        >>> m.characterize(gwp, 25, context='to air')

        generations may determine whether this was a terrible mistake.

        :param flowable:
        :param ref_quantity:
        :param value:
        :param kwargs:
        :return:
        """
        return self._query.characterize(flowable, ref_quantity, self, value, **kwargs)

    def get_factors(self, flows, **kwargs):
        return self._query.get_factors(self, flows, **kwargs)

    def do_lcia(self, inventory, **kwargs):
        return self._query.do_lcia(self, inventory, **kwargs)

    def quantity_relation(self, flowable, ref_quantity=None, context=None, locale='GLO', **kwargs):
        if isinstance(flowable, FlowInterface):
            if ref_quantity is None:
                ref_quantity = flowable.reference_entity
            if context is None:
                context = flowable.context
            flowable = flowable.name
        return self._query.quantity_relation(flowable, ref_quantity, self, context, locale=locale, **kwargs)

    def norm(self, **kwargs):
        return self._query.norm(self.external_ref, **kwargs)
