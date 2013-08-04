from twisted.internet import defer

import treq

from filepath import RSFilePath

def handleResponse(response):
    #print response.code, response.phrase
    return response

class RSClient(object):
    def list(self, path, keys=()):
        
        def parse_results(json):
            results = []
            for key, value in json.iteritems():
                is_directory = key.endswith('/')
                current_version = value
                
                md = {
                      'size': 0L if is_directory else 2139L,
                      'directory': is_directory,
                      'permissions': 16895 if is_directory else 33206,
                      'hardlinks': 0,
                      # FIXME: we assume unreasonably that current_version is a numeric timestamp
                      'modified': current_version/1000,
                      'owner': '0',
                      'group': '0'}
                
                meta = [md[k] for k in keys]
                results.append( (key, meta) )
            
            return results
            
        uri = 'https://heahdk.net/storage/cyroxx/public/'
        d = treq.get(uri)
        d.addCallback(handleResponse)
        d.addCallback(treq.json_content)
        d.addCallback(parse_results)
        
        return d
    