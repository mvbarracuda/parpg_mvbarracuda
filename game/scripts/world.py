import fife, math, random
import pychan
import pychan.widgets as widgets

from scripts.common.eventlistenerbase import EventListenerBase
from loaders import loadMapFile
from savers import saveMapFile
from agents.hero import Hero
from agents.girl import Girl
from agents.cloud import Cloud
from agents.beekeeper import Beekeeper
from agents.agent import create_anonymous_agents
from settings import Setting

TDS = Setting()

class MapListener(fife.MapChangeListener):
	def __init__(self, map):
		fife.MapChangeListener.__init__(self)
		map.addChangeListener(self)

	def onMapChanged(self, map, changedLayers):
		return
		print "Changes on map ", map.getId()
		for layer in map.getLayers():
			print layer.getId()
			print "    ", ["%s, %x" % (i.getObject().getId(), i.getChangeInfo()) for i in layer.getChangedInstances()]

	def onLayerCreate(self, map, layer):
		pass

	def onLayerDelete(self, map, layer):
		pass


class World(EventListenerBase):
	def __init__(self, engine):
		super(World, self).__init__(engine, regMouse=True, regKeys=True)
		self.engine = engine
		self.eventmanager = engine.getEventManager()
		self.model = engine.getModel()
		self.view = self.engine.getView()
		self.filename = ''
		self.pump_ctr = 0 # for testing purposis
		self.ctrldown = False
		self.instancemenu = pychan.loadXML('gui/instancemenu.xml')
		# we keep a copy of all possible buttons to avoid reloading of XML
		self.all_btns = [btn for btn in self.instancemenu.children]
		self.instance_to_agent = {}
		# dynamic_widgets should no longer be necessary; commenting them out to be safe
		#self.dynamic_widgets = {}   
		
	def show_instancemenu(self, clickpoint, instance):
		"""Handles the display of the right-click context menu."""
		# IMPORTANT: We assume that the ALWAYS_PRESENT_BUTTONS are 
		# _NEVER_ removed from the instancemenu
		# IMPORTANT: World and Agent functions that handle different 
		# actions must be named "buttonNameHandler", e.g. 
		# "talkButtonHandler"
		
		# no right-click menu for clicking on Hero
		if instance.getFifeId() == self.hero.agent.getFifeId():
			return
		# Buttons that will always be available, regardless of the 
		# instance type.
		# IMPORTANT: kickButton is listed here only to allow easier 
		# testing of the range check/queueing code 
		ALWAYS_PRESENT_BTNS = ('moveButton', 
				       'inspectButton', 
				       'kickButton'
				       )
		# Pattern matching the name of the handler functions
		NAME_PATTERN = "%sHandler"
		
		if self.instance_to_agent.has_key(instance.getFifeId()):
			# we got an agent here; remove any unhandled actions
			for btn in self.all_btns:
				#do we have this button in the current menu?
				btn_present = bool(self.instancemenu.findChild(name=btn.name))
				# do we need this button in the current menu?
				btn_needed = hasattr(self.instance_to_agent[instance.getFifeId()],NAME_PATTERN % btn.name) \
					   or btn.name in ALWAYS_PRESENT_BTNS
				if btn_needed and not btn_present:
					self.instancemenu.addChild(btn)
				elif not btn_needed and btn_present:
					self.instancemenu.removeChild(btn)
		else:
			# inst is not Agent; only leave always_present actions
			for btn in self.instancemenu.children[:]:
				if not btn.name in ALWAYS_PRESENT_BTNS:
					self.instancemenu.removeChild(btn)

		# map a dictionary of button names to the their World fuctions
		mapdict = dict([ (btn.name,getattr(self, NAME_PATTERN % btn.name))
				 for btn in self.instancemenu.children])
		self.instancemenu.mapEvents (mapdict)
		
		# add some global data
		self.instancemenu.clickpoint = clickpoint
		self.instancemenu.instance = instance		
		self.instancemenu.position = (clickpoint.x, clickpoint.y)
		# show the menu
		self.instancemenu.show()
		return 

	def hide_instancemenu(self):
		if self.instancemenu:
			self.instancemenu.hide()

	def reset(self):
		self.map, self.agentlayer = None, None
		self.cameras = {}
		self.hero, self.girl, self.clouds, self.beekeepers = None, None, [], []
		self.cur_cam2_x, self.initial_cam2_x, self.cam2_scrolling_right = 0, 0, True
		self.target_rotation = 0
		self.instance_to_agent = {}

	def load(self, filename):
		self.filename = filename
		self.reset()
		self.map = loadMapFile(filename, self.engine)
		self.maplistener = MapListener(self.map)

		self.agentlayer = self.map.getLayer('TechdemoMapGroundObjectLayer')
		self.hero = Hero(self.model, 'PC', self.agentlayer)
		self.instance_to_agent[self.hero.agent.getFifeId()] = self.hero
		self.hero.start()

		self.girl = Girl(self.model, 'NPC:girl', self.agentlayer)
		self.instance_to_agent[self.girl.agent.getFifeId()] = self.girl
		self.girl.start()

		self.beekeepers = create_anonymous_agents(self.model, 'beekeeper', self.agentlayer, Beekeeper)
		for beekeeper in self.beekeepers:
			self.instance_to_agent[beekeeper.agent.getFifeId()] = beekeeper
			beekeeper.start()

		cloudlayer = self.map.getLayer('TechdemoMapTileLayer')
		self.clouds = create_anonymous_agents(self.model, 'Cloud', cloudlayer, Cloud)
		for cloud in self.clouds:
			cloud.start(0.1, 0.05)

		for cam in self.view.getCameras():
			self.cameras[cam.getId()] = cam
		self.cameras['main'].attach(self.hero.agent)

		self.view.resetRenderers()
		renderer = fife.FloatingTextRenderer.getInstance(self.cameras['main'])
		textfont = self.engine.getGuiManager().createFont('fonts/rpgfont.png', 0, str(TDS.readSetting("FontGlyphs", strip=False)));
		renderer.changeDefaultFont(textfont)

		renderer = fife.FloatingTextRenderer.getInstance(self.cameras['small'])
		renderer.changeDefaultFont(None)

		renderer = self.cameras['main'].getRenderer('CoordinateRenderer')
		renderer.clearActiveLayers()
		renderer.addActiveLayer(self.map.getLayer(str(TDS.readSetting("CoordinateLayerName"))))

		renderer = self.cameras['main'].getRenderer('QuadTreeRenderer')
		renderer.setEnabled(True)
		renderer.clearActiveLayers()
		if str(TDS.readSetting("QuadTreeLayerName")):
			renderer.addActiveLayer(self.map.getLayer(str(TDS.readSetting("QuadTreeLayerName"))))

		self.cameras['small'].getLocationRef().setExactLayerCoordinates( fife.ExactModelCoordinate( 40.0, 40.0, 0.0 ))
		self.initial_cam2_x = self.cameras['small'].getLocation().getExactLayerCoordinates().x
		self.cur_cam2_x = self.initial_cam2_x
		self.cam2_scrolling_right = True
		self.cameras['small'].setEnabled(False)

		self.target_rotation = self.cameras['main'].getRotation()

	def save(self, filename):
		saveMapFile(filename, self.engine, self.map)

	def keyPressed(self, evt):
		keyval = evt.getKey().getValue()
		keystr = evt.getKey().getAsString().lower()
		if keystr == 't':
			r = self.cameras['main'].getRenderer('GridRenderer')
			r.setEnabled(not r.isEnabled())
		elif keystr == 'c':
			r = self.cameras['main'].getRenderer('CoordinateRenderer')
			r.setEnabled(not r.isEnabled())
		elif keystr == 's':
			c = self.cameras['small']
			c.setEnabled(not c.isEnabled())
		elif keystr == 'r':
			pass
