"""
Pydantic Model definitions for data exchange.

TODO: decide on a consistent structure / format for entity identification.  Currently:

 * EntityRef and subclasses use entity_id
 * FlowSpec uses external_ref
 * ExteriorFlow uses flow
 * Exchange and subclasses use <type> e.g. process and flow.external_ref (exchange.flow is FlowSpec)
 * Quantity-related subclasses use <mod>_<type> e.g. ref_quantity, query_quantity

 = This tells me that FragmentFlows should use 'fragment' and 'parent_fragment'

"""

from pydantic import BaseModel
from pydantic.typing import List, Dict, Optional
from synonym_dict import LowerDict


class ResponseModel(BaseModel):
    # There's good reason for having this child class later on.
    # It is to allow for global response model configuration via inheritance.
    pass


class OriginMeta(ResponseModel):
    origin: str
    is_lcia_engine: bool
    interfaces: List[str]
    '''
    # report the authorization status of the query: based on auth token, what interfaces can the user access?
    read: List(str)  
    write: List(str)
    values: List(str)
    '''


class OriginCount(ResponseModel):
    origin: str
    count: dict


class EntityRef(ResponseModel):
    origin: str
    entity_id: str
    entity_type: Optional[str]

    @classmethod
    def from_entity(cls, entity):
        return cls(origin=entity.origin, entity_id=entity.external_ref, entity_type=entity.entity_type)


class Entity(EntityRef):
    entity_type: str
    properties: Dict

    @classmethod
    def from_entity(cls, entity, **kwargs):
        obj = cls(origin=entity.origin,
                  entity_id=entity.external_ref,
                  entity_type=entity.entity_type,
                  properties=LowerDict())

        for key, val in kwargs.items():
            obj.properties[key.lower()] = entity[key]

        obj.properties['name'] = entity['name']  # entity.name is doctored

        if entity.entity_type == 'quantity':
            obj.properties['unit'] = entity.unit
            # if entity.is_lcia_method:
            #     obj.properties['indicator'] = entity['indicator']  # this should be handled by signature_fields()

        if entity.uuid is not None:
            obj.properties['uuid'] = entity.uuid
        return obj

    @classmethod
    def from_json(cls, j):
        obj = cls(origin=j.pop('origin'), entity_id=j.pop('externalId'), entity_type=j.pop('entityType'),
                  properties=dict())

        if obj.entity_type == 'quantity':
            obj.properties['unit'] = j.pop('referenceUnit', None)
            obj.properties['is_lcia_method'] = bool('Indicator' in j)

        for key, val in j.items():
            obj.properties[key] = val
        return obj


class FlowEntity(Entity):
    """
    Open questions: should context and locale be properties? or attributes? should referenceQuantity be an attribute?
    """
    context: List[str]
    locale: str

    @classmethod
    def from_flow(cls, entity, **kwargs):
        obj = cls(origin=entity.origin,
                  entity_id=entity.external_ref,
                  entity_type=entity.entity_type,
                  context=list(entity.context),
                  locale=entity.locale,
                  properties=dict())

        obj.properties['name'] = entity.name
        obj.properties[entity.reference_field] = entity.reference_entity.external_ref

        for key, val in kwargs.items():
            obj.properties[key] = entity[key]
        return obj

    @classmethod
    def from_exchange(cls, ex):
        """
        This is from an antelope Exchange or ExchangeRef
        :param ex:
        :return:
        """
        return cls(origin=ex.origin, entity_id=ex.flow.external_ref, entity_type='flow', context=list(ex.flow.context),
                   locale=ex.flow.locale, properties={'name': ex.flow['name'],
                                                      ex.flow.reference_field: ex.flow.reference_entity.external_ref})

    @classmethod
    def from_exchange_model(cls, ex):
        """
        ExchangeModel includes a FlowSpec instead of a flow
        :param ex:
        :return:
        """
        return cls(origin=ex.origin, entity_id=ex.flow.external_ref, entity_type='flow', context=ex.flow.context,
                   locale=ex.flow.locale, properties={'name': ex.flow.flowable,
                                                      'referenceQuantity': ex.flow.quantity_ref})


class Context(ResponseModel):
    name: str
    parent: Optional[str]
    sense: Optional[str]
    elementary: bool
    subcontexts: List[str]

    @classmethod
    def from_context(cls, cx):
        if cx.parent is None:
            parent = ''
        else:
            parent = cx.parent.name
        return cls(name=cx.name, parent=parent or '', sense=cx.sense, elementary=cx.elementary,
                   subcontexts=list(k.name for k in cx.subcompartments))


class FlowSpec(ResponseModel):
    """
    Non-context exchange terminations do not get included in flow specifications, because they are part of the model and
    not the flow
    """
    external_ref: Optional[str]
    flowable: str
    quantity_ref: str
    context: List[str]
    locale: str

    @classmethod
    def from_flow(cls, flow):
        return cls(external_ref=flow.external_ref, flowable=flow.name, quantity_ref=flow.reference_entity.external_ref,
                   context=list(flow.context), locale=flow.locale)

    @classmethod
    def from_exchange(cls, x, locale=None):
        if x.type == 'context':
            cx = list(x.termination)
        elif x.type in ('reference', 'cutoff'):
            cx = None
        else:
            raise TypeError('%s\nUnknown exchange type %s' % (x, x.type))
        loc = locale or x.flow.locale
        return cls(external_ref=x.flow.external_ref, flowable=x.flow.name, quantity_ref=x.flow.reference_entity.external_ref,
                   context=cx, locale=loc)


