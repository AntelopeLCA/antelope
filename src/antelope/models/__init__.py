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
from typing import List, Dict, Optional
# from synonym_dict import LowerDict


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

    @property
    def external_ref(self):  # what, was there some taboo against this?
        return self.entity_id

    @classmethod
    def from_entity(cls, entity):
        return cls(origin=entity.origin, entity_id=entity.external_ref, entity_type=entity.entity_type)

    @property
    def link(self):
        return '%s/%s' % (self.origin, self.entity_id)

    def __hash__(self):
        return hash(self.link)


class Entity(EntityRef):
    entity_type: str
    properties: Dict

    def signature_fields(self):
        # refs just return everything they know
        for k in self.properties.keys():
            yield k

    @classmethod
    def from_search(cls, entity):
        ent = cls(origin=entity.origin, entity_id=entity.external_ref, entity_type=entity.entity_type,
                  properties=dict())
        for k in entity.signature_fields():
            ent.properties[k] = entity[k]
        return ent

    @classmethod
    def from_entity(cls, entity):
        ent = cls(origin=entity.origin, entity_id=entity.external_ref, entity_type=entity.entity_type,
                  properties=dict())
        # ent.properties.update(kwargs)  # I don't know why this was here but I don't think I want it
        for k in entity.signature_fields():
            ent.properties[k] = entity[k]

        if entity.uuid is not None and entity.uuid != entity.external_ref:
            ent.properties['uuid'] = entity.uuid
        # a bit of bleed from foreground here- but we need fragments to work-- bonus this also supports (RX) exchanges
        if hasattr(entity, 'flow'):
            ent.properties['flow'] = FlowEntity.from_flow(entity.flow)
        if hasattr(entity, 'direction'):
            ent.properties['direction'] = entity.direction

        if entity.entity_type == 'quantity':
            ent.properties['unit'] = str(ent.properties.pop('referenceUnit', entity.unit))
            ent.properties['Synonyms'] = []
            for k in ('Method', 'Category', 'Indicator', 'Synonyms'):
                if entity.has_property(k):
                    ent.properties[k] = entity[k]
        elif entity.entity_type == 'flow':
            ent.properties['referenceQuantity'] = entity.reference_entity.external_ref
            ent.properties['locale'] = entity.locale
            ent.properties['context'] = list(entity.context)
            ent.properties['Synonyms'] = [t for t in entity.synonyms if t != entity['name']]  # FlowInterface.synonyms
        elif entity.entity_type == 'process':
            ent.properties['referenceExchange'] = [ReferenceExchange.from_exchange(x) for x in entity.reference_entity]

        return ent

    @classmethod
    def from_flow(cls, flow):
        ent = cls.from_entity(flow)
        ent.properties['locale'] = flow.locale
        ent.properties['context'] = list(flow.context)
        return ent

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

    def serialize(self):
        """
        this simulates LcEntity.serialize()
        :return:
        """
        j = {

            'entityType': self.entity_type,
            'externalId': self.entity_id,
            'origin': self.origin
        }
        for k, v in self.properties.items():
            if k in ('is_lcia_method', 'uuid'):
                continue
            elif k == 'unit':
                j['referenceUnit'] = v
            else:
                j[k] = v
        return j


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
        if entity.reference_entity:
            obj.properties[entity.reference_field] = entity.reference_entity.external_ref
        obj.properties['unit'] = entity.unit
        obj.properties['Synonyms'] = []

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
        ExchangeModel formerly included a FlowSpec instead of a flow-- but now it includes a FlowEntity
        :param ex:
        :return:
        """
        return cls(origin=ex.origin, entity_id=ex.flow.external_ref, entity_type='flow', context=ex.flow.context,
                   locale=ex.flow.locale, properties=ex.flow.properties)

    def serialize(self):
        j = super(FlowEntity, self).serialize()
        j['context'] = self.context
        j['locale'] = self.locale
        return j


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
    origin: Optional[str] = None
    external_ref: Optional[str] = None
    flowable: str
    quantity_ref: str
    context: List[str]
    locale: str

    @classmethod
    def from_flow(cls, flow):
        return cls(origin=flow.origin, external_ref=flow.external_ref, flowable=flow.name,
                   quantity_ref=flow.reference_entity.external_ref,
                   context=list(flow.context), locale=flow.locale)

    @classmethod
    def from_termination(cls, term):
        return cls(origin=term.term_flow.origin, external_ref=term.term_flow.external_ref, flowable=term.term_flow.name,
                   quantity_ref=term.term_flow.reference_entity.external_ref,
                   context=list(term.term_node), locale=term.term_flow.locale)

    @classmethod
    def from_exchange(cls, x, locale=None):
        if x.type == 'context':
            cx = list(x.termination)
        elif x.type in ('reference', 'cutoff'):
            cx = []
        else:
            raise TypeError('%s\nUnknown exchange type %s' % (x, x.type))
        loc = locale or x.flow.locale
        return cls(origin=x.flow.origin, external_ref=x.flow.external_ref, flowable=x.flow.name,
                   quantity_ref=x.flow.reference_entity.external_ref,
                   context=cx, locale=loc)


class DirectedFlow(ResponseModel):
    flow: FlowSpec
    direction: str

    @property
    def origin(self):
        return self.flow.origin

    @property
    def external_ref(self):
        return self.flow.external_ref

    @property
    def quantity_ref(self):
        return self.flow.quantity_ref

    @property
    def name(self):
        return self.flow.flowable

    @classmethod
    def from_observed(cls, obj):
        return cls(flow=FlowSpec.from_flow(obj.flow), direction=obj.direction)


class ExteriorFlow(DirectedFlow):
    """
    An ExteriorFlow is essentially a row in the LCI Environment `B` matrix. It consists of a directed flow,
    enhanced with a context. Now I know a flow already has a context, but (a) context is not required for a flow and
    (b) flows can be terminated to contexts other than their 'default'
    """
    context: List[str]

    @property
    def termination(self):
        return self.context

    @classmethod
    def from_background(cls, flow, direction, context):
        if hasattr(context, 'entity_type'):
            if context.entity_type == 'context':
                cx = context.as_list()
            else:
                raise TypeError('supplied Context %s (type %s)' % (context, context.entity_type))
        elif context is None:
            cx = []
        else:
            cx = list(context)
        return cls(flow=FlowSpec.from_flow(flow), direction=direction, context=cx)

    @classmethod
    def from_exterior(cls, obj):
        if obj.type == 'context':
            context = obj.termination.as_list()
        elif obj.type == 'cutoff':
            context = []
        else:
            raise TypeError('exchange is not exterior (type %s)' % obj.type)
        return cls(flow=FlowSpec.from_exchange(obj), direction=obj.direction, context=context)


class Exchange(ResponseModel):
    """
    Do we need to add locale?? no it's in the flow entity
    """
    origin: str
    process: str
    flow: FlowEntity
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
        return cls(origin=x.process.origin, process=x.process.external_ref, flow=FlowEntity.from_flow(x.flow),
                   direction=x.direction, termination=term, context=cx, type=x.type, comment=x.comment, str=str(x),
                   **kwargs)


class ReferenceExchange(Exchange):
    is_reference: bool = True
    termination: None

    @classmethod
    def from_exchange(cls, x, **kwargs):
        if x.termination is not None:
            cx = list(x.termination)
        else:
            cx = None
        return cls(origin=x.process.origin, process=x.process.external_ref, flow=FlowEntity.from_flow(x.flow),
                   direction=x.direction, termination=None, context=cx, type=x.type, comment=x.comment, str=str(x),
                   **kwargs)


class ReferenceValue(ReferenceExchange):
    value: float = 0.0

    @classmethod
    def from_rx(cls, x):
        return cls.from_exchange(x, value=x.value)


class ExchangeValues(Exchange):
    """
    dict mapping reference flows to allocated value
    This should really be called ExchangeValues- in fact the method is already called exchangeValues!
    """
    values: Dict
    uncertainty: Optional[Dict] = None

    @classmethod
    def from_ev(cls, x):
        return cls.from_exchange(x, values=x.values)


class UnallocatedExchange(Exchange):
    is_reference: bool = False
    value: float
    uncertainty: Optional[Dict] = None

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
    uncertainty: Optional[Dict] = None

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
     - None: generate all exchanges
     - 'interior'
     - 'exterior'
     - 'cutoff'

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
    ref_unit: Optional[str] = None
    query_quantity: str
    query_unit: Optional[str] = None
    context: List[str]
    value: Dict

    @classmethod
    def from_cf(cls, cf):
        ch = cls.null(cf)
        for loc in cf.locations:
            ch.value[loc] = cf[loc]
        return ch

    @classmethod
    def from_cfs(cls, cfs):
        rq = set(k.ref_quantity for k in cfs)
        qq = set(k.quantity for k in cfs)
        fb = set(k.flowable for k in cfs)
        if len(rq) + len(qq) + len(fb) != 3:
            raise ValueError('disagreeable CFs')
        ch = cls.null(cfs[0])
        for cf in cfs:
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


class FlowFactors(ResponseModel):
    """
    Client POSTs a list of FlowSpecs; server returns a list of characterizations that match the specs, grouped
    by flow external_ref (so as to be cached in the flow's chars_seen).

    The challenge here is with contexts: in order for lookup_cf to find the CF, it needs to be cached with a
    local context; but in order for the results to be portable/reproducible, the QR results should report the
    canonical contexts.  So, we add a context field where we reproduce the posted context.
    """
    origin: str
    external_ref: str
    context: List[str]
    factors: List[QuantityConversion]

    def add_qr_result(self, qrr):
        self.factors.append(QuantityConversion.from_qrresult(qrr))


class AggregatedLciaScore(ResponseModel):
    origin: str
    entity_id: str
    component: str
    result: float


class SummaryLciaScore(AggregatedLciaScore):
    node_weight: Optional[float]
    unit_score: Optional[float]

    def __str__(self):
        def number(arg):
            if arg is None:
                return 'None'
            return '%10.3g' % float(arg)

        return 'S%8.3g = %-s x %-s | %s' % (self.result, number(self.node_weight),
                                            number(self.unit_score),
                                            self.component)


class LciaDetail(ResponseModel):
    exchange: Optional[ExteriorFlow]
    factor: QuantityConversion
    result: float

    @classmethod
    def from_detailed_lcia_result(cls, d):
        return cls(exchange=ExteriorFlow.from_exterior(d.exchange),
                   factor=QuantityConversion.from_qrresult(d.factor),
                   result=d.result)


class DisaggregatedLciaScore(AggregatedLciaScore):
    details: List[LciaDetail] = []

    '''
    :meta exclude:
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
        return cls(origin=origin, entity_id=entity_id, component=component, result=c.cumulative_result,
                   details=[LciaDetail.from_detailed_lcia_result(d) for d in
                            sorted(c.details(), key=lambda x: x.result, reverse=True)])
    '''


class LciaResult(ResponseModel):
    """
    Note that a core LciaResult can contain either (detailed) components or summaries, but not both.
    """
    scenario: Optional[str]
    object: str
    quantity: Entity
    scale: float
    total: float

    components: List[DisaggregatedLciaScore] = []
    summaries: List[SummaryLciaScore] = []

    @classmethod
    def from_lcia_result(cls, obj, res):
        return cls(scenario=res.scenario, object=obj.name, quantity=Entity.from_entity(res.quantity), scale=res.scale,
                   total=res.total())

    @classmethod
    def summary(cls, obj, res):
        return cls(scenario=res.scenario, object=obj.name, quantity=Entity.from_entity(res.quantity), scale=res.scale,
                   total=res.total(), summaries=res.serialize_components(detailed=False))

    @classmethod
    def detailed(cls, obj, res):
        return cls(scenario=res.scenario, object=obj.name, quantity=Entity.from_entity(res.quantity), scale=res.scale,
                   total=res.total(), components=res.serialize_components(detailed=True))
