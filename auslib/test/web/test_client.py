import mock
import unittest
from xml.dom import minidom

from auslib.web.base import app, AUS
from auslib.web.views.client import ClientRequestView

class ClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Error handlers are removed in order to give us better debug messages
        cls.error_spec = app.error_handler_spec
        # Ripped from https://github.com/mitsuhiko/flask/blob/1f5927eee2288b4aaf508af5dc1f148aa2140d91/flask/app.py#L394
        app.error_handler_spec = {None: {}}

    @classmethod
    def tearDownClass(cls):
        app.error_handler_spec = cls.error_spec

    def setUp(self):
        app.config['DEBUG'] = True
        AUS.setDb('sqlite:///:memory:')
        AUS.db.create()
        AUS.db.setDomainWhitelist('a.com')
        self.client = app.test_client()
        self.view = ClientRequestView()
        AUS.rules.t.insert().execute(backgroundRate=100, mapping='b', update_type='minor', product='b', data_version=1)
        AUS.releases.t.insert().execute(name='b', product='b', version='1.0', data_version=1, data="""
{
    "name": "b",
    "schema_version": 1,
    "appv": "1.0",
    "extv": "1.0",
    "hashFunction": "sha512",
    "platforms": {
        "p": {
            "buildID": "2",
            "locales": {
                "l": {
                    "complete": {
                        "filesize": "3",
                        "from": "*",
                        "hashValue": "4",
                        "fileUrl": "http://a.com/z"
                    }
                }
            }
        }
    }
}
""")
        AUS.rules.t.insert().execute(backgroundRate=100, mapping='c', update_type='minor', product='c',
                                     distribution='default', data_version=1)
        AUS.releases.t.insert().execute(name='c', product='c', version='10.0', data_version=1, data="""
{
    "name": "c",
    "schema_version": 1,
    "appv": "10.0",
    "extv": "10.0",
    "hashFunction": "sha512",
    "platforms": {
        "p": {
            "buildID": "11",
            "locales": {
                "l": {
                    "complete": {
                        "filesize": "12",
                        "from": "*",
                        "hashValue": "13",
                        "fileUrl": "http://a.com/y"
                    }
                }
            }
        }
    }
}
""")
        AUS.rules.t.insert().execute(backgroundRate=100, mapping='d', update_type='minor', product='d', data_version=1)
        AUS.releases.t.insert().execute(name='d', product='d', version='20.0', data_version=1, data="""
{
    "name": "d",
    "schema_version": 1,
    "appv": "20.0",
    "extv": "20.0",
    "hashFunction": "sha512",
    "platforms": {
        "p": {
            "buildID": 21,
            "locales": {
                "l": {
                    "complete": {
                        "filesize": 22,
                        "from": "*",
                        "hashValue": "23",
                        "fileUrl": "http://evil.com/y"
                    }
                }
            }
        }
    }
}
""")

        AUS.rules.t.insert().execute(backgroundRate=100, mapping='e', update_type='minor', product='e', data_version=1)
        AUS.releases.t.insert().execute(name='e', product='e', version='22.0', data_version=1, data="""
{
    "name": "e",
    "schema_version": 1,
    "hashFunction": "sha512",
    "platforms": {
        "p": {
            "buildID": 25,
            "locales": {
                "l": {
                    "complete": {
                        "filesize": 22,
                        "from": "*",
                        "hashValue": "23",
                        "fileUrl": "http://a.com/y"
                    }
                }
            }
        }
    }
}
""")

        AUS.rules.t.insert().execute(backgroundRate=100, mapping='f', update_type='minor', product='f', data_version=1)
        AUS.releases.t.insert().execute(name='f1', product='f', version='22.0', data_version=1, data="""
{
    "name": "f1",
    "schema_version": 3,
    "platforms": {
        "p": {
            "buildID": 5
        }
    }
}
""")
        AUS.releases.t.insert().execute(name='f2', product='f', version='23.0', data_version=1, data="""
{
    "name": "f2",
    "schema_version": 3,
    "platforms": {
        "p": {
            "buildID": 6
        }
    }
}
""")
        AUS.releases.t.insert().execute(name='f3', product='f', version='25.0', data_version=1, data="""
{
    "name": "f3",
    "schema_version": 3,
    "hashFunction": "sha512",
    "platforms": {
        "p": {
            "buildID": 29,
            "locales": {
                "l": {
                    "partials": [
                        {
                            "filesize": 2,
                            "from": "f1",
                            "hashValue": 3,
                            "fileUrl": "http://a.com/p1"
                        },
                        {
                            "filesize": 4,
                            "from", "f2",
                            "hashValue": 5,
                            "fileUrl": "http://a.com/p2"
                    ],
                    "completes": [
                        {
                            "filesize": 30,
                            "from": "*",
                            "hashValue": "31",
                            "fileUrl": "http://a.com/y"
                        }
                    ]
                }
            }
        }
    }
}
""")

    def testGetHeaderArchitectureWindows(self):
        self.assertEqual(self.view.getHeaderArchitecture('WINNT_x86-msvc', 'Firefox Intel Windows'), 'Intel')

    def testGetHeaderArchitectureMacIntel(self):
        self.assertEqual(self.view.getHeaderArchitecture('Darwin_x86-gcc3-u-ppc-i386', 'Firefox Intel Mac'), 'Intel')

    def testGetHeaderArchitectureMacPPC(self):
        self.assertEqual(self.view.getHeaderArchitecture('Darwin_ppc-gcc3-u-ppc-i386', 'Firefox PPC Mac'), 'PPC')

    def testDontUpdateToYourself(self):
        ret = self.client.get('/update/3/b/1.0/2/p/l/a/a/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

    def testDontUpdateBackwards(self):
        ret = self.client.get('/update/3/b/1.0/5/p/l/a/a/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

    def testDontDecreaseVersion(self):
        ret = self.client.get('/update/3/c/15.0/1/p/l/a/a/default/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

    def testVersion3Get(self):
        ret = self.client.get('/update/3/a/1.0/1/a/a/a/a/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        # An empty update contains an <updates> tag with a newline, which is what we're expecting here
        self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

    def testVersion3GetWithUpdate(self):
        ret = self.client.get('/update/3/b/1.0/1/p/l/a/a/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        # We need to load and re-xmlify these to make sure we don't get failures due to whitespace differences.
        returned = minidom.parseString(ret.data)
        expected = minidom.parseString("""<?xml version="1.0"?>
<updates>
    <update type="minor" version="1.0" extensionVersion="1.0" buildID="2">
        <patch type="complete" URL="http://a.com/z" hashFunction="sha512" hashValue="4" size="3"/>
    </update>
</updates>
""")
        self.assertEqual(returned.toxml(), expected.toxml())

    def testVersion2Get(self):
        ret = self.client.get('/update/2/b/1.0/0/p/l/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        # We need to load and re-xmlify these to make sure we don't get failures due to whitespace differences.
        returned = minidom.parseString(ret.data)
        expected = minidom.parseString("""<?xml version="1.0"?>
<updates>
    <update type="minor" version="1.0" extensionVersion="1.0" buildID="2">
        <patch type="complete" URL="http://a.com/z" hashFunction="sha512" hashValue="4" size="3"/>
    </update>
</updates>
""")
        self.assertEqual(returned.toxml(), expected.toxml())

    def testVersion2GetIgnoresRuleWithDistribution(self):
        ret = self.client.get('/update/2/c/10.0/1/p/l/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        # We need to load and re-xmlify these to make sure we don't get failures due to whitespace differences.
        self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

    def testVersion4Get(self):
        ret = self.client.get('/update/4/b/1.0/1/p/l/a/a/a/a/1/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        # We need to load and re-xmlify these to make sure we don't get failures due to whitespace differences.
        returned = minidom.parseString(ret.data)
        expected = minidom.parseString("""<?xml version="1.0"?>
<updates>
    <update type="minor" version="1.0" extensionVersion="1.0" buildID="2">
        <patch type="complete" URL="http://a.com/z" hashFunction="sha512" hashValue="4" size="3"/>
    </update>
</updates>
""")
        self.assertEqual(returned.toxml(), expected.toxml())

    def testGetURLNotInWhitelist(self):
        ret = self.client.get('/update/3/d/20.0/1/p/l/a/a/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

    def testEmptySnippetMissingExtv(self):
        ret = self.client.get('/update/3/e/20.0/1/p/l/a/a/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

    def testRobotsExists(self):
        ret = self.client.get('/robots.txt')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/plain')
        self.assertTrue('User-agent' in ret.data)

    def testSchema3MultiplePartials(self):
        ret = self.client.get('/update/3/f/22.0/5/p/l/a/a/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        # We need to load and re-xmlify these to make sure we don't get failures due to whitespace differences.
        returned = minidom.parseString(ret.data)
        expected = minidom.parseString("""<?xml version="1.0"?>
<updates>
    <update type="minor" displayVersion="25.0" appVersion="25.0" platformVersion="25.0" buildID="29">
        <patch type="partial" URL="http://a.com/p1" hashFunction="sha512" hashValue="3" size="2"/>
        <patch type="complete" URL="http://a.com/y" hashFunction="sha512" hashValue="31" size="30"/>
    </update>
</updates>
""")
        self.assertEqual(returned.toxml(), expected.toxml())

        ret = self.client.get('/update/3/f/23.0/6/p/l/a/a/a/a/update.xml')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        # We need to load and re-xmlify these to make sure we don't get failures due to whitespace differences.
        returned = minidom.parseString(ret.data)
        expected = minidom.parseString("""<?xml version="1.0"?>
<updates>
    <update type="minor" displayVersion="25.0" appVersion="25.0" platformVersion="25.0" buildID="29">
        <patch type="partial" URL="http://a.com/p1" hashFunction="sha512" hashValue="3" size="2"/>
        <patch type="complete" URL="http://a.com/y" hashFunction="sha512" hashValue="31" size="30"/>
    </update>
</updates>
""")
        self.assertEqual(returned.toxml(), expected.toxml())


class ClientTestWithErrorHandlers(unittest.TestCase):
    """Most of the tests are run without the error handler because it gives more
       useful output when things break. However, we still need to test that our
       error handlers works!"""
    def setUp(self):
        app.config['DEBUG'] = True
        AUS.setDb('sqlite:///:memory:')
        AUS.db.create()
        AUS.db.setDomainWhitelist('a.com')
        self.client = app.test_client()
        self.view = ClientRequestView()

    def testEmptySnippetOn404(self):
        ret = self.client.get('/whizzybang')
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.mimetype, 'text/xml')
        self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

    def testEmptySnippetOn500(self):
        with mock.patch('auslib.web.views.client.ClientRequestView.get') as m:
            m.side_effect = Exception('I break!')
            ret = self.client.get('/update/4/b/1.0/1/p/l/a/a/a/a/1/update.xml')
            self.assertEqual(ret.status_code, 200)
            self.assertEqual(ret.mimetype, 'text/xml')
            self.assertEqual(minidom.parseString(ret.data).getElementsByTagName('updates')[0].firstChild.nodeValue, '\n')

