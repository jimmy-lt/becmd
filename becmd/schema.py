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
from validx import Bool, Dict, Float, Str

import becmd.net
import becmd.errors


log = logging.getLogger(__name__)


#: Set of reserved configuration keys.
CONFIG_RESERVED_KEYS = {'becmd', 'hosts', 'logging'}

#: Logging configuration keys.
LOGGING_CONFIG_KEYS = {'datefmt', 'format', 'level', 'style'}

#: List of logging levels.
LOGGING_LEVELS = {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'}
#: Logging format styles.
LOGGING_STYLES = {'%', '{', '$'}


#: Regular expression excluding all reserved configuration keys.
RESERVED_KEYS_PATTERN = r'^(?:(?!{}).+)$'.format(r'|'.join(CONFIG_RESERVED_KEYS))


#: Validation schema for a host configuration.
Host = Dict(
    {
        'api_key': Str(nullable=False),
        'host': Str(pattern=r'^[0-9A-Za-z\._-]+$', nullable=False),
        'insecure_tls': Bool(),
        'timeout': Float(),
        'use_cache': Bool(),
        'use_https': Bool(),
    },
    dispose=['default', ],
)

#: Host configuration keys.
HOST_CONFIG_KEYS = set(Host.schema)

#: Host validator where the command line arguments are optional.
OptionalHost = Host.clone()
OptionalHost.dispose = []
OptionalHost.optional = list(HOST_CONFIG_KEYS)

#: Validation schema for the common hosts configuration.
CommonHost = OptionalHost.clone(
    update={
        '/schema': {'default': Str(pattern=RESERVED_KEYS_PATTERN)},
    },
    unset={
        '/': ['host', ],
    }
)
CommonHost.defaults = {
    'insecure_tls': False,
    'timeout': becmd.net.DEFAULT_REQUEST_TIMEOUT,
    'use_cache': True,
    'use_https': True,
}
CommonHost.optional += ['default', ]

#: Validation schema for the common logger configuration.
CommonLogging = Dict(
    {
        'datefmt': Str(nullable=False),
        'format': Str(nullable=False),
        'level': Str(options=LOGGING_LEVELS, nullable=False),
        'style': Str(options=LOGGING_STYLES, nullable=False),
    },
    defaults={
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'format': '%(levelname)s: %(message)s',
        'level': 'ERROR',
        'style': '%',
    },
    optional=['datefmt', 'format', 'level', 'style'],
)

#: Validation schema for the common configuration statements.
Common = Dict(
    {
        'config': Str(nullable=False),
        'hosts': CommonHost,
        'logging': CommonLogging,
        'refresh': Bool(),
    },
    defaults={
        'hosts': CommonHost({}),
        'logging': CommonLogging({}),
    },
    optional=['config', 'hosts', 'logging', 'refresh'],
)

#: Validation schema for a set of host configurations.
ConfigHost = Dict(
    extra=(Str(pattern=RESERVED_KEYS_PATTERN, nullable=False), OptionalHost)
)

#: Validation schema for a becmd configuration.
Config = Dict(
    {
        'becmd': Common,
        'hosts': ConfigHost,
    },
    defaults={
        'becmd': Common({}),
        'hosts': ConfigHost({}),
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
