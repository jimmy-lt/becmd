# becmd/api.json
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
from operator import itemgetter

#: List of interface keys to ignore while parsing.
INTERFACE_PRIMARY_IGNORE = {'examples', 'filters'}


def argparser_from_actions(parser, definition):
        """Update a command line parser from a Beyond Security beSECURE
        JSON API action definition.


        :param parser: The command line parser to update from the interface
                       description.
        :type parser: ~argparse.ArgumentParser

        :param definition: Description of the Beyond Security beSECURE JSON API
                      interface.
        :type definition: python:dict

        """
        sub = parser.add_subparsers(title='action',
                                    dest='action',
                                    metavar='<action>')
        # name: Name of the interface action.
        for name in sorted(definition.get('functions', [])):
            # a_def: Definition of the action.
            a_def = definition.get(name)
            if not a_def:
                continue

            # Add a parser for the action.
            action = sub.add_parser(name, help=a_def.get('description', ''))
            # i_name: Name of the action's input (parameter).
            # i_desc: Description of the action's input.
            for i_name, i_desc in a_def.get('input', {}).items():
                action.add_argument(
                    '--{}'.format(i_name.replace('_', '-')),
                    default=i_desc.get('default')
                )


def argparser_from_interface(parser, interface):
    """Update a command line argument parser from a Beyond Security beSECURE
    JSON API interface description.


    :param parser: The command line parser to update from the interface
                   description.
    :type parser: ~argparse.ArgumentParser

    :param interface: Description of the Beyond Security beSECURE JSON API
                      interface.
    :type interface: python:dict

    """
    subparser = parser.add_subparsers(title='primary',
                                      dest='primary',
                                      metavar='<primary>')
    # p_name: Name of the primary interface.
    # secondaries: List of secondary interface definitions.
    for p_name, secondaries in sorted(interface.items(), key=itemgetter(0)):
        if p_name in INTERFACE_PRIMARY_IGNORE:
            continue

        if p_name == 'version':
            parser.add_argument(
                '-A', '--api-version',
                action='version',
                version='\n'.join(
                    '{}: {}'.format(k, v)
                    for k, v in sorted(secondaries.items(), key=itemgetter(0))
                )
            )
            continue

        # Add a new parser for the primary interface.
        primary = subparser.add_parser(p_name, help=secondaries.get('description', ''))
        if secondaries.get('functions'):
            argparser_from_actions(primary, secondaries)
            continue

        p_sub = primary.add_subparsers(title='secondary',
                                       dest='secondary',
                                       metavar='<secondary>')
        # s_name: Name of the secondary interface.
        # s_def: Definition of the secondary interface.
        for s_name, s_def in sorted(secondaries.items(), key=itemgetter(0)):
            # Add a new parser for the secondary interface.
            secondary = p_sub.add_parser(s_name, help=s_def.get('description', ''))
            argparser_from_actions(secondary, s_def)
