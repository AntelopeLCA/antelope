"""
The FlowableInterface and QuantityInterface is for flowable objects that can be indexed by a flowable/quantity database,
  and quantity objects that report the extent of flowable objects.

The requirements are defined by usage in the TermManager

QuantityInterface:
 - quantity_terms() which generates synonyms for the quantity
 - unit() which returns a string
 - link, returns a string

Basically, it needs:
 - a reference_entity property, which satisfies the QuantityInterface
 - name and link properties, both of which return strings
 - a context property, which returns a tuple
"""

class FlowableInterface(object):
    @property
    def name(self):
        raise NotImplemented

    @property
    def link(self):
        raise NotImplemented

    @property
    def synonyms(self):
        yield self.name
        yield self.link

