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
from validx import Dict, Str


#: Validation schema for a host configuration.
Host = Dict(
    {
        'api_key': Str(nullable=False),
        'host': Str(pattern=r'^[0-9A-Za-z\._-]+$', nullable=False),
    },
)

#: Validation schema for a set of host configurations.
HostConfig = Dict(extra=(Str(nullable=False), Host))

#: Validation schema for a becmd configuration.
Config = Dict(
    {
        'hosts': HostConfig,
    },
    optional=['hosts', ],
)
