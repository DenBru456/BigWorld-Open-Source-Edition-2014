import BigWorld
import FantasyDemo

from Helpers.VideoModeUtils import enumVideoModes, enumAspectRatios

from TextListPage import TextListPage
from ValueChooserPage import ValueChooserPage

from functools import partial

import OpenAutomate

def aspectRatioStatus():
	ratios, current = enumAspectRatios()
	if current >= 0:
		return "[" + ratios[current][0] + "]"
	else:
		return "[Auto]"
		
def getResolutionStatus():
	return "[%dx%d]" % BigWorld.screenSize()
	
def selectOnOffText( boolFn ):
	return ["[Off]", "[On]"][int(boolFn())]

class VideoSettingsPage( TextListPage ):
	caption = "Video Settings"

	def populate( self ):
		if BigWorld.isVideoWindowed():
			toggleWindowedMsg = 'Switch to Full Screen'
			resolutionText    = 'Select Window Size...'
		else:
			toggleWindowedMsg = 'Switch to Windowed Mode'
			resolutionText    = 'Select Resolution...'
		
		self.addItem( toggleWindowedMsg, self.toggleWindowed )
		self.addItem( resolutionText, self.selectResolution, getResolutionStatus() )
		self.addItem( 'Select Fullscreen Aspect Ratio...', self.selectAspectRatio, aspectRatioStatus() )
		self.addItem( 'Vertical Sync...', self.selectVertialSync, selectOnOffText( BigWorld.isVideoVSync ) )
		self.addItem( 'Triple Buffering...', self.selectTripleBuffering, selectOnOffText( BigWorld.isTripleBuffered ) )
		
	def toggleWindowed( self ):
		curModeIdx = BigWorld.videoModeIndex()
		BigWorld.changeVideoMode( curModeIdx, not BigWorld.isVideoWindowed() )
		self.repopulate()
		
	def selectResolution( self ):
		def changeMode( mode ):
			if not BigWorld.isVideoWindowed():
				FantasyDemo.enableAutomaticAspectRatio( True )

			if BigWorld.isVideoWindowed():
				BigWorld.resizeWindow( mode[1], mode[2] )
			else:
				BigWorld.changeVideoMode( mode[0], False )

			self.repopulate()
		
		modes, curSel = enumVideoModes()
		items = [ (mode[4], mode)  for mode in modes ]
		page = ValueChooserPage( self.menu,
					items, curSel,
					changeMode
				)
		self.menu.push( page )
		
	def selectAspectRatio( self ):
		def setAspectRatio( ratio ):
			if ratio > 0:
				BigWorld.changeFullScreenAspectRatio( ratio )
			FantasyDemo.enableAutomaticAspectRatio( ratio == 0 )
			# TODO: UGLY! Work out a way to decouple this from here
			FantasyDemo.rds.fdgui.chooseResolutionBracket()
			self.menu.doLayout()
			self.repopulate()
	
		ratios, curSel = enumAspectRatios()
		items = [ (ratio[0], ratio[1]) for ratio in ratios ]
		items = [ ("Automatic", 0) ] + items
		page = ValueChooserPage( self.menu,
					items, curSel+1,
					setAspectRatio
				)
		self.menu.push( page )
		
	def selectVertialSync( self ):
		items  = [ ("On", True), ("Off", False) ]
		curSel = int(BigWorld.isVideoVSync())
		page = ValueChooserPage( self.menu,
					items, curSel,
					partial( self.applyAndRefresh, BigWorld.setVideoVSync )
				)
		self.menu.push( page )
		
	def selectTripleBuffering( self ):
		items  = [ ("On", True), ("Off", False) ]
		curSel = int(BigWorld.isTripleBuffered())
		page = ValueChooserPage( self.menu,
					items, curSel,
					partial( self.applyAndRefresh, BigWorld.setTripleBuffering )
				)
		self.menu.push( page )

	def applyAndRefresh( self, applyFn, value ):
		applyFn( value )
		self.repopulate()
