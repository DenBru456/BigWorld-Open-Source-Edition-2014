# Verify File Paths
from maya import cmds
import os
from functools import partial
import shutil

def cleanPath(path):    
    return os.path.normcase(path).replace('\\','/')

def pathInResPaths(path, respaths):
    path = path.lower()
    path = cleanPath(path)
    for respath in respaths:
        if path.find(respath, 0) == 0:
            return True
    return False

def updateTextScrollList(filesNeedingReview, fileTextScrollList):
    cmds.textScrollList(fileTextScrollList, edit=True, removeAll=True)
    cmds.textScrollList(fileTextScrollList, edit=True, append=filesNeedingReview.keys())

def getCopyDestinationDir(respaths):
    dirArray = cmds.fileDialog2(caption="Select Resource Path For Copy Destination", fileMode=3, dialogStyle=1)
    # Handle dialog cancel
    if dirArray is None or not dirArray[0]:
        return None
    destDir = dirArray[0]

    if not pathInResPaths(destDir, respaths):
        cmds.confirmDialog(title="Bad Destination Dir", message="The destination dir:\n  '%s'\ndoes not exist within the resource paths specified in paths.xml.\n\nPlease select an appropriate destination or adjust your paths.xml appropriately." % (destDir) )
        return None
    return destDir
    
