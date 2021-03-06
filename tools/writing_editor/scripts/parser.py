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

import re
from lib.pyparsing import *
from PyQt4 import QtGui, QtCore

class Parser():
    """
    The parser
    """
    def __init__(self, widget, result_function):
        """
        Initialize the parser
        @type document: QtGui.QTextEdit
        @param document: The QTextEdit
        @type result_function: function
        @param result_function: the function that handles the results
        @return: None
        """
        self.widget = widget
        self.resultFunction = result_function
        self.makeFunctions()
        self.funcs = ["SCRIPTNAME", "NPC", "CALLSECTION", "ENDSECTION", "SECTION", 
                      "SCRIPTNAME", "ENDOPTION", "OPTION", "PLAYSOUND", 
                      "SAY", "ATTACK", "RETURN", "ELIF", "IF", "ELSE", "PC", "."]

        self.func_by_name = {"NPC":self.npc, "PC":self.pc, "CALLSECTION":self.callsection,
                             "ENDSECTION":self.endsection, "SECTION": self.section,
                             "SCRIPTNAME":self.scriptname, "ENDOPTION":self.endoption,
                             "OPTION":self.option, "PLAYSOUND":self.playsound,
                             "SAY":self.say, "ATTACK":self.attack, "RETURN":self.return_,
                             "ELIF":self.elif_, "IF":self.if_, "ELSE":self.else_,
                             ".":self.option_item}


    def makeFunctions(self):
        """
        Setup all the matching functions
        @return: None
        """
        self.text = Word(alphanums)
        self.nums = Word(nums)
        self.period = Literal(".")
        self.space = Literal(" ")
        self.colon = Literal(":")
        self.quote = Literal("\"")

        self.npc = Combine(Word("NPC") + self.space + self.text)
        self.pc = Word("PC")
        self.section = Combine(Word("SECTION") + self.space + self.text)
        self.endsection = Word("ENDSECTION")
        self.callsection = Combine(Word("CALLSECTION") + self.space + self.text)
        self.scriptname = Combine(Word("SCRIPTNAME") + self.space + self.text)
        self.option = Combine(Word("OPTION") + self.space + self.text)
        self.option_item = Combine(self.nums + Optional(self.space) + self.period + Optional(self.space) + self.text)
        self.endoption = Combine(Word("ENDOPTION") + self.space + self.text)
        self.playsound = Combine(Word("PLAYSOUND") + self.space + self.quote + self.text + self.quote)
        self.say = Combine(self.text + self.space + Word("SAY") + self.space + self.quote 
                           + self.text + self.quote)
        self.attack = Combine(self.text + self.space + Word("ATTACK") + self.space + self.text)
        self.return_ = Combine(Word("RETURN") + self.space + self.text)
        self.if_ = Combine(Word("IF") + self.space + self.text + self.colon)
        self.elif_ = Combine(Word("ELIF") + self.space + self.text + self.colon)
        self.else_ = Combine(Word("ELSE") + self.colon)

        
    def findType(self, string):
        """
        Find the type of command that is in the string given
        @type string: string
        @param string: the string to find the type of
        @return: the type
        """
        type_ = None
        for func in self.funcs:
            regex = re.compile(func + "{0,1}")
            if (regex.search(str(string)) != None):
                type_ = func
                break

        return type_

    def parse(self):
        """
        Parse the text
        @return: the parsed text
        """        
        doc = self.widget.document().toPlainText()
        if (doc == ""):
            return

        for line in doc.split('\n'):
            if (line == ""):
                continue

            line_type = self.findType(line)
            try:
                command = self.func_by_name[line_type]
            except KeyError, e:
                self.createErrorBox(e)
                return

            parse = command.scanString(line)
            for result in parse:
                self.resultFunction(result[0][0], line_type)


    def createErrorBox(self, error):
        """
        Create an error box saying that the text couldn't be parsed
        @type error: KeyError
        @param error: The error that was generated
        @return: None
        """
        msg_box = QtGui.QMessageBox()
        msg_box.setText("Error while parsing")
        msg_box.setInformativeText("Could not find the type \"%s\" in self.func_by_name" % str(error))
        msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
        msg_box.setWindowTitle("Error")
        msg_box.setWindowIcon(QtGui.QIcon("data/images/error.png"))
        
        ret = msg_box.exec_()
        if (ret == QtGui.QMessageBox.Ok):
            msg_box.close()
