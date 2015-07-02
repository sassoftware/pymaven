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


import unittest

from pymaven import Artifact
from pymaven.errors import ArtifactParseError


class TestArtifact(unittest.TestCase):
    def _assertArtifactOrder(self, a1, a2):
        assert a1 < a2
        assert a2 > a1
        assert not a1 >= a2
        assert not a2 <= a1
        assert not a1 == a2
        assert a1 != a2

    def test_invalid_coordinate(self):
        tests = ("foo", "1:2:3:4:5:6")
        for input in tests:
            self.assertRaises(ArtifactParseError, Artifact, input)

    def test_path(self):
        test_pairs = (
            ("foo.bar:baz", "foo/bar/baz"),
            ("foo.bar:baz:1", "foo/bar/baz/1/baz-1.jar"),
            ("foo.bar:baz:pkg:1", "foo/bar/baz/1/baz-1.pkg"),
            ("foo.bar:baz:pkg:sources:1", "foo/bar/baz/1/baz-1-sources.pkg"),
            ("foo.bar:baz:pkg:javadoc:1", "foo/bar/baz/1/baz-1-javadoc.pkg"),
            ("foo.bar:baz:[1,2)", "foo/bar/baz"),
            )

        for input, expected in test_pairs:
            artifact = Artifact(input)
            assert artifact.path == expected

    def test_comparison(self):
        test_pairs = (
            # compare group id
            (Artifact("f:a:1"), Artifact("g:a:1")),
            # compare artifact id
            (Artifact("g:a:1"), Artifact("g:b:1")),
            # compare type
            (Artifact("g:a:1"), Artifact("g:a:pom:1")),
            (Artifact("g:a:jar:1"), Artifact("g:a:pom:1")),
            (Artifact("g:a:pom:1"), Artifact("g:a:war:1")),
            # compare classifier
            (Artifact("g:a:jar:c:1"), Artifact("g:a:1")),
            (Artifact("g:a:jar:a:1"), Artifact("g:a:jar:c:1")),
            # compare version
            (Artifact("g:a:1"), Artifact("g:a:2")),
            # mask version
            (Artifact("f:a:2"), Artifact("g:a:1")),
            (Artifact("g:a:2"), Artifact("g:b:1")),
            (Artifact("g:a:2"), Artifact("g:a:pom:1")),
            (Artifact("g:a:jar:2"), Artifact("g:a:pom:1")),
            (Artifact("g:a:pom:2"), Artifact("g:a:war:1")),
            (Artifact("g:a:jar:c:2"), Artifact("g:a:1")),
            (Artifact("g:a:jar:a:2"), Artifact("g:a:jar:c:1")),
            )

        for pair in test_pairs:
            self._assertArtifactOrder(*pair)

        # verify identity
        a = Artifact("foo:bar:1")
        assert not a < a
        assert a <= a
        assert a >= a
        assert a == a
        assert not a != a

        # compare to non-artifact
        assert a > "aardvark"
        assert a != "aardvark"
        assert "aardvark" < a
        assert "aardvark" != a
        assert a > 10
        assert a != 10
        assert 10 < a
        assert 10 != a

    def test_tostring(self):
        a = Artifact("foo:bar")
        assert str(a) == "foo:bar"

        a = Artifact("foo:bar:1")
        assert str(a) == "foo:bar:jar:1"

        a = Artifact("foo:bar:pom:1")
        assert str(a) == "foo:bar:pom:1"

        a = Artifact("foo:bar:pom:sources:1")
        assert str(a) == "foo:bar:pom:sources:1"
