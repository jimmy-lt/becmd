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

import becmd.api
import becmd.net
import becmd.errors

from becmd import __version__
from becmd.utils import mapping_expand, mapping_update
from becmd.schema import (
    CONFIG_RESERVED_KEYS,
    LOGGING_LEVELS,
    CommonLogging,
    Config,
    Host,
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


def get_argparser():
    """Generate a command line argument parser for the *becmd* command line
    utility.


    :returns: The generated command line argument parser.
    :rtype: ~argparse.ArgumentParser

    """
    log.debug("Enter: get_argparser()")

    parser = argparse.ArgumentParser(prog=PROG_NAME,
                                     description=PROG_DESCRIPTION)

    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    parser.add_argument('-H', '--host',
                        type=str,
                        dest='hosts.default',
                        metavar='HOST',
                        help="remote host to connect to")

    parser.add_argument('-K', '--api-key',
                        type=str,
                        dest='hosts.api_key',
                        metavar='API_KEY',
                        help="authorization token to the remote host's REST API")

    parser.add_argument('-L', '--log-level',
                        type=str,
                        choices=LOGGING_LEVELS,
                        dest='logging.level',
                        metavar='LEVEL',
                        help="minimum severity level of the emitted log messages")

    parser.add_argument('-R', '--refresh',
                        action='store_true',
                        help="set metadata as expired before running the command")

    parser.add_argument('-W', '--wait',
                        type=float,
                        dest='hosts.timeout',
                        metavar='TIMEOUT',
                        help="maximum time in seconds that you allow becmd to connect with remote host")

    parser.add_argument('-X', '--no-cache',
                        action='store_false',
                        default=None,
                        dest='hosts.use_cache',
                        help="disable caching of the responses from the remote host")

    parser.add_argument('-c', '--config',
                        type=str,
                        help="path to the becmd configuration file")

    # Only long options to disable security options.
    parser.add_argument('--no-https',
                        action='store_false',
                        default=None,
                        dest='hosts.use_https',
                        help="disable usage of HTTPS to communicate with remote host")

    parser.add_argument('--insecure-tls',
                        action='store_true',
                        default=None,
                        dest='hosts.insecure_tls',
                        help="proceed even for TLS connections considered insecure")

    log.debug("Exit: get_argparser() -> {!r}".format(parser))
    return parser


def parse_args(parser, args, partial=False):
    """Parse a list of arguments using a given :class:`~argparse.ArgumentParser`
    object.


    :param parser: The command line parser to parse the arguments with.
    :type parser: ~argparse.ArgumentParser

    :param args: List of arguments to be parsed.
    :type args: python:list

    :param partial: When ``True``, parser can parse all given arguments
                    otherwise if ``False``, only a subset of the arguments can
                    be parsed. Defaults to ``False``.
    :type partial: python:bool


    :returns: A dictionary with parsed arguments.
    :rtype: python:dict

    """
    log.debug("Enter: parse_args(parser={!r}, args{!r}, partial={!r})".format(
        parser, args, partial
    ))

    if partial:
        namespace = parser.parse_known_args(args)[0]
    else:
        namespace = parser.parse_args(args)

    opts = mapping_expand({
        k: v for k, v in vars(namespace).items() if v is not None
    })

    log.debug(
        "Exit: parse_args(parser={!r}, args{!r}, partial={!r}) -> {!r}".format(
            parser, args, partial, opts
        )
    )
    return opts


def read_config(name=None, update=None):
    """Read a ``becmd`` configuration file.


    :param name: File name to load the configuration from. When not given, try
                 to load the configuration from the default locations.
    :type name: python:str

    :param update: Additional data with which to update the final configuration.
    :type update: python:dict


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

    cfg = {k: v for k, v in data.items() if k in CONFIG_RESERVED_KEYS}
    cfg.update({
        'hosts': {
            k: v for k, v in data.items() if k not in CONFIG_RESERVED_KEYS
        },
    })

    if update is not None:
        mapping_update(cfg, update)

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


def cache_from_config(host, clear=False):
    """Setup caching from given host configuration.


    :param host: A dictionary with the host configuration.
    :type host: python:dict

    :param clear: Whether to clear already cached entries or not.
    :type clear: python:bool

    """
    log.debug("Enter: cache_from_config(host={!r}, clear={!r})".format(
        host, clear
    ))

    if not host.get('use_cache'):
        return

    cache_d = BaseDirectory.save_cache_path(PROG_NAME)
    becmd.net.cache_setup(os.path.join(cache_d, host['host']), clear=clear)

    log.debug("Exit: cache_from_config(host={!r}, clear={!r}) -> None".format(
        host, clear
    ))


def endpoint_from_config(config, host):
    """Generate a Beyond Security beSECURE endpoint for given host out of the
    provided configuration


    :param config: A dictionary with the configuration passed to ``becmd``.
    :type config: python:dict

    :param host: A dictionary with the host configuration.
    :type host: python:dict


    :returns: A Beyond Security beSECURE API endpoint URL generator.
    :rtype: ~becmd.api.Endpoint

    """
    log.debug("Enter: endpoint_from_config(config={!r}, host={!r})".format(
        config, host
    ))

    api = config.get('api', {}).copy()
    params = api.pop('params', {})
    endpoint = becmd.api.Endpoint(host, **api, **params)

    log.debug(
        "Exit: endpoint_from_config(config={!r}, host={!r}) -> {!r}".format(
            config, host, endpoint
        )
    )
    return endpoint


def host_from_config(config, name=None, update=None):
    """Build a host configuration data structure from given configuration.


    :param config: A dictionary with the configuration passed to ``becmd``.
    :type config: python:dict

    :param name: Host name identifier to generate the configuration for. When
                 not given, generate the configuration for the default host.
    :type name: python:str

    :param update: Additional data with which to update the final configuration.
    :type update: python:dict


    :returns: A merged host configuration.
    :rtype: python:dict

    """
    log.debug(
        "Enter: host_from_config(config={!r}, name={!r}, update={!r})".format(
            config, name, update
        )
    )

    common = config.get(PROG_NAME, {}).get('hosts', {})
    name = name or common.get('default', '')

    # Setup host configuration.
    host = common.copy()
    host.update(config.get('hosts', {}).get(name, {}))
    if update is not None:
        host.update(update)
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
            "Exit: host_from_config(config={!r}, name={!r}, update={!r}) -> {!r}".format(
                config, name, update, host
            )
        )


def logging_from_config(config, update=None):
    """Setup logging from given configuration.


    :param config: A dictionary with the configuration passed to ``becmd``.
    :type config: python:dict

    :param update: Additional data with which to update the final configuration.
    :type update: python:dict

    """
    log.debug(
        "Enter: logging_from_config(config={!r}, update={!r})".format(
            config, update
        )
    )

    common = config.get(PROG_NAME, {}).get('logging', {})
    if update is not None:
        mapping_update(common, update)

    # Validate logging configuration.
    try:
        validate(CommonLogging, common)
    except becmd.errors.ValidationError:
        log.warning("Could not validate logging configuration.")
        raise
    else:
        logging.basicConfig(**common)
    finally:
        log.debug(
            "Exit: logging_from_config(config={!r}, update={!r}) -> None".format(
                config, update
            )
        )


def main():
    """Entry point of the *becmd* program."""
    parser = get_argparser()
    opts = parse_args(parser, sys.argv[1:], partial=True)
    try:
        cfg = read_config(opts.get('config'), update={PROG_NAME: opts})
    except becmd.errors.ValidationError:
        sys.exit(1)

    logging_from_config(cfg, update=opts.get('logging'))
    if not cfg[PROG_NAME]['hosts'].get('default'):
        log.error("Could not find a host to connect to.")
        sys.exit(1)

    # Get host configuration.
    try:
        host = host_from_config(cfg, update=opts.get('hosts'))
    except becmd.errors.ValidationError:
        sys.exit(1)

    cache_from_config(host, opts.get('refresh'))
    try:
        interface = becmd.net.get(
            becmd.api.InterfaceEndpoint(host),
            timeout=host['timeout'],
            insecure=host['insecure_tls']
        )
    except becmd.errors.NetworkError:
        log.error("Could not fetch JSON API interface for host: {}".format(
            host['host']
        ))
        sys.exit(1)

    becmd.api.argparser_from_interface(parser, interface)
    opts = parse_args(parser, sys.argv[1:], partial=False)
    endpoint = endpoint_from_config(opts, host)


if __name__ == '__main__':
    main()
