#!/usr/bin/python

#   This file is part of PARPG.

#   PARPG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   PARPG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>.

"""Composite game object classes are kept here"""

from base import *

class ImmovableContainer(GameObject, Container, Lockable, Scriptable, 
                         Trappable, Destructable):
    """Composite class that can be used for crates, chests, etc."""
    def __init__ (self, **kwargs):
        GameObject   .__init__(self, **kwargs)
        Container    .__init__(self, **kwargs)
        Lockable     .__init__(self, **kwargs)
        Scriptable   .__init__(self, **kwargs)
        Trappable    .__init__(self, **kwargs)
        Destructable .__init__(self, **kwargs)
        self.blocking = True
