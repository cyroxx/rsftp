from pprint import pformat
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.internet.ssl import ClientContextFactory
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers


class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            print 'Some data received:'
            print display
            self.remaining -= len(display)

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.finished.callback(None)

class WebClientContextFactory(ClientContextFactory):
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)

def display(response):
    print "Received response"
    print response

contextFactory = WebClientContextFactory()
agent = Agent(reactor, contextFactory)

def ask():
    d = agent.request(
        'GET',
        'https://heahdk.net/storage/cyroxx/public/',
        #'http://www.google.de',
        Headers({'User-Agent': ['Twisted Web Client Example']}),
        None)
    
    def cbRequest(response):
        print 'Response type:', type(response)
        print 'Response version:', response.version
        print 'Response code:', response.code
        print 'Response phrase:', response.phrase
        print 'Response headers:'
        print pformat(list(response.headers.getAllRawHeaders()))
        d = readBody(response)
        d.addCallback(cbBody)
        return d
    
    def cbBody(body):
        print 'Response body:'
        print body
        return body
    
    d.addCallback(cbRequest)
    
    return d