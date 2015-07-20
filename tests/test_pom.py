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
import unittest

import mock

from pymaven import Artifact
from pymaven import VersionRange as VR
from pymaven.client import MavenClient
from pymaven.client import Struct
from pymaven.pom import Pom


class TestPom(unittest.TestCase):

    def _mock_client(self, *args):
        client = mock.MagicMock(spec=MavenClient)
        side_effect = []
        for arg in args:
            a = mock.MagicMock(spec=Artifact)
            a.contents = mock.MagicMock(spec=Struct)
            a.contents.__enter__.return_value = StringIO(arg)
            side_effect.append(a)

        client.get_artifact.side_effect = side_effect
        return client

    def test_parent(self):
        """Test pom parent processing"""
        client = self._mock_client(FOO_BAR_1_POM, FOO_PARENT_1_POM)

        pom = Pom("foo:bar:1", client)
        assert pom.parent.group_id == "foo"
        assert pom.parent.artifact_id == "parent"
        assert pom.parent.version == "1"
        assert pom.parent.properties["groupId"] == "foo"
        assert pom.parent.properties["artifactId"] == "parent"
        assert pom.parent.properties["version"] == "1"
        assert pom.parent.properties["project.groupId"] == "foo"
        assert pom.parent.properties["project.artifactId"] == "parent"
        assert pom.parent.properties["project.version"] == "1"
        assert pom.parent.properties["pom.groupId"] == "foo"
        assert pom.parent.properties["pom.artifactId"] == "parent"
        assert pom.parent.properties["pom.version"] == "1"
        assert pom.properties["parent.groupId"] == "foo"
        assert pom.properties["parent.artifactId"] == "parent"
        assert pom.properties["parent.version"] == "1"
        client.get_artifact.assert_called_with("foo:parent:pom:1")

    def test_replace_properties(self):
        """Test Pom._replace_properties"""
        client = self._mock_client(FOO_BAR_1_POM, FOO_PARENT_1_POM)
        pom = Pom("foo:bar:1", client)
        properties = {
            "prop1": "\na string\n",
            "prop2": "${prop1}",
        }
        assert "prop1" == pom._replace_properties("prop1", properties)
        assert "a string" == pom._replace_properties("${prop1}", properties)
        assert "a string" == pom._replace_properties("${prop2}", properties)
        assert "baz version string" == pom._replace_properties("${bazChild}")
        assert "baz version string" == pom._replace_properties("${bazVersion}")
        assert "${unmatched}" == pom._replace_properties("${unmatched}")
        assert "${parentProp}" == \
            pom.parent._replace_properties("${parentProp}")
        assert "resolve" == pom._replace_properties("${resolveProp}")
        assert "resolve" == pom._replace_properties("${parentProp}")

    def test_find_relocations(self):
        """Test Pom._find_relocations()"""
        for args, coordinate in (
                ((RELOCATION_1, FOO_BAR_1_POM), "foo.org:bar:pom:1"),
                ((RELOCATION_2, FOO_BAR_1_POM), "foo:baz:pom:1"),
                ((RELOCATION_3, FOO_BAR_1_POM), "foo:bar:pom:alpha"),
                ((RELOCATION_4, FOO_BAR_1_POM), "foo.org:baz:pom:alpha"),
                ):
            client = self._mock_client(*args)
            pom = Pom(coordinate, client)
            client.get_artifact.assert_called_with(coordinate)
            assert len(pom.dependencies["relocation"]) == 1
            relocations = list(pom.dependencies["relocation"])
            assert relocations[0] == (("foo", "bar", VR("1")), True)

    def test_find_prereqs(self):
        """Test Pom._find_prerequisites()"""
        client = self._mock_client(PREREQUISITES_1)
        pom = Pom("foo:bar:1", client)

        assert "prereq1" == pom.properties["prerequisites.one"]
        assert "prereq1" == pom.properties["project.prerequisites.one"]
        assert "prereq2" == pom.properties["prerequisites.two"]
        assert "prereq2" == pom.properties["project.prerequisites.two"]

    def test_find_import_deps(self):
        """Test Pom._find_import_deps()"""
        client = self._mock_client(IMPORT_DEPS_1, FOO_PARENT_1_POM,
                                   FOO_PARENT_1_POM)
        pom = Pom("foo:bar:1", client)

        import_deps = list(pom._find_import_deps()["import"])
        assert import_deps[0] == (("foo", "parent", "1"), True)

    def test_dependency_management(self):
        """Test Pom.dependency_management"""
        client = self._mock_client(COM_TEST_USE, COM_TEST_BOM, COM_TEST_BOM2)
        pom = Pom("com.test:use:1", client)

        dep_mgmt = pom.dependency_management
        assert ("1.0.0", "import", False) == dep_mgmt[("com.test", "bom")]
        assert ("2.0.0", "import", False) == dep_mgmt[("com.test", "bom2")]
        assert ("2.0.0", None, True) == dep_mgmt[("com.test", "project1")]
        assert ("1.0.0", None, False) == dep_mgmt[("com.test", "project2")]

    def test_deps(self):
        client = self._mock_client(COM_TEST_DEP, COM_TEST_PROJECT1,
                                   COM_TEST_PROJECT2)
        pom = Pom("com.test:dep:1.0.0", client)

        compile_deps = list(pom.dependencies["compile"])
        runtime_deps = list(pom.dependencies["runtime"])

        assert len(compile_deps) == 1
        assert compile_deps[0] == (("com.test", "project1", "1.0.0"), True)

        assert len(runtime_deps) == 1
        assert runtime_deps[0] == (("com.test", "project2", "1.0.0"), True)

    def test_dependency_version_range(self):
        client = self._mock_client(COM_TEST_PROJECT3, COM_TEST_PROJECT2)
        client.find_artifacts.return_value = [
            Artifact("com.test:project2:2.0.0"),
            Artifact("com.test:project2:1.0.0"),
            ]
        pom = Pom("com.test:project3:1.0.0", client)

        deps = list(pom.dependencies["compile"])
        assert len(pom.dependencies) == 1
        assert len(deps) == 1
        assert deps[0] == (("com.test", "project2", "[1.0,2.0)"), True)

        client = self._mock_client(COM_TEST_PROJECT4)
        client.find_artifacts.return_value = [
            Artifact("com.test:project2:2.0.0-SNAPSHOT"),
            Artifact("com.test:project2:1.0.0"),
            ]
        pom = Pom("com.test:project4:1.0.0", client)

        deps = list(pom.dependencies["compile"])
        assert len(pom.dependencies) == 1
        assert len(deps) == 1
        assert deps[0] == (("com.test", "project2", "release"), True)

        client = self._mock_client(
            COM_TEST_PROJECT4.replace("version>release", "version>latest"))
        client.find_artifacts.return_value = [
            Artifact("com.test:project2:2.0.0-SNAPSHOT"),
            Artifact("com.test:project2:1.0.0"),
            ]
        pom = Pom("com.test:project4:1.0.0", client)

        deps = list(pom.dependencies["compile"])
        assert len(pom.dependencies) == 1
        assert len(deps) == 1
        assert deps[0] == (("com.test", "project2", "latest"), True)

        client = self._mock_client(
            COM_TEST_PROJECT4.replace("version>release",
                                      "version>latest.release"))
        client.find_artifacts.return_value = [
            Artifact("com.test:project2:2.0.0-SNAPSHOT"),
            Artifact("com.test:project2:1.0.0"),
            ]
        pom = Pom("com.test:project4:1.0.0", client)

        deps = list(pom.dependencies["compile"])
        assert len(pom.dependencies) == 1
        assert len(deps) == 1
        assert deps[0] == (("com.test", "project2", "latest.release"), True)

        client = self._mock_client(
            COM_TEST_PROJECT4.replace("version>release",
                                      "version>latest.integration"))
        client.find_artifacts.return_value = [
            Artifact("com.test:project2:2.0.0-SNAPSHOT"),
            Artifact("com.test:project2:1.0.0"),
            ]
        pom = Pom("com.test:project4:1.0.0", client)

        deps = list(pom.dependencies["compile"])
        assert len(pom.dependencies) == 1
        assert len(deps) == 1
        assert deps[0] == (("com.test", "project2", "latest.integration"), True)

    def test_profiles(self):
        client = self._mock_client(COM_TEST_PROFILE_1, COM_TEST_PROJECT1)
        pom = Pom("com.test:profile:1.0.0", client)

        compile_deps = list(pom.dependencies["compile"])
        assert "true" == pom.properties["active_profile"]
        assert compile_deps[0] == (("com.test", "project1", VR("1.0.0")), True)

        for input, expected in (
                ("[1.5,", "true"),
                ("![1.5,", "false"),
                ("!1.5", "true"),
                ("1.5", "false"),
                ("![1.5,1.7]", "true"),
                ("[1.5,1.7]", "false"),
                ("1.8", "true"),
                ("!1.8", "false"),
                ("[1.8,)", "true"),
                ("![1.8,)", "false"),
                ("![1.5,1.8)", "true"),
                ("[1.5,1.8)", "false"),
                ("![,1.8)", "true"),
                ("[,1.8)", "false"),
                ("[,1.8]", "true"),
                ("![,1.8]", "false"),
                ):
            client = self._mock_client(
                COM_TEST_PROFILE_2.replace("@JDK@", input))
            pom = Pom("com.test:profile:1.0.0", client)
            actual = pom.properties["default_profile"]
            assert expected == actual, \
                "%s: Wanted %s, got %s" % (input, expected, actual)

