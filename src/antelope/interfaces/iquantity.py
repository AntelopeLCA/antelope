"""
It's taken me a long time to figure out how the quantity interface should work, but it is finally coming together.

There are two quantitative relations common to all LCA implementations, which I have named the exchange relation and
the quantity relation.  The first relates magnitudes of flows to one another through a particular process or activity,
and includes essentially all inventory modeling.  The second relates magnitudes of quantities to one another through
a particular flow in a particular context / locale, and includes both quantity conversion (e.g. kg to MJ) and LCIA.

The quantity interface is meant to capture that entire second group. The core of it is the 'quantity relation', which
is a function that maps (flowable, reference quantity, query quantity, context, locale) => a real number

Of course, the quantity_relation can be messy "under the hood": the key question in designing the interface is how to
expose "fuzzy" matches to the user: matches that require reference quantity conversion, use of a proxy locale, or when
there are multiple matches (i.e. inexact or proxy flowable or context)

There are also multiple forms for the response to take: pure numeric (or numeric with uncertainty in some fantasy
future world), as a characterization factor or QuantityConversion object, as an LCIA Result object.

The proposed model for the quantity interface is as follows:

 QRResult interface: has properties 'flowable', 'ref', 'query', 'context', 'value', 'locale', 'origin'
 QuantityConversion includes sequential QRResults and masks locale and origin

 cf (flow[able], query quantity, ref quantity=None, context=None, locale='GLO', strategy='first')
     => number.  quantity_relation(*).value = cf(:) (except the args are not in the same order)
        amount of the query quantity that corresponds to a unit of the ref quantity
 quantity_relation (flowable, ref quantity, query quantity, context, locale='GLO', strategy='first')
     =>  single QRresult, chosen by named strategy.
 quantity_conversions (flow[able], query quantity, ref quantity=None, context=None, locale='GLO') "comprehensive"
     => [list of valid results (flowable / context proxies),
         list of geographic proxies,
         list of mismatched results (ref quantity conversion error]
 do_lcia(query quantity, exchanges iterable, locale='GLO')
     => LciaResult object, with a detail for each exchange item.  locale is used if it is more specific than the

For cf and QuantityConversion, 'flowable' could be replaced with a flow entity, from which would be taken ref quantity
and context.  If ref quantity is not supplied, nor is flow an entity, QuantityConversion will return all valid results
and cf() will fail.  For the Quantity Relation, all 4 core arguments are explicitly required (locale still optional).

Additional methods:

 profile (flow[able], ref_quantity=None, context=None)
     => sequence of cfs from quantity conversions for all characterized quantities for the flow[able]
 factors (quantity, flowable=None, ref_quantity=None, context=None)
     => sequence of characterizations for the named quantity, optionally filtered by flowable and/or compartment,
        optionally converted to the named reference
"""

from .abstract_query import AbstractQuery


class QuantityRequired(Exception):
    pass


class NoFactorsFound(Exception):
    pass


class ConversionReferenceMismatch(Exception):
    pass


class FlowableMismatch(Exception):
    pass


_interface = 'quantity'


