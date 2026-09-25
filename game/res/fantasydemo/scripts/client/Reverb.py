import BigWorld
import GUI
import FMOD
import Math

ENABLE_DEBUGGING = True

class Reverb( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
                
	def onEnterWorld( self, prereqs ):	
		self.reverb = FMOD.EventReverb( self.presetName )

		self.reverb.minDistance = self.innerRadius
		self.reverb.maxDistance = self.outerRadius
		self.reverb.active = True
		
		self.reverb.source = Math.Matrix()
		self.reverb.source.setTranslate( self.position )
		
		
		if ENABLE_DEBUGGING:
			self.model = BigWorld.Model( "helpers/models/unit_cube.model" )
			
			t = GUI.Text( "Reverb: %s, Inner: %f, Outer: %f" % (self.presetName, self.innerRadius, self.outerRadius) )
			t.explicitSize = True
			t.height = 0.75
			t.width = 0
			t.filterType = "LINEAR"
			t.verticalAnchor = "BOTTOM"
			t.position = (0, self.model.height + 0.1, 0)
			
			attch = GUI.Attachment()
			attch.faceCamera = True
			attch.component = t
			
			self.model.root.attach( attch )
        
	def onLeaveWorld( self ):
		self.reverb.active = False
		self.reverb = None		
		self.model = None

