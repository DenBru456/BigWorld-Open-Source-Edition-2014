# Modify Resource Paths
from maya import cmds
import os
from functools import partial

def updateTextScrollList(pathsManager, pathsList):
    cmds.textScrollList(pathsList, edit=True, removeAll=True)
    cmds.textScrollList(pathsList, edit=True, append=pathsManager.getArrayOfPaths())

def addPath(pathsManager, pathsList, *args):
    dirArray = cmds.fileDialog2(caption="Select Resource Path to Add", fileMode=3, dialogStyle=1)
    # Handle dialog cancel
    if dirArray is None or not dirArray[0]:
        return None
    destDir = str(dirArray[0])

    pathsManager.addPath(destDir)
    updateTextScrollList(pathsManager, pathsList)

def modifyPath(pathsManager, pathsList, *args):
    selection = cmds.textScrollList(pathsList, query=True, selectItem=True)
    if not selection or not selection[0]:
        return
    originalText = str(selection[0])
    absPath = os.path.abspath(originalText)
    dirArray = cmds.fileDialog2(caption="Select Resource Path to Add", fileMode=3, dialogStyle=1, startingDirectory=absPath)
    # Handle dialog cancel
    if dirArray is None or not dirArray[0]:
        return None
    destDir = str(dirArray[0])

    pathsManager.modifyPath(originalText, destDir)
    updateTextScrollList(pathsManager, pathsList)

def removePath(pathsManager, pathsList, *args):
    selection = cmds.textScrollList(pathsList, query=True, selectItem=True)
    if not selection or not selection[0]:
        return
    selectedText = str(selection[0])
    result = cmds.confirmDialog( title='Confirm Remove', message='Are you sure you want to remove the path:\n  "%s"'%(selectedText), button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
    if result == 'Yes':
        pathsManager.removePath(selectedText)
        updateTextScrollList(pathsManager, pathsList)

def toggleAbsRelPath(pathsManager, pathsList, *args):
    selection = cmds.textScrollList(pathsList, query=True, selectItem=True)
    selectionIndices = cmds.textScrollList(pathsList, query=True, selectIndexedItem=True)
    if not selection or not selection[0]:
        return
    sel = str(selection[0])
    pathsManager.toggleAbsRelPath(sel)
    updateTextScrollList(pathsManager, pathsList)
    cmds.textScrollList(pathsList, edit=True, selectIndexedItem=selectionIndices)
    

def gui(pathsManager):
    form = cmds.setParent(q=True)

    filenameText = cmds.text(l='Filename: %s' % pathsManager.xmlfile )

    pathsList = cmds.textScrollList( numberOfRows=8, allowMultiSelection=False )
    updateTextScrollList(pathsManager, pathsList)

    buttonAdd    = cmds.button(l='Add', c=partial(addPath, pathsManager, pathsList) )
    buttonRemove = cmds.button(l='Remove Sel.', c=partial(removePath, pathsManager, pathsList) )
    buttonModify = cmds.button(l='Modify Sel.', c=partial(modifyPath, pathsManager, pathsList) )
    buttonToggleAbsRel = cmds.button(l='Toggle Sel. Abs/Rel', c=partial(toggleAbsRelPath, pathsManager, pathsList) )
    buttonSaveExit = cmds.button(l='Save and Exit', c='from maya import cmds; cmds.layoutDialog(dismiss="OK")')
    buttonCancel = cmds.button(l='Cancel', c='from maya import cmds; cmds.layoutDialog(dismiss="Cancel")')

    spacer = 5
    edgeOffset = 5

    cmds.formLayout(form, edit=True,
                    attachForm=[(filenameText, 'top', edgeOffset)]
                                + [(n, 'left', edgeOffset) for n in [filenameText, buttonAdd, pathsList, buttonSaveExit]]
                                + [(n, 'right', edgeOffset) for n in [filenameText, buttonToggleAbsRel, pathsList, buttonCancel]]
                                + [(n, 'bottom', edgeOffset) for n in [buttonSaveExit, buttonCancel]],
                    attachNone=[(filenameText, 'bottom')],
                    attachControl=[(pathsList, 'top', spacer, filenameText)]
                                + [(pathsList, 'bottom', spacer, n) for n in [buttonAdd, buttonRemove, buttonModify, buttonToggleAbsRel]]
                                + [(n, 'bottom', spacer, buttonSaveExit) for n in [buttonAdd, buttonRemove]]
                                + [(n, 'bottom', spacer, buttonCancel) for n in [buttonModify, buttonToggleAbsRel]],
                    attachPosition=[(buttonAdd, 'right', spacer, 25), (buttonRemove, 'left', spacer, 25), (buttonRemove, 'right', spacer, 50), (buttonModify, 'left', spacer, 50), (buttonModify, 'right', spacer, 75), (buttonToggleAbsRel, 'left', spacer, 75)]
                                + [(buttonSaveExit, 'right', spacer, 50), (buttonCancel, 'left', spacer, 50)]
                   )
    
def main():
    failing = False
    
    try: # Check if user has installed correctly
        import bw_common as bwcommon
    except:
        cmds.confirmDialog( title='Missing bw_common.py!', message="Please refer to the content creation manual for BigWorld melscript installation instructions", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
        failing = True
    
    if failing == False:
        pluginPath = bwcommon.bwGetVisualPluginPath()
        pathsXMLFile = os.path.join(pluginPath, "paths.xml")

        pathsManager = bwcommon.PathsXMLManager(pathsXMLFile)
        result = cmds.layoutDialog(ui=partial(gui,pathsManager), title="Modify Resource Paths")
        if result != "Cancel":
            pathsManager.write()