COM_TEST_PROFILE_1 = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>profile</artifactId>
    <version>1.0.0</version>
    <profiles>
        <profile>
            <activation>
                <activeByDefault>true</activeByDefault>
            </activation>
            <properties>
                <active_profile>true</active_profile>
            </properties>
            <dependencies>
                <dependency>
                    <groupId>com.test</groupId>
                    <artifactId>project1</artifactId>
                </dependency>
            </dependencies>
            <dependencyManagement>
                <dependencies>
                    <dependency>
                        <groupId>com.test</groupId>
                        <artifactId>project1</artifactId>
                        <version>1.0.0</version>
                    </dependency>
                </dependencies>
            </dependencyManagement>
        </profile>
    </profiles>
</project>
"""

COM_TEST_DEP = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>project1</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>com.test</groupId>
            <artifactId>project1</artifactId>
            <version>1.0.0</version>
        </dependency>
        <dependency>
            <groupId>com.test</groupId>
            <artifactId>project2</artifactId>
            <version>1.0.0</version>
            <scope>runtime</scope>
        </dependency>
    </dependencies>
</project>
"""

COM_TEST_PROFILE_2 = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>profile</artifactId>
    <version>1.0.0</version>
    <profiles>
        <profile>
            <activation>
                <activeByDefault>true</activeByDefault>
            </activation>
            <properties>
                <default_profile>false</default_profile>
            </properties>
        </profile>
        <profile>
            <activation>
                <jdk>@JDK@</jdk>
            </activation>
            <properties>
                <default_profile>true</default_profile>
            </properties>
        </profile>
    </profiles>
