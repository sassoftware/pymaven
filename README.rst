..  Copyright (c) SAS Institute Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

==================================
``pymaven``: A Python Maven Client
==================================

.. image:: https://github.com/sassoftware/pymaven/workflows/CI/badge.svg?branch=master
   :target: https://github.com/sassoftware/pymaven/actions?workflow=CI
   :alt: CI Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

.. teaser-begin

Pymaven is a Python library for interfacing with the maven build system. There
are two major interfaces:

- ``pymaven.MavenClient`` provides a basic maven repository client.
- ``pymaven.Pom`` provides an object that can provide progromatic access to a maven pom file

.. teaser-end
