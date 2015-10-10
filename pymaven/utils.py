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


from functools import wraps
from urlparse import urlsplit, urlunsplit
import posixpath


def memoize(name):
    def wrap(func):
        @wraps(func)
        def wrapper(slf, *args, **kwargs):
            if getattr(slf, name) is None:
                setattr(slf, name, func(slf, *args, **kwargs))
            return getattr(slf, name)
        return wrapper
    return wrap


def pad(seq, target_length, padding=None):
    """Extend the sequence *seq* with *padding* (default: None) if the length
    of *seq* is less than *target_length*. Modifies *seq* in place.

    >>> pad([], 5, 1)
    [1, 1, 1, 1, 1]
    >>> pad([1, 2, 3], 7)
    [1, 2, 3, None, None, None, None]
    >>> pad([1, 2, 3], 2)
    [1, 2, 3]

    :param list seq: list to padding
    :param int target_length: length to pad *seq* TestCommand
    :param padding: value to pad *seq* with
    :return: *seq* with appropriate padding
    """
    length = len(seq)
    if length < target_length:
        seq.extend([padding] * (target_length - length))
    return seq


def _first_of_each(*args, **kwargs):
    default = kwargs.get("default")
    return [next((s for s in sequence if s), default) for sequence in args]


def urljoin(*parts):
    """Join urls in a less surprising manner than urlparse.urljoin

    Inspired by this stackoverflow question:
    http://codereview.stackexchange.com/questions/13027/joining-url-path-components-intelligently

    >>> urljoin('http://foo.com', 'https://foo.com')
    'http://foo.com/'
    >>> urljoin('http://foo.com', 'bar')
    'http://foo.com/bar'
    >>> urljoin('http://foo.com/bar', 'baz')
    'http://foo.com/bar/baz'
    >>> urljoin('http://foo.com/bar', 'baz/spam')
    'http://foo.com/bar/baz/spam'
    >>> urljoin('http://foo.com', '/bar')
    'http://foo.com/bar'
    >>> urljoin('http://foo.com', 'bar', '?param=1&other=2')
    'http://foo.com/bar?param=1&other=2'
    >>> urljoin('http://foo.com', 'bar', '?param=1&other=2', '?not=3')
    'http://foo.com/bar?param=1&other=2'
    >>> urljoin('http://foo.com', 'bar', '#anchor', '#not')
    'http://foo.com/bar#anchor'
    >>> urljoin('http://foo.com', 'bar', '?param=1&other=2', '#anchor')
    'http://foo.com/bar?param=1&other=2#anchor'
    >>> urljoin('http://foo.com', 'bar', '?param=1&other=2', '#anchor',
    ...         '?not=3')
    'http://foo.com/bar?param=1&other=2#anchor'
    >>> urljoin('http://foo.com', 'bar', '?param=1&other=2', '#anchor', '#not')
    'http://foo.com/bar?param=1&other=2#anchor'
    >>> urljoin('http://foo.com', 'bar', '?param=1&other=2', '#anchor', '#not',
    ...         '?not=3')
    'http://foo.com/bar?param=1&other=2#anchor'
    >>> urljoin('#anchor', '?param=1&other=2', 'bar', 'http://foo.com')
    'http://foo.com/bar?param=1&other=2#anchor'
    """
    schemes, netlocs, paths, queries, fragments = \
        zip(*[urlsplit(part) for part in parts])
    scheme, netloc, query, fragment = _first_of_each(schemes, netlocs, queries,
                                                     fragments)
    path = posixpath.normpath(posixpath.join(*paths) or '/')
    return urlunsplit((scheme, netloc, path, query, fragment))
