'''
This module implements post-processing related UI actions.
'''

import os.path
import WorldEditor
import BigWorld
import PostProcessing
import ResMgr

CHAIN_EXT = ".ppchain"
CHAIN_EXT_LEN = len( CHAIN_EXT )
INPUT_CANCEL = "<cancel>"


g_chainsFolder = ""
g_currentChain = ""


#-------------------------------------------------------------------------------
# Functions used in the UI's "Chains" dialog.
#-------------------------------------------------------------------------------


def init( chainsFolder ):
	global g_chainsFolder
	g_chainsFolder = chainsFolder


def getCurrentChain():
	global g_currentChain
	return g_currentChain

def setChain( chain ):
	global g_currentChain

	if nameOnly( chain ) == nameOnly( g_currentChain ) or not continueWithUnsavedChanges():
		return

	if chain != "":
		newChain = chain + CHAIN_EXT
		g_currentChain = ResMgr.resolveToAbsolutePath( newChain )
		chainDS = ResMgr.openSection( g_currentChain )
		if chainDS != None:
			WorldEditor.userEditingPostProcessing( False )
			newEffects = PostProcessing.load( chainDS )
			PostProcessing.chain( newEffects )
		else:
			msg = ResMgr.localise( "SCRIPT/POST_PROCESSING_UI_ADAPTER_PY/FAILED_LOADING_CHAIN", g_currentChain )
			WorldEditor.addCommentaryMsg( msg, 1 );
	else:
		WorldEditor.userEditingPostProcessing( False )
		PostProcessing.defaultChain()
		g_currentChain = ""


def newChain():
	global g_currentChain

	if g_currentChain != "" and not continueWithUnsavedChanges():
		return
	
	# Clear the current chain name so "saveChanges" creates a new chain.
	g_currentChain = ""
	saveChanges()


def renameChain( newName ):
	global g_currentChain
	global g_chainsFolder
	
	if not isNameValid( newName ):
		WorldEditor.messageBox( "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_NAME_INVALID_TEXT", "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_NAME_INVALID_TITLE", "error" )
	else:
		oldPath, oldChain = os.path.split(g_currentChain)
		newChain = oldPath + "/" + newName + CHAIN_EXT
		newPath = ResMgr.resolveToAbsolutePath( newChain )
		ResMgr.rename( g_currentChain, newPath )
		g_currentChain = newPath
	

def duplicateChain():
	global g_currentChain
	global g_chainsFolder
	
	if g_currentChain != "":
		oldPath, oldChain = os.path.split(g_currentChain)
		newChain = oldPath + "/" + generateChainName( nameOnly( oldChain ) )
		newPath = ResMgr.resolveToAbsolutePath( newChain )
		ResMgr.copy( g_currentChain, newPath )
		g_currentChain = newPath
	else:
		newChain = g_chainsFolder + generateChainName( "default chain" )
		g_currentChain = ResMgr.resolveToAbsolutePath( newChain )
		chainDS = ResMgr.openSection( g_currentChain, True )
		if chainDS != None:
			PostProcessing._save( chainDS )
	

def deleteChain():
	global g_currentChain

	if WorldEditor.messageBox( "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/DELETE_TEXT", "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/DELETE_TITLE", "warning_yesno" ) == "no":
		return
	
	if not ResMgr.remove( g_currentChain ):
		msg = ResMgr.localise( "SCRIPT/POST_PROCESSING_UI_ADAPTER_PY/FAILED_REMOVING_CHAIN", g_currentChain )
		WorldEditor.addCommentaryMsg( msg, 1 );
		return

	g_currentChain = ""

	# Reset to the default chain, which will end up calling setChain( "" ).
	WorldEditor.userEditingPostProcessing( False )
	PostProcessing.defaultChain()

		
def saveChanges():
	global g_currentChain

	ok = False
	
	newChain = False
	
	if g_currentChain == "":
		if not getNewChainName():
			return
		newChain = True
		
	if g_currentChain != "":
		print "Saving to " + g_currentChain
		chainDS = ResMgr.openSection( g_currentChain, newChain )
		if chainDS != None:
			PostProcessing._save( chainDS )
			WorldEditor.userEditingPostProcessing( False )
			ok = True
	
	if ok:
		msg = ResMgr.localise( "SCRIPT/POST_PROCESSING_UI_ADAPTER_PY/CHAIN_SAVED_TO", g_currentChain )
		WorldEditor.addCommentaryMsg( msg );
	else:
		msg = ResMgr.localise( "SCRIPT/POST_PROCESSING_UI_ADAPTER_PY/FAILED_SAVING_CHAIN", g_currentChain )
		WorldEditor.addCommentaryMsg( msg, 1 );
	
	
