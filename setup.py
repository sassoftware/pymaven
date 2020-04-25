# -*- encoding: utf-8 -*-
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

import codecs
import os
import re

from setuptools import find_packages, setup


# Global Variables

NAME = "pymaven"
PACKAGES = find_packages(where="src")
META_PATH = os.path.join("src", NAME, "__init__.py")
KEYWORDS = ["maven", "client"]
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/sassoftware/pymaven/issues",
    "Source Code": "https://github.com/sassoftware/pymaven",
}
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
INSTALL_REQUIRES = [
    "lxml>=4.5.0,<5",
    "requests>=2.7.0,<3",
    "six>=1.10,<2",
]
EXTRAS_REQUIRE = {
    "docs": ["sphinx", "sphinx-rtd-theme"],
    "tests:python_version < '3.4'": ["coverage[toml]>=5.0.2,<6", "mock", "pytest"],
    "tests:python_version >= '3.4'": ["coverage[toml]>=5.0.2,<6", "pytest"],
}
EXTRAS_REQUIRE["dev:python_version < '3.4'"] = (
    EXTRAS_REQUIRE["tests:python_version < '3.4'"]
    + EXTRAS_REQUIRE["docs"]
    + ["pre-commit"]
)
EXTRAS_REQUIRE["dev:python_version >= '3.4'"] = (
    EXTRAS_REQUIRE["tests:python_version >= '3.4'"]
    + EXTRAS_REQUIRE["docs"]
    + ["pre-commit"]
)

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*path):
    """Read a file at path"""
    with codecs.open(os.path.join(HERE, *path), "rb", "utf-8") as fh:
        return fh.read()


META_FILE = read(META_PATH)


def get_dunder(name):
    """Extract dunder (__<name>__) variables from path"""
    m = re.search(
        r"^__{name}__ = ['\"]([^'\"]*)['\"]".format(name=name), META_FILE, re.M
    )
    if m:
        return m.group(1)
    raise RuntimeError(
        "Unable to find __{name}__ in {path}".format(name=name, path=META_FILE)
    )


VERSION = get_dunder("version")
URL = get_dunder("url")
LONG = (
    read("README.rst")
    + "\n\n"
    # + "Latest Release\n"
    # + "==============\n\n"
    # + re.search(  # type: ignore
    #     r"(`\d+\.\d+\.\d+`_ - .*?\r?\n.*?)\r?\n\r?\n----\r?\n\r?\n\r?\n",
    #     read("CHANGELOG.rst"),
    #     re.S,
    # ).group(1)
    # + "`Full Changelog <{url}/blob/{version}/CHANGELOG.rst>`_.\n\n".format(
    #     url=URL, version=VERSION
    # ),
    + read("AUTHORS.rst")
)

if __name__ == "__main__":
    setup(
        name=NAME,
        description=get_dunder("description"),
        license=get_dunder("license"),
        url=URL,
        project_urls=PROJECT_URLS,
        version=VERSION,
        author=get_dunder("author"),
        author_email=get_dunder("email"),
        maintainer=get_dunder("author"),
        maintainer_email=get_dunder("email"),
        keywords=KEYWORDS,
        long_description=LONG,
        long_description_content_type="text/x-rst",
        packages=PACKAGES,
        package_dir={"": "src"},
        python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        include_package_data=True,
        options={"bdist_wheel": {"universal": "1"}},
    )
