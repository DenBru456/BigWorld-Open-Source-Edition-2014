import PostProcessing
import BigWorld
import ResMgr
import GUI
import FDGUI
import Math
from Helpers.PyGUI import Window, DraggableWindow, PyGUIEvent, PyGUIBase
import Keys
from Helpers import collide
from functools import partial
from PostProcessing.Effects import DepthOfField
from Helpers import BWKeyBindings
from Helpers.BWKeyBindings import BWKeyBindingAction
import FantasyDemo


ppds = ResMgr.openSection( "system/post_processing/chains/dslr.ppchain" )
resources = [ "gui/maps/dslr/activated.tga",
				   "gui/maps/dslr/off.tga",
				   "gui/maps/dslr/overlay.tga",
				   "gui/maps/dslr/off.tga",
				   "gui/maps/dslr/off.tga",
				   "gui/maps/dslr/off.tga" ]



#class DSLR( DraggableWindow ):
class DSLR( PyGUIBase ):
	factoryString="FDGUI.DSLR"

	def __init__( self, component ):
		#DraggableWindow.__init__( self, component )
		PyGUIBase.__init__( self, component )
		self.savedChain = None
		self.chain = PostProcessing.load( ppds )
		self.nearRangePct = 0.001
		self.inFocusPct = 0.002
		self.farRangePct = 0.004
		self.zFocus = 0.002
		self.targetEntity = None


	def active( self, isActivating ):
		if self.isActive == isActivating:
			return

		if isActivating:
			if self.savedChain == None:			#activating for the first time
				PostProcessing.chain( self.chain )
				self.focusOnEntity( BigWorld.player() )
			else:								#successive times
				PostProcessing.chain( self.savedChain )
			if self.targetEntity:
				self.focusOnEntity( self.targetEntity )
		
		if not isActivating:
			self.savedChain = PostProcessing.chain()

		self.component.focus = True
		#DraggableWindow.active(self, isActivating)
		PyGUIBase.active(self, isActivating)


	def onSave( self, dataSection ):
		#DraggableWindow.onSave( self, dataSection )
		PyGUIBase.onSave( self, dataSection )


	def onLoad( self, dataSection ):
		#DraggableWindow.onLoad( self, dataSection )
		PyGUIBase.onLoad( self, dataSection )
		
		
	def getMouseCollidePos( self ):
		mp = GUI.mcursor().position
		collisionType, target = collide.collide( mp.x, mp.y )
		return ( collisionType, target )
		
		
	def setMaterialZFocus( self, zFocus ):
		self.zFocus = zFocus
		print "setMaterialZFocus", zFocus
		DepthOfField.zFocus.set( zFocus, 0.25 )


	def focusOnMouseWorldPosition( self ):
		self.targetEntity = None
		collisionType, target = self.getMouseCollidePos()
		if collisionType != collide.COLLIDE_NONE:
			if collisionType == collide.COLLIDE_ENTITY:
				#print "collision with entity : ", target
				self.focusOnEntity( target )
			else:
				#print "collision at ", self.getMouseCollidePos(), " : ", collisionType, target
				focusPt = target
				cam = Math.Matrix( BigWorld.camera().invViewMatrix )
				zFocus = (focusPt - cam.applyToOrigin()).length
				self.setMaterialZFocus( zFocus )
		else:
			print "no colision at ", self.getMouseCollidePos()


	def focusOnEntity( self, entity ):
		try:
			focusPt = entity.model.node( "biped Head" )
		except:
			focusPt = entity.model.root
		cam = BigWorld.camera().invViewMatrix
		zFocus = Math.Vector4Distance( focusPt, cam )
		self.setMaterialZFocus( zFocus )
		self.targetEntity = entity
			
			
	def narrowRange( self, shifted, ctrled  ):
		aperture = DepthOfField.aperture
		focalLength = DepthOfField.focalLength
		
		if shifted:
			newAperture = max(0.0025, aperture.get() * 0.8)
			aperture.set( newAperture )
			#FantasyDemo.addChatMsg( -1, "Aperture %0.2f" % (newAperture,) )
		elif ctrled:
			newFocalLength = max(0.05, focalLength.get() * 0.8)
			newFocalLength = max(aperture.get() * 2.0, newFocalLength)
			focalLength.set( newFocalLength )
			#FantasyDemo.addChatMsg( -1, "Focal Length %0.2f" % (newFocalLength,) )


	def widenRange( self, shifted, ctrled ):
		aperture = DepthOfField.aperture
		focalLength = DepthOfField.focalLength

		if shifted:
			newAperture = min(0.25, aperture.get() / 0.8)
			newAperture = min(focalLength.get() / 2.0, newAperture)
			aperture.set( newAperture )
			#FantasyDemo.addChatMsg( -1, "Aperture %0.2f" % (newAperture,) )
		elif ctrled:
			newFocalLength = min(0.5, focalLength.get() / 0.8)
			focalLength.set( newFocalLength )
			#FantasyDemo.addChatMsg( -1, "Focal Length %0.2f" % (newFocalLength,) )


	def handleKeyEvent( self, event ):
		if ( event.isKeyDown() ):
			if event.key == Keys.KEY_ESCAPE :
				PyGUIBase.active(self, False)
				self.component.focus = False
				return True
			elif event.key == Keys.KEY_LEFTMOUSE:
				self.focusOnMouseWorldPosition()
				return True
			elif event.key == Keys.KEY_P:
				self.focusOnEntity( BigWorld.player() )
				return True
			elif event.key == Keys.KEY_LBRACKET:
				self.widenRange( event.isShiftDown(), event.isCtrlDown() )
				return True
			elif event.key == Keys.KEY_RBRACKET:
				self.narrowRange( event.isShiftDown(), event.isCtrlDown() )
				return True

		# listen to KEY_TAB but don't use up the event
		# camera is about to change, which will detach
		# this effect's vector4 providers.  So rehook them up.
		if event.key == Keys.KEY_TAB:
			if ( not event.isKeyDown() ):
				if self.targetEntity != None:
					self.focusOnEntity( self.targetEntity )
				
		
		return False


	@staticmethod
	def create():
		
		menu = GUI.Window( "" )
		menu.activated = GUI.Simple("")
		menu.off = GUI.Simple( "" )
		menu.overlay = GUI.Simple( "" )
		menu.activated.textureName = resources[0]
		menu.off.textureName = resources[1]
		menu.overlay.textureName = resources[2]
		menu.overlay.materialFX = "ADD"
		menu.off.position = (0,0,1.0)
		menu.activated.position = (0,0,0.5)
		menu.overlay.position = (0,0,0.5)
		menu.reSort()
		menu.off.materialFX="SOLID"
		menu.activated.materialFX="BLEND"
		menu.overlay.materialFX="ADD"
		width = menu.off.texture.width
		height = menu.off.texture.height
		menu.widthMode = menu.heightMode = "PIXEL"
		menu.size = (250,183)
		menu.activated.widthMode = menu.activated.heightMode = "CLIP"
		menu.off.widthMode = menu.off.heightMode = "CLIP"
		menu.overlay.widthMode = menu.overlay.heightMode = "CLIP"
		menu.activated.size = (2,2)
		menu.off.size = (2,2)
		menu.overlay.size = (2,2)
		menu.horizontalAnchor = "RIGHT"
		menu.verticalAnchor = "BOTTOM"
		menu.position=(1,-1,0.5)
		
		viewfinder = GUI.Window( "gui/maps/dslr/viewfinder.tga" )
		viewfinder.size=2,2
		viewfinder.materialFX="BLEND"
		viewfinder.menu = menu
		viewfinder.menu.visible = 0
		viewfinder.colour = (192,255,192,32)
		
		viewfinder.script = DSLR( viewfinder )
		viewfinder.script.active(1)
		
		viewfinder.save( "gui/dslr.gui" )
		
		return viewfinder


g_dslr = None
class DSLRActionHandler( BWKeyBindings.BWActionHandler ):

	@BWKeyBindings.BWKeyBindingAction( "DSLRKey" )
	def dslrKey( self, isDown ):
		if isDown:
			if BigWorld.getGraphicsSetting( "POST_PROCESSING_QUALITY" ) == 0: #VERY HIGH
				global g_dslr
				if not g_dslr:
					g_dslr = DSLR.create()
				else:
					g_dslr.script.active(0)
					g_dslr.script.active(1)
			else:
				FantasyDemo.addChatMsg( -1, 'DLSR is only available when the Post Processing graphics setting is set to HIGH' )
