# becmd/net.py
# ============
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

import requests
import requests_cache.core


log = logging.getLogger(__name__)


#: Default amount of time is seconds to wait when emitting a network request.
DEFAULT_REQUEST_TIMEOUT = 15.0


def cache_setup(name, clear=False):
    """Setup caching for all requests made by the ``requests`` package.


    :param name: Path to the file keeping track of the requests.
    :type name: python:str

    :param clear: Whether to clear already cached entries or not.
    :type clear: python:bool

    """
    log.debug("Enter: cache_setup(location={!r}, clear={!r})".format(
        name, clear
    ))

    log.info("Install cache file at '{}.sqlite'.".format(name))
    requests_cache.core.install_cache(backend='sqlite', cache_name=name)
    if clear:
        log.info("Clear cached entries from file '{}.sqlite'.".format(name))
        requests_cache.core.clear()
    else:
        log.info("Clean expired cache entries from file '{}.sqlite'.".format(
            name
        ))
        requests_cache.core.remove_expired_responses()

    log.debug("Exit: cache_setup(location={!r}, clear={!r}) -> None".format(
        name, clear
    ))
