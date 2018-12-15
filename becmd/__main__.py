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
from becmd.schema import Config, validate


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

    parser.add_argument('-c', '--config',
                        type=str,
                        help="path to the becmd configuration file")

    return vars(parser.parse_args(args))


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
        'hosts': {k: v for k, v in data.items()},
    }

    # Parse configuration.
    try:
        cfg = validate(Config, cfg)
    except becmd.errors.ValidationError:
        log.error("Could not validate configuration file: '{}'.".format(path))
        raise
    else:
        return cfg
    finally:
        log.debug("Exit: read_cfg(name={!r}) -> {!r}".format(name, cfg))


def main():
    """Entry point of the *becmd* program."""
    opts = parse_args(sys.argv[1:])
    try:
        cfg = read_config(opts['config'])
    except becmd.errors.ValidationError:
        sys.exit(1)


if __name__ == '__main__':
    main()
