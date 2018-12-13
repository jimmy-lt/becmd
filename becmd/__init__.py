# becmd/__init__.py
# ================
#
# Copying
# -------
#
# Copyright (c) 2018 becmd authors and contributors.
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
# You should have received a copy of the MIT License along with
# becmd. If not, see <http://opensource.org/licenses/MIT>.
#
import semver


#: Semantic version information of becmd.
VERSION_INFO = semver.VersionInfo(
    major=0,
    minor=0,
    patch=0,
    prerelease='alpha0',
    build=None
)

#: Project version string.
__version__ = str(VERSION_INFO)
