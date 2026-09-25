#BigWorld Object Divider

import math
import maya.cmds as cmds
import bw_common

MODEL_LAYER_SUFFIX = "_bw_model_layer"

#--------------------------------------------------
# Main proc
#--------------------------------------------------
def sliderUI():
	global sliderWin      
	doesExist = cmds.window( 'sliderWin', exists=True )
	if doesExist == False:
		sliderWin = cmds.window( title="BigWorld Object Divider", topLeftCorner=[500, 500], w=10, h=200, retain=True )        
		addUIWidgets()
	cmds.showWindow( sliderWin )     
	 
#--------------------------------------------------
# Echoes the value of a slider in the script window
#--------------------------------------------------
def getSliderValue():
	xVal = bw_common.convertToCurrentUnits( cmds.floatSliderGrp( sliderX, query=True, value=True ) )
	yVal = bw_common.convertToCurrentUnits( cmds.floatSliderGrp( sliderY, query=True, value=True ) )
	zVal = bw_common.convertToCurrentUnits( cmds.floatSliderGrp( sliderZ, query=True, value=True ) )
	overlapVal = bw_common.convertToCurrentUnits( cmds.floatSliderGrp( sliderOverlap, query=True, value=True ) )
	hideOriginal = cmds.checkBox( hideCB, query=True, value=True )
	objectDivide( xVal, yVal, zVal, overlapVal, hideOriginal )

#--------------------------------------------------
# Adds a slider and a button to the window
#--------------------------------------------------
def addUIWidgets():
	global sliderX
	global sliderY
	global sliderZ
	global sliderOverlap
	global hideCB
	cmds.columnLayout()
	cmds.iconTextButton( style='textOnly', label='This macro will divide an object, so that it is less than the maximum export size' )
	sliderX = cmds.floatSliderGrp( columnWidth=[1,100], label='Maximum X size (m)', field=True, value=70, min=50, max=1200 )
	sliderY = cmds.floatSliderGrp( columnWidth=[1,100], label='Maximum Y size (m)', field=True, value=70, min=50, max=2400 )
	sliderZ = cmds.floatSliderGrp( columnWidth=[1,100], label='Maximum Z size (m)', field=True, value=70, min=50, max=1200 )
	cmds.iconTextButton( style='textOnly', label='Object size restricted to chunk size.' )
	cmds.iconTextButton( style='textOnly', label='Recommended maximum setting is 70m' )
	sliderOverlap = cmds.floatSliderGrp( columnWidth=[1,100], label="Overlap size (m)", field=True, value=0.1, min=0.01, max=1 )
	hideCB = cmds.checkBox( label='Hide original objects' )
	cmds.button( label="Cut Objects", command="bw_object_divider.getSliderValue()" )
	cmds.button( label='Close', command=('cmds.deleteUI(\"' + sliderWin + '\", window=True)') )

#--------------------------------------------------
# Divide Objects
#--------------------------------------------------
def objectDivide( divisionX, divisionY, divisionZ, overlapSize, hideOriginal):
	allSelectedObjects = cmds.ls( selection=True )
	if len( allSelectedObjects ) != 0:
		for obj in allSelectedObjects:
			originalObj = obj
			cmds.select( originalObj )
			boundingBox = cmds.polyEvaluate( boundingBox=True, ae=True )
			lengthX = abs( boundingBox[0][0] - boundingBox[0][1] )
			lengthY = abs( boundingBox[1][0] - boundingBox[1][1] )
			lengthZ = abs( boundingBox[2][0] - boundingBox[2][1] )
			cutsX = int( math.ceil( lengthX/divisionX ) )
			cutsY = int( math.ceil( lengthY/divisionX ) )
			cutsZ = int( math.ceil( lengthZ/divisionX ) )
			for xCut in range( cutsX ):
				cmds.select( clear=True )
				cmds.select( originalObj )
				duplicateObj = cmds.duplicate( originalObj )
				xTopCut = boundingBox[0][1] - (divisionX*xCut) + overlapSize
				xBotCut = boundingBox[0][1] - (divisionX*(xCut+1)) - overlapSize
				cmds.polyCut( pc=[xTopCut,0,0], ro=[0,270,0], ef=True,eo=[0,0,0], df=True ) #Cut above 
				cmds.polyCut( pc=[xBotCut,0,0], ro=[0,90,0], ef=True,eo=[0,0,0], df=True ) #Cut below
				slicedXObj = cmds.ls( selection=True )                
				xCutBBox = cmds.polyEvaluate( boundingBox=True, ae=True )                
				if xCutBBox[0][0] > xTopCut or xCutBBox[0][1] < xBotCut: # Is cut object ouside cut planes (polyCut can leave residual polygons)
					cmds.delete()
				else:
					for yCut in range( cutsY ):
						cmds.select( clear=True )
						cmds.select( slicedXObj )
						duplicateSlicedXObj = cmds.duplicate( slicedXObj )
						yTopCut = boundingBox[1][1] - (divisionY*yCut) + overlapSize
						yBotCut = boundingBox[1][1] - (divisionY*(yCut+1)) - overlapSize
						cmds.polyCut( pc=[0,yTopCut,0], ro=[90,0,0], ef=True,eo=[0,0,0], df=True )
						cmds.polyCut( pc=[0,yBotCut,0], ro=[270,0,0], ef=True,eo=[0,0,0], df=True )
						slicedYObj = cmds.ls( selection=True )                        
						yCutBBox = cmds.polyEvaluate( boundingBox=True, ae=True )
						if yCut == len( range( cutsY ) )-1: #Delete the duplicated object when its finished using it.
							cmds.delete( slicedXObj )
						if yCutBBox[1][0] > yTopCut or yCutBBox[1][1] < yBotCut: # Is cut object ouside cut planes (polyCut can leave residual polygons)                            
							cmds.delete()
						else:
							for zCut in range( cutsZ ):
								cmds.select( clear=True )
								cmds.select( slicedYObj )
								duplicateSlicedZObj = cmds.duplicate( slicedYObj )
								zTopCut = boundingBox[2][1] - (divisionZ*zCut) + overlapSize
								zBotCut = boundingBox[2][1] - (divisionZ*(zCut+1)) - overlapSize
								cmds.polyCut( pc=[0,0,zTopCut], ro=[0,180,0], ef=True,eo=[0,0,0], df=True ) #This cuts away everything above
								cmds.polyCut( pc=[0,0,zBotCut], ro=[0,0,0], ef=True,eo=[0,0,0], df=True ) #This cuts away everything below
								zCutBBox = cmds.polyEvaluate( boundingBox=True, ae=True )
								slicedZObj = cmds.ls( selection=True )
								layerName = str( slicedZObj[0] )
															  
								if zCutBBox[2][0] > zTopCut or zCutBBox[2][1] < zBotCut: # Is cut object ouside cut planes (polyCut can leave residual polygons)
									cmds.delete()
								else:
									# Put each section on a new bwPrefabLayer providing its bounding box is not outside the cut planes
									# This prevents layers being created that contain nothing.
									cmds.createDisplayLayer( name=(layerName + MODEL_LAYER_SUFFIX), nr=True )  
								if zCut == len( range( cutsZ ) )-1: #This deletes the duplicated object when its finished using it.
									cmds.delete( slicedYObj )
			if hideOriginal == True:
					cmds.hide( originalObj )
	else:
		cmds.confirmDialog( title='Nothing Selected', message='Select the objects you want to divide.', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )

def main():
	sliderUI()