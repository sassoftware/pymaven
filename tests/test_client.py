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


from StringIO import StringIO
import os
import tempfile
import unittest

import mock
import requests

from pymaven import Artifact
from pymaven.client import HttpRepository
from pymaven.client import LocalRepository
from pymaven.client import MavenClient
from pymaven.client import Struct
from pymaven.errors import MissingPathError
from pymaven.errors import MissingArtifactError


class TestMavenClient(unittest.TestCase):
    def test_invalid_repo(self):
        self.assertRaises(ValueError, MavenClient, "foo://bar.com")

    @mock.patch("pymaven.client.LocalRepository")
    def test_find_artifacts(self, _LocalRepository):
        _repo1 = mock.Mock(spec=LocalRepository)
        _repo2 = mock.Mock(spec=LocalRepository)

        _LocalRepository.side_effect = [_repo1, _repo2]

        _repo1.get_versions.return_value = [Artifact("foo:bar:2.0"),
                                            Artifact("foo:bar:2.0-SNAPSHOT"),
                                            Artifact("foo:bar:1.0"),
                                            Artifact("foo:bar:1.0-SNAPSHOT"),
                                            ]

        _repo2.get_versions.return_value = [Artifact("foo:bar:3.0"),
                                            Artifact("foo:bar:3.0-SNAPSHOT"),
                                            Artifact("foo:bar:1.0"),
                                            Artifact("foo:bar:1.0-SNAPSHOT"),
                                            ]
        client = MavenClient("foobar", "foobaz")
        expected = [Artifact("foo:bar:3.0"),
                    Artifact("foo:bar:3.0-SNAPSHOT"),
                    Artifact("foo:bar:2.0"),
                    Artifact("foo:bar:2.0-SNAPSHOT"),
                    Artifact("foo:bar:1.0"),
                    Artifact("foo:bar:1.0-SNAPSHOT"),
                    ]
        actual = client.find_artifacts("foo:bar")
        assert expected == actual, "client.find_artifacts(%s)" % input

    @mock.patch("pymaven.client.LocalRepository")
    def test_get_artifact(self, _LocalRepository):

        _repo = mock.Mock(spec=LocalRepository)

        _repo.exists.side_effect = [True, False]
        _repo.open.return_value = StringIO("some data")

        _LocalRepository.return_value = _repo

        client = MavenClient("/maven")

        actual = client.get_artifact("foo:bar:2.0.0")
        assert "some data" == actual.contents.read()
        _repo.exists.assert_called_with("foo/bar/2.0.0/bar-2.0.0.jar")
        _repo.open.assert_called_with("foo/bar/2.0.0/bar-2.0.0.jar")

        _repo.reset_mock()
        self.assertRaises(MissingArtifactError, client.get_artifact,
                          "foo:bar:3.0")
        _repo.exists.assert_called_with("foo/bar/3.0/bar-3.0.jar")
        _repo.open.assert_not_called()

        _repo.reset_mock()
        self.assertRaises(AssertionError, client.get_artifact,
                          "foo:bar:[1.0,2.0]")
        _repo.open.assert_not_called()


