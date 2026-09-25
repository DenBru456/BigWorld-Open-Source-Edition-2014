import BigWorld
import GUI

from .. import DraggableWindow
from .. import PyGUIEvent
from .. import FocusManager
from .. import IME

import random
from functools import partial

def clear():
	for x in GUI.roots():
		GUI.delRoot( x )

def _deleteComponent( t ):
	if t.parent:
		t.parent.delChild(t)
	else:
		GUI.delRoot(t)
		
class TestWindow( DraggableWindow ):

	factoryString = "PyGUI.Test.TestWindow"
	
	def __init__( self, component ):
		DraggableWindow.__init__( self, component )
		
	@PyGUIEvent( "button1", "onClick" )
	def buttonClicked( self ):
		#print "TestWindow.buttonClicked"
		
		t = GUI.Text( "Button Clicked!" )
		t.colour = (255,0,0,255)
		t.position.y = 0.85
		t.verticalAnchor = "TOP"
		GUI.addRoot(t)
		
		BigWorld.callback( 2.5, partial(_deleteComponent, t) )
		
	@PyGUIEvent( "button2", "onActivate", True )
	@PyGUIEvent( "button2", "onDeactivate", False )
	def buttonToggled( self, newState ):
		#print "TestButton.buttonToggled", newState		
		self.component.statusLabel.text = "Toggle state: %s" % ("True" if newState else "False")
	
	@PyGUIEvent( "slider", "onBeginDrag" )
	def sliderBeginDrag( self, value ):
		#print "draggableBeginDrag"
		self.component.draggableStatus.text = "Dragging (value=%d)" % int(value)
	
	@PyGUIEvent( "slider", "onEndDrag" )
	def sliderEndDrag( self, value ):
		#print "draggableEndDrag"
		self.component.draggableStatus.text = ""
		
	@PyGUIEvent( "slider", "onValueChanged" )
	def sliderValueChanged( self, value ):
		#print "draggableDragging"
		self.component.draggableStatus.text = "Dragging (value=%d)" % int(value)
		self.component.draggableStatus.colour = (	int(random.random()*127), 
													int(random.random()*127), 
													int(random.random()*127), 
													255 )
													
													
	@PyGUIEvent( "editField", "onEnter" )
	def editFieldOnEnter( self, text ):	
		t = GUI.Text( "Entered Text: %s" % text )
		t.colour = (255,0,0,255)
		t.position.y = 0.9
		t.verticalAnchor = "TOP"
		GUI.addRoot(t)
		
		BigWorld.callback( 2.5, partial(_deleteComponent, t) )		
		self.component.editField.script.setText( "" )
		
	@PyGUIEvent( "editField", "onEscape" )
	def editFieldOnEscape( self ):
		FocusManager.setFocusedComponent( None )		
		
	@PyGUIEvent( "editField", "onChangeFocus" )
	def editFieldOnChangeFocus( self, state ):
		self.component.editField.script.setText( "" if state else "Enter Text Here" )
		self.component.editField.languageIndicator.visible = state



def test():
	BigWorld.camera(BigWorld.CursorCamera()) # Change camera type since FreeCamera eats mouse input
	BigWorld.setCursor( GUI.mcursor() )
	GUI.mcursor().visible = True

	clear()
	w = GUI.load("gui/tests/window.gui")
	if w is None or w.script is None:
		print "Fail to load gui/tests/window.gui, please check the specified path"
	else:
		w.script.active( True )
	IME.fini()
	IME.init()
	return w


		