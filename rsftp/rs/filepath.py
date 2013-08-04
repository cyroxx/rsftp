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
                info = self.__extractChildInfo(key, value, childinfo)
                childinfo, is_directory, current_version = info

                # try to use <current_version> info as the modified timestamp
                if isinstance(current_version, (int, long)):
                    modified = current_version / 1000
                else:
                    modified = 0

                md = {
                      'size': 0L,
                      'directory': is_directory,
                      'permissions': 16895 if is_directory else 33206,
                      'hardlinks': 0,
                      'modified': modified,
                      'owner': '0',
                      'group': '0'}

                meta = [md[k] for k in keys]
                results.append((key, meta))

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
                childinfo, _, _ = self.__extractChildInfo(key, value, childinfo)

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
        m = getattr(self, '_handleResponse_' + str(status), self._handleResponseDefault)
        return m(response, uri)

    def _handleResponse_403(self, response, uri):
        raise PermissionDeniedError(uri)

    def _handleResponse_404(self, response, uri):
        raise NotFoundError(uri)

    def _handleResponseDefault(self, response, uri):
        return response

    def __extractChildInfo(self, key, value, childinfo):
        is_directory = key.endswith(self.sep)
        current_version = value

        normkey = key[:-1] if is_directory else key
        childinfo[normkey] = {
                              'is_directory': is_directory,
                              'current_version': current_version}

        return childinfo, is_directory, current_version

    def __str__(self):
        return self.path
