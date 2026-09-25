import sys
from bwdebug import ERROR_MSG

import BigWorld
import ResMgr

import Utils

DEFAULT_VISUAL_STATES_LOCATION = "gui/visual_states"

# TODO: put docstrings on these

def readMappingSection( dataSection ):
	if not dataSection.has_key( "mapping" ):
		return (None, None)
	dataSection = dataSection._mapping
	mappingName = dataSection.asString.strip()
	mappingType = mappingName if mappingName else 'UV'

	mapping = [None, None, None, None]
	mapping[0] = dataSection.readVector2( "coords0" )
	mapping[1] = dataSection.readVector2( "coords1" )
	mapping[2] = dataSection.readVector2( "coords2" )
	mapping[3] = dataSection.readVector2( "coords3" )
	mapping = tuple( mapping )

	return mappingType, mapping


def writeMappingSection( dataSection, mappingType, mapping ):
	if mappingType is None:
		return
	dataSection = dataSection.createSection( "mapping" )
	dataSection.asString = mappingType
	dataSection.writeVector2( "coords0", mapping[0] )
	dataSection.writeVector2( "coords1", mapping[1] )
	dataSection.writeVector2( "coords2", mapping[2] )
	dataSection.writeVector2( "coords3", mapping[3] )

class VisualState( object ):
	cachedTextures = {}
	
	@staticmethod
	def cacheTexture( textureName ):
		cache = VisualState.cachedTextures
		if textureName.strip() != "" and not cache.has_key( textureName ):
			cache[textureName] = BigWorld.Texture( textureName )
			
	@staticmethod
	def clearTextureCache():
		VisualState.cachedTextures = {}
 
	def __init__( self ):
		self._standardComponents = {}

	def onSave( self, dataSection ):
		pass

	def onLoad( self, dataSection ):
		if dataSection.has_key( "standardComponents" ):
			for key, value in dataSection._standardComponents.items():
				scs = StandardComponentState()
				scs.onLoad( self, value )
				self._standardComponents[ key ] = scs

	def apply( self, componentScript ):
		for compName, scs in self._standardComponents.iteritems():
			c = getattr( componentScript.component, compName, None )
			if c is not None:
				scs.apply( c )



class StandardComponentState:
	def __init__( self):
		self.textureName = ""
		self.textureMappingType = None
		self.textureMapping = None
		self.colour = (255,255,255,255)
		self.materialFX = "BLEND"
		

	def apply( self, component ):
		component.textureName = self.textureName
		if self.textureMapping:
			Utils.applyMapping( component,
							self.textureMappingType,
							self.textureMapping )
		component.colour = self.colour
		if self.materialFX != "":
			component.materialFX = self.materialFX
		else:
			component.materialFX = "BLEND"
		
	def onLoad( self, visualState, dataSection ):			
		self.textureName = dataSection.readString( "textureName", self.textureName )
		self.materialFX = dataSection.readString( "materialFX", self.materialFX )
		self.colour = dataSection.readVector4( "colour", self.colour )
		self.textureMappingType, self.textureMapping = readMappingSection( dataSection )
		VisualState.cacheTexture( self.textureName )
		
	def onSave( self, dataSection ):
		dataSection.writeString( "textureName", self.textureName )
		dataSection.writeString( "materialFX", self.materialFX )
		dataSection.writeVector4( "colour", self.colour )
		writeMappingSection( dataSection, self.textureMappingType, self.textureMapping )
		
		
class VisualStateComponent( object ):

	def __init__( self, component, visualStateClassName ):
		self.visualStateClassName = visualStateClassName
		self.externalReference = ""
		self._visualStates = {}
		self._cachedTextures = {}


	def onSave( self, dataSection ):
		if self.externalReference != "":
			dataSection.writeString( "visualStates/external", self.externalReference )
		else:
			dataSection.writeString( "visualStates", self.visualStateClassName )
			visualStatesSection = dataSection._visualStates
			for (stateName, state) in self._visualStates.items():
				stateSection = visualStatesSection.createSection( stateName )
				state.onSave( stateSection )


	def onLoad( self, dataSection ):
		if dataSection.has_key( "visualStates" ):
			visualStatesSection = dataSection._visualStates

			if visualStatesSection.has_key( "external" ):
				self.externalReference = visualStatesSection._external.asString
				extName = visualStatesSection._external.asString
				ext = ResMgr.openSection( extName )
				if ext is not None:
					visualStatesSection = ext
				else:
					ERROR_MSG( "Failed to open external visual state '%s'." % extName )
			else:
				self.externalReference = ""

			self.loadVisualStatesDS( visualStatesSection )
			
			
	def loadVisualStatesDS( self, visualStatesSection ):					
		self.visualStateClassName = visualStatesSection.asString
		components = self.visualStateClassName.strip('"').split('.')

		module = __import__('__main__')
		for comp in components[:-1]:
			module = getattr( module, comp )
		visualStateClass = getattr( module, components[-1] )

		for (stateName, stateSection) in visualStatesSection.items():
			visualState = visualStateClass()
			visualState.onLoad( stateSection )
			self._visualStates[ stateName ] = visualState
			
			
	def loadVisualStates( self, visualStatesXMLName ):
		# Look in the default location if we don't specify a full path
		if '/' not in visualStatesXMLName:
			visualStatesXMLName = DEFAULT_VISUAL_STATES_LOCATION + '/' + visualStatesXMLName
		ds = ResMgr.openSection( visualStatesXMLName )
		if ds is not None:
			self.loadVisualStatesDS( ds )
			self.externalReference = visualStatesXMLName
		else:
			ERROR_MSG( "Failed to open visual state '%s'." % visualStatesXMLName )


	def setVisualState( self, stateName ):
		state = self._visualStates.get( stateName, None )
		if state:
			state.apply( self )
		else:
			ERROR_MSG( "No Visual State '%s' on %s" % (stateName, self) )