</project>
"""

COM_TEST_PROJECT1 = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>project1</artifactId>
    <version>1.0.0</version>
</project>
"""

COM_TEST_PROJECT2 = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>project2</artifactId>
    <version>1.0.0</version>
</project>
"""

COM_TEST_PROJECT3 = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>project1</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>com.test</groupId>
            <artifactId>project2</artifactId>
            <version>[1.0,2.0)</version>
        </dependency>
    </dependencies>
</project>
"""

COM_TEST_PROJECT4 = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>project1</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>com.test</groupId>
            <artifactId>project2</artifactId>
            <version>release</version>
        </dependency>
    </dependencies>
</project>
"""

COM_TEST_METADATA = """\
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
    <groupId>com.test</groupId>
    <artifactId>project2</artifactId>
    <versioning>
        <latest>2.0.0</latest>
        <release>1.0.0</release>
        <versions>
            <version>2.0.0</version>
            <version>1.0.0</version>
        </versions>
    </versioning>
</metadata>
"""

COM_TEST_BOM2 = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.test</groupId>
  <artifactId>bom2</artifactId>
  <version>2.0.0</version>
  <packaging>pom</packaging>
  <properties>
    <project1Version>2.0.0</project1Version>
  </properties>
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>com.test</groupId>
        <artifactId>project1</artifactId>
        <version>${project1Version}</version>
        <optional>true</optional>
      </dependency>
    </dependencies>
  </dependencyManagement>
  <modules>
    <module>parent</module>
  </modules>
</project>
"""

