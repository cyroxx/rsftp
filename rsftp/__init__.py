import operator
import os

from twisted.cred import checkers
from twisted.internet import defer
from twisted.protocols.ftp import FTPShell, FTPRealm, IFTPShell, FileNotFoundError, PermissionDeniedError, errnoToFailure
from twisted.python.filepath import IFilePath, AbstractFilePath
from twisted.python.compat import comparable

import treq

import rs
from rs.filepath import NotFoundError

BASE_URI = 'https://heahdk.net/storage/cyroxx/public/'

class MyFTPRealm(FTPRealm):
    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is IFTPShell:
#                if avatarId is checkers.ANONYMOUS:
                avatar = MyFTPShell( rs.RSFilePath(BASE_URI) )
#                else:
                #avatar = MyFTPShell(self.getHomeDirectory(avatarId))
                return (IFTPShell, avatar,
                        getattr(avatar, 'logout', lambda: None))
        raise NotImplementedError(
            "Only IFTPShell interface is supported by this realm")
        

class MyFTPShell(object):
    
    def __init__(self, filesystemRoot):
        self.filesystemRoot = filesystemRoot
        
        
    def list(self, path, keys=()):
        """
        Return the list of files at given C{path}, adding C{keys} stat
        informations if specified.

        @param path: the directory or file to check.
        @type path: C{str}

        @param keys: the list of desired metadata
        @type keys: C{list} of C{str}
        """
        d = self._path(path)
        
        def cbList(filePath):
            return filePath.ftp_list(keys)
        
        def ebNotFound(failure):
            failure.trap(NotFoundError)
            raise FileNotFoundError(path)
        
        d.addCallback(cbList)
        d.addErrback(ebNotFound)
        
        return d
    
    def access(self, path):
                   
        d = self._path(path)
        
        # 1. does it exist?
        # 2. do we have the permission to access?

        def ebPath(failure):
            print "[rsftp71] ", path
            raise FileNotFoundError(path)
        
        d.addErrback(ebPath)
        
        return d
    
    def rename(self, fromPath, toPath):
        # Not really implemented yet, so deny
        return defer.fail(PermissionDeniedError(fromPath))
        
    def _path(self, path):
        root = self.filesystemRoot
        
        if path:
            # append the segments one by one to the path            
            d = None
            for segment in path:
                if not d:
                    d = root.child(segment)
                else:
                    def cbAppendPath(path):
                        return path.child(segment)
                    
                    d.addCallback(cbAppendPath)
                
        else:
            d = defer.succeed(root)
            
        return d
