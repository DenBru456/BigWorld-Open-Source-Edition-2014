# Attach HitBoxes
# This script will add and hitboxes to all selected nodes and attempt to align them with the parent to child vector.

import math
import maya.OpenMaya as om # Required for vector math
import maya.cmds as cmds
import bw_common as bwcommon

BOX_SUFFIX = "_bwhitbox"
MAGIC_LIMB_WIDTH = 2.5 # The inverse of this number determines the width of each limb compared to its length

#--------------------------------------------------
# Main proc
#--------------------------------------------------
def sliderUI():
	global sliderWin
	doesExist = cmds.window( 'sliderWin', exists=True )
	if doesExist == False:
		sliderWin = cmds.window( title="Leaf Node Hitbox Size", width = 100, height = 200 )
		addUIWidgets()
	cmds.showWindow( sliderWin )
	 
#--------------------------------------------------
# Echoes the value of a slider in the script window
#--------------------------------------------------
def getSliderValue():
	leafNodeSize = cmds.floatSliderGrp( endNodeSize, query=True, value=True )
	addHitboxes( leafNodeSize )
	cmds.deleteUI( sliderWin, window=True )

#--------------------------------------------------
# Adds a slider and a button to the window
#--------------------------------------------------
def addUIWidgets():
	global endNodeSize
	cmds.columnLayout()
	cmds.iconTextButton( style='textOnly', label='Choose the size of your leaf node hitBoxes(m)' )
	endNodeSize = cmds.floatSliderGrp( columnWidth=[1,90], label='Leaf node size (m)', field=True, value=0.1, min=0.001, max=1 )
	cmds.button( label="OK", command="bw_add_hitbox.getSliderValue()" )
	cmds.button( label='Close', command=('cmds.deleteUI(\"' + sliderWin + '\", window=True)') )
	
def calcdist( v1, v2 ):
	v = om.MVector( 0,0,0 )
	v.x = v1.x - v2.x
	v.y = v1.y - v2.y
	v.z = v1.z - v2.z
	return math.sqrt( v.x*v.x + v.y*v.y + v.z*v.z )

