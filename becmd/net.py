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

import becmd.errors


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


def get(url, timeout=DEFAULT_REQUEST_TIMEOUT, insecure=False):
    """Send an HTTP GET request using provided URL. A JSON response is expected
    from the remote host.


    :param url: The URL to send the HTTP request to.
    :type url: python:str

    :param timeout: How many seconds to wait for the server to send data before
                    giving up.
    :type timeout: python:float

    :param insecure: Whether to apply the security checks when establishing the
                     connection with the remote host.
    :type insecure: python:bool


    :returns: Parsed JSON response from the remote host.
    :rtype: python:dict

    """
    log.debug("Enter: get(url={!r}, timeout={!r}, insecure={!r})".format(
        url, timeout, insecure
    ))

    data = None
    try:
        r = requests.get(str(url), timeout=timeout, verify=not insecure)
        r.raise_for_status()
    except requests.exceptions.RequestException:
        log.exception("Could not get URL: {!s}.".format(url))
        raise becmd.errors.NetworkError
    else:
        if r.from_cache:
            log.debug("Using response from cache for URL: {!s}.".format(url))
        data = r.json()
    finally:
        log.debug("Exit: get(url={!r}, timeout={!r}, insecure={!r}) -> {!r}".format(
            url, timeout, insecure, data
        ))

    return data
