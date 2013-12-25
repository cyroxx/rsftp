============
rsftp
============

|build|_

``rsftp`` is a work-in-progress FTP adapter for `remoteStorage <http://remotestorage.io>`_ backends.

The aim is to make it easy to up- and download your files to/from a remoteStorage provider using the well-known File Transfer Protocol.
This way, more people will likely see the benefits of a remoteStorage.

Quick start
===========

1. Configure your remoteStorage backend in ``settings.py``.
2. Spin up the server: ``python ftpserver.py``

Contribute
==========

``rsftp`` is hosted on `GitHub <http://github.com/cyroxx/rsftp>`_.

Feel free to fork and send contributions over.

Developing
==========

Install dependencies:

::

    pip install -r requirements.txt

Optionally install PyOpenSSL:

::

    pip install PyOpenSSL

Run Tests (unit & integration):

::

    trial rsftp

Lint:

::

    pep8 rsftp
    pyflakes rsftp

Security
===============

This application is currently not suited for a public-facing installation as it grants full access to anonymous users. In future versions, anonymous access shall be dropped in favor of proper user management. Until then, you should run and test the application locally.

Apart from that, I'm in no way a security expert or specialist, so I recommend to pentest or validate the code before storing any sensitive data with it.

.. |build| image:: https://travis-ci.org/cyroxx/rsftp.png?branch=master
.. _build: https://travis-ci.org/cyroxx/rsftp