def doCopy(files, respaths, fileTextScrollList, filesNeedingReview):
    destinationDir = getCopyDestinationDir(respaths)
    if not destinationDir or not os.path.exists(destinationDir) or not os.path.isdir(destinationDir):
        return
    for f in files:		
        fBasename = os.path.basename(f)
        destFile = os.path.join(destinationDir, fBasename)
        print "CP %s -> %s" %(f, destFile)
        shouldCopy = True
        if not os.path.isfile(f):
            shouldCopy = False
        if os.path.exists(destFile):
            result = cmds.confirmDialog( title='Overwrite Files?', message='Do you want to overwrite the file "%s"?' % destFile, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if result == "No":
                shouldCopy = False
        if shouldCopy:
            shutil.copy(f, destFile)
        for node in filesNeedingReview[f]:
            cmds.setAttr(node+".fileTextureName", destFile, type="string")
            print "ADJUSTING %s to %s" % (node+".fileTextureName", destFile)
        del filesNeedingReview[f]
    if len(filesNeedingReview.keys()) == 0:
        cmds.layoutDialog(dismiss='Abort')
    updateTextScrollList(filesNeedingReview, fileTextScrollList)

def copyAll(respaths, fileTextScrollList, filesNeedingReview, *args):
    allItems = cmds.textScrollList(fileTextScrollList, query=True, allItems=True)
    if not allItems:
        cmds.layoutDialog(dismiss="Abort")
        return
    doCopy(allItems, respaths, fileTextScrollList, filesNeedingReview)

def copySelection(respaths, fileTextScrollList, filesNeedingReview, *args):
    selection = cmds.textScrollList(fileTextScrollList, query=True, selectItem=True)
    if not selection:
        return
    doCopy(selection, respaths, fileTextScrollList, filesNeedingReview)

def gui(respaths, filesNeedingReview):
    form = cmds.setParent(q=True)

    filenameText = cmds.text(l='Filenames that need changing:')

    fileTextScrollList = cmds.textScrollList( numberOfRows=10, allowMultiSelection=True )
    updateTextScrollList(filesNeedingReview, fileTextScrollList)

    buttonCopyAll       = cmds.button(l='Copy All to ...', c=partial(copyAll, respaths, fileTextScrollList, filesNeedingReview) )
    buttonCopySelection = cmds.button(l='Copy Sel. to ...', c=partial(copySelection, respaths, fileTextScrollList, filesNeedingReview) )
    buttonCancel = cmds.button(l='Cancel', c='from maya import cmds; cmds.layoutDialog(dismiss="Abort")')

    spacer = 5
    edgeOffset = 5

    cmds.formLayout(form, edit=True,
                    attachForm=[(filenameText, 'top', edgeOffset)]
                                + [(n, 'left', edgeOffset) for n in [filenameText, buttonCopyAll, fileTextScrollList]]
                                + [(n, 'right', edgeOffset) for n in [filenameText, buttonCancel, fileTextScrollList]]
                                + [(n, 'bottom', edgeOffset) for n in [buttonCopyAll, buttonCopySelection, buttonCancel]],
                    attachNone=[(filenameText, 'bottom')],
                    attachControl=[(fileTextScrollList, 'top', spacer, filenameText)]
                                + [(fileTextScrollList, 'bottom', spacer, n) for n in [buttonCopyAll, buttonCopySelection, buttonCancel]],
                    attachPosition=[(buttonCopyAll, 'right', spacer, 33), (buttonCopySelection, 'left', spacer, 33), (buttonCopySelection, 'right', spacer, 66), (buttonCancel, 'left', spacer, 66)])

def getObjectsSurfaceShader(obj):
    surfaceShaderList = []
    shapes = cmds.listRelatives(obj, children=True, fullPath=True)
    if not shapes:
        return None
    shadingGroups = cmds.listConnections(shapes[0], type="shadingEngine")
    if not shadingGroups:
        return None
    for i in shadingGroups:
        surfaceShader = cmds.listConnections(i + ".surfaceShader")
        surfaceShaderList.append(surfaceShader)
    return surfaceShaderList

def findFirstFileTextureNodeFrom(node):
    if cmds.objectType(node) == "file":
        return node
    connectedNodes = cmds.listConnections(node, source=True, destination=False)
    if not connectedNodes:
        return None
    for n in connectedNodes:
        ret = findFirstFileTextureNodeFrom(n)
        if ret is not None:
            return ret
    return None

def getFileTextureNodesAttachedToObjects(objects):
    fileNodes = []
    for obj in objects:
        ssList = []
        ssList = getObjectsSurfaceShader(obj)
        if not ssList:
            continue
        for node in ssList:
            fileNode = findFirstFileTextureNodeFrom(node)
            if fileNode != None:
                fileNodes.append(fileNode)
    return fileNodes

# @param silentSuccess is set to True when this function is called from the
#        export process.
# @param selection is set to True when in Export Selection mode. In this event
#        we only consider fileTexture nodes connected to the current selection.
def main( silentSuccess=False, selection=False):
    failing = False
    
    try: # Check if user has installed correctly
        import bw_common as bwcommon
    except:
        cmds.confirmDialog( title='Missing bw_common.py!', message="Please refer to the content creation manual for BigWorld melscript installation instructions", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
        failing = True
    
    if failing == False:
        pluginPath = bwcommon.bwGetVisualPluginPath()
        pathsXMLFile = os.path.join(pluginPath, "paths.xml")

        resPathsManager = bwcommon.PathsXMLManager(pathsXMLFile)

        respaths = resPathsManager.getArrayOfAbsPaths()

        filesNeedingReview = {}
        fileNodes = []
        if selection:            
            fileNodes = getFileTextureNodesAttachedToObjects(cmds.ls(sl=True, long=True))
        else:
            # We only want to include checks for materials that are attached to
            # exportable items - anything that's a 'transform' is a good start.
            fileNodes = getFileTextureNodesAttachedToObjects(cmds.ls(type='transform', long=True))
        if not silentSuccess and len(fileNodes) == 0:
            cmds.confirmDialog(message="No fileTexture nodes exist.")
            return
        for f in fileNodes:
            texName = cmds.getAttr(f+'.fileTextureName')
            texName = os.path.expandvars(texName)
            texName = os.path.abspath(texName)
            if not pathInResPaths(texName, respaths):
                if texName not in filesNeedingReview:
                    filesNeedingReview[texName] = []
                filesNeedingReview[texName].append(f)
        if len(filesNeedingReview) > 0:
            result=cmds.layoutDialog(ui=partial(gui,respaths,filesNeedingReview), title="Review Texture File Locations")
        if not silentSuccess and len(filesNeedingReview) == 0:
            cmds.confirmDialog(message="All texture paths are in the res-path.")
