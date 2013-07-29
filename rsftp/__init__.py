import operator
import os

from twisted.cred import checkers
from twisted.internet import defer
from twisted.protocols.ftp import FTPShell, FTPRealm, IFTPShell, FileNotFoundError, errnoToFailure
from twisted.python import filepath

import treq

import client

BASE_URI = 'https://heahdk.net/storage/cyroxx/public/'

class MyFTPRealm(FTPRealm):
    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is IFTPShell:
#                if avatarId is checkers.ANONYMOUS:
                avatar = MyFTPShell(filepath.FilePath('/'))
#                else:
                #avatar = MyFTPShell(self.getHomeDirectory(avatarId))
                return (IFTPShell, avatar,
                        getattr(avatar, 'logout', lambda: None))
        raise NotImplementedError(
            "Only IFTPShell interface is supported by this realm")
        

class MyFTPShell(FTPShell):
    def list(self, path, keys=()):
        """
        Return the list of files at given C{path}, adding C{keys} stat
        informations if specified.

        @param path: the directory or file to check.
        @type path: C{str}

        @param keys: the list of desired metadata
        @type keys: C{list} of C{str}
        """
        filePath = self._path(path)
        print type(filePath), filePath
        
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
            
        
        
        uri = BASE_URI
        d = treq.get(uri)
        d.addCallback(treq.json_content)
        d.addCallback(parse_results)

        return d
    
    def access(self, path):
        #print path
        return defer.succeed(None)
    
    def stat(self, path, keys=()):
        p = self._path(path)
        if p.isdir():
            try:
                statResult = self._statNode(p, keys)
            except (IOError, OSError), e:
                return errnoToFailure(e.errno, path)
            except:
                return defer.fail()
            else:
                return defer.succeed(statResult)
        else:
            return self.list(path, keys).addCallback(lambda res: res[0][1])
    
    def _statNode(self, filePath, keys):
        """
        Shortcut method to get stat info on a node.

        @param filePath: the node to stat.
        @type filePath: C{filepath.FilePath}

        @param keys: the stat keys to get.
        @type keys: C{iterable}
        """
        #print 'FilePath:', filePath
        #print 'keys:', keys
        mystat = {
             'size': 50L,
             'directory': False, 
             'permissions': 33206,
             'hardlinks': 0,
             'modified': 1375043497.990811,
             'owner': '0',
             'group': '0'}
        return [mystat.get(k) for k in keys]