def addHitboxes( leafNodeSize ):
	allSelectedObjects = cmds.ls( long=True, selection=True )
	bwcommon.bwCreateMaterial ( "BW_hitboxSG", "bw_hitbox", 1, 0, 0, "bw_hitbox_bmp", "%BIGWORLD_RES_DIR%/helpers/maps/AID_BSP.bmp" )
	cubeSize = bwcommon.convertToCurrentUnits( leafNodeSize )
	if len( allSelectedObjects ) != 0:
		for node in allSelectedObjects:
			allChildren = cmds.listRelatives( node, type="transform" )
			if allChildren != None: # Find the first child node     
				childPos = cmds.xform( allChildren[0], worldSpace=True, query=True, translation=True )
				hasChild = True                        
			else:
				hasChild = False
			
			newHitbox = cmds.polyCube( ch=True, o=True, w=cubeSize, h=cubeSize, d=cubeSize, cuv=1 )
			cmds.sets( newHitbox, forceElement="BW_hitboxSG" ) # Assign hitbox material
			cmds.rename( newHitbox[0], (node + BOX_SUFFIX) )
			renameNewHitbox = cmds.ls(long=True, selection=True )
			cmds.delete( cmds.parentConstraint( node, renameNewHitbox ) ) # Parent and align the new hitbox to the selected object
			cmds.parent( renameNewHitbox, node )
			 
			parentPos = cmds.xform( node, worldSpace=True, query=True, translation=True )
			
			if hasChild == True:
				vecChild = om.MVector( childPos[0],childPos[1],childPos[2] )
				vecParent = om.MVector( parentPos[0],parentPos[1],parentPos[2] )
				vecToChild = vecChild - vecParent # Vector to the child from the parent
				vecToChild.normalize()
				nodeMatrix = cmds.xform( node, query=True, matrix=True, worldSpace=True )                
				nodeXVec = om.MVector( nodeMatrix[0],nodeMatrix[1],nodeMatrix[2] )
				nodeYVec = om.MVector( nodeMatrix[4],nodeMatrix[5],nodeMatrix[6] )
				nodeZVec = om.MVector( nodeMatrix[8],nodeMatrix[9],nodeMatrix[10] )
				dotProductX = vecToChild * nodeXVec # See if node X axis is aligned to vecToChild
				dotProductY = vecToChild * nodeYVec # See if node Y axis is aligned to vecToChild
				dotProductZ = vecToChild * nodeZVec # See if node Z axis is aligned to vecToChild                
				distToChild = calcdist ( vecChild, vecParent )
				
				cmds.setAttr( (newHitbox[1]+'.height'), distToChild/MAGIC_LIMB_WIDTH, clamp=True )
				cmds.setAttr( (newHitbox[1]+'.width'), distToChild/MAGIC_LIMB_WIDTH, clamp=True )
				cmds.setAttr( (newHitbox[1]+'.depth'), distToChild/MAGIC_LIMB_WIDTH, clamp=True )                
				
				# reference to the renameNewHitbox[0] included the unicode partition [u'|pCube1_bwhitbox'] "|", need to strip it off
				test = renameNewHitbox[0].startswith( "|" )
				if test == True:
					renameNewHitboxClean = str(renameNewHitbox[0])
					renameNewHitboxClean = renameNewHitboxClean[1:]
				else:
					renameNewHitboxClean = str(renameNewHitbox[0])
					
				# Aligned to Y
				if dotProductY > 0.95: # Parent Y axis is pointing towards Child node
					cmds.setAttr( (newHitbox[1]+'.height'), distToChild, clamp=True ) #Make the box as high as the distance to the child node
					#Move the boxes pivot to the edge of the box
					cmds.move( 0,-(distToChild/2),0, renameNewHitboxClean+'.scalePivot', renameNewHitboxClean+'.rotatePivot', objectSpace=True )
				elif dotProductY < -0.95: #The parent node Y axis is pointing away from the child
					cmds.setAttr( (newHitbox[1]+'.height'), distToChild, clamp=True )
					cmds.move( 0,(distToChild/2),0, renameNewHitboxClean+'.scalePivot', renameNewHitboxClean+'.rotatePivot', objectSpace=True ) #opposite side of box     
				# Aligned to X    
				elif dotProductX > 0.95: # Parent X axis is pointing towards Child node
					cmds.setAttr( (newHitbox[1]+'.width'), distToChild, clamp=True ) #Make the box as wide as the distance to the child node
					cmds.move( -(distToChild/2),0,0, renameNewHitboxClean+'.scalePivot', renameNewHitboxClean+'.rotatePivot', objectSpace=True )
				elif dotProductX < -0.95: #The parent node X axis is pointing away from the child
					cmds.setAttr( (newHitbox[1]+'.width'), distToChild, clamp=True )
					cmds.move( (distToChild/2),0,0, renameNewHitboxClean+'.scalePivot', renameNewHitboxClean+'.rotatePivot', objectSpace=True ) #opposite side of box     
				# Aligned to Z
				elif dotProductZ > 0.95: # Parent Z axis is pointing towards Child node
					cmds.setAttr( (newHitbox[1]+'.depth'), distToChild, clamp=True ) #Make the box as deep as the distance to the child node
					#Move the boxes pivot to the edge of the box
					cmds.move( 0,0,-(distToChild/2), renameNewHitboxClean+'.scalePivot', renameNewHitboxClean+'.rotatePivot', objectSpace=True )
				elif dotProductZ < -0.95: #The parent node Z axis is pointing away from the child
					cmds.setAttr( (newHitbox[1]+'.depth'), distToChild, clamp=True )
					cmds.move( 0,0,(distToChild/2), renameNewHitboxClean+'.scalePivot', renameNewHitboxClean+'.rotatePivot', objectSpace=True ) #opposite side of box     
				#Nothing is aligned
				else: # None of the hitbox axis are aligned to the vector to child, the box is just added at distToChild size
					cmds.setAttr( (newHitbox[1]+'.height'), distToChild, clamp=True )
					cmds.setAttr( (newHitbox[1]+'.width'), distToChild, clamp=True )
					cmds.setAttr( (newHitbox[1]+'.depth'), distToChild, clamp=True )  
				
				cmds.delete( cmds.parentConstraint(node, renameNewHitboxClean) ) #Align the box with parent node
			
			addedHitboxes = True
	else:
		cmds.confirmDialog( title='Nothing Selected', message='No nodes were selected to add BigWorld HitBox\'s to. \nPlease select the nodes you would like to add hitBoxes and try again.', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
		addedHitboxes = False
		
	if addedHitboxes == True:
		cmds.confirmDialog( title='HitBoxes added', message="Adjust HitBox parameters height/width/length as desired. \nHitBox's must remain a child of the rig's node or they will be ignored on export. \nDo not move or rotate the hitbox's pivot.\nThe HitBox suffix \"_bwhitbox\" should not be modified. \nUse the \"Export HitBox to XML\" shelf button to generate your skeleton collider.", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
		cmds.select( deselect=True )
		allSceneNodes = cmds.ls( long=True )
		for node in allSceneNodes: #Select all the Hitboxes
			if node.endswith( "_bwhitbox" ):
				cmds.select( node, add=True )
	
	cmds.createDisplayLayer( name="BigWorld_Hitboxes", nr=True )
	
def main():
	sliderUI()
