# coding: utf-8

import pychan
import pychan.widgets as widgets
import sys

def u2s(string):
	return string.encode(sys.getfilesystemencoding())

class FileBrowser(object):
	"""
	FileBrowser displays directory and file listings from the vfs.
	The fileSelected parameter is a callback invoked when a file selection has been made; its
    signature must be fileSelected(path,filename). If selectdir is set, fileSelected's
		filename parameter should be optional.
	The savefile option provides a box for supplying a new filename that doesn't exist yet.
  The selectdir option allows directories to be selected as well as files.
	"""
	def __init__(self, engine, fileSelected, savefile=False, selectdir=False, extensions=('xml',), guixmlpath="gui/filebrowser.xml"):
		self.engine = engine
		self.fileSelected = fileSelected

		self._widget = None
		self.savefile = savefile
		self.selectdir = selectdir
		
		self.guixmlpath = guixmlpath

		self.extensions = extensions
		self.path = './saves/'
		self.dir_list = []
		self.file_list = []

	def showBrowser(self):
		if self._widget:
			self._widget.show()
			return
		self._widget = pychan.loadXML(self.guixmlpath)
		self._widget.mapEvents({
			'dirList'       : self._setDirectory,
			'selectButton'  : self._selectFile,
			'closeButton'   : self._widget.hide
		})
		self._setDirectory()
		if self.savefile:
			self._file_entry = widgets.TextField(name='saveField', text=u'')	
			self._widget.findChild(name="fileColumn").addChild(self._file_entry)
		self._widget.show()

	def _setDirectory(self):
		selection = self._widget.collectData('dirList')
		if not (selection < 0):
			new_dir = u2s(self.dir_list[selection])
			lst = self.path.split('/')
			if new_dir == '..' and lst[-1] != '..' and lst[-1] != '.':
				lst.pop()
			else:
				lst.append(new_dir)
			self.path = '/'.join(lst)
			
		def decodeList(list):
			fs_encoding = sys.getfilesystemencoding()
			if fs_encoding is None: fs_encoding = "ascii"
		
			newList = []
			for i in list:
				try: newList.append(unicode(i, fs_encoding))
				except:
					newList.append(unicode(i, fs_encoding, 'replace'))
					print "WARNING: Could not decode item:", i
			return newList
			
		

		self.dir_list = []
		self.file_list = []
		
		dir_list = ('..',) + filter(lambda d: not d.startswith('.'), self.engine.getVFS().listDirectories(self.path))
		file_list = filter(lambda f: f.split('.')[-1] in self.extensions, self.engine.getVFS().listFiles(self.path))
				
		self.dir_list = decodeList(dir_list)
		self.file_list = decodeList(file_list)
		self._widget.distributeInitialData({
			'dirList'  : self.dir_list,
			'fileList' : self.file_list
		})

	def _selectFile(self):
		self._widget.hide()
		selection = self._widget.collectData('fileList')
		data = self._widget.collectData('saveField')

		if self.savefile:
			if data:
				if (data.split('.')[1] == 'dat'):
					self.fileSelected(self.path, u2s(self._widget.collectData('saveField')))
				else:
					self._warningMessage()
				return
			

		if selection >= 0 and selection < len(self.file_list):
			self.fileSelected(self.path, u2s(self.file_list[selection]))
			return
		
		if self.selectdir:
			self.fileSelected(self.path)
			return

		print 'FileBrowser: error, no selection.'

	def _warningMessage(self):
		window = widgets.Window(title="Warning")
		text = "Please save the file as a .dat"
		label = widgets.Label(text=text)
		ok_button = widgets.Button(name="ok_button", text="Ok")
		window.addChildren([label, ok_button])
		window.mapEvents({'ok_button':window.hide})
		window.show()