class ExteriorFlow(ResponseModel):
    """
    Do we really need both an ExteriorFlow model and a FlowSpec model? this one has direction, and origin+flow;
    that one has flowable+ref entity, and locale (but we added locale)

    This is currently unused, but that's because we haven't implemented the {origin}/exterior route yet
    """
    origin: str
    flow: str
    direction: str  # antelope_interface specifies the direction as w/r/t/ context, as in "Input" "to air". This SEEMS WRONG.
    context: List[str]
    locale: Optional[str] = 'GLO'  # ???


class DirectedFlow(ResponseModel):
    flow: FlowSpec
    direction: str

    @classmethod
    def from_exchange(cls, obj):
        return cls(flow=FlowSpec.from_flow(obj.flow), direction=obj.direction)


class Exchange(ResponseModel):
    """
    Do we need to add locale??
    """
    origin: str
    process: str
    flow: FlowSpec
    direction: str
    termination: Optional[str]
    context: Optional[List[str]]
    type: str  # {'reference', 'self', 'node', 'context', 'cutoff'}, per
    comment: Optional[str]

    @classmethod
    def from_exchange(cls, x, **kwargs):
        if x.type == 'context':
            cx = list(x.termination)
            term = None
        else:
            term = x.termination
            cx = None
        return cls(origin=x.process.origin, process=x.process.external_ref, flow=FlowSpec.from_flow(x.flow),
                   direction=x.direction, termination=term, context=cx, type=x.type, comment=x.comment, str=str(x), **kwargs)


class ReferenceExchange(Exchange):
    is_reference = True
    termination: None


class ReferenceValue(ReferenceExchange):
    value = float

    @classmethod
    def from_rx(cls, x):
        return cls.from_exchange(x, value=x.value)


class ExchangeValues(Exchange):
    """
    dict mapping reference flows to allocated value
    This should really be called ExchangeValues- in fact the method is already called exchangeValues!
    """
    values: Dict
    uncertainty: Optional[Dict]

    @classmethod
    def from_ev(cls, x):
        return cls.from_exchange(x, values=x.values)


class UnallocatedExchange(Exchange):
    is_reference: bool = False
    value: float
    uncertainty: Optional[Dict]

    @classmethod
    def from_inv(cls, x):
        """
        This works for ExchangeRefs as well as exchanges
        :param x:
        :return:
        """
        return cls.from_exchange(x, value=x.value, is_reference=x.is_reference)


class AllocatedExchange(Exchange):

    ref_flow: str
    value: float
    uncertainty: Optional[Dict]

    @property  # maybe this will prevent it from getting serialized but still operate
    def is_reference(self):
        return False

    @classmethod
    def from_inv(cls, x, ref_flow: str):
        return cls.from_exchange(x, ref_flow=ref_flow, value=x.value)


def generate_pydantic_exchanges(xs, type=None):
    """

    :param xs: iterable of exchanges
    :param type: [None] whether to filter the exchanges by type. could be one of None, 'reference', 'self', 'node',
    'context', 'cutoff'
    :return:
    """
    for x in xs:
        if type and (type != x.type):
            continue
        if x.is_reference:
            yield ReferenceExchange.from_exchange(x)
            continue

        else:
            yield Exchange.from_exchange(x)


Exch_Modes = (None, 'reference', 'interior', 'exterior', 'cutoff')


def generate_pydantic_inventory(xs, mode=None, values=False, ref_flow=None):
    """
    Not currently used

    :param xs: iterable of exchanges
    :param mode: [None] whether to filter the exchanges by type. could be one of:
     None: generate all exchanges
     'interior'
     'exterior'
     'cutoff'
    :param values: (bool) [False] whether to include exchange values.
    :param ref_flow: (ignored if values=False) the reference flow with which the exchange value was computed. If None,
     this implies the exchange reports un-allocated exchange values
    :return:
    """
    if hasattr(ref_flow, 'entity_type'):
        if ref_flow.entity_type == 'flow':
            ref_flow = ref_flow.external_ref
        elif ref_flow.entity_type == 'exchange':
            ref_flow = ref_flow.flow.external_ref
        else:
            raise TypeError(ref_flow.entity_type)

    for x in xs:
        if x.is_reference:
            if mode and (mode != 'reference'):
                continue
            if values:
                yield ReferenceValue.from_rx(x)
            else:
                yield ReferenceExchange.from_exchange(x)
            continue

        else:
            if x.type in ('self', 'node'):
                if mode and (mode != 'interior'):
                    continue
            elif x.type in ('context', 'elementary'):
                if mode and (mode != 'exterior'):
                    continue
            elif x.type == 'cutoff':
                if mode and (mode != 'cutoff'):
                    continue

            yield AllocatedExchange.from_inv(x, ref_flow=ref_flow)


