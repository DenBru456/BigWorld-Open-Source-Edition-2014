import BigWorld
import ResMgr

# the resource to use for graphics presets
graphicsPresetsResource = 'system/data/graphics_settings_presets.xml'

############################################################################
# This class implements the graphics presets							   #
############################################################################
class GraphicsPresets:
	"""
	This class implements the GraphicsPresets functionality.
	
	The graphics presets store a number of graphics settings in a dictionary
	and lets you apply them all at once.
	
	The graphics presets are stored in an xml file.
	
	When initialised, the graphics presets will check against the currently set
	graphics options to see if any of its options are selected.
	
	The graphics presets have the following members:
	
	GraphicsPresets.entries - a dictionary of dictionaries that store the values
	for each preset graphics setting
	
	GraphicsPresets.entryNames - a list of the names of the presets in the order
	they appear in the .xml file. These names are the same as the keys for the 
	GraphicsSettings.entries dictionary
	
	GraphicsPresets.selectedOption - this is an index into the GraphicsPresets.entryNames
	member or -1 if a preset has not been set
	"""	
	# the constructor
	def __init__(self):
		sect = ResMgr.openSection( graphicsPresetsResource )
		
		# Entries is a dictionary of dictionaries of graphics presets
		self.entries = {}
		# Entry names is a list of the names of the entries in the
		# order they appear in the presets file
		self.entryNames = []
		# The currently selected option as an index into entry names
		# -1 means no preselected option selected (i.e. advanced settings)
		self.selectedOption = -1

		# load up the preset groups
		for group in sect.values():
			# only allow named groups
			if group.asString != "":
				# init the map for the current entry
				entry = {}
				# create the entries for this group
				for setting in group.values():
					if setting.name == 'entry':
						entry[setting.readString('label')] = setting.readInt('activeOption')
				
				# add the entry to the dictionary and add the name to the entry list
				self.entries[group.asString] = entry
				self.entryNames.append(group.asString)
		
		self.setSelectedOption()

	# Set up the currently selected option
	def setSelectedOption(self):
		# init to -1 as that means no preset selected
		self.selectedOption = -1
		# create a dictionary from the currently set graphics options		
		currentOptionMap = {}		
		for currentOption in BigWorld.graphicsSettings():
			currentOptionMap[currentOption[0]] = currentOption[1]

		# iterate over the dictionary presets and compare them to the currently set
		# graphics options, if all the options match our preset, we have found a
		# preset option
		for i in range(0, len(self.entryNames)):
			foundOption = True
			for setting in self.entries[self.entryNames[i]].items():
				if currentOptionMap.get(setting[0]) != setting[1]:
					foundOption = False
					break
			if foundOption == True:
				self.selectedOption = i
				break

	# select a graphics preset
	# option is an index into the entryNames
	def selectGraphicsOptions(self, option):
		currentOption = self.entries[self.entryNames[option]]
		for setting in currentOption.items():
			try:
				BigWorld.setGraphicsSetting( setting[0], setting[1] )
			except:
				print 'selectGraphicsOptions: unable to set option ', setting[0]
		self.selectedOption = option
