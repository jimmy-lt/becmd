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
import zlib
import base64
import urllib.parse

from operator import itemgetter
from contextlib import suppress
from collections.abc import MutableMapping

import becmd.net


#: List of interface keys to ignore while parsing.
INTERFACE_PRIMARY_IGNORE = {'examples', 'filters'}


class Endpoint(MutableMapping):
    """Beyond Security beSECURE API endpoint URL generator.


    :param host: Host for which to generate the endpoint URL for.
    :type host: python:dict

    :param primary: Name of the primary function to be called.
    :type primary: python:str

    :param secondary: Name of the secondary function to be called.
    :type secondary: python:str

    :param action: Name of the action to be applied by the function.
    :type action: python:str

    :param params: Additional parameters to pass to the action.
    :type params: ~typing.Any

    """
    #: List of reserved query parameters.
    _RESERVED = {'action', 'apikey', 'primary', 'secondary'}

    #: Path to the JSON API endpoint.
    PATH = '/json.cgi'


    def __init__(self, host, primary, secondary=None, action=None, **params):
        """Constructor for :class:`becmd.api.Endpoint`."""
        # Host configuration dictionary.
        self._host = host

        # Name of the primary interface.
        self._primary = primary
        # Name of the secondary interface.
        self._secondary = secondary
        # Name of the action.
        self._action = action
        # Parameters for the action.
        self._params = {}

        # Assign parameters to the action.
        for k, v in params.items():
            self[k] = v


    def __iter__(self):
        """Iterate over the six components of the endpoint's URL structure.

        The components are similar to the ones returned by
        :func:`urllib.parse.urlparse`:

        1. ``scheme``, URL scheme specifier.
        2. ``netloc``, Network location part.
        3. ``path``, Hierarchical path.
        4. ``params``, Parameters for last path element.
        5. ``query``, Query component.
        6. ``fragment``, Fragment identifier.

        """
        # scheme
        if self._host.get('use_https'):
            yield 'https'
        else:
            yield 'http'

        # netloc
        yield self._host.get('host', '')
        # path
        yield self.PATH
        # params
        yield ''

        # query
        function = {
            k: getattr(self, k)
            for k in self._RESERVED
            if getattr(self, k, None)
        }

        yield urllib.parse.urlencode({
            'apikey': self._host['api_key'],
            **function,
            **self._params,
        })

        # fragment
        yield ''


    def __len__(self):
        """Get the number of parameters given to the action.


        :returns: The number of parameters given the the endpoint's action.
        :rtype: python:int

        """
        return len(self._params)


    def __str__(self):
        """String representation of the endpoint.


        :returns: The URL to the endpoint.
        :rtype: python:str

        """
        return urllib.parse.urlunparse(self)


    def __delitem__(self, key):
        """Remove an action parameter from the endpoint.


        :param key: Name of the action parameter to be removed.
        :type key: python:str

        """
        del self._params[key]


    def __getitem__(self, key):
        """Get the value assigned to an action parameter.


        :param key: Name of the action parameter to be retrieved.
        :type key: python:str


        :returns: The value assigned the the action parameter.
        :rtype: ~typing.Any

        """
        return self._params[key]


    def __setitem__(self, key, value):
        """Add a new parameter to the action.


        :param key: Name of the parameter to be added.
        :type key: python:str

        :param value: Value to be assigned to the action parameter.
        :type value: ~typing.Any

        """
        if key in self._RESERVED:
            raise KeyError("reserved parameter name")
        self._params[key] = value


    @property
    def action(self):
        """Get the name of the action assigned to the endpoint."""
        return self._action


    @property
    def primary(self):
        """Get the name of the primary interface assigned to the endpoint."""
        return self._primary


    @property
    def secondary(self):
        """Get the name of the secondary interface assigned to the endpoint."""
        return self._secondary


    def fetch(self):
        """Query the remote host and return provided data.


        :returns: The data retrieved from the remote host.
        :rtype: ~typing.Any

        """
        data = becmd.net.get(self,
                             timeout=self._host['timeout'],
                             insecure=self._host['insecure_tls'])
        try:
            data = data['data']
        except KeyError:
            try:
                data = data['result']
            except KeyError:
                with suppress(KeyError):
                    data = zlib.decompress(
                        base64.b64decode(data['compresseddata'])
                    )

        return data


class InterfaceEndpoint(Endpoint):
    """Beyond Security beSECURE API interface endpoint URL generator.


    :param host: Host for which to generate the endpoint URL for.
    :type host: python:dict

    """

    def __init__(self, host):
        """Constructor for :class:`becmd.api.InterfaceEndpoint`."""
        super().__init__(host, primary='interface')


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
                                    dest='api.action',
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
                i_name = i_name.replace('_', '-')
                action.add_argument(
                    '--{}'.format(i_name),
                    default=i_desc.get('default'),
                    dest='api.params.{}'.format(i_name)
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
                                      dest='api.primary',
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
                                       dest='api.secondary',
                                       metavar='<secondary>')
        # s_name: Name of the secondary interface.
        # s_def: Definition of the secondary interface.
        for s_name, s_def in sorted(secondaries.items(), key=itemgetter(0)):
            # Add a new parser for the secondary interface.
            secondary = p_sub.add_parser(s_name, help=s_def.get('description', ''))
            argparser_from_actions(secondary, s_def)
