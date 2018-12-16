# becmd/utils.py
# ==============
#
# Copying
# -------
#
# Copyright (c) 2018 becmd authors.
#
# This file is part of the *becmd* project.
#
# becmd is a free software project. You can redistribute it and/or
# modify if under the terms of the MIT License.
#
# This software project is distributed *as is*, WITHOUT WARRANTY OF ANY
# KIND; including but not limited to the WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE and NONINFRINGEMENT.
#
# You should have received a copy of the MIT License along with becmd.
# If not, see <http://opensource.org/licenses/MIT>.
#
from collections.abc import Mapping


def mapping_expand(mapping, separator='.'):
    """Transform a flat mapping data structure where the keys are a separated
    hierarchical sequence into a nested mapping structure. The mapping keys are
    expected to be strings.

    .. code-block::

        >>> f = {'a': 1, 'b.c.d': 2, 'e.f.g.h': 3}
        >>> mapping_expand(f)
        {'a': 1, 'b': {'c': {'d': 2}}, 'e': {'f': {'g': {'h': 3}}}}


    :param mapping: The flatting mapping data structure to be expanded.
    :type mapping: ~collections.abc.Mapping

    :param separator: The value separating each key hierarchy.
    :type separator: python:str


    :returns: The expended mapping.
    :rtype: ~collections.abc.Mapping

    """
    root = mapping.__class__()
    for k, v in mapping.items():
        *parts, last = k.split(separator)

        d = root
        for p in parts:
            d = d.setdefault(p, mapping.__class__())

        d[last] = v

    return root


def mapping_update(mapping, *args, **kwargs):
    """Deep update a nested mapping data structure.

    Unlike Python's ``dict.update()`` method, if the same key is present in
    both the target and this mapping and the value is a dictionary, it
    will be updated instead of being overwritten.

    .. code-block:: python

        >>> d1 = {'baz': {'foo': 'foo'}, 'fizz': 'buzz'}
        >>> d2 = {'baz': {'bar': 'bar'}, 'fizz': 'fizzbuzz'}
        >>> mapping_update(d1, d2)
        {'baz': {'foo': 'foo', 'bar': 'bar'}, 'fizz': 'fizzbuzz'}


    :param mapping: The mapping data structure to be updated.
    :type mapping: ~collections.abc.Mapping


    :returns: The updating mapping.
    :rtype mapping: ~collections.abc.Mapping

    """
    for k, v in mapping.__class__(*args, **kwargs).items():
        if isinstance(v, Mapping):
            mapping[k] = mapping_update(mapping.get(k, {}), v)
        else:
            mapping[k] = v

    return mapping
