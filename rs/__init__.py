import treq

class RSClient(object):
    def list(self):
        uri = 'https://heahdk.net/storage/cyroxx/public/'
        d = treq.get(uri)
        
        def dummy(response):
            #print response
            pass
            
        d.addCallback(dummy)
        
        return d
    