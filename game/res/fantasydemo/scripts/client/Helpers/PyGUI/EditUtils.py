import BigWorld, GUI, Math, ResMgr

# TODO: put docstrings on these

def setup():
	BigWorld.camera(BigWorld.CursorCamera()) # Change camera type since FreeCamera eats mouse input
	BigWorld.setCursor( GUI.mcursor() )
	GUI.mcursor().visible = True


def clearAll():
	while len(GUI.roots()):
		GUI.delRoot(GUI.roots()[0])


def clone( component ):
	ResMgr.purge( "gui/temp_clone.gui", True )
	component.save( "gui/temp_clone.gui" )
	return GUI.load( "gui/temp_clone.gui" )


weatherWindow = None
def weather():
	global weatherWindow
	setup()
	weatherWindow = GUI.load( "gui/weather_window.gui" )
	GUI.addRoot( weatherWindow )
	return weatherWindow

def saveWeather():
	global weatherWindow
	if weatherWindow:
		weatherWindow.save( "gui/weather_window.gui" )

