import unittest

from ..flow_ref import FlowRef


class _DummyQuery(object):
    origin = 'test.origin'

    def validate(self):
        return True

    def get_item(self, entity, item):
        raise KeyError(item)



class FlowRefTest(unittest.TestCase):
    def test_flow_ref(self):
        fr = FlowRef('dummy_flow_2345', _DummyQuery())
        self.assertEqual(fr.link, 'test.origin/dummy_flow_2345')

    def test_flow_name(self):
        fr = FlowRef('dummy_flow_6789', _DummyQuery(), name='A dummy flow')
        self.assertEqual(fr.name, 'A dummy flow')

    def test_flow_loc(self):
        fr = FlowRef('dummy_flow_4567', _DummyQuery(), name='A dummy flow, AT')
        self.assertEqual(fr.name, 'A dummy flow, AT')
        self.assertIn('A dummy flow', list(fr.synonyms))
        self.assertEqual(fr.locale, 'AT')

    def test_flow_nonloc(self):
        fr = FlowRef('dummy_flow_4567', _DummyQuery(), name='A dummy flow, ZZZZ')
        self.assertEqual(fr.name, 'A dummy flow, ZZZZ')
        self.assertNotIn('A dummy flow', list(fr.synonyms))
        self.assertEqual(fr.locale, 'GLO')


if __name__ == '__main__':
    unittest.main()
