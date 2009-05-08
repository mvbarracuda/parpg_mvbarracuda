#!/usr/bin/python

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, shutil

from scripts.common import utils
# add paths to the swig extensions
utils.addPaths ('../../engine/swigwrappers/python', '../../engine/extensions')

import fife_compat
import fife, fifelog
from scripts import world
from scripts import engine
from scripts.common import eventlistenerbase
from basicapplication import ApplicationBase
from settings import Setting

TDS = Setting()

class ApplicationListener(eventlistenerbase.EventListenerBase):
    def __init__(self, engine, world):
        super(ApplicationListener, self).__init__(engine,
                                                  regKeys=True,regCmd=True, regMouse=False, 
                                                  regConsole=True, regWidget=True)
        self.engine = engine
        self.world = world
        engine.getEventManager().setNonConsumableKeys([fife.Key.ESCAPE,])
        self.quit = False
        self.aboutWindow = None

    def keyPressed(self, evt):
        """Function to deal with keypress events
           @param evt: The event that was captured"""
        keyval = evt.getKey().getValue()
        if keyval == fife.Key.ESCAPE:
            self.quit = True
        evt.consume()
          
    def onCommand(self, command):
        """Enables the game to be closed via the 'X' button on the window frame"""
        self.quit = (command.getCommandType() == fife.CMD_QUIT_GAME)
        if self.quit:
            command.consume()

class PARPG(ApplicationBase):
    """Main Application class
       We use an MV data model.
       self.world is our view
       self.engine is our model"""
    def __init__(self):
        super(PARPG,self).__init__()
        self.world = world.World(self.engine)
        self.model = engine.Engine(self.world)
        self.listener = ApplicationListener(self.engine, self.world)
        self.model.loadMap(str(TDS.readSetting("MapFile")))

    def loadSettings(self):
        """Load the settings from a python file and load them into the engine.
           Called in the ApplicationBase constructor."""
        import settings
        self.settings = settings

        eSet = self.engine.getSettings()
        eSet.setDefaultFontGlyphs(str(TDS.readSetting("FontGlyphs",strip=False)))
        eSet.setDefaultFontPath(str(TDS.readSetting("Font")))
        eSet.setBitsPerPixel(int(TDS.readSetting("BitsPerPixel")))
        eSet.setInitialVolume(float(TDS.readSetting("InitialVolume")))
        eSet.setSDLRemoveFakeAlpha(int(TDS.readSetting("SDLRemoveFakeAlpha")))
        eSet.setScreenWidth(int(TDS.readSetting("ScreenWidth")))
        eSet.setScreenHeight(int(TDS.readSetting("ScreenHeight")))
        eSet.setRenderBackend(str(TDS.readSetting("RenderBackend")))
        eSet.setFullScreen(int(TDS.readSetting("FullScreen")))
        try:
            eSet.setWindowTitle(str(TDS.readSetting("WindowTitle")))
            eSet.setWindowIcon(str(TDS.readSetting("WindowIcon")))
        except:
            pass            
        try:
            eSet.setImageChunkingSize(int(TDS.readSetting("ImageChunkSize")))
        except:
            pass

    def initLogging(self):
        """Initialize the LogManager"""
        LogModules = TDS.readSetting("LogModules",type='list')
        self.log = fifelog.LogManager(self.engine,
                                      int(TDS.readSetting("LogToPrompt")),
                                      int(TDS.readSetting("LogToFile")))
        if LogModules:
            self.log.setVisibleModules(*LogModules)

    def createListener(self):
        # already created in constructor
        pass

    def _pump(self):
        """Main game loop
           There are in fact 2 main loops, this one and the one in World"""
        if self.listener.quit:
            self.breakRequested = True
        else:
            self.world.pump()

def main():
    """Application code starts from here"""
    app = PARPG()
    app.run()

if __name__ == '__main__':
    main()

