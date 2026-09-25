'''
This module implements all weather editor related UI actions.
'''

import WorldEditor
import BigWorld
import Weather
import Personality
import ResMgr
from functools import partial
g_systemIdx = 0
g_skyBoxIdx = 0
g_dirty = False


def markDirty():
	global g_dirty
	g_dirty = True


def saveUndoState( desc ):
	WorldEditor.saveWeatherUndoState( desc )


def onInitWeatherUI():
	if WorldEditor.getOptionInt("render/useDefaultWeather") ==  1:
		selectDefaultWeather()
	else:
		selectWeatherSystemByIdx(g_systemIdx)


def lbnWeatherSystemItemSelect( index ):
	global g_systemIdx
	global g_skyBoxIdx
	g_systemIdx = index
	try:
		if index >= 0:
			name = Weather.weatherXML.values()[index].name
			Weather.weather().summon( name, immediate = True )
	except IndexError:
		pass
	g_skyBoxIdx = 0	
	#callback next frame seems to work better (i.e. works at all). Something
	#to do with how MFC is refreshing its lists
	BigWorld.callback(0,partial(WorldEditor.selectSkyBoxByIdx,g_skyBoxIdx))


def lbnWeatherSystemItemToggleState( index, state ):
	(systemName,section) = Weather.weatherXML.items()[index]
	toggleExcludeWeatherSystem(systemName, section)	


def selectWeatherSystemByIdx( idx ):
	WorldEditor.selectWeatherSystemByIdx(idx)
	lbnWeatherSystemItemSelect(idx)


def lbnSkyBoxItemSelect( index ):
	global g_skyBoxIdx
	g_skyBoxIdx = index	


def currentSystemAndSection():
	weatherDS = Weather.weatherXML
	weather = Weather.weather()
	systemName = weather.system.name	
	systemSection = weatherDS[systemName]
	return (weather.system, systemSection)


def resummon():
	weather = Weather.weather()
	weather.summon( weather.system.name, immediate = True, resummon = True )


def saveUndoState_onWeatherAdjust( tag ):
	markDirty()
	saveUndoState( "Modify Weather System property - " + tag )


def onWeatherAdjust( tag ):	
	weatherDS = Weather.weatherXML
	weather = Weather.weather()
	systemName = weather.system.name
	systemSection = weatherDS[systemName]
	
	if "bloom/" in tag:
		import Bloom
		Bloom.loadStyle( systemSection["bloom"], 0.0 )
	elif tag == "sun":
		weather.sun(systemSection.readVector4( "sun" ))
	elif tag == "ambient":
		weather.ambient(systemSection.readVector4( "ambient" ))
	elif tag == "fog":
		weather.fog(systemSection.readVector4( "fog" ))
	elif tag == "temperature":
		pass
	elif tag == "fogFactor":
		weather.system.skyBoxFogFactor = systemSection.readFloat( "fogFactor" )
		weather.fog(systemSection.readVector4( "fog" ))
	else:
		resummon()


def newSystemName():
	weatherDS = Weather.weatherXML
	name = "New_System"
	idx = 0
	while weatherDS.has_key(name):
		idx += 1
		name = "New_System_%0.3d" % (idx,)
	return name


def actAddWeatherSystemExecute():
	saveUndoState( "Add Weather System" )
	markDirty()
	weatherDS = Weather.weatherXML
	global g_systemIdx
	g_systemIdx = len(weatherDS)
	name = newSystemName()
	ds = weatherDS.createSection( name )	
	WorldEditor.refreshWeatherSystemList()
	BigWorld.callback(0.1,partial(actAddWeatherSystemExecutePart2,g_systemIdx))


def actAddWeatherSystemExecutePart2(idx):
	selectWeatherSystemByIdx( idx )
	WorldEditor.renameCurrentWeatherSystem()


def actRenameWeatherSystemExecute():
	'''
	This function is called when the rename weather system
	action is invoked, i.e. via hotkey or button press
	'''	
	WorldEditor.renameCurrentWeatherSystem()


