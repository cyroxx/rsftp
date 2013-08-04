from twisted.internet import defer

import treq
from twisted.python.filepath import InsecurePath

class NotFoundError(Exception):
    pass

class PermissionDeniedError(Exception):
    pass

class RSFilePath(object):
    sep = '/'.encode("ascii")
    childinfo = None
    
    def __init__(self, path, access_token=''):
        self.path = path
        self.access_token = access_token
        
    def child(self, name):
        """
        Obtain a direct child of this file path.  The child may or may not
        exist.

        @param name: the name of a child of this path. C{name} must be a direct
            child of this path and may not contain a path separator.
        @return: the child of this path with the given C{name}.
        @raise InsecurePath: if C{name} describes a file path that is not a
            direct child of this file path.
        """
        #print "child called: ", self.path
        #print name
        
        sep = self.sep
        childinfo = self.childinfo
        
        def cbGetChildInfo(childinfo):
            child = childinfo.get(name)
            if child:
                
                # XXX maybe DRY refactor the path construction a bit more
                if child['is_directory']:
                    newpath = ''.join([self.path, name, sep])
                else:
                    newpath = ''.join([self.path, name])
                    
                return defer.succeed(self.clonePath(newpath))
            else:
                return defer.fail(InsecurePath("%r is not a child of %s" % (name, self.path)))
        
        if childinfo:
            d = defer.succeed(childinfo)
        else:
            d = self._getChildInfo()
        
        d.addCallback(cbGetChildInfo)
        return d
            
#        path = ''.join([self.path, name, sep])
#        
#        def gotResponse(response):
#            return self._handleResponse(response, path)
#        
#        d = treq.get(path)
#        d.addCallback(gotResponse)
#        
#        def cbHandleResponse(response):
#            print "child ", path
#            return RSFilePath.clone(path)
#        
#        def ebHandleResponse(failure):
#            raise InsecurePath("%r is not a child of %s" % (path, self.path))
#            #return failure
#        
#        d.addCallbacks(cbHandleResponse, ebHandleResponse)            
        
        
#        myd = defer.Deferred()
#        myd.errback(NotFoundError)
#        return d
        #raise NotImplementedError
        #return d

    def open(self, mode="r"):
        """
        Opens this file path with the given mode.

        @return: a file-like object.
        @raise Exception: if this file path cannot be opened.
        """
        raise NotImplementedError

    def changed(self):
        """
        Clear any cached information about the state of this path on disk.
        """
        raise NotImplementedError

    def getsize(self):
        """
        Retrieve the size of this file in bytes.

        @return: the size of the file at this file path in bytes.
        @raise Exception: if the size cannot be obtained.
        """
        raise NotImplementedError

    def getModificationTime(self):
        """
        Retrieve the time of last access from this file.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """
        raise NotImplementedError

    def getStatusChangeTime(self):
        """
        Retrieve the time of the last status change for this file.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """
        raise NotImplementedError

    def getAccessTime(self):
        """
        Retrieve the time that this file was last accessed.

        @return: a number of seconds from the epoch.
        @rtype: L{float}
        """
        raise NotImplementedError

    def exists(self):
        """
        Check if this file path exists.

        @return: C{True} if the file at this file path exists, C{False}
            otherwise.
        @rtype: L{bool}
        """
        print "exists called: ", self.path
        d = self._get()
        d.addCallback(self._handleResponse)
        
        dummyd = defer.succeed(True)
        return d

    def isdir(self):
        """
        Check if this file path refers to a directory.

        @return: C{True} if the file at this file path is a directory, C{False}
            otherwise.
        """
        return self.path.endswith(self.sep)

    def isfile(self):
        """
        Check if this file path refers to a regular file.

        @return: C{True} if the file at this file path is a regular file,
            C{False} otherwise.
        """
        return not self.isdir()

    def children(self):
        """
        List the children of this path object.

        @return: a sequence of the children of the directory at this file path.
        @raise Exception: if the file at this file path is not a directory.
        """
        raise NotImplementedError

    def basename(self):
        """
        Retrieve the final component of the file path's path (everything
        after the final path separator).

        @return: the base name of this file path.
        @rtype: L{str}
        """
        raise NotImplementedError

    def parent(self):
        """
        A file path for the directory containing the file at this file path.
        """
        raise NotImplementedError

    def sibling(self, name):
        """
        A file path for the directory containing the file at this file path.

        @param name: the name of a sibling of this path. C{name} must be a direct
            sibling of this path and may not contain a path separator.

        @return: a sibling file path of this one.
        """
        raise NotImplementedError
    
    def listdir(self):
        print "listdir called: ", self.path
        
        def parse_results(json):
            results = [k for k, v in json.iteritems()]
            
            return results
            
        d = self._list()
        d.addCallback(parse_results)
        
        return d
    
    def ftp_list(self, keys=()):
        def parse_results(json):
            results = []
            childinfo = {}
            for key, value in json.iteritems():
                is_directory = key.endswith('/')
                current_version = value                
                
                # try to use <current_version> info as the modified timestamp
                if isinstance( current_version, ( int, long ) ):
                    modified = current_version / 1000
                else:
                    modified = 0
                
                md = {
                      'size': 0L,
                      'directory': is_directory,
                      'permissions': 16895 if is_directory else 33206,
                      'hardlinks': 0,
                      # FIXME: we assume unreasonably that current_version is a numeric timestamp
                      'modified': modified,
                      'owner': '0',
                      'group': '0'}
                
                meta = [md[k] for k in keys]
                results.append( (key, meta) )
                
                normkey = key[:-1] if is_directory else key
                childinfo[normkey] = {'is_directory': is_directory, 'current_version': current_version}
            
            self.childinfo = childinfo 
            
            return results
        
        d = self._list()
        d.addCallback(parse_results)
        
        return d
    
    def clonePath(self, path):
        return RSFilePath(path, self.access_token)
    
    def _list(self):
        def gotResponse(response):
            return self._handleResponse(response, self.path)
        
        d = self._get()
        d.addCallback(gotResponse)
        d.addCallback(treq.json_content)
        
        return d
    
    def _getChildInfo(self):
        
        def gotListing(json):
            childinfo = {}
            
            for key, value in json.iteritems():
                is_directory = key.endswith('/')
                current_version = value
                
                normkey = key[:-1] if is_directory else key
                childinfo[normkey] = {'is_directory': is_directory, 'current_version': current_version}
            
            self.childinfo = childinfo
            
            return childinfo
        
        d = self._list()
        d.addCallback(gotListing)
        
        return d
    
    def _get(self):
        headers = None
        if self.access_token:
            headers = {'Authorization': 'Bearer ' + self.access_token}

        d = treq.get(self.path, headers=headers)
        
        return d
       
    def _handleResponse(self, response, uri=''):
        status = response.code
        m = getattr(self, '_handleResponse_'+str(status), self._handleResponseDefault)
        return m(response, uri)
    
    def _handleResponse_403(self, response, uri):
        raise PermissionDeniedError, uri
    
    def _handleResponse_404(self, response, uri):
        raise NotFoundError, uri
    
    def _handleResponseDefault(self, response, uri):
        return response
    
    def __str__(self):
        return self.path