def discardChanges():
	if not WorldEditor.isUserEditingPostProcessing() or \
		WorldEditor.messageBox( "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/DISCARD_TEXT", "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/DISCARD_TITLE", "warning_yesno" ) == "yes":
		# Reset to the default chain, which will end up calling setChain( "" ).
		WorldEditor.userEditingPostProcessing( False )
		PostProcessing.defaultChain()


def onExit():
	if WorldEditor.isUserEditingPostProcessing():
		if WorldEditor.messageBox( "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_MODIFIED_TEXT", "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_MODIFIED_TITLE", "warning_yesno" ) == "yes":
			saveChanges()


#-------------------------------------------------------------------------------
# Internal helper functions
#-------------------------------------------------------------------------------


def nameOnly( chainPath ):
	chainName = chainPath
	if len( chainName ) > CHAIN_EXT_LEN and chainName[-CHAIN_EXT_LEN:] == CHAIN_EXT:
		chainName = chainName[:-CHAIN_EXT_LEN]
	fnameStart = chainName.rfind( "/" )
	if fnameStart == -1:
		fnameStart = chainName.rfind( "\\" )
		
	if fnameStart > 0:
		chainName = chainName[fnameStart + 1:]
	
	return chainName


def continueWithUnsavedChanges():
	if WorldEditor.isUserEditingPostProcessing():
		needsSave = WorldEditor.messageBox( "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_MODIFIED_TEXT", "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_MODIFIED_TITLE", "warning_yesnocancel" )
		if needsSave == "cancel":
			return False
		elif needsSave == "yes":
			saveChanges()

	return True
	

def getChains():
	chainNames = []
	
	dirDS = ResMgr.openSection( g_chainsFolder )

	for filename in dirDS.keys():
		if filename[-CHAIN_EXT_LEN:] == CHAIN_EXT:
			chainNames.append( filename[:-CHAIN_EXT_LEN] )
	
	return chainNames


def isNameValid( inputStr ):
	if inputStr == "":
		return False

	if inputStr.find( "\\" ) != -1 or inputStr.find( "/" ) != -1 or inputStr.find( ":" ) != -1 or \
		inputStr.find( "*" ) != -1 or inputStr.find( "?" ) != -1 or inputStr.find( "\"" ) != -1 or \
		inputStr.find( "<" ) != -1 or inputStr.find( ">" ) != -1 or inputStr.find( "|" ) != -1:
		return False

	chains = getChains()
	
	for chain in chains:
		if chain == inputStr:
			return False

	return True
	

def getNewChainName( defaultStr = "" ):
	global g_currentChain

	inputStr = ""
	while inputStr != INPUT_CANCEL and not isNameValid( inputStr ):
		inputStr = WorldEditor.stringInputBox( "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_NAME_TEXT", "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_NAME_TITLE", 80, defaultStr )
		if inputStr != INPUT_CANCEL and not isNameValid( inputStr ):
			WorldEditor.messageBox( "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_NAME_INVALID_TEXT", "`WORLDEDITOR/GUI/PAGE_POST_PROCESSING/CHAIN_NAME_INVALID_TITLE", "error" )
			
	if inputStr == INPUT_CANCEL: # got the special cancel string, so don't save.
		return False
		
	if len( inputStr ) <= CHAIN_EXT_LEN or inputStr[-CHAIN_EXT_LEN:] != CHAIN_EXT:
		inputStr = inputStr + CHAIN_EXT
	
	g_currentChain = ResMgr.resolveToAbsolutePath( g_chainsFolder + inputStr )
	return True


def generateChainName( oldName ):
	maxIdx = 0
	chains = getChains()
	postfix = " copy "
	for chain in chains:
		if oldName == chain[ : len( oldName ) ]:
			pos = chain.rfind( postfix )
			numStr = chain[ pos + len( postfix ) : ].strip( " " )
			if pos > 0 and numStr.isdigit():
				try:
					num = int( numStr )
					if num > maxIdx:
						maxIdx = num
				except:
					pass
				
	pos = oldName.rfind( postfix )
	numStr = "%02d" % (maxIdx + 1)
	newChain = ""
	if pos > 0:
		newChain = oldName[ : pos + len( postfix )]  + numStr + CHAIN_EXT
	else:
		newChain = oldName + postfix + numStr + CHAIN_EXT
	return newChain