#			self.model.deleteMaps()
#			self.metamodel.deleteDatasets()
#			self.view.clearCameras()
#			self.load(self.filename)
		elif keystr == 'o':
			self.target_rotation = (self.target_rotation + 90) % 360
		elif keyval in (fife.Key.LEFT_CONTROL, fife.Key.RIGHT_CONTROL):
			self.ctrldown = True

	def keyReleased(self, evt):
		keyval = evt.getKey().getValue()
		if keyval in (fife.Key.LEFT_CONTROL, fife.Key.RIGHT_CONTROL):
			self.ctrldown = False

	def mouseWheelMovedUp(self, evt):
		if self.ctrldown:
			self.cameras['main'].setZoom(self.cameras['main'].getZoom() * 1.05)

	def mouseWheelMovedDown(self, evt):
		if self.ctrldown:
			self.cameras['main'].setZoom(self.cameras['main'].getZoom() / 1.05)

	def changeRotation(self):
		currot = self.cameras['main'].getRotation()
		if self.target_rotation != currot:
			self.cameras['main'].setRotation((currot + 5) % 360)

	def mousePressed(self, evt):
		# quick and dirty way to clear queued actions
		self.hero.action_stack.clear()
		if evt.isConsumedByWidgets():
			return

		clickpoint = fife.ScreenPoint(evt.getX(), evt.getY())
		if (evt.getButton() == fife.MouseEvent.LEFT):
			self.hide_instancemenu()
			target_mapcoord = self.cameras['main'].toMapCoordinates(clickpoint, False)
			target_mapcoord.z = 0
			l = fife.Location(self.agentlayer)
			l.setMapCoordinates(target_mapcoord)
			self.hero.run(l)

		if (evt.getButton() == fife.MouseEvent.RIGHT):
			self.hide_instancemenu()
			instances = self.cameras['main'].getMatchingInstances(clickpoint, self.agentlayer)
			print "selected instances on agent layer: ", [i.getObject().getId() for i in instances]
			if instances:
				self.show_instancemenu(clickpoint, instances[0])

	def mouseMoved(self, evt):
		renderer = fife.InstanceRenderer.getInstance(self.cameras['main'])
		renderer.removeAllOutlines()

		pt = fife.ScreenPoint(evt.getX(), evt.getY())
		instances = self.cameras['main'].getMatchingInstances(pt, self.agentlayer);
		for i in instances:
			if i.getObject().getId() in ('girl', 'beekeeper'):
				renderer.addOutlined(i, 173, 255, 47, 2)

	def onConsoleCommand(self, command):
		result = ''
		try:
			result = str(eval(command))
		except:
			pass
		return result

	def moveButtonHandler(self):
		self.hide_instancemenu()
		self.hero.run(self.instancemenu.instance.getLocationRef())

	def talkButtonHandler(self):
		self.hide_instancemenu()
		instance = self.instancemenu.instance
		self.hero.talk(instance.getLocationRef())
		if instance.getObject().getId() == 'beekeeper':
			beekeeperTexts = TDS.readSetting("beekeeperTexts", type='list', text=True)
			txtindex = random.randint(0, len(beekeeperTexts) - 1)
			instance.say(beekeeperTexts[txtindex], 5000)
		if instance.getObject().getId() == 'girl':
			girlTexts = TDS.readSetting("girlTexts", type='list', text=True)
			txtindex = random.randint(0, len(girlTexts) - 1)
			instance.say(girlTexts[txtindex], 5000)

	def kickButtonHandler(self):
		self.hide_instancemenu()
		inst = self.instancemenu.instance
		#proof-of-concept range checking + action queueing
		if self.hero.distance_to (inst) > 3:
			self.hero.action_stack.add_action (self.hero.agent.follow, 
							  ('run',inst,4 * float(TDS.readSetting("TestAgentSpeed"))), 
							 lambda x: self.hero.distance_to(x) <= 3,
							 (inst,)
							 )
			self.hero.action_stack.add_action (self.kickButtonHandler)
			self.hero.action_stack.run()
			return
		
		self.hero.kick(self.instancemenu.instance.getLocationRef())
		self.instancemenu.instance.say('Hey!', 1000)
		
	def kissButtonHandler(self):
		self.hide_instancemenu()
		self.instance_to_agent[self.instancemenu.instance.getFifeId()].kissButtonHandler (self.instancemenu.instance,self.hero)

	def inspectButtonHandler(self):
		self.hide_instancemenu()
		inst = self.instancemenu.instance
		saytext = ['Engine told me that this instance has']
		if inst.getId():
			saytext.append(' name %s,' % inst.getId())
		saytext.append(' ID %s and' % inst.getFifeId())
		saytext.append(' object name %s' % inst.getObject().getId())
		self.hero.agent.say('\n'.join(saytext), 3500)

	def pump(self):
		if self.cameras['small'].isEnabled():
			loc = self.cameras['small'].getLocation()
			c = loc.getExactLayerCoordinatesRef()
			if self.cam2_scrolling_right:
				self.cur_cam2_x = c.x = c.x+0.1
				if self.cur_cam2_x > self.initial_cam2_x+10:
					self.cam2_scrolling_right = False
			else:
				self.cur_cam2_x = c.x = c.x-0.1
				if self.cur_cam2_x < self.initial_cam2_x-10:
					self.cam2_scrolling_right = True
			self.cameras['small'].setLocation(loc)
		self.changeRotation()
		self.pump_ctr += 1
