#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from setuptools import setup, find_packages
import imp
import os

def read_file(filename):
    """Read  file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    with open(filepath) as fh:
        return fh.read()


setup(
    name="libmaven",
    version=imp.load_source("libmaven.constants",
                            "libmaven/constants.py").getVersion(),
    description="Python access to maven",
    author="Walter Scheper",
    author_email="Walter.Scheper@sas.com",
    license="Apache License 2.0",
    packages=find_packages(),
    install_requires=read_file("requirements.txt"),
)
