#
# Copyright (c) 2015 SAS Institute, Inc.
#
"""
Test version handling
"""
import unittest

from libmaven import errors
from libmaven.versioning import Restriction
from libmaven.versioning import Version
from libmaven.versioning import VersionRange


class TestRestriction(unittest.TestCase):
    def test_no_lower_limit(self):
        r = Restriction.fromstring("(,1.0]")
        assert r.lower_bound is None
        assert not r.lower_bound_inclusive
        assert str(r.upper_bound) == "1.0"
        assert r.upper_bound_inclusive

    def test_inclusive_range(self):
        r = Restriction.fromstring("[1.0]")
        assert str(r.lower_bound) == "1.0"
        assert r.lower_bound_inclusive
        assert str(r.upper_bound) == "1.0"
        assert r.upper_bound_inclusive

        r = Restriction.fromstring("[1.2,1.3]")
        assert str(r.lower_bound) == "1.2"
        assert r.lower_bound_inclusive
        assert str(r.upper_bound) == "1.3"
        assert r.upper_bound_inclusive

    def test_exclusive_upper_bound(self):
        r = Restriction.fromstring("[1.0,2.0)")
        assert str(r.lower_bound) == "1.0"
        assert r.lower_bound_inclusive
        assert str(r.upper_bound) == "2.0"
        assert not r.upper_bound_inclusive

        r = Restriction.fromstring("[1.5,)")
        assert str(r.lower_bound) == "1.5"
        assert r.lower_bound_inclusive
        assert r.upper_bound == None
        assert not r.upper_bound_inclusive

    def test_invalid_restrictions(self):
        tests = ("(1.0)", "[1.0)", "(1.0]", "(1.0,1.0]", "[1.0,1.0)",
                 "(1.0,1.0)", "[1.1,1.0]",)
        for spec in tests:
            self.assertRaises(
                errors.RestrictionParseError,
                Restriction.fromstring,
                spec,
                )