def actRenameWeatherSystem( oldName, newName ):
	'''
	This function is called when an in-place system rename is complete,
	and we are tasked with actually performing the renaming.
	'''
	if oldName == newName:
		return

	markDirty()
	saveUndoState( "Rename Weather System" )
	weatherDS = Weather.weatherXML
	children = weatherDS.items()
	
	for (key,value) in children:
		weatherDS.deleteSection(key)
	
	for (key,value) in children:
		if key == oldName:
			weatherDS.createSection(newName).copy(value)
		else:
			weatherDS.createSection(key).copy(value)

	weather = Weather.weather()
	weather.summon( newName, immediate = True )
	WorldEditor.refillWeatherSystemProperties()
	Personality.addChatMsg(-1,"%s renamed to %s" % (oldName,newName) )


def actRemoveWeatherSystemExecute():
	saveUndoState( "Remove Weather System" )
	markDirty()
	weatherDS = Weather.weatherXML
	(system,section) = currentSystemAndSection()
	while (weatherDS.deleteSection(system.name)):
		pass
	WorldEditor.refreshWeatherSystemList()
	global g_systemIdx
	g_systemIdx = max( 0, g_systemIdx )
	selectWeatherSystemByIdx(g_systemIdx)


def actDefaultWeatherSystemExecute():
	saveUndoState( "Set Default Weather System" )
	markDirty()
	spaceName = WorldEditor.spaceName()
	(system,section) = currentSystemAndSection()
	weatherDS = Weather.weatherXML
	
	for systemDS in weatherDS.values():
		defaults = list(systemDS.readStrings( "default" ))
		if spaceName in defaults:
			defaults.remove(spaceName)
			while systemDS.has_key("default"):
				systemDS.deleteSection("default")		
			systemDS.writeStrings("default", defaults)

	section.createSection( "default" ).asString = spaceName
	
	#This is to update the (default) in the weather system list
	WorldEditor.refreshWeatherSystemList()
	global g_systemIdx
	selectWeatherSystemByIdx(g_systemIdx)
	
	Personality.addChatMsg( -1, "%s is now the default weather for space %s" % (system.name, spaceName) )


def toggleExcludeWeatherSystem( systemName, section ):
	global g_spaceExclusions
	spaceName = WorldEditor.spaceName()	
	saveUndoState( "Exclude Weather System" )
	markDirty()
	
	exclusions = list(section.readStrings("exclude"))
	if spaceName in exclusions:
		while section.has_key("exclude"):
			section.deleteSection("exclude")
		exclusions.remove(spaceName)
		section.writeStrings("exclude", exclusions)
		Personality.addChatMsg( -1, "%s is no longer excluded from space %s" % (systemName, WorldEditor.spaceName()) )
	else:
		section.createSection( "exclude" ).asString = spaceName
		Personality.addChatMsg( -1, "%s excluded from space %s" % (systemName, spaceName) )


def actAddSkyBox( skyBoxName ):
	global g_skyBoxIdx
	m = BigWorld.Model( skyBoxName )
	if m == None:
		return False
	markDirty()
	saveUndoState( "Add Weather System Sky Box" )
	(system,section) = currentSystemAndSection()
	ds = section.createSection( "skyBox" )
	ds.asString = skyBoxName
	resummon()
	WorldEditor.refreshSkyBoxList()
	g_skyBoxIdx = len(system.skyBoxes)
	#callback next frame seems to work better (i.e. works at all). Something
	#to do with how MFC is refreshing its lists
	BigWorld.callback(0,partial(WorldEditor.selectSkyBoxByIdx,g_skyBoxIdx))
	return True


def actClearSkyBoxesExecute():
	saveUndoState( "Clear Weather System Sky Boxes" )
	markDirty()
	(system,section) = currentSystemAndSection()
	while (section.deleteSection("skyBox")):
		pass
	resummon()
	WorldEditor.refreshSkyBoxList()


