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
import sys
import logging
import argparse

from becmd import __version__


log = logging.getLogger(__name__)


#: Name of the command line utility program.
PROG_NAME = 'becmd'
#: Short description text for the program.
PROG_DESCRIPTION = (
    "Command line manager for Beyond Security beSECURE vulnerability scanner."
)


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

    return vars(parser.parse_args(args))


def main():
    """Entry point of the *becmd* program."""
    opts = parse_args(sys.argv[1:])


if __name__ == '__main__':
    main()
