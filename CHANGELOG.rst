Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/>`_ and this project adheres to `Semantic Versioning <http://semver.org/>`_.

Changes for the upcoming release can be found in the `"changelog.d" directory <https://github.com/sassoftware/pymaven/tree/master/changelog.d>`_.

.. Do *NOT* add changelog entries here!

   This file is managed by towncrier and is compiled at release time.

   See https://github.com/sassoftware/pymaven/CONTRIBUTING.rst for details.

.. towncrier release notes start

`0.2.0`_ - 2017-06-07
---------------------

Chores
^^^^^^

- Unpin dependency versions. Allow major version compatibility.

----

`0.1.0`_ - 2015-10-10
---------------------

Features
^^^^^^^^

- A simple maven repository client that can fetch and search for artifacts and metadata.
- Support for local and http maven repositories.
- A simple cache for http maven repositories
- A python binding to POM data that dynamically loads information from POM inheritance and dependency management.
- Python implementation of Maven version comparision and Maven version ranges.

.. _0.2.0: https://github.com/sassoftware/pymaven/compare/0.1.0...0.2.0
.. _0.1.0: https://github.com/sassoftware/pymaven/compare/114b10e...0.1.0
