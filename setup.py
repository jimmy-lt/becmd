# setup.py
# ========
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
import os

from contextlib import suppress
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION = ''
with suppress(OSError), open(os.path.join(HERE, 'README.rst')) as fp:
    LONG_DESCRIPTION = fp.read()


setup(
    name='becmd',
    version='0.0.0-alpha0',
    license='MIT',
    url='https://github.com/spack971/becmd',

    author='Jimmy Thrasibule',
    author_email='dev@jimmy.lt',

    description="Command line manager for Beyond Security beSECURE vulnerability scanner.",
    long_description=LONG_DESCRIPTION,
    keywords='command-line api vulnerability-scanner beyond security besecure',

    packages=find_packages(),

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 1 - Planning',

        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',

        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3.7',

        'Topic :: Security',
        'Topic :: Utilities',
    ],

    install_requires=[
        'semver',
    ],

    entry_points={
        'console_scripts': [
            'becmd = becmd.__main__:main',
        ],
    },
)
