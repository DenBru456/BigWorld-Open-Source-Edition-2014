# -*- coding: utf-8 -*

import BigWorld
import Helpers.PyGUI as PyGUI
from functools import partial
from bwdebug import ERROR_MSG
import types
import Cursor
import BWReplay

from Helpers.PyGUI import PyGUIEvent


def formatNumber(num, places=0):
	"""Format a number with grouped thousands and given decimal places"""

	formatted = "%.*f" % (places, float( num ))
	integer, point, decimal = formatted.partition('.')

	index = 3
	while index < len(integer):
		integer = integer[:-index] + ',' + integer[-index:]
		index += 4

	return integer + point + decimal


class StatsWindow( PyGUI.DraggableWindow  ):

	factoryString = "FDGUI.StatsWindow"

	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )
		self.component.script = self
		self.timeCallback = None


	def onActive( self ):
		BigWorld.callback( 1.0, self.updateCallback )
		self.updateStats()


	def updateCallback( self ):
		if self.isActive:
			BigWorld.callback( 1.0, self.updateCallback )
			self.updateStats()


	def updateStats( self ):
		self.component.fps.text = "%.2f" % (float( BigWorld.getWatcher( "Render/FPSAverage" ) ),)

		self.component.textureMemory.text = "%s/%s MB" % \
				(formatNumber( float(BigWorld.getWatcher( "Memory/TextureManagerReckoningFrame" )) / 1048576, 1 ),
					formatNumber( float(BigWorld.getWatcher( "Memory/TextureManagerReckoning" )) / 1048576, 1 ))

		drawCalls = BigWorld.getWatcher( "Render/Draw Calls" )
		primitives = BigWorld.getWatcher( "Render/Primitives" )
		self.component.drawCalls.text = formatNumber(drawCalls)
		self.component.primitives.text = formatNumber(primitives)
		self.component.primitivesPerDrawCall.text = formatNumber(int( float( primitives ) / float( drawCalls ) + 0.5 ))

		loadedChunks = int( BigWorld.getWatcher( "Chunks/Loaded Chunks" ) )
		self.component.drawnArea.text = '%s sqkm' % (formatNumber( loadedChunks / 100.0, 2 ),)

		self.component.totalEntitiesLabel.text = "Total entities in AOI:"
		self.component.totalEntities.text = formatNumber(int(BigWorld.getWatcher( "Entities/Active Entities" )))
		#self.component.totalEntities.text = "%s / %s" % (BigWorld.getWatcher( "Entities/Active Entities" ),
		#												"unknown" )

		servername = BigWorld.server()
		if servername is not None and servername != "":
			self.component.latency.text = "%s ms" % formatNumber( float(
				BigWorld.getWatcher( "ConnectionControl/Latency" ) ) * 1000 )

			self.component.bandwidthToServer.text = "%s kbps" % formatNumber( float(
				BigWorld.getWatcher( "ConnectionControl/bps out" ) ) / 1024, 1 )
			self.component.messagesToServer.text = formatNumber( 
				BigWorld.getWatcher( "ConnectionControl/Messages out" ), 1 )
			self.component.bandwidthFromServer.text = "%s kbps" % formatNumber(
				float( BigWorld.getWatcher( "ConnectionControl/bps in" ) ) / 1024,
				1 )
			self.component.messagesFromServer.text = formatNumber(
			BigWorld.getWatcher( "ConnectionControl/Messages in" ), 1 )

		maxBandwidth = int(BigWorld.getWatcher( "Debug/Max bandwidth per second" ))
		self.component.bandwidth.text = "%d kbps" % (maxBandwidth/1024,)
		self.component.bandwidthSlider.script.value = maxBandwidth/1024
		self.component.entityFilteringCheckBox.script.setToggleState( \
			BigWorld.getWatcher( "Client Settings/Filters/Enabled" ) == 'true' )


	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )


	@PyGUIEvent( "bandwidthSlider", "onValueChanged" )
	def onBandwidthSlider( self, value ):
		if BWReplay.isLoaded():
			origValue = int(BigWorld.getWatcher( "Debug/Max bandwidth per second" ))/1024
			self.component.bandwidthSlider.script.value = origValue
			return
		value = int(value) * 1024
		BigWorld.setWatcher( "Debug/Max bandwidth per second", str(value) )
		self.component.bandwidth.text = "%d kbps" % (value/1024,)


	@PyGUIEvent( "entityFilteringCheckBox", "onActivate", True )
	@PyGUIEvent( "entityFilteringCheckBox", "onDeactivate", False )
	def onEntityFilteringCheckBox( self, on ):
		BigWorld.setWatcher( "Client Settings/Filters/Enabled", 'true' if on else 'false' )


	def active( self, show ):
		if self.isActive == show:
			return

		PyGUI.DraggableWindow.active( self, show )
		Cursor.showCursor( show )

		if show:
			self.onActive()



