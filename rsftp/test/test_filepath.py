from twisted.trial.unittest import TestCase

import treq

from rsftp import rs
from rsftp.test.mocks import mock_get, fakeGet404, fakeListResponseNonNumeric


class RSFilePathTestCase(TestCase):
    def setUp(self):
        self.test = rs.RSFilePath('https://example.com/public/')

    def tearDown(self):
        pass

    def test_child(self):
        self.patch(treq, 'get', mock_get)

        name = 'pictures'
        d = self.test.child(name)

        def cbChild(childPath):
            self.assertEqual(childPath.path, 'https://example.com/public/pictures/')

        d.addCallback(cbChild)

        return d

    def test_childNonExistentPath(self):
        self.patch(treq, 'get', fakeGet404)

        name = 'doesnotexist/'
        d = self.test.child(name)

        return self.assertFailure(d, rs.filepath.NotFoundError)

    def test_listNonNumericVersionNumber(self):
        self.patch(treq, 'get', fakeListResponseNonNumeric)

        keys = ('modified',)
        d = self.test.ftp_list(keys)

        def cbList(results):
            self.assertEqual(results[0][1][0], 0)   # results[0] = ('pictures/', (0,))
            self.assertEqual(results[1][1][0], 0)   # results[1] = ('test.txt', (0,))

        d.addCallback(cbList)

        return d
