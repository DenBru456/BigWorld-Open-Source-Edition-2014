import BigWorld, GUI

from Button import Button
from CheckBox import CheckBox

class RadioButton( CheckBox ):

	factoryString = "PyGUI.RadioButton"

	def __init__( self, component ):
		CheckBox.__init__( self, component )
		self.buttonStyle = Button.RADIOBUTTON_STYLE


	@staticmethod
	def create( texture="", label="", groupName="", visualStates="", **kwargs ):
		c = CheckBox.createInternal( texture, label, **kwargs )
		b = RadioButton( c, **kwargs )
		if visualStates:
			b.loadVisualStates( visualStates )
		b.groupName = groupName
		b.onBound()
		return c
		
