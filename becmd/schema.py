# becmd/schema.py
# ===============
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
import logging

import validx.exc
from validx import Dict, Str

import becmd.errors


log = logging.getLogger(__name__)


#: Set of reserved configuration keys.
CONFIG_RESERVED_KEYS = {'becmd', 'hosts', }

#: Host configuration keys.
HOST_CONFIG_KEYS = {'api_key', 'host'}

#: Regular expression excluding all reserved configuration keys.
RESERVED_KEYS_PATTERN = r'^(?:(?!{}).+)$'.format(r'|'.join(CONFIG_RESERVED_KEYS))


#: Validation schema for the general configuration statements.
Program = Dict(
    {
        'default': Str(pattern=RESERVED_KEYS_PATTERN),
    },
    optional=['default', ],
)

#: Validation schema for a host configuration.
Host = Dict(
    {
        'api_key': Str(nullable=False),
        'host': Str(pattern=r'^[0-9A-Za-z\._-]+$', nullable=False),
    },
)


#: Host validator where the command line arguments are optional.
HostOpt = Host.clone()
HostOpt.optional = ['api_key', 'host']


#: Validation schema for a set of host configurations.
HostConfig = Dict(extra=(
    Str(pattern=RESERVED_KEYS_PATTERN, nullable=False), HostOpt
))

#: Validation schema for a becmd configuration.
Config = Dict(
    {
        'becmd': Program,
        'hosts': HostConfig,
    },
    optional=['becmd', 'hosts'],
)


def validate(schema, obj):
    """Validate a given object against its validation schema.


    :param schema: Data structure validation schema.
    :type schema: ~validx.Validator

    :param obj: The object data structure to be validated.
    :type obj: ~typing.Any


    :returns: The validated object data structure.
    :rtype: ~typing.Any


    :raises becmd.errors.ValidationError:
        When the schema fails to validate given object.

    """
    log.debug("Enter: validate(schema={!r}, obj={!r})".format(schema, obj))

    out = obj
    try:
        out = schema(obj)
    except validx.exc.ValidationError as errors:
        errors.sort()
        for ctx, msg in validx.exc.format_error(errors):
            log.error('{}: {}'.format(ctx, msg))

        raise becmd.errors.ValidationError
    else:
        return out
    finally:
        log.debug("Exit: validate(schema={!r}, obj={!r}) -> {!r}".format(
            schema, obj, out
        ))
