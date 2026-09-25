#bigworld_maya_common.py contains all commonly used functions for shelf buttons.

import maya.cmds as cmds
import copy
import os
import xml.etree.ElementTree as ET

def convertCoordinateToBW( mayaCoordinate ):
    mayaCoordinate = copy.deepcopy( mayaCoordinate )
    zMin = mayaCoordinate[2][0]
    zMax = mayaCoordinate[2][1]
    mayaCoordinate[2][0] = -zMin
    mayaCoordinate[2][1] = -zMax
    return mayaCoordinate

def convertToMeters( inputUnit ):
    unitType = cmds.currentUnit( query=True, linear=True )
    if unitType == "mm":
        convertedUnit = inputUnit/1000.0
    elif unitType == "cm":
        convertedUnit = inputUnit/100.0
    elif unitType == "m":
        convertedUnit = inputUnit/1.0
    elif unitType == "km":
        convertedUnit = inputUnit/0.001
    elif unitType == "in":
        convertedUnit = inputUnit/39.3700787
    elif unitType == "ft":
        convertedUnit = inputUnit/3.280839895
    elif unitType == "yd":
        convertedUnit = inputUnit/1.0936133
    elif unitType == "mi":
        convertedUnit = inputUnit/0.000621371192
    else:
        print "unknown unit type, division may be incorrect"
        convertedUnit = 1.0 * inputUnit
    return convertedUnit

def convertToCurrentUnits( inputUnit ):
    unitType = cmds.currentUnit( query=True, linear=True )
    if unitType == "mm":
        convertedUnit = 1000.0 * inputUnit
    elif unitType == "cm":
        convertedUnit = 100.0 * inputUnit
    elif unitType == "m":
        convertedUnit = 1.0 * inputUnit
    elif unitType == "km":
        convertedUnit = 0.001 * inputUnit
    elif unitType == "in":
        convertedUnit = 39.3700787 * inputUnit
    elif unitType == "ft":
        convertedUnit = 3.280839895 * inputUnit
    elif unitType == "yd":
        convertedUnit = 1.0936133 * inputUnit
    elif unitType == "mi":
        convertedUnit = 0.000621371192 * inputUnit
    else:
        print "unknown unit type, division may be incorrect"
        convertedUnit = 1.0 * inputUnit
    return convertedUnit

def vectorSubtract( vectorA, vectorB ):
    x = vectorA[0] - vectorB[0]
    y = vectorA[1] - vectorB[1]
    z = vectorA[2] - vectorB[2]
    vectorC =[x,y,z]
    return vectorC

def bwCreateMaterial( sgName, materialName, rCol, gCol, bCol, bitmapName, texturePath ):
    if not (cmds.objExists( sgName )):   
        hullMaterial = cmds.shadingNode( 'lambert', asShader=True, name=materialName ) # Make a shader
        cmds.setAttr( (materialName+".color"), rCol, gCol, bCol, type='double3' ) # Set colour
        shaderGroup = cmds.sets( renderable=True, noSurfaceShader=True, empty=True, name=sgName )# Create shader group 
        cmds.connectAttr(( hullMaterial + ".outColor" ), ( shaderGroup + ".surfaceShader" ), force=True )# connecting the shader to a shadergroup    
        fileNode = cmds.shadingNode ( 'file', asTexture=True, name=bitmapName )# connecting a file .bmp to the material
        cmds.connectAttr( (fileNode + ".outColor"), (hullMaterial + ".color" ), force=True )
        filepath = texturePath
        cmds.setAttr ( (fileNode + ".fileTextureName"), filepath, type="string" )
        cmds.setAttr ( (hullMaterial + '.transparency'), 0.5, 0.5, 0.5, type='double3' )

def bwRename( objName, type ):
    objName = objName.replace( "exit_portal", "" )
    objName = objName.replace( "heaven_portal", "" )
    objName = objName.replace( "_portal", "" )
    objName = objName.replace( "_bsp", "" )
    objName = objName.replace( "_hull", "" )
    if type == "portal":
        objName = objName + "_portal"
    elif type == "exit":
        objName = objName + "exit_portal"    
    elif type == "heaven":
        objName = objName + "heaven_portal"
    elif type == "bsp":
        objName = objName + "_bsp"
    elif type == "hull":
        objName = objName + "_hull"
    return objName


def bwGetVisualPluginPath():
    if not cmds.pluginInfo('visual', query=True, loaded=True):
        try:
            cmds.loadPlugin('visual')
        except:
            cmds.confirmDialog( title='Missing visual plugin!', message="No 'visual.mll' plugin found in the MAYA_PLUG_IN_PATH. Please ensure this variable is set correctly before starting Maya.", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
            return ""
    pluginPath = cmds.pluginInfo('visual', query=True, path=True)
    return os.path.dirname(os.path.normpath(pluginPath))

class PathsXMLManager(object):
    def __init__(self, pathsXMLFile):
        self.xmlfile = pathsXMLFile
        self.xmldirname = os.path.dirname(self.xmlfile)
        self.tree = ET.parse(pathsXMLFile)
        self.root = self.tree.getroot()
        self.paths = self.root.find('Paths')
        self.dirty = False

    def getArrayOfPaths(self):
        return [n.text for n in self.paths.findall('Path')]

    def makePathAbs(self, path):
        if os.path.isabs(path):
            # Make sure that the path contains a disk drive. Default to same
            # drive as the plugin if path starts with /.
            if path[0] in ['\\', '/']:
                path = self.xmldirname[0:2] + path
        else:
            path = os.path.abspath(os.path.join(self.xmldirname, path))
        return path.replace('\\','/')

    def makePathRel(self, path):
        return os.path.relpath(path, self.xmldirname).replace('\\','/')

    def normAbsPath(self, path):
        path = self.makePathAbs(path)
        return os.path.normcase(path).replace('\\','/')

    def getArrayOfAbsPaths(self):
        return map(lambda x: self.normAbsPath(x), self.getArrayOfPaths())

    def isPathUnique(self, path):
        return (self.normAbsPath(path) not in self.getArrayOfAbsPaths())

    def addPath(self, newPath):
        if self.isPathUnique(newPath):
            subelm = ET.SubElement(self.paths, 'Path')
            subelm.text = self.normAbsPath(newPath)
            self.dirty = True

    def removePath(self, path):
        normPath = self.normAbsPath(path)
        for p in self.paths.findall('Path'):
            normP = self.normAbsPath(p.text)
            if normP == normPath:
                self.paths.remove(p)
                self.dirty = True

    def modifyPath(self, oldPath, newPath):
        normOldPath = self.normAbsPath(oldPath)
        for p in self.paths.findall('Path'):
            normP = self.normAbsPath(p.text)
            if normP == normOldPath:
                p.text = newPath
                self.dirty = True

    def toggleAbsRelPath(self, path):
        normPath = self.normAbsPath(path)
        for p in self.paths.findall('Path'):
            normP = self.normAbsPath(p.text)
            if normP == normPath:
                if os.path.isabs(path):
                    if normP[0].lower() == self.xmldirname[0].lower():
                        p.text = self.makePathRel(normPath)
                else:
                    p.text = self.makePathAbs(normPath)
                self.dirty = True

    def dump(self):
        ET.dump(self.root)

    def write(self):
        if self.dirty:
            if os.access(self.xmlfile,os.W_OK) :
                self.tree.write(self.xmlfile)
                self.dirty = False
            else:
                cmds.confirmDialog( title='File is Read Only!', message="Could not write to file paths.xml.", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
                


