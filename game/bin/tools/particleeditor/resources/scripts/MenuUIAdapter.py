import ParticleEditorDirector
import ParticleEditor
import ResMgr

from os import startfile

#---------------------------
# The file menu
#---------------------------

def doOpenFile( item ):
	"""This function enables the Open ParticleEditor ParticleSystem Dialog, 
	which allows a ParticleSystem to be loaded."""
	ParticleEditor.openFile()
    
def doSavePS( item ):
	"""This function forces ParticleEditor to reload all of its textures."""
	ParticleEditor.savePS()
    
def doReloadTextures( item ):
	"""This function forces ParticleEditor to reload all of its textures."""
	ParticleEditor.reloadTextures()    
    
def doExit( item ):
	"""This function closes ParticleEditor."""
	ParticleEditor.exit()
    
#---------------------------
# The edit menu
#---------------------------    
    
def doUndo( item ):
	"""This function undoes the most recent operation."""
	ParticleEditor.undo()

def updateUndo( item ):
	"""Checks whether it is possible to undo the most recent operation."""
	return ParticleEditor.canUndo()
  
def doRedo( item ):
	"""This function redoes the most recent undo operation."""
	ParticleEditor.redo()
  
def updateRedo( item ):
	"""This function checks whether it is possible to redo the most recent undo operation."""
	return ParticleEditor.canRedo()    
    
#---------------------------
# The view menu
#---------------------------

def doShowToolbar( item ):
	"""This function shows the specified toolbar."""
	ParticleEditor.showToolbar( "0" )
    
def doHideToolbar( item ):
	"""This function hides the specified toolbar."""
	ParticleEditor.hideToolbar( "0" )
    
def updateToolbar( item ):
	"""This function updates the status of the tick next to the specified toolbar in the
 	view->toolbars menu."""
	return ParticleEditor.updateShowToolbar( "0" )
    
def doShowStatusbar( item ):
	"""This function shows the status bar."""
	ParticleEditor.showStatusbar()  
    
def doHideStatusbar( item ):
	"""This function hides the status bar."""
	ParticleEditor.hideStatusbar()
    
def updateShowStatusbar( item ):
	"""This function updates the status of the tick next to the status bar in the view menu."""
	return ParticleEditor.updateShowStatusbar()       
    
def doShowPanels( item ):
	"""This function toggles whether the side panel is displayed or not."""
	ParticleEditor.toggleShowPanels()
	
def doShowPanelUAL( item ):
	"""This function toggles whether the UAL panel is displayed or not."""
	ParticleEditor.toggleShowUALPanel()

def doShowPanelMsgs( item ):
	"""This function toggles whether the UAL panel is displayed or not."""
	ParticleEditor.toggleShowMsgsPanel()

def doDefaultPanelLayout( item ):
	"""This function loads the default panel arrangement."""
	ParticleEditor.loadDefaultPanels()
    
def doLoadPanelLayout( item ):
	"""This function loads the most recent panel arrangement."""
	ParticleEditor.loadRecentPanels()    
                   
#---------------------------
# The help menu
#---------------------------

def doAboutApp( item ):
	"""This function displays the ParticleEditor About box."""
	ParticleEditor.aboutApp()
    
def doToolsReferenceGuide( item ):
	"""This function will open up the Content Tools Reference Guide PDF."""
	ParticleEditor.doToolsReferenceGuide()
    
def doContentCreation( item ):
	"""This function will open up the BigWorld Technology Content Creation Manual."""
	ParticleEditor.doContentCreation()
    
def doShortcuts( item ):
	"""This function will open up the ParticleEditor Shortcuts reference guide."""
	ParticleEditor.doShortcuts()

def doRequestFeature( item ):
	startfile( "mailto:support@bigworldtech.com?subject=ParticleEditor %2D Feature Request %2F Bug Report" )
