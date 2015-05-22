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


"""
The artifact module provides objects and functions for working with artifacts
in a maven repository
"""

import re

from .errors import ArtifactParseError
from .versioning import VersionRange


MAVEN_COORDINATE_RE = re.compile(
    r'(?P<group_id>[^:]+)'
    r':(?P<artifact_id>[^:]+)'
    r'(:(?P<type>[^:]+)(:(?P<classifier>[^:]+))?)?'
    r':(?P<version>[^:])'
    )


class Artifact(object):
    """Represents an artifact within a maven repository."""
    def __init__(self, coordinates):
        self._coordinates = coordinates
        self.version = None
        self.type = "jar"
        self.classifier = None

        parts = coordinates.split(':')
        length = len(parts)
        if length < 2 or length > 5:
            raise ArtifactParseError(
                "Too many items in coordinates: '%s'" % coordinates)

        self.group_id, self.artifact_id = parts[:2]
        if length == 3:
            self.version = parts[2]
        elif length == 4:
            self.type = parts[2]
            self.version = parts[3]
        elif length == 5:
            self.type = parts[2]
            self.classifier = parts[3]
            self.version = parts[4]

        if self.version:
            self.version = VersionRange(self.version)

    def __cmp__(self, other):
        if self is other:
            return 0

        if not isinstance(other, Artifact):
            if isinstance(other, basestring):
                try:
                    return cmp(self, Artifact(other))
                except ArtifactParseError:
                    pass
            return 1

        result = cmp(self.group_id, other.group_id)
        if result == 0:
            result = cmp(self.artifact_id, other.artifact_id)

            if result == 0:
                result = cmp(self.type, other.type)

                if result == 0:
                    if self.classifier is None:
                        if other.classifier is not None:
                            result = 1
                    else:
                        if other.classifier is None:
                            result = -1
                        else:
                            result = cmp(self.classifier, other.classifier)

                    if result == 0:
                        result = cmp(self.version.version,
                                     other.version.version)

        return result

    def __str__(self):
        s = ':'.join((self.group_id, self.artifact_id))
        if self.version:
            s += ':' + self.type
            if self.classifier:
                s += ':' + self.classifier
            s += ':' + str(self.version.version if self.version.version
                           else self.vserion)
        return s

    def __repr__(self):
        return "<pymaven.Artifact(%r)" % self._coordinates

    @property
    def coordinate(self):
        return self._coordinates

    @property
    def path(self):
        path = "/%s/%s" % (self.group_id.replace('.', '/'), self.artifact_id)

        if self.version:
            version = (self.version.version if self.version.version
                       else self.version)
            path += "/%s/%s-%s" % (version, self.artifact_id, version)
            if self.classifier:
                path += "-%s" % self.classifier
            path += ".%s" % self.type
        return path
