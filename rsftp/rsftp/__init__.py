from twisted.internet import defer
from twisted.protocols.ftp import FTPRealm, IFTPShell
from twisted.protocols import basic, ftp

import rs
from rs.filepath import NotFoundError, PermissionDeniedError

from settings import BASE_URI, ACCESS_TOKEN


class RSFTPRealm(FTPRealm):
    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is IFTPShell:
#                if avatarId is checkers.ANONYMOUS:
                avatar = RSFTPShell(rs.RSFilePath(BASE_URI, ACCESS_TOKEN))
#                else:
                #avatar = RSFTPShell(self.getHomeDirectory(avatarId))
                return (IFTPShell, avatar,
                        getattr(avatar, 'logout', lambda: None))
        raise NotImplementedError(
            "Only IFTPShell interface is supported by this realm")


class _RSFileReader(object):
    #implements(IReadFile)

    def __init__(self, fObj):
        self.fObj = fObj
        self._send = False

    def _close(self, passthrough):
        self._send = True
        self.fObj.close()
        return passthrough

    def send(self, consumer):
        assert not self._send, "Can only call IReadFile.send *once* per instance"
        self._send = True
        d = basic.FileSender().beginFileTransfer(self.fObj, consumer)
        d.addBoth(self._close)
        return d


class RSFTPShell(object):

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
            failure.trap(NotFoundError, PermissionDeniedError)

            if failure.check(NotFoundError):
                raise ftp.FileNotFoundError(path)
            elif failure.check(PermissionDeniedError):
                raise ftp.PermissionDeniedError(path)
            else:
                return failure

        d.addCallback(cbList)
        d.addErrback(ebNotFound)

        return d

    def access(self, path):

        d = self._path(path)

        # 1. does it exist?
        # 2. do we have the permission to access?

        def ebPath(failure):
#            print "[rsftp71] ", path
            raise ftp.FileNotFoundError(path)

        d.addErrback(ebPath)

        return d

    def openForReading(self, path):
        """
        Open C{path} for reading.

        @param path: The path, as a list of segments, to open.
        @type path: C{list} of C{unicode}
        @return: A L{Deferred} is returned that will fire with an object
            implementing L{IReadFile} if the file is successfully opened.  If
            C{path} is a directory, or if an exception is raised while trying
            to open the file, the L{Deferred} will fire with an error.
        """
        def cbFileOpened(f):
            return _RSFileReader(f)

        def cbPathConstructed(path):
            d2 = path.open()
            d2.addCallback(cbFileOpened)

            return d2

        d1 = self._path(path)
        d1.addCallback(cbPathConstructed)

        return d1

    def removeFile(self, path):
        def cbPathConstructed(path):
            path.remove()

        d = self._path(path)
        d.addCallback(cbPathConstructed)

        return d

    def rename(self, fromPath, toPath):
        # Not really implemented yet, so deny
        return defer.fail(ftp.PermissionDeniedError(fromPath))

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