class TestVersion(unittest.TestCase):
    """Tests the Version object"""
    def _assert_version_equal(self, v1, v2):
        V1 = Version(v1)
        V2 = Version(v2)
        assert V1 == V2, \
            "%s != %s" % (V1._parsed, V2._parsed)
        assert V2 == V1, \
            "%s != %s" % (V2._parsed, V1._parsed)

    def _assert_version_order(self, v1, v2):
        V1 = Version(v1)
        V2 = Version(v2)
        assert V1 < V2, \
            "%s >= %s" % (V1._parsed, V2._parsed)
        assert V2 > V1, \
            "%s >= %s" % (V2._parsed, V1._parsed)

    def test_from_string(self):
        test_pairs = (
            # test some major.minor.tiny parsing
            ("1", [1]), ("1.0", [1]), ("1.0.0", [1]),
            ("1.0.0.0", [1]), ("11", [11]), ("11.0", [11]),
            ("1-1", [1, [1]]), ("1-1-1", [1, [1, [1]]]), (" 1 ", [1]),
            # test qualifeirs
            ("1-ALPHA", [1, ["alpha"]]), ("1-alpha", [1, ["alpha"]]),
            ("1ALPHA", [1, ["alpha"]]), ("1-alpha", [1, ["alpha"]]),
            ("1-A", [1, ["a"]]), ("1-a", [1, ["a"]]),
            ("1A", [1, ["a"]]), ("1a", [1, ["a"]]),
            ("1-BETA", [1, ["beta"]]), ("1-beta", [1, ["beta"]]),
            ("1-B", [1, ["b"]]), ("1-b", [1, ["b"]]),
            ("1B", [1, ["b"]]), ("1b", [1, ["b"]]),
            ("1-MILESTONE", [1, ["milestone"]]), ("1-milestone", [1, ["milestone"]]),
            ("1-M", [1, ["m"]]), ("1-m", [1, ["m"]]),
            ("1M", [1, ["m"]]), ("1m", [1, ["m"]]),
            ("1-RC", [1, ["rc"]]), ("1-rc", [1, ["rc"]]),
            ("1-SNAPSHOT", [1, ["snapshot"]]), ("1-snapshot", [1, ["snapshot"]]),
            ("1-SP", [1, ["sp"]]), ("1-sp", [1, ["sp"]]),
            ("1-GA", [1]), ("1-ga", [1]),
            ("1-FINAL", [1]), ("1-final", [1]),
            ("1-CR", [1, ["rc"]]), ("1-cr", [1, ["rc"]]),
            # test some transistion
            ("1-alpha1", [1, ["alpha", [1]]]), ("1-alpha2", [1, ["alpha", [2]]]),
            ("1.0alpha1", [1, ["alpha", [1]]]),
            ("1-beta1", [1, ["beta", [1]]]), ("1-beta2", [1, ["beta", [2]]]),
            ("1.0beta1", [1, ["beta", [1]]]),
            ("1-BETA1", [1, ["beta", [1]]]), ("1-BETA2", [1, ["beta", [2]]]),
            ("1.0BETA1", [1, ["beta", [1]]]),
            ("1-milestone1", [1, ["milestone", [1]]]), ("1-milestone2", [1, ["milestone", [2]]]),
            ("1.0milestone1", [1, ["milestone", [1]]]),
            ("1-MILESTONE1", [1, ["milestone", [1]]]), ("1-milestone2", [1, ["milestone", [2]]]),
            ("1.0MILESTONE1", [1, ["milestone", [1]]]),
            ("1-alpha2snapshot", [1, ["alpha", [2, ["snapshot"]]]]),
            )

        for test, expected in test_pairs:
            v = Version(test)
            assert v._parsed == expected, \
                "Version(%s) == %s, want %s" % (test, v._parsed, expected)

    def test_versio_qualifiers(self):
        version_qualifiers = (
            "1-alpha2snapshot", "1-alpha2", "1-alpha-123", "1-beta-2",
            "1-beta123", "1-m2", "1-m11", "1-rc", "1-cr2", "1-rc123",
            "1-SNAPSHOT", "1", "1-sp", "1-sp2", "1-sp123", "1-abc", "1-def",
            "1-pom-1", "1-1-snapshot", "1-1", "1-2", "1-123",
            )
        for idx, low in enumerate(version_qualifiers[:-1]):
            for high in version_qualifiers[idx+1:]:
                self._assert_version_order(low, high)

    def test_version_numbers(self):
        version_numbers = (
            "2.0", "2-1", "2.0.a", "2.0.0.a", "2.0.2", "2.0.123", "2.1.0",
            "2.1-a", "2.1b", "2.1-x", "2.1-1", "2.1.0.1", "2.2", "2.123",
            "11.a2", "11.a11", "11.b2", "11.b11", "11.m2", "11.m11", "11",
            "11.a", "11b", "11c", "11m",
            )
        for idx, low in enumerate(version_numbers[:-1]):
            for high in version_numbers[idx+1:]:
                self._assert_version_order(low, high)

        unicode_version_numbers = (
            # again, but with unicode input
            u"2.0", u"2-1", u"2.0.a", u"2.0.0.a", u"2.0.2", u"2.0.123", u"2.1.0",
            u"2.1-a", u"2.1b", u"2.1-x", u"2.1-1", u"2.1.0.1", u"2.2", u"2.123",
            u"11.a2", u"11.a11", u"11.b2", u"11.b11", u"11.m2", u"11.m11", u"11",
            u"11.a", u"11b", u"11c", u"11m",
            )
        for idx, low in enumerate(unicode_version_numbers[:-1]):
            for high in unicode_version_numbers[idx+1:]:
                self._assert_version_order(low, high)

    def test_version_equality(self):
        self._assert_version_equal("1", "1")
        self._assert_version_equal("1", "1.0")
        self._assert_version_equal("1", "1.0.0")
        self._assert_version_equal("1.0", "1.0.0")
        self._assert_version_equal("1", "1-0")
        self._assert_version_equal("1", "1.0-0")
        self._assert_version_equal("1.0", "1.0-0")
        # no separator between number and character
        self._assert_version_equal("1a", "1-a")
        self._assert_version_equal("1a", "1.0-a")
        self._assert_version_equal("1a", "1.0.0-a")
        self._assert_version_equal("1.0a", "1-a")
        self._assert_version_equal("1.0.0a", "1-a")
        self._assert_version_equal("1x", "1-x")
        self._assert_version_equal("1x", "1.0-x")
        self._assert_version_equal("1x", "1.0.0-x")
        self._assert_version_equal("1.0x", "1-x")
        self._assert_version_equal("1.0.0x", "1-x")

        # aliases
        self._assert_version_equal("1ga", "1")
        self._assert_version_equal("1final", "1")
        self._assert_version_equal("1cr", "1rc")

        # special "aliases" a, b and m for alpha, beta and milestone
        self._assert_version_equal("1a1", "1-alpha-1")
        self._assert_version_equal("1b2", "1-beta-2")
        self._assert_version_equal("1m3", "1-milestone-3")

        # case insensitive
        self._assert_version_equal("1X", "1x")
        self._assert_version_equal("1A", "1a")
        self._assert_version_equal("1B", "1b")
        self._assert_version_equal("1M", "1m")
        self._assert_version_equal("1Ga", "1")
        self._assert_version_equal("1GA", "1")
        self._assert_version_equal("1Final", "1")
        self._assert_version_equal("1FinaL", "1")
        self._assert_version_equal("1FINAL", "1")
        self._assert_version_equal("1Cr", "1Rc")
        self._assert_version_equal("1cR", "1rC")
        self._assert_version_equal("1m3", "1Milestone3")
        self._assert_version_equal("1m3", "1MileStone3")
        self._assert_version_equal("1m3", "1MILESTONE3")

        # unicode
        self._assert_version_equal(u"1", "1")
        self._assert_version_equal(u"1", "1.0")
        self._assert_version_equal(u"1", "1.0.0")
        self._assert_version_equal(u"1.0", "1.0.0")
        self._assert_version_equal(u"1", "1-0")
        self._assert_version_equal(u"1", "1.0-0")
        self._assert_version_equal(u"1.0", "1.0-0")

        self._assert_version_equal("1", u"1")
        self._assert_version_equal("1", u"1.0")
        self._assert_version_equal("1", u"1.0.0")
        self._assert_version_equal("1.0", u"1.0.0")
        self._assert_version_equal("1", u"1-0")
        self._assert_version_equal("1", u"1.0-0")
        self._assert_version_equal("1.0", u"1.0-0")

        self._assert_version_equal(u"1", u"1")
        self._assert_version_equal(u"1", u"1.0")
        self._assert_version_equal(u"1", u"1.0.0")
        self._assert_version_equal(u"1.0", u"1.0.0")
        self._assert_version_equal(u"1", u"1-0")
        self._assert_version_equal(u"1", u"1.0-0")
        self._assert_version_equal(u"1.0", u"1.0-0")

    def test_version_compare(self):
        self._assert_version_order("1", "2")
        self._assert_version_order("1.5", "2")
        self._assert_version_order("1", "2.5")
        self._assert_version_order("1.0", "1.1")
        self._assert_version_order("1.1", "1.2")
        self._assert_version_order("1.0.0", "1.1")
        self._assert_version_order("1.0.1", "1.1")
        self._assert_version_order("1.1", "1.2.0")
        self._assert_version_order("1.0-alpha-1", "1.0")
        self._assert_version_order("1.0-alpha-1", "1.0-alpha-2")
        self._assert_version_order("1.0-alpha-1", "1.0-beta-1")
        self._assert_version_order("1.0-beta-1", "1.0-SNAPSHOT")
        self._assert_version_order("1.0-SNAPSHOT", "1.0")
        self._assert_version_order("1.0-alpha-1-SNAPSHOT", "1.0-alpha-1")
        self._assert_version_order("1.0", "1.0-1")
        self._assert_version_order("1.0-1", "1.0-2")
        self._assert_version_order("1.0.0", "1.0-1")
        self._assert_version_order("2.0-1", "2.0.1")
        self._assert_version_order("2.0.1-klm", "2.0.1-lmn")
        self._assert_version_order("2.0.1", "2.0.1-xyz")
        self._assert_version_order("2.0.1", "2.0.1-123")
        self._assert_version_order("2.0.1-xyz", "2.0.1-123")
        # unicode input
        self._assert_version_order(u"1", "2")
        self._assert_version_order(u"1.5", "2")
        self._assert_version_order(u"1", "2.5")
        self._assert_version_order(u"1.0", "1.1")
        self._assert_version_order(u"1.1", "1.2")
        self._assert_version_order(u"1.0.0", "1.1")
        self._assert_version_order(u"1.0.1", "1.1")
        self._assert_version_order(u"1.1", "1.2.0")
        self._assert_version_order(u"1.0-alpha-1", "1.0")
        self._assert_version_order(u"1.0-alpha-1", "1.0-alpha-2")
        self._assert_version_order(u"1.0-alpha-1", "1.0-beta-1")
        self._assert_version_order(u"1.0-beta-1", "1.0-SNAPSHOT")
        self._assert_version_order(u"1.0-SNAPSHOT", "1.0")
        self._assert_version_order(u"1.0-alpha-1-SNAPSHOT", "1.0-alpha-1")
        self._assert_version_order(u"1.0", "1.0-1")
        self._assert_version_order(u"1.0-1", "1.0-2")
        self._assert_version_order(u"1.0.0", "1.0-1")
        self._assert_version_order(u"2.0-1", "2.0.1")
        self._assert_version_order(u"2.0.1-klm", "2.0.1-lmn")
        self._assert_version_order(u"2.0.1", "2.0.1-xyz")
        self._assert_version_order(u"2.0.1", "2.0.1-123")
        self._assert_version_order(u"2.0.1-xyz", "2.0.1-123")

        self._assert_version_order("1", u"2")
        self._assert_version_order("1.5", u"2")
        self._assert_version_order("1", u"2.5")
        self._assert_version_order("1.0", u"1.1")
        self._assert_version_order("1.1", u"1.2")
        self._assert_version_order("1.0.0", u"1.1")
        self._assert_version_order("1.0.1", u"1.1")
        self._assert_version_order("1.1", u"1.2.0")
        self._assert_version_order("1.0-alpha-1", u"1.0")
        self._assert_version_order("1.0-alpha-1", u"1.0-alpha-2")
        self._assert_version_order("1.0-alpha-1", u"1.0-beta-1")
        self._assert_version_order("1.0-beta-1", u"1.0-SNAPSHOT")
        self._assert_version_order("1.0-SNAPSHOT", u"1.0")
        self._assert_version_order("1.0-alpha-1-SNAPSHOT", u"1.0-alpha-1")
        self._assert_version_order("1.0", u"1.0-1")
        self._assert_version_order("1.0-1", u"1.0-2")
        self._assert_version_order("1.0.0", u"1.0-1")
        self._assert_version_order("2.0-1", u"2.0.1")
        self._assert_version_order("2.0.1-klm", u"2.0.1-lmn")
        self._assert_version_order("2.0.1", u"2.0.1-xyz")
        self._assert_version_order("2.0.1", u"2.0.1-123")
        self._assert_version_order("2.0.1-xyz", u"2.0.1-123")

        self._assert_version_order(u"1", u"2")
        self._assert_version_order(u"1.5", u"2")
        self._assert_version_order(u"1", u"2.5")
        self._assert_version_order(u"1.0", u"1.1")
        self._assert_version_order(u"1.1", u"1.2")
        self._assert_version_order(u"1.0.0", u"1.1")
        self._assert_version_order(u"1.0.1", u"1.1")
        self._assert_version_order(u"1.1", u"1.2.0")
        self._assert_version_order(u"1.0-alpha-1", u"1.0")
        self._assert_version_order(u"1.0-alpha-1", u"1.0-alpha-2")
        self._assert_version_order(u"1.0-alpha-1", u"1.0-beta-1")
        self._assert_version_order(u"1.0-beta-1", u"1.0-SNAPSHOT")
        self._assert_version_order(u"1.0-SNAPSHOT", u"1.0")
        self._assert_version_order(u"1.0-alpha-1-SNAPSHOT", u"1.0-alpha-1")
        self._assert_version_order(u"1.0", u"1.0-1")
        self._assert_version_order(u"1.0-1", u"1.0-2")
        self._assert_version_order(u"1.0.0", u"1.0-1")
        self._assert_version_order(u"2.0-1", u"2.0.1")
        self._assert_version_order(u"2.0.1-klm", u"2.0.1-lmn")
        self._assert_version_order(u"2.0.1", u"2.0.1-xyz")
        self._assert_version_order(u"2.0.1", u"2.0.1-123")
        self._assert_version_order(u"2.0.1-xyz", u"2.0.1-123")


