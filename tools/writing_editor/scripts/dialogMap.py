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

from PyQt4 import QtGui, QtCore
from scripts.parser import Parser


class DialogMap(QtGui.QTreeWidget):
    """
    The dialog map which will show the flow of the dialog
    """
    def __init__(self, settings, main_edit, parent):
        """
        Initialize the dialog map
        @type settings: settings.Settings
        @param settings: the settings for the editor
        @type main_edit: QtGui.QTextEdit
        @param main_edit: The main text editor
        @type parent: Any Qt widget
        @param parent: The widgets' parent
        @return: None
        """
        QtGui.QWidget.__init__(self, parent)
        
        self.settings = settings
        self.parent = parent
        self.resize(int(self.settings.res_width), int(self.settings.res_height))
        self.parser = Parser(main_edit, self.handleResult)

        self.parentItem = None
        self.inOption = False

        self.setColumnCount(1)
        self.setEditTriggers(self.NoEditTriggers)
        self.setHeaderLabel("")
        
    def handleResult(self, result, type_):
        """
        Take the result, determine where to put it in the dialog map, then put it there
        @type result: string
        @param result: the result to be handled
        @type type_: string
        @param type_: the type of result
        @return: None
        """
        text = result.split(' ')

        if (type_ == "SCRIPTNAME"):
            self.setHeaderLabel(text[1])

        elif (type_ == "SAY"):
            sayText = text[0] + " says " + text[2]
            self.sayItem = QtGui.QTreeWidgetItem()
            self.sayItem.setText(0, sayText)
            self.insertItem(self.sayItem)

        elif (type_ == "ATTACK"):
            attackText = text[0] + " attacks " + text[2]
            self.attackItem = QtGui.QTreeWidgetItem()
            self.attackItem.setText(0, attackText)
            self.insertItem(self.attackItem)

        elif (type_ == "OPTION"):
            optionText = "Option " + text[1]
            self.optionItem = QtGui.QTreeWidgetItem()
            self.optionItem.setText(0, optionText)
            self.insertItem(self.optionItem)
            self.parentItem = self.optionItem
            self.inOption = True

        elif (self.inOption and type_ == "."):
            option_text = result.split('.')
            itemText = option_text[0] + ': ' + option_text[1]
            self.optionItem = QtGui.QTreeWidgetItem()
            self.optionItem.setText(0, itemText)
            self.parentItem.addChild(self.optionItem)

        elif (type_ == "ENDOPTION"):
            self.inOption = False

    def insertItem(self, item):
        """
        Insert an item at the correct place in the dialog tree
        @type item: QtGui.QTreeWidgetItem
        @param item: the item to insert
        @return: None
        """
        if (self.parentItem == None):
            self.insertTopLevelItem(self.topLevelItemCount(), item)
        else:
            self.parentItem.addChild(item)

    def clear(self):
        """
        Clear the dialog map
        """
        self.setHeaderLabel("")
        self.invisibleRootItem().takeChildren()
