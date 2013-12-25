from twisted.internet import defer
from twisted.web._newclient import ResponseDone
from twisted.python.failure import Failure

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