class QuantityInterface(AbstractQuery):
    """
    QuantityInterface
    """
    '''
    qdb- and native-level queries
    '''

    def profile(self, flow, **kwargs):
        """
        Generate characterizations for the named flow or flowable, with the reference quantity noted in each case
        :param flow:
        :return: list of characterizations
        """
        return self._perform_query(_interface, 'profile', QuantityRequired,
                                   flow, **kwargs)

    def characterize(self, flowable, ref_quantity, query_quantity, value, context=None, location='GLO', **kwargs):
        """
        Add Characterization data for a flowable, reporting the amount of a query quantity that is equal to a unit
        amount of a reference quantity, for a given context and location.

        At the native level, this is only used internally. At the qdb level there is basically no reason to use it--
        characterizations should only get added via import_cfs() which is part of get_canonical()

        :param flowable: string or flow external ref
        :param ref_quantity: string or external ref
        :param query_quantity: string or external ref
        :param value: float or dict of locations to floats
        :param context: string
        :param location: string, ignored if value is dict
        :param kwargs: overwrite=False, origin=query_quantity.origin, others?
        :return: new or updated characterization
        """
        return self._perform_query(_interface, 'characterize', QuantityRequired,
                                   flowable, ref_quantity, query_quantity, value,
                                   context=context, location=location, **kwargs)

    def factors(self, quantity, flowable=None, context=None, **kwargs):
        """
        Return characterization factors for the given quantity, subject to optional flowable and context
        filter constraints. This is ill-defined because the reference unit is not explicitly reported in current
        serialization for characterizations (it is implicit in the flow)-- but it can be added as a keyword.
        :param quantity:
        :param flowable:
        :param context:
        :return: a generator of Characterizations
        """
        return self._perform_query(_interface, 'factors', QuantityRequired,
                                   quantity, flowable=flowable, context=context, **kwargs)

    def cf(self, flow, quantity, ref_quantity=None, context=None, locale='GLO', strategy=None, **kwargs):
        """
        Determine a characterization factor value for a given quantity
        :param flow: flow entity ref or flowable string
        :param quantity:
        :param ref_quantity: [None] if flow is entity, flow.reference_entity is used unless specified
        :param context: [None] if flow is entity, flow.context is used
        :param locale: ['GLO']
        :param strategy: [None] TBD by implementation
        :param kwargs:
        :return: a float
        """
        return self._perform_query(_interface, 'cf', QuantityRequired, flow, quantity,
                                   ref_quantity=ref_quantity, context=context, locale=locale, strategy=strategy,
                                   **kwargs)

    def quantity_relation(self, flowable, ref_quantity, query_quantity, context, locale='GLO', **kwargs):
        """
        Return a single number that converts the a unit of the reference quantity into the query quantity for the
        given flowable, compartment, and locale (default 'GLO').  If no locale is found, this would be a great place
        to run a spatial best-match algorithm.
        :param flowable:
        :param ref_quantity:
        :param query_quantity:
        :param context:
        :param locale: ['GLO']
        :return: a QrResult
        """
        return self._perform_query(_interface, 'quantity_relation', QuantityRequired,
                                   flowable, ref_quantity, query_quantity, context, locale=locale, **kwargs)

    def do_lcia(self, quantity, inventory, locale='GLO', **kwargs):
        """
        Successively implement the quantity relation over an iterable of exchanges.
        we should probably generalize this to automatically expect a list of results, to support running whole
        methodologies. This is now supported in antelope_foreground and xdb.

        :param quantity:
        :param inventory:
        :param locale:
        :param kwargs:
        :return: an LciaResult whose components are processes encountered in the inventory
        """
        return self._perform_query(_interface, 'do_lcia', QuantityRequired,
                                   quantity, inventory, locale=locale, **kwargs)

    def lcia(self, process, ref_flow, quantity_ref, **kwargs):
        """
        Perform process foreground LCIA for the given quantity reference.  Included for compatibility with antelope v1.
        In this query, the inventory is computed remotely; whereas with quantity.do_lcia() inventory knowledge is
        required

        The way we imagine this working in the days of future XDB/QDB:
         - it's not foreground LCIA at all, it's encapsulated LCIA
         - it's not part of the quantity interface, it's part of the basic interface
         - it requires background data implemented at the server, even if the client is denied background authorization
           (hence the basic interface)
         - either the quantity ref must be known locally or resolvable to a do_lcia operation by the catalog
         - there is also the implied need for sys_lcia which is a POST operation that uses sys_lci

        It needs to be rewritten.

        :param process:
        :param ref_flow:
        :param quantity_ref:
        :param kwargs:
        :return: an LciaResult whose components are flows
        """
        return self._perform_query(_interface, 'lcia', QuantityRequired,
                                   process, ref_flow, quantity_ref, **kwargs)

    '''
    def fragment_lcia(self, fragment, quantity_ref, scenario=None, **kwargs):
        """
        Perform fragment LCIA by first traversing the fragment to determine node weights, and then combining with
        unit scores.
        Not sure whether this belongs in Quantity or Foreground. but probably foreground.
        :param fragment:
        :param quantity_ref:
        :param scenario:
        :param kwargs:
        :return: an LciaResult whose components are FragmentFlows
        """
        return self._perform_query(_interface, 'fragment_lcia', QuantityRequired,
                                   fragment, quantity_ref, scenario, **kwargs)
    '''

    def norm(self, quantity_ref, region=None, **kwargs):
        """
        Return a normalization factor for the named quantity ref, as a single number.
        :param quantity_ref:
        :param region: not well supported
        :param kwargs:
        :return: a floating-point number, which is 0.0 if no normalisationFactors (OpenLCA spec) are available.
        """
        return self._perform_query(_interface, 'norm', QuantityRequired,
                                   quantity_ref, region=region, **kwargs)

    '''
    core required functionality
    NOTE: a foreground interface must have access to a qdb to run get_canonical
    def new_quantity(self, name, ref_unit=None, **kwargs):
        """
        Creates a new quantity entity and adds it to the foreground
        :param name:
        :param ref_unit:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'new_quantity', QuantityRequired,
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
        return self._perform_query(_interface, 'new_flow', QuantityRequired,
                                   name, ref_quantity=ref_quantity, context=context,
                                   **kwargs)

    '''
    '''
    qdb-only queries
    '''

    def get_canonical(self, quantity, **kwargs):
        """
        This is not really qdb-specific as trivial for non-qdbs.
        Retrieve a canonical quantity based on a synonym or other distinguishable term.  Canonical quantities
        include standard concepts like "mass" that have a semantic scope that is broader than LCA, and also reference
        versions of LCIA methods such as CML2001 / GWP-100. It is up to the implementation to canonicalize these.
        :param quantity: external_id of quantity
        :return: QuantityRef
        """
        return self.make_ref(self._perform_query(_interface, 'get_canonical',
                                                 QuantityRequired,
                                                 quantity, **kwargs))

    def get_factors(self, quantity, flow_specs, **kwargs):
        """
        Accept an iterable of flow specifications (either a flow UUID which is known(?) and/or (flowable, ref_quantity,
        context, locale)). Return a list of FlowFactors
        :param quantity: a query quantity
        :param flow_specs: an iterable of FlowSpec
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'get_factors', QuantityRequired,
                                   quantity, flow_specs, **kwargs)

    def flows_with_origin(self, origin, flowable=None, context=None, locale=None, **kwargs):
        """
        Return a list of flows matching the supplied characteristics
        :param origin:
        :param flowable:
        :param context:
        :param locale:
        :param kwargs:
        :return:
        """
        return self._perform_query(_interface, 'flows_with_origin', QuantityRequired,
                                   origin, flowable=flowable, context=context, locale=locale, **kwargs)

    def post_flows(self, flows):
        """
        flows_with_origin as POST/PUT/PATCH
        :param flows: iterable of inputs to f_w_o
        :return:
        """
        pass

