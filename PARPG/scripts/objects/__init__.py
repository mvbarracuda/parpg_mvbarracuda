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
import containers
import actors

object_modules = [containers, actors,]

def getAllObjects ():
    """Returns a dictionary with the names of the concrete game object classes
    mapped to the classes themselves"""
    result = {}
    for module in object_modules:
        for class_name in module.__all__:
            result[class_name] = getattr (module,class_name)
            
    return result