class TestVersionRange(unittest.TestCase):
    def test_no_lower_limit(self):
        vr = VersionRange.fromstring("(,1.0]")
        assert len(vr.restrictions) == 1
        assert vr.version is None

    def test_single_spec(self):
        vr = VersionRange.fromstring("1.0")
        assert len(vr.restrictions) == 1
        assert str(vr.version) == "1.0"

    def test_inclusive_range(self):
        vr = VersionRange.fromstring("[1.0]")
        assert len(vr.restrictions) == 1
        assert vr.version is None

        vr = VersionRange.fromstring("[1.2,1.3]")
        assert len(vr.restrictions) == 1
        assert vr.version is None

    def test_exclusive_upper_bound(self):
        vr = VersionRange.fromstring("[1.0,2.0)")
        assert len(vr.restrictions) == 1
        assert vr.version is None

        vr = VersionRange.fromstring("[1.5,)")
        assert len(vr.restrictions) == 1
        assert vr.version is None

    def test_multiple_restrictions(self):
        vr = VersionRange.fromstring("(,1.0],[1.2,)")
        assert len(vr.restrictions) == 2
        assert vr.version is None

    def test_snapshots(self):
        vr = VersionRange.fromstring("[1.0,)")
        assert Version("1.0-SNAPSHOT") not in vr

        vr = VersionRange.fromstring("[1.0,1.1-SNAPSHOT]")
        assert Version("1.1-SNAPSHOT") in vr

        vr = VersionRange.fromstring("[1.0,1.2]")
        assert Version("1.1-SNAPSHOT") in vr
        assert Version("1.2-SNAPSHOT") in vr
        assert Version("1.3-SNAPSHOT") not in vr

        vr = VersionRange.fromstring("[1.0,1.2-SNAPSHOT]")
        assert Version("1.1-SNAPSHOT") in vr
        assert Version("1.2-SNAPSHOT") in vr

        vr = VersionRange.fromstring("[1.0-SNAPSHOT,1.2]")
        assert Version("1.0-SNAPSHOT") in vr
        assert Version("1.1-SNAPSHOT") in vr

        vr = VersionRange.fromstring("1.0-SNAPSHOT")
        assert Version("1.0-SNAPSHOT") in vr

    def test_long_version(self):
        vr = VersionRange.fromstring("[5.0.9.0,5.0.10.0)")
        assert Version("5.0.9.0") in vr

    def test_contains(self):
        test_pairs = (("2.0.5", True), ("2.0.4", True), ("[2.0.5]", True),
                      ("[2.0.6,)", False), ("[2.0.6]", False),
                      ("2.0,2.1]", True), ("[2.0,2.0.3]", False),
                      ("[2.0,2.0.5]", True), ("[2.0,2.0.5)", False),)
        v = Version("2.0.5")
        for spec, expected in test_pairs:
            vr = VersionRange.fromstring(spec)
            assert (v in vr) == expected

    def test_invalid_ranges(self):
        for spec in ("[1.0,1.2),1.3", "[1.0,1.2),(1.1,1.3]",
                     "[1.1,1.3),(1.0,1.2]", "(1.1,1.2],[1.0,1.1)",):
            self.assertRaises(
                errors.VersionRangeParseError, VersionRange.fromstring, spec)