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

# there should be NO references to FIFE here!
import pickle, sys
from gamestate import GameState
from objects import *
from objectLoader import ObjectXMLParser
from objects.action import *

# design note:
# there is a map file that FIFE reads. We use that file for half the map
# format because the map editor in FIFE uses it, and secondly because it
# save us writing a bunch of new code.
# However, the objects and characters on a map are liable to change
# whilst the game is being run, so when we change the map, we need to
# to grab the objects and npc data EITHER from the engine state, or grab
# from another file if in their initial state
# This other file has the name AAA_objects.xml where AAA.xml is the name
# of the original mapfile.

class Engine:
    """Engine holds the logic for the game.
       Since some data (object position and so forth) is held in the
       fife, and would be pointless to replicate, we hold a instance of
       the fife view here. This also prevents us from just having a
       function heavy controller."""
    
    def __init__(self, view):
        """Initialise the instance.
           @type view: world
           @param view: A world instance
           @return: None"""
        # a World object (the fife stuff, essentially)
        self.view = view
        self.mapchange = False
        self.gameState = GameState()

    def reset(self):
        """Clears the data on a map reload so we don't have objects/npcs from
           other maps hanging around.
           @return: None"""

    def save(self, path, filename):
        """Writes the saver to a file.
           @type filename: string
           @param filename: the name of the file to write to
           @return: None"""
        fname = '/'.join([path,filename])
        try:
            f = open(fname, 'w')
        except(IOError):
            sys.stderr.write("Error: Can't find save game: " + fname + "\n")
            return
        
        # can't pickle SwigPyObjects
        behaviours = {}
        behaviours[self.gameState.PC.ID] = self.gameState.PC.behaviour;
        self.gameState.PC.behaviour = None;
        
        npcs = [npc for npc in self.gameState.objects.values() if npc.trueAttr("NPC")]
        for npc in npcs:
            behaviours[npc.ID] = npc.behaviour;
            npc.behaviour = None;
        
        pickle.dump(self.gameState, f)
        f.close()
        
        # restore behaviours
        for npc in npcs:
            npc.behaviour = behaviours[npc.ID];
        self.gameState.PC.behaviour = behaviours[self.gameState.PC.ID]

    def load(self, path, filename):
        """Loads a saver from a file.
           @type filename: string
           @param filename: the name of the file to load from
           @return: None"""
        fname = '/'.join([path, filename])
        try:
            f = open(fname, 'r')
        except(IOError):
            sys.stderr.write("Error: Can't find save game file\n")
            return
        self.gameState = pickle.load(f)
        f.close()
        if self.gameState.currentMap:
            self.loadMap(self.gameState.currentMap) 

    def createObject (self, layer, attributes, instance):
        """Create an object and add it to the current map.
            Inputs:
                layer = FIFE layer object exists in
                attributes = dictionary of all object attributes
                instance = FIFE instance corresponding to the object
            Return:
                Nothing
        """
        # create the extra data
        extra = {}
        extra['agent_layer'] = layer
        extra['engine'] = self
        
        obj = createObject(attributes, extra)
        
        if obj.trueAttr("PC"):
            self.addPC( layer, obj, instance)
        else:
            self.addObject( layer, obj, instance)

        

    def addPC(self, layer, pc, instance):
        """Add the PC to the map
            Inputs:
                layer = FIFE layer object exists in
                pc = PlayerCharacter object
                instance = FIFE instance of PC
            Returns:
                Nothing
        """
        # add to view data 
        self.view.activeMap.addObject(pc.ID, instance)          
        
        # sync with game data
        if not self.gameState.PC:
            self.gameState.PC = pc
            
        self.gameState.PC.setup()


    def addObject(self, layer, obj, instance):
        """Adds an object to the map.
            Inputs:
                layer = FIFE layer object exists in
                obj = corresponding object class
                instance = FIFE instance of object
            Returns:
                Nothing
        """
        
        ref = self.gameState.getObjectById(obj.ID) 
        if ref is None:
            # no, add it to the game state
            obj.map_id = self.gameState.currentMap
            self.gameState.objects[obj.ID] = obj
        else:
            # yes, use the current game state data
            obj.X = ref.X
            obj.Y = ref.Y
            obj.gfx = ref.gfx  
            
        # add it to the view
        self.view.activeMap.addObject(obj.ID, instance)          
       
        if obj.trueAttr("NPC"):
            # create the agent
            obj.setup()
            
            # create the PC agent
            obj.start()

    def addDoors(self, doors):
        """Add all the doors to the map as well.
           As an object they will have already been added.
           @type doors: list
           @param doors: List of doors
           @return: None"""
        for i in doors:
            self.doors[str(i.id)] = MapDoor(i.id, i.destmap, (i.destx, i.desty))

    def objectActive(self, ident):
        """Given the objects ID, pass back the object if it is active,
           False if it doesn't exist or not displayed
           @type ident: string
           @param ident: ID of object
           @rtype: boolean
           @return: Status of result (True/False)"""
        for i in self.gameState.getObjectsFromMap(self.gameState.currentMap):
            if (i.ID == ident):
                # we found a match
                return i         
        # no match
        return False

    def getItemActions(self, obj_id):
        """Given the objects ID, return the text strings and callbacks.
           @type obj_id: string
           @param obj_id: ID of object
           @rtype: list
           @return: List of text and callbacks"""
        actions=[]
        # note: ALWAYS check NPC's first!
        obj = self.gameState.getObjectById(obj_id)
        
        if obj:
            if obj.trueAttr("NPC"):
                # keep it simple for now, None to be replaced by callbacks
                actions.append(["Talk", "Talk", self.initTalk, obj])
                actions.append(["Attack", "Attack", self.nullFunc, obj]) 
            elif obj.trueAttr("Door"):
                actions.append(["Change Map", "Change Map", \
                       self.gameState.PC.approach, [obj.X, obj.Y], \
                        ChangeMapAction(self, self.doors[str(i.ID)].map, [i.destx, i.desty])])
                pass
            else:
                actions.append(["Examine", "Examine", self.gameState.PC.approach,  
                                [obj.X, obj.Y], ExamineBoxAction(self, obj.name, obj.text)])
                # is it a container?
                if obj.trueAttr("container"):
                    actions.append(["Open", "Open", self.gameState.PC.approach, [obj.X, obj.Y], OpenBoxAction(self, "Box")])
                # can you pick it up?
                if obj.trueAttr("carryable"):
                    actions.append(["Pick Up", "Pick Up", self.nullFunc, obj])       
                    
        return actions
    
    def nullFunc(self, userdata):
        """Sample callback for the context menus."""
        print userdata
    
    def initTalk(self, npcInfo):
        """ Starts the PC talking to an NPC. """
        # TODO: work more on this when we get NPCData and HeroData straightened
        # out
        npc = self.gameState.getObjectById(npcInfo.ID)
        if npc:
            npc.talk()
        self.gameState.PC.approach([npc.getLocation().getLayerCoordinates().x, npc.getLocation().getLayerCoordinates().y])

    def loadMap(self, map_name, map_file):
        """Load a new map. TODO: needs some error checking
           @type map_file: string
           @param map_file: Name of map file to load
           @return: None"""
        self.gameState.currentMap = map_file
        self.view.loadMap(map_name, str(map_file))
        self.view.setActiveMap(map_name)

        self.reset()        
        
        # create the PC agent
        self.view.activeMap.addPC(self.gameState.PC.behaviour.agent)
        self.gameState.PC.start()

    def handleMouseClick(self,position):
        """Code called when user left clicks the screen.
           @type position: fife.ScreenPoint
           @param position: Screen position of click
           @return: None"""
        self.gameState.PC.run(position)
        
    def changeMap(self, map, targetPosition):
        """Registers for a mapchange on the next pump().
           @type map: ???
           @param map: Name of the target map.
           @type targetPosition: ???
           @param targetPosition: Position of PC on target map.
           @return: None"""
        # save the postions
        self.updateGameState()
        # set the PC position
        self.gameState.PC.posx = targetPosition[0]
        self.gameState.PC.posy = targetPosition[1]
        # set the parameters for the mapchange
        self.targetMap = map
        # issue the mapchange
        self.mapchange = True

    def handleCommands(self):
        if self.mapchange:
            self.loadMap(self.targetMap)
            self.mapchange = False

    def pump(self):
        """Main loop in the engine."""
        self.handleCommands()

