from twisted.internet import defer
from twisted.web._newclient import Response
from twisted.web._newclient import ResponseDone
from twisted.python.failure import Failure
from twisted.web import http_headers

from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport

import treq
import rs

list_response = """
{

    "pictures/": 1369068087582,
    "test.txt": 1369069155472

}
"""

list_response_non_numeric = """
{

    "pictures/": "foobarbaz",
    "test.txt": "bozbangbol"

}
"""


class FakeResponse(object):

    code = 200
    phrase = "OK"

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def deliverBody(self, protocol):
        reason = Failure(ResponseDone("Response body fully received"))

        protocol.connectionMade()
        protocol.dataReceived(self.body)
        protocol.connectionLost(reason)


def mock_get(uri, **kwargs):
    response = FakeResponse(list_response)
    return defer.succeed(response)


def fakeListResponseNonNumeric(uri, **kwargs):
    response = FakeResponse(list_response_non_numeric)
    return defer.succeed(response)


def fakeGet404(uri, **kwargs):
    response = FakeResponse('')

    response.code = 404
    response.phrase = "Not Found"

    return defer.succeed(response)


class RSFilePathTestCase(TestCase):
    def setUp(self):
        self.test = rs.RSFilePath('https://example.com/public/')

    def tearDown(self):
        pass

    def test_child(self):
        self.patch(treq, 'get', mock_get)

        name = 'pictures'
        d = self.test.child(name)

        def cbChild(childPath):
            self.assertEqual(childPath.path, 'https://example.com/public/pictures/')

        d.addCallback(cbChild)

        return d

    def test_childNonExistentPath(self):
        self.patch(treq, 'get', fakeGet404)

        name = 'doesnotexist/'
        d = self.test.child(name)

        return self.assertFailure(d, rs.filepath.NotFoundError)

    def test_listNonNumericVersionNumber(self):
        self.patch(treq, 'get', fakeListResponseNonNumeric)

        keys = ('modified',)
        d = self.test.ftp_list(keys)

        def cbList(results):
            self.assertEqual(results[0][1][0], 0)   # results[0] = ('pictures/', (0,))
            self.assertEqual(results[1][1][0], 0)   # results[1] = ('test.txt', (0,))

        d.addCallback(cbList)

        return d
