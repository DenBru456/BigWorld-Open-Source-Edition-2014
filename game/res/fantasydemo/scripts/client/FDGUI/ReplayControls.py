import BigWorld
import GUI
import Helpers.PyGUI as PyGUI
import BWReplay
import Cursor

from Helpers.PyGUI import PyGUIEvent

class ReplayControls( PyGUI.DraggableWindow ):

	factoryString = "FDGUI.ReplayControls"

	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )
		self.isDraggingSlider = False

	def avatarInit( self, avatar ):
		# Hide controls if it was active
		self.active( False )

	@PyGUIEvent( "pauseButton", "onClick" )
	def pauseClick( self ):
		if not BWReplay.isLoaded():
			return
		BWReplay.pausePlayback()

		BWReplay.setSpeedScale( 1.0 )
		self._updateSpeedText()

	@PyGUIEvent( "playButton", "onClick" )
	def playClick( self ):
		if not BWReplay.isLoaded():
			return
		BWReplay.resumePlayback()

		BWReplay.setSpeedScale( 1.0 )
		self._updateSpeedText()

	@PyGUIEvent( "stopButton", "onClick" )
	def stopClick( self ):
		if not BWReplay.isLoaded():
			return
		BWReplay.stopPlayback()

	@PyGUIEvent( "slowButton", "onClick" )
	def slowClick( self ):
		if not BWReplay.isLoaded():
			return

		scaleLimit = 4

		if BWReplay.getSpeedScale() >= scaleLimit:
			return

		newScale = min( BWReplay.getSpeedScale() * 2, scaleLimit )


		BWReplay.setSpeedScale( newScale )
		self._updateSpeedText()

	@PyGUIEvent( "fastButton", "onClick" )
	def fastClick( self ):
		if not BWReplay.isLoaded():
			return

		scaleLimit = (1.0/16)

		if BWReplay.getSpeedScale() <= scaleLimit:
			return

		newScale = max( BWReplay.getSpeedScale() / 2, scaleLimit )

		BWReplay.setSpeedScale( newScale )
		self._updateSpeedText()

	@PyGUIEvent( "slider", "onValueChanged" )
	def sliderMoving( self, value ):
		if not BWReplay.isLoaded():
			return

		updateHz = BWReplay.getUpdateHz()

		timeIn = value / updateHz
		timeInMin = int(timeIn / 60)
		timeInSec = timeIn - (timeInMin * 60)

		total = BWReplay.getTotalTicks() / updateHz
		totalInMin = int(total / 60)
		totalInSec = total - (totalInMin * 60)

		self.component.infoText.text = "%02d:%02d / %02d:%02d" % \
					(timeInMin, timeInSec, totalInMin, totalInSec)
					
		self._updateSpeedText()

	@PyGUIEvent( "slider", "onBeginDrag" )
	def sliderBeginDrag( self, value ):
		if not BWReplay.isLoaded():
			return

		self.isDraggingSlider = True

	@PyGUIEvent( "slider", "onEndDrag" )
	def sliderEndDrag( self, value ):
		if not BWReplay.isLoaded():
			return

		BWReplay.setCurrentTick( value )

		self.isDraggingSlider = False

	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )

	def active( self, show ):
		PyGUI.DraggableWindow.active( self, show )
		Cursor.showCursor( show )

	def onBound( self ):
		PyGUI.DraggableWindow.onBound( self )
		
	def _updateSpeedText( self ):
		self.component.speedScale.text = "x%.2g" % (1/BWReplay.getSpeedScale())