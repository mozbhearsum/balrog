import simplejson as json
import mock
import unittest
from xml.dom import minidom

from auslib.AUS import AUS
from auslib.blob import ReleaseBlobV1, ReleaseBlobV2

def RandomAUSTest(AUS, backgroundRate, force, mapping):
    with mock.patch('auslib.db.Rules.getRulesMatchingQuery') as m:
        m.return_value=[dict(backgroundRate=backgroundRate, priority=1, mapping=mapping, update_type='minor')]

        results = AUS.rand.getRange()
        resultsLength = len(results)
        def se(*args, **kwargs):
            return results.pop()
        with mock.patch('auslib.AUS.AUSRandom.getInt') as m2:
            m2.side_effect = se
            served = 0
            tested = 0
            while len(results) > 0:
                updateQuery = dict(
                    channel='foo', force=force, buildTarget='a', buildID='0',
                    locale='a', version='1.0'
                )
                r, _ = AUS.evaluateRules(updateQuery)
                tested +=1
                if r:
                    served += 1
                # bail out if we're not asking for any randint's
                if resultsLength == len(results):
                    break
            return (served, tested)

class TestAUSThrottling(unittest.TestCase):
    def setUp(self):
        self.AUS = AUS()
        self.AUS.setDb('sqlite:///:memory:')
        self.AUS.db.create()
        self.AUS.db.releases.t.insert().execute(name='b', product='b', version='b', data_version=1, data='{"name": "b", "extv": "1.0", "schema_version": 1, "platforms": {"a": {"buildID": "1", "locales": {"a": {}}}}}')

    def testThrottling100(self):
        (served, tested) = RandomAUSTest(self.AUS, backgroundRate=100, force=False, mapping='b')
        self.assertEqual(served, 1)
        self.assertEqual(tested, 1)

    def testThrottling50(self):
        (served, tested) = RandomAUSTest(self.AUS, backgroundRate=50, force=False, mapping='b')
        self.assertEqual(served,  50)
        self.assertEqual(tested, 100)

    def testThrottling25(self):
        (served, tested) = RandomAUSTest(self.AUS, backgroundRate=25, force=False, mapping='b')
        self.assertEqual(served,  25)
        self.assertEqual(tested, 100)

    def testThrottlingZero(self):
        (served, tested) = RandomAUSTest(self.AUS, backgroundRate=0, force=False, mapping='b')
        self.assertEqual(served,   0)
        self.assertEqual(tested, 100)

    def testThrottling25WithForcing(self):
        (served, tested) = RandomAUSTest(self.AUS, backgroundRate=25, force=True, mapping='b')
        self.assertEqual(served, 1)
        self.assertEqual(tested, 1)