@mock.patch("pymaven.client.HttpRepository._request")
class TestHttpRespository(unittest.TestCase):
    def test_listdir(self, _request):
        res = mock.MagicMock(spec=Struct)
        res.__enter__.return_value = StringIO(SIMPLE_METADATA)
        _request.side_effect = [res, requests.exceptions.HTTPError]
        expected = ["1.0-SNAPSHOT",
                    "1.0",
                    "3.0-SNAPSHOT",
                    "2.0.0",
                    "1.1",
                    ]
        repo = HttpRepository("http://foo.com/repo")
        actual = repo.listdir("foo/bar")
        assert expected == actual
        self.assertRaises(MissingPathError, repo.listdir, "/baz")

    def test_get_versions(self, _request):
        res = mock.MagicMock(spec=Struct)
        res.__enter__.return_value = StringIO(SIMPLE_METADATA)
        _request.return_value = res

        repo = HttpRepository("http://foo.com/repo")
        for input, expected in (
                ("foo:bar", [Artifact("foo:bar:3.0-SNAPSHOT"),
                             Artifact("foo:bar:2.0.0"),
                             Artifact("foo:bar:1.1"),
                             Artifact("foo:bar:1.0"),
                             Artifact("foo:bar:1.0-SNAPSHOT"),
                             ]),
                ("foo:bar:1.0", [Artifact("foo:bar:1.0")]),
                ("foo:bar:[1.0]", [Artifact("foo:bar:1.0")]),
                ("foo:bar:[1.0,2.0)", [Artifact("foo:bar:1.1"),
                                       Artifact("foo:bar:1.0"),
                                       ]),
                ("foo:bar:[2.0,3.0)", [Artifact("foo:bar:3.0-SNAPSHOT"),
                                       Artifact("foo:bar:2.0.0"),
                                       ]),
                ):
            actual = repo.get_versions(input)
            assert expected == actual, "HttpRepository.get_versions(%s)" % input
            # reset res contents
            res.__enter__.return_value.seek(0)

    def test_open(self, _request):
        res = mock.MagicMock(spec=Struct)
        res.__enter__.return_value = StringIO(SIMPLE_METADATA)
        _request.side_effect = [res, requests.exceptions.HTTPError]

        repo = HttpRepository("http://foo.com/repo")
        with repo.open("maven-metadata.xml") as fh:
            assert SIMPLE_METADATA == fh.read()
        self.assertRaises(MissingPathError, repo.open, "some/path")


class TestLocalRepository(unittest.TestCase):
    @mock.patch("pymaven.client.os")
    def test_get_versions(self, _os):
        _os.listdir.return_value = ["1.0-SNAPSHOT",
                                    "2.0.0",
                                    "3.0-SNAPSHOT",
                                    "1.1",
                                    "1.0",
                                    ]
        repo = LocalRepository("/maven")

        for input, expected in (
                ("foo:bar", [Artifact("foo:bar:3.0-SNAPSHOT"),
                             Artifact("foo:bar:2.0.0"),
                             Artifact("foo:bar:1.1"),
                             Artifact("foo:bar:1.0"),
                             Artifact("foo:bar:1.0-SNAPSHOT"),
                             ]),
                ("foo:bar:1.0", [Artifact("foo:bar:1.0")]),
                ("foo:bar:[1.0]", [Artifact("foo:bar:1.0")]),
                ("foo:bar:[1.0,2.0)", [Artifact("foo:bar:1.1"),
                                       Artifact("foo:bar:1.0"),
                                       ]),
                ("foo:bar:[2.0,3.0)", [Artifact("foo:bar:3.0-SNAPSHOT"),
                                       Artifact("foo:bar:2.0.0"),
                                       ]),
                ):
            actual = repo.get_versions(input)
            assert expected == actual, \
                "LocalRepository.get_versions(%s)" % input

    def test_open(self):
        with tempfile.NamedTemporaryFile() as tmp:
            repo = LocalRepository(os.path.dirname(tmp.name))
            tmp.write("the file\n")
            tmp.flush()
            with repo.open(tmp.name) as fh:
                assert "the file\n" == fh.read()

        self.assertRaises(MissingPathError, repo.open, "/does/not/exist")


SIMPLE_METADATA = """\
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <groupId>foo</groupId>
  <artifactId>bar</artifactId>
  <version>3.0</version>
  <versioning>
    <latest>3.0</latest>
    <release>3.0</release>
    <versions>
      <version>1.0-SNAPSHOT</version>
      <version>1.0</version>
      <version>3.0-SNAPSHOT</version>
      <version>2.0.0</version>
      <version>1.1</version>
    </versions>
    <lastUpdated>20150521051651</lastUpdated>
  </versioning>
</metadata>
"""

FOO_BAR_3_0_POM = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>foo</groupId>
    <artifactId>bar</artifactId>
    <version>2.0.0</version>
</project>
"""
