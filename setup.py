# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2019 EventGhost Project <http://www.eventghost.org/>
#
# EventGhost is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# EventGhost is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with EventGhost. If not, see <http://www.gnu.org/licenses/>.

"""
This file is part of the **pyWinMCERemote**
project https://github.com/kdschlosser/pyWinMCERemote

:platform: Windows
:license: GPL version 2 or newer
:synopsis: setup program

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""


from distutils.core import setup

from pyWinMCERemote import (
    __version__,
    __author__,
    __url__,
    __description__,
    __author_email__,
    __long_description__,
    __license__
)

setup(
    name='pyWinMCERemote',
    author_email=__author_email__,
    author=__author__,
    version=__version__,
    url=__url__,
    packages=['pyWinMCERemote', 'pyWinMCERemote.IRDecoder'],
    description=__description__,
    long_description=__long_description__,
    license=__license__,
    requires=['comtypes', 'six'],
)
