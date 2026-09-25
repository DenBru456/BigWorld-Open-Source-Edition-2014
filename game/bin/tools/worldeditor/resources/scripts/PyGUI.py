import WorldEditor
import Keys
import GUI
import string

class PyGUIBase:

	def __init__( self ):
		#derived classes must set this
		self.component = None
		self.eventHandler = None

	def visible( self, state ):
		if ( self.component ):
			if ( state ):
				GUI.addRoot( self.component )
			else:
				GUI.delRoot( self.component )

	def setEventHandler( self, eh ):
		self.eventHandler = eh


class Button( PyGUIBase ):
	
	def __init__( self, textLabel ):

		PyGUIBase.__init__( self )

		self.clickState = 0
		self.buttonEvent = "GenericButtonEvent"

		#setup GUI
		self.button = GUI.Simple( "terrainEditor/maps/gui/button_default.tga" )
		self.button.position = ( 0,0,0.5 )
		self.button.colour = ( 255, 255, 255, 192 )
		self.button.width = 256
		self.button.height = 32
		self.button.script = self
		self.textures( "terrainEditor/maps/gui/button_default.tga", "terrainEditor/maps/gui/button_rollover.tga", "terrainEditor/maps/gui/button_mousedown.tga" )

		self.label = GUI.Text()
		self.label.text = textLabel
		self.button.addChild( self.label )

		self.component = self.button

	def setButtonEvent( self, ev ):
		self.buttonEvent = ev

	def textures( self, tex1, tex2, tex3 ):
		self.textureDefault = tex1
		self.textureFocus = tex2
		self.textureMouseDown = tex3

	def focus( self, state, c ):

		if ( state ):
			c.textureName = self.textureFocus
		else:
			c.textureName = self.textureDefault


	def handleEvent( self, type, key, modifiers, c ):

		if ( WorldEditor.isKeyDown( key ) ):

			if ( key == Keys.KEY_LEFTMOUSE ) :
				c.textureName = self.textureMouseDown
				self.clickState = 1
				return 1

		else:
			
			if ( key == Keys.KEY_LEFTMOUSE ) :
				c.textureName = self.textureFocus
				if ( self.clickState == 1 ):
					if ( self.eventHandler != None ):
						self.eventHandler.onClick( self.buttonEvent )
				return 1
		
		return 0


class EditField( PyGUIBase ):

	def __init__( self ):

		PyGUIBase.__init__( self )
		
		self.component = GUI.Text()
		self.component.text = "_"
		self.component.position = ( 0,0,0.5 )
		self.component.colour = ( 92, 92, 92, 128 )
		self.component.width = 256
		self.component.height = 32
		self.component.script = self

	def focus( self, state, c ):
		if ( state ):
			c.colour = ( 128, 128, 128, 255 )
			c.text = c.text + "_"
		else:
			c.colour = ( 92, 92, 92, 128 )
			c.text = c.text[0:len(c.text)-1]

	def handleEvent( self, type, key, modifiers, c ):

		shiftDown = WorldEditor.isKeyDown( Keys.KEY_LSHIFT ) or WorldEditor.isKeyDown( Keys.KEY_RSHIFT )

		if ( WorldEditor.isKeyDown( key ) ):

			if ( key == Keys.KEY_BACKSPACE ) :
				c.text = c.text[0:len(c.text)-1]
				c.text = c.text[0:len(c.text)-1]	
				c.text = c.text + "_"

				return 1

			elif ( key >= Keys.KEY_1 and key <= Keys.KEY_0 ) :
				character = WorldEditor.keyToString( key )

				c.text = c.text[0:len(c.text)-1]
				c.text = c.text + character
				c.text = c.text + "_"

				return 1

			elif ( key >= Keys.KEY_Q and key <= Keys.KEY_P ) :
				character = WorldEditor.keyToString( key )
				if ( not shiftDown ):
					character = string.swapcase( character )

				c.text = c.text[0:len(c.text)-1]
				c.text = c.text + character
				c.text = c.text + "_"

				return 1

			elif ( key >= Keys.KEY_A and key <= Keys.KEY_L ) :
				character = WorldEditor.keyToString( key )
				if ( not shiftDown ):
					character = string.swapcase( character )

				c.text = c.text[0:len(c.text)-1]
				c.text = c.text + character
				c.text = c.text + "_"

				return 1

			elif ( key >= Keys.KEY_Z and key <= Keys.KEY_M ) :
				character = WorldEditor.keyToString( key )
				if ( not shiftDown ):
					character = string.swapcase( character )

				c.text = c.text[0:len(c.text)-1]
				c.text = c.text + character
				c.text = c.text + "_"

				return 1

			elif ( key == Keys.KEY_SPACE ) :

				c.text = c.text[0:len(c.text)-1]
				c.text = c.text + " "
				c.text = c.text + "_"

				return 
				
			elif ( key == Keys.KEY_RETURN ) :
				if ( self.eventHandler != None ):
					textString = c.text
					self.eventHandler.onClick( c.text[0:len(c.text)-1] )
				

			if ( key == Keys.KEY_LEFTMOUSE ) :
				c.colour = ( 128, 255, 128, 255 )
				return 1

		else:
			
			if ( key == Keys.KEY_LEFTMOUSE ) :
				c.colour = ( 128, 128, 128, 255 )
				return 1
		
		return 0
