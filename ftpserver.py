# The MIT License (MIT)
#
# Copyright (c) Twisted Matrix Laboratories.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
An example FTP server with minimal user authentication.
"""

from rsftp import RSFTPRealm
from twisted.cred.checkers import AllowAnonymousAccess, FilePasswordDB
from twisted.cred.portal import Portal
from twisted.internet import reactor
from twisted.protocols.ftp import FTPFactory

#
# First, set up a portal (twisted.cred.portal.Portal). This will be used
# to authenticate user logins, including anonymous logins.
#
# Part of this will be to establish the "realm" of the server - the most
# important task in this case is to establish where anonymous users will
# have default access to. In a real world scenario this would typically
# point to something like '/pub' but for this example it is pointed at the
# current working directory.
#
# The other important part of the portal setup is to point it to a list of
# credential checkers. In this case, the first of these is used to grant
# access to anonymous users and is relatively simple; the second is a very
# primitive password checker.  This example uses a plain text password file
# that has one username:password pair per line. This checker *does* provide
# a hashing interface, and one would normally want to use it instead of
# plain text storage for anything remotely resembling a 'live' network. In
# this case, the file "pass.dat" is used, and stored in the same directory
# as the server. BAD.
#
# Create a pass.dat file which looks like this:
#
# =====================
#   jeff:bozo
#   grimmtooth:bozo2
# =====================
#
p = Portal(RSFTPRealm('./'),
           [AllowAnonymousAccess(), FilePasswordDB("pass.dat")])

#
# Once the portal is set up, start up the FTPFactory and pass the portal to
# it on startup. FTPFactory will start up a twisted.protocols.ftp.FTP()
# handler for each incoming OPEN request. Business as usual in Twisted land.
#
f = FTPFactory(p)

#
# You know this part. Point the reactor to port 21 coupled with the above factory,
# and start the event loop.
#
reactor.listenTCP(21, f)
reactor.run()