COM_TEST_BOM = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.test</groupId>
  <artifactId>bom</artifactId>
  <version>1.0.0</version>
  <packaging>pom</packaging>
  <properties>
    <project1Version>1.0.0</project1Version>
    <project2Version>1.0.0</project2Version>
  </properties>
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>com.test</groupId>
        <artifactId>project1</artifactId>
        <version>${project1Version}</version>
      </dependency>
      <dependency>
        <groupId>com.test</groupId>
        <artifactId>project2</artifactId>
        <version>${project1Version}</version>
      </dependency>
    </dependencies>
  </dependencyManagement>
  <modules>
    <module>parent</module>
  </modules>
</project>
"""

COM_TEST_USE = """\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.test</groupId>
  <artifactId>use</artifactId>
  <version>1.0.0</version>
  <packaging>jar</packaging>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>com.test</groupId>
        <artifactId>bom</artifactId>
        <version>1.0.0</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
      <dependency>
        <groupId>com.test</groupId>
        <artifactId>bom2</artifactId>
        <version>2.0.0</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.test</groupId>
      <artifactId>project1</artifactId>
    </dependency>
    <dependency>
      <groupId>com.test</groupId>
      <artifactId>project2</artifactId>
      <optional>true</optional>
    </dependency>
  </dependencies>
</project>
"""

IMPORT_DEPS_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>foo</groupId>
    <artifactId>bar</artifactId>
    <version>1</version>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>foo</groupId>
                <artifactId>parent</artifactId>
                <version>1</version>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>foo</groupId>
                <artifactId>baz</artifactId>
                <version>1</version>
            </dependency>
            <dependency>
                <groupId>foo</groupId>
                <artifactId>spam</artifactId>
                <version>1</version>
                <scope>compile</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
"""

PREREQUISITES_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>foo.org</groupId>
    <artifactId>bar</artifactId>
    <version>1</version>
    <prerequisites>
        <one>prereq1</one>
        <two>prereq2</two>
    </prerequisites>
</project>
"""

RELOCATION_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>foo.org</groupId>
    <artifactId>bar</artifactId>
    <version>1</version>
    <distributionManagement>
        <relocation>
            <groupId>foo</groupId>
        </relocation>
    </distributionManagement>
</project>
"""

RELOCATION_2 = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>foo</groupId>
    <artifactId>baz</artifactId>
    <version>1</version>
    <distributionManagement>
        <relocation>
            <artifactId>bar</artifactId>
        </relocation>
    </distributionManagement>
</project>
"""

RELOCATION_3 = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>foo</groupId>
    <artifactId>bar</artifactId>
    <version>alpha</version>
    <distributionManagement>
        <relocation>
            <version>1</version>
        </relocation>
    </distributionManagement>
</project>
"""

RELOCATION_4 = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>foo.org</groupId>
    <artifactId>baz</artifactId>
    <version>alpha</version>
    <distributionManagement>
        <relocation>
            <groupId>foo</groupId>
            <artifactId>bar</artifactId>
            <version>1</version>
        </relocation>
    </distributionManagement>
</project>
"""

FOO_BAR_1_POM = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>foo</groupId>
        <artifactId>parent</artifactId>
        <version>1</version>
    </parent>
    <artifactId>bar</artifactId>
    <properties>
        <bazChild>${bazVersion}</bazChild>
        <resolveProp>resolve</resolveProp>
    </properties>
</project>
"""

FOO_PARENT_1_POM = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>foo</groupId>
    <artifactId>parent</artifactId>
    <version>1</version>
    <properties>
        <parentProp>${resolveProp}</parentProp>
        <bazVersion>baz version string
</bazVersion>
    </properties>
</project>
"""
