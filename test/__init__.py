from twisted.internet import defer

from twisted.trial.unittest import TestCase

import treq
import rs

def mock_get(uri):
    return defer.succeed('mytest-kkk')
    

class RSClientTestCase(TestCase):
    def setUp(self):
        self.test = rs.RSClient() 
        self.patch(treq, 'get', mock_get)
    
    def tearDown(self):
        pass
    
    def test_client(self):
        #return defer.succeed(None)
        
        return self.test.list()