def replaceSkyBoxesSection( skyBoxList, section ):
	'''
	This method replaces all the skyBox children in the given data section,
	with the ones in the list.  Then it triggers a refresh of the weather
	editor skybox list.  Then it refreshes the ones actually visible in the
	3d window
	'''
	while (section.deleteSection("skyBox")):
		pass
	for i in skyBoxList:
		sbs = section.createSection("skyBox")
		sbs.asString = i
	WorldEditor.refreshSkyBoxList()


def actSkyBoxUpExecute():
	global g_skyBoxIdx
	markDirty()
	saveUndoState( "Move Weather System Sky Box Up" )
	(system,section) = currentSystemAndSection()
	system.edUnloadSkyBoxes()	
	b = system.skyBoxes[g_skyBoxIdx]
	system.skyBoxes[g_skyBoxIdx] = system.skyBoxes[g_skyBoxIdx-1]
	system.skyBoxes[g_skyBoxIdx-1] = b
	replaceSkyBoxesSection( system.skyBoxes, section )	
	system.edReloadSkyBoxes()
	g_skyBoxIdx -= 1
	WorldEditor.selectSkyBoxByIdx(g_skyBoxIdx)


def actSkyBoxDownExecute():
	global g_skyBoxIdx
	markDirty()
	saveUndoState( "Move Weather System Sky Box Down" )	
	(system,section) = currentSystemAndSection()
	system.edUnloadSkyBoxes()	
	b = system.skyBoxes[g_skyBoxIdx]
	system.skyBoxes[g_skyBoxIdx] = system.skyBoxes[g_skyBoxIdx+1]
	system.skyBoxes[g_skyBoxIdx+1] = b
	replaceSkyBoxesSection( system.skyBoxes, section )
	system.skyBoxes = system.skyBoxes
	system.edReloadSkyBoxes()
	g_skyBoxIdx += 1
	WorldEditor.selectSkyBoxByIdx(g_skyBoxIdx)


def actSkyBoxDelExecute():
	global g_skyBoxIdx
	markDirty()
	saveUndoState( "Delete Weather System Sky Box" )
	(system,section) = currentSystemAndSection()
	system.edUnloadSkyBoxes()	
	system.skyBoxes.pop(g_skyBoxIdx)
	replaceSkyBoxesSection( system.skyBoxes, section )
	system.skyBoxes = system.skyBoxes
	system.edReloadSkyBoxes()
	if g_skyBoxIdx == len(system.skyBoxes):
		g_skyBoxIdx = max(0,g_skyBoxIdx-1)
	WorldEditor.selectSkyBoxByIdx(g_skyBoxIdx)


def onSave( spaceName, ss ):
	spaceName = spaceName + "/"
	global g_dirty
	if g_dirty:
		weatherDS = Weather.weatherXML
		weatherDS.save()
		g_dirty = False
		Personality.addChatMsg( -1, "Saved weather systems file" )


def selectDefaultWeather():
	spaceName = WorldEditor.spaceName()
	idx = 0
	weatherDS = Weather.weatherXML
	for systemDS in weatherDS.values():
		defaults = list(systemDS.readStrings( "default" ))
		if spaceName in defaults:
			g_systemIdx = idx
			selectWeatherSystemByIdx(g_systemIdx)
		else:
			idx+=1


def onChangeSpace( spaceID, spaceSettings ):
	global g_systemIdx
	WorldEditor.refreshWeatherSystemList()
	if WorldEditor.getOptionInt("render/useDefaultWeather") ==  1:
		selectDefaultWeather()
	else:
		selectWeatherSystemByIdx(g_systemIdx)


def onUndoWeather():
	resummon()
	WorldEditor.refreshWeatherSystemList()
	global g_systemIdx
	selectWeatherSystemByIdx(g_systemIdx)


Personality.addSaveSpaceListener( onSave )
Personality.addCameraSpaceChangeListener( onChangeSpace )
