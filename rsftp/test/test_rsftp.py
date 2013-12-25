from twisted.trial.unittest import TestCase

import treq

from rsftp import RSFTPShell
from rsftp.rs.filepath import RSFilePath

from rsftp.test.mocks import mock_get


class PathTestCase(TestCase):
    def setUp(self):
        self.shell = RSFTPShell(RSFilePath('http://example.com/'))

    def tearDown(self):
        pass

    def test_path(self):
        self.patch(treq, 'get', mock_get)

        d = self.shell._path(['public', 'example', 'mytest'])

        def cbGotNewPath(filepath):
            self.assertEqual(filepath.path, 'http://example.com/public/example/mytest')

        d.addCallback(cbGotNewPath)

        return d
