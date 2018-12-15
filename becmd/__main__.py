# becmd/__main__.py
# =================
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
import os
import sys
import logging

import toml
import argparse

from xdg import BaseDirectory

import becmd.errors
from becmd import __version__
from becmd.schema import (
    CONFIG_RESERVED_KEYS,
    HOST_CONFIG_KEYS,
    LOGGING_CONFIG_KEYS,
    LOGGING_LEVELS,
    Config,
    Host,
    Logging,
    validate,
)


log = logging.getLogger(__name__)


#: Name of the command line utility program.
PROG_NAME = 'becmd'
#: Short description text for the program.
PROG_DESCRIPTION = (
    "Command line manager for Beyond Security beSECURE vulnerability scanner."
)
#: File name of the program configuration file.
PROG_CONFIG_NAME = 'config.toml'


def parse_args(args):
    """Parse the arguments passed to the *becmd* program.


    :param args: List of arguments passed to the program.
    :type args: python:list


    :returns: A dictionary with the parsed arguments.
    :rtype: python:dict

    """
    parser = argparse.ArgumentParser(prog=PROG_NAME,
                                     description=PROG_DESCRIPTION)

    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    parser.add_argument('-H', '--host',
                        type=str,
                        dest='default',
                        metavar='HOST',
                        help="remote host to connect to")

    parser.add_argument('-K', '--api-key',
                        type=str,
                        dest='cmd.api_key',
                        metavar='API_KEY',
                        help="authorization token to the remote host's REST API")

    parser.add_argument('-L', '--log-level',
                        type=str,
                        choices=LOGGING_LEVELS,
                        dest='cmd.level',
                        metavar='LEVEL',
                        help="minimum severity level of the emitted log messages")

    parser.add_argument('-c', '--config',
                        type=str,
                        help="path to the becmd configuration file")

    return {
        k: v
        for k, v in vars(parser.parse_args(args)).items()
        if v is not None
    }


def read_config(name=None):
    """Read a ``becmd`` configuration file.


    :param name: File name to load the configuration from. When not given, try
                 to load the configuration from the default locations.
    :type name: python:str


    :returns: A dictionary with parsed configuration statements.
    :rtype: python:dict

    """
    log.debug("Enter: read_config(name={!r})".format(name))

    # Try to find a configuration file.
    path = name
    if path is None:
        try:
            path = os.path.join(
                next(BaseDirectory.load_config_paths(PROG_NAME)),
                PROG_CONFIG_NAME
            )
            log.info("Found configuration file: '{}'.".format(path))
        except StopIteration:
            log.info("No configuration file found.")

    # Load configuration file.
    data = {}
    if path:
        try:
            with open(path, 'r') as fp:
                data = toml.load(fp)
        except IOError:
            log.warning("Could not read configuration file: '{}'.".format(path))

    cfg = {
        PROG_NAME: data.get(PROG_NAME, {'logging': {}}),
        'hosts': {
            k: v for k, v in data.items() if k not in CONFIG_RESERVED_KEYS
        },
    }

    # Validate configuration.
    try:
        cfg = validate(Config, cfg)
    except becmd.errors.ValidationError:
        log.error("Could not validate configuration file: '{}'.".format(path))
        raise
    else:
        return cfg
    finally:
        log.debug("Exit: read_cfg(name={!r}) -> {!r}".format(name, cfg))


def host_from_config(config, name=None, cmd_prefix='cmd.'):
    """Build a host configuration data structure from given configuration.

    The host configuration is built in the following order:

    1. Common configuration.
    2. Host specific configuration.
    3. Command line statements.


    :param config: A dictionary with the configuration passed to ``becmd``.
    :type config: python:dict

    :param name: Host name identifier to generate the configuration for. When
                 not given, generate the configuration for the default host.
    :type name: python:str

    :param cmd_prefix: Prefix used to denote command line arguments.
    :type cmd_prefix: python:str


    :returns: A merged host configuration.
    :rtype: python:dict

    """
    log.debug(
        "Enter: host_from_config(config={!r}, name={!r}, cmd_prefix={!r})".format(
            config, name, cmd_prefix
        )
    )

    common = config.get(PROG_NAME, {})
    name = name or common.get('default', '')

    # Setup host configuration.
    host = {k: v for k, v in common.items() if k in HOST_CONFIG_KEYS}
    host.update(config.get('hosts', {}).get(name, {}))
    host.update({
        k.lstrip(cmd_prefix): v
        for k, v in common.items()
        if k.lstrip(cmd_prefix) in HOST_CONFIG_KEYS
    })
    host['host'] = host.get('host') or name

    # Validate host configuration.
    try:
        host = validate(Host, host)
    except becmd.errors.ValidationError:
        log.error("Could not validate host: {}.".format(name))
        raise
    else:
        return host
    finally:
        log.debug(
            "Exit: host_from_config(config={!r}, name={!r}, cmd_prefix={!r}) -> {!r}".format(
                config, name, cmd_prefix, host
            )
        )


def logging_from_config(config, cmd_prefix='cmd.'):
    """Setup logging from given configuration.

    The configuration is built in the following order:

    1. Common configuration.
    2. Command line statements.


    :param config: A dictionary with the configuration passed to ``becmd``.
    :type config: python:dict

    :param cmd_prefix: Prefix used to denote command line arguments.
    :type cmd_prefix: python:str

    """
    log.debug(
        "Enter: logging_from_config(config={!r}, cmd_prefix={!r})".format(
            config, cmd_prefix
        )
    )

    common = config.get(PROG_NAME, {}).get('logging', {})
    common.update({
        k.lstrip(cmd_prefix): v
        for k, v in config.get(PROG_NAME, {}).items()
        if k.lstrip(cmd_prefix) in LOGGING_CONFIG_KEYS
    })

    # Validate logging configuration.
    try:
        validate(Logging, common)
    except becmd.errors.ValidationError:
        log.warning("Could not validate logging configuration.")
        raise
    else:
        logging.basicConfig(**common)
    finally:
        log.debug(
            "Exit: logging_from_config(config={!r}, cmd_prefix={!r}) -> None".format(
                config, cmd_prefix
            )
        )


def main():
    """Entry point of the *becmd* program."""
    opts = parse_args(sys.argv[1:])
    try:
        cfg = read_config(opts.get('config'))
    except becmd.errors.ValidationError:
        sys.exit(1)

    # Inject command line options into the configuration.
    cfg.setdefault(PROG_NAME, {}).update(opts)
    logging_from_config(cfg)

    if not cfg[PROG_NAME].get('default'):
        log.error("Could not find a host to connect to.")
        sys.exit(1)

    # Get host configuration.
    try:
        host = host_from_config(cfg)
    except becmd.errors.ValidationError:
        sys.exit(1)


if __name__ == '__main__':
    main()