"""
Quantity Types
"""


class Characterization(ResponseModel):
    origin: str
    flowable: str
    ref_quantity: str
    ref_unit: str
    query_quantity: str
    query_unit: str
    context: List[str]
    value: Dict

    @classmethod
    def from_cf(cls, cf):
        ch = cls.null(cf)
        for loc in cf.locations:
            ch.value[loc] = cf[loc]
        return ch

    @classmethod
    def null(cls, cf):
        ch =  cls(origin=cf.origin, flowable=cf.flowable,
                  ref_quantity=cf.ref_quantity.external_ref, ref_unit=cf.ref_quantity.unit,
                  query_quantity=cf.quantity.external_ref, query_unit=cf.quantity.unit,
                  context=list(cf.context), value=dict())
        return ch


class Normalizations(ResponseModel):
    """
    This is written to replicate the normalisation data stored per-method in OpenLCA JSON-LD format
    """
    origin: str
    quantity: str
    norm: Dict
    weight: Dict

    @classmethod
    def from_q(cls, q):
        n = cls(origin=q.origin, quantity=q.external_ref, norm=dict(), weight=dict())
        if q.has_property('normSets'):
            sets = q['normSets']
            try:
                norms = q['normalisationFactors']
            except KeyError:
                norms = [0.0]*len(sets)
            try:
                wgts = q['weightingFactors']
            except KeyError:
                wgts = [0.0]*len(sets)
            for i, set in sets:
                n.norm[set] = norms[i]
                n.weight[set] = wgts[i]
        return n


class QuantityConversion(ResponseModel):
    """
    Technically, a quantity conversion can include chained QR Results, but we are flattening it (for now)
    """
    origin: str
    flowable: str
    ref_quantity: str
    query_quantity: str
    context: List[str]
    locale: str
    value: float

    @classmethod
    def from_qrresult(cls, qrr):
        return cls(origin=qrr.origin, flowable=qrr.flowable,
                   ref_quantity=qrr.ref.external_ref, query_quantity=qrr.query.external_ref,
                   context=list(qrr.context), locale=qrr.locale, value=qrr.value)


def _context_to_str(cx):
    if isinstance(cx, tuple):
        if len(cx) == 0:
            context = None
        else:
            context = str(cx[-1])
    elif hasattr(cx, 'entity_type') and cx.entity_type == 'context':
        context = cx.name
    elif cx is None:
        context = None
    else:
        raise TypeError('%s: Unrecognized context type %s' % (cx, type(cx)))
    return context


class LciaResult(ResponseModel):
    scenario: Optional[str]
    object: str
    quantity: Entity
    scale: float
    total: float

    @classmethod
    def from_lcia_result(cls, object, res):
        return cls(scenario=res.scenario, object=object.name, quantity=Entity.from_entity(res.quantity), scale=res.scale,
                   total=res.total())


class AggregatedLciaScore(ResponseModel):
    component: str
    result: float


class SummaryLciaScore(AggregatedLciaScore):
    node_weight: Optional[float]
    unit_score: Optional[float]


class SummaryLciaResult(LciaResult):
    components: List[SummaryLciaScore]

    @classmethod
    def from_lcia_result(cls, object, res):
        return cls(scenario=res.scenario, object=object.name, quantity=Entity.from_entity(res.quantity), scale=res.scale,
                   total=res.total(), components=res.serialize_components(detailed=False))


class LciaDetail(ResponseModel):
    exchange: Optional[FlowSpec]
    factor: QuantityConversion
    result: float


class DisaggregatedLciaScore(AggregatedLciaScore):
    origin: str
    entity_id: str
    details: List[LciaDetail]
    summaries: List[SummaryLciaScore]  # these are different data types

    @classmethod
    def from_component(cls, obj, c):
        if hasattr(c.entity, 'name'):
            component = c.entity.name
        else:
            component = str(c.entity)
        if hasattr(c.entity, 'external_ref'):
            origin = c.entity.origin
            entity_id = c.entity.external_ref
        else:
            origin = obj.origin
            entity_id = obj.external_ref
        obj = cls(origin=origin, entity_id=entity_id, component=component, result=c.cumulative_result,
                  details=[], summaries=[])
        for d in sorted(c.details(), key=lambda x: x.result, reverse=True):
            if hasattr(d, 'node_weight'):
                obj.summaries.append(SummaryLciaScore(**d.serialize(detailed=False)))
            else:
                obj.details.append(LciaDetail(exchange=FlowSpec.from_exchange(d.exchange),
                                              factor=QuantityConversion.from_qrresult(d.factor),
                                              result=d.result))
        return obj


class DetailedLciaResult(LciaResult):
    components: List[DisaggregatedLciaScore]

    @classmethod
    def from_lcia_result(cls, obj, res):
        mod = cls(scenario=res.scenario, object=obj.name, quantity=Entity.from_entity(res.quantity), scale=res.scale,
                  total=res.total(), components=[])
        for c in res.components():
            mod.components.append(DisaggregatedLciaScore.from_component(obj, c))
        return mod
