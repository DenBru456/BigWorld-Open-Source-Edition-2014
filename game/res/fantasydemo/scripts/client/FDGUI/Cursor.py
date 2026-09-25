import BigWorld
import GUI

from bwdebug import WARNING_MSG

_mouseModeRefCount = 0

def showCursor( show ):
	global _mouseModeRefCount

	if show:
		_mouseModeRefCount += 1
		if _mouseModeRefCount > 0:
			BigWorld.setCursor( GUI.mcursor() )
			GUI.mcursor().visible = True
			GUI.mcursor().clipped = False
	else:
		_mouseModeRefCount -= 1
		if _mouseModeRefCount == 0:
			BigWorld.setCursor( BigWorld.dcursor() )
			GUI.mcursor().visible = False
			GUI.mcursor().clipped = True

		if _mouseModeRefCount < 0:
			WARNING_MSG( "mouseModeRefCount is negative!" )


def forceShowCursor( show ):
	if show:
		BigWorld.setCursor( GUI.mcursor() )
		GUI.mcursor().visible = True
		GUI.mcursor().clipped = False		
	else:
		BigWorld.setCursor( BigWorld.dcursor() )
		GUI.mcursor().visible = False
		GUI.mcursor().clipped = True
