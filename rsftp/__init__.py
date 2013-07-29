import operator
import os

from twisted.cred import checkers
from twisted.internet import defer
from twisted.protocols.ftp import FTPShell, FTPRealm, IFTPShell, FileNotFoundError, errnoToFailure

import client


class MyFTPRealm(FTPRealm):
    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is IFTPShell:
#                if avatarId is checkers.ANONYMOUS:
                avatar = MyFTPShell(self.anonymousRoot)
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
#        print path, keys
        filePath = self._path(path)
        if filePath.isdir():
            entries = filePath.listdir()
            fileEntries = [filePath.child(p) for p in entries]
        elif filePath.isfile():
            entries = [os.path.join(*filePath.segmentsFrom(self.filesystemRoot))]
            fileEntries = [filePath]
        else:
            return defer.fail(FileNotFoundError(path))

        results = []
        for fileName, filePath in zip(entries, fileEntries):
            ent = []
            results.append((fileName, ent))
            if keys:
                try:
                    ent.extend(self._statNode(filePath, keys))
                except (IOError, OSError), e:
                    return errnoToFailure(e.errno, fileName)
                except:
                    return defer.fail()
#        results = [('test', [])]
        results = [
                   ('test', [0L, True, 16895, 0, 1374426641.523584, '0', '0']),
                   ('tkkg.txt', [2139L, False, 33206, 0, 1375043497.990811, '0', '0']),
        ]
        
        def pkkk(response):
            print 'kkk', response
            
        client.ask().addCallback(pkkk)
        #print results

        return defer.succeed(results)
    
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