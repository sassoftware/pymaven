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


from .artifact import Artifact
from .client import MavenClient
from .pom import Pom
from .versioning import Version, VersionRange


__all__ = ["Artifact", "MavenClient", "Pom", "Version", "VersionRange"]

__version__ = "0.3.0.dev0"

__title__ = "pymaven"
__description__ = "Maven client written in Python"
__url__ = "https://github.com/sassoftware/pymaven"

__author__ = "Walter Scheper"
__email__ = "Walter.Scheper@sas.com"

__license__ = "Apache 2.0"
__copyright__ = "Copyright (c) SAS Institute Inc"
