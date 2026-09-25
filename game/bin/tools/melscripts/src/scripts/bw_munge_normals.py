#Munge normals

import maya.cmds as cmds
import bw_common as bwcommon

def main():
	failed = False
	allSelectedObjects = cmds.ls( selection=True, objectsOnly=True )
	
	#find out if only 1 object is selected
	if len( allSelectedObjects ) == 2:
		objToModify = allSelectedObjects[0]
		splayFromObj = allSelectedObjects[1]
		try:
			splayFromPoint = cmds.xform ( splayFromObj, worldSpace=True, query=True, translation=True )
		except:
			cmds.confirmDialog( title='Incorrect selection', message='Select the verts of the object you wish to modify.\nAdd to this selection the target object from which the normals are to be projected.', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
			failed = True
		objVertList = cmds.ls( sl=True, fl=True )
		# Removing splayFromobj from list
		objVertList.pop()
		# test for vertex selection
		if cmds.filterExpand( objVertList, sm=31 ) != None:
			for vert in objVertList:
				vertPosition = cmds.pointPosition( vert, world=True )
				splayVector = bwcommon.vectorSubtract( vertPosition,splayFromPoint )
				cmds.polyNormalPerVertex( vert, xyz=[splayVector[0], splayVector[1], splayVector[2]] )
		else:
			cmds.confirmDialog( title='No vertices selected', message='Incorrect selection\nSelect the verts of the object you wish to modify', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )    
			failed = True
	else:    
		cmds.confirmDialog( title='Incorrect selection', message='Select the verts of the object you wish to modify.\nAdd to this selection the target object from which the normals are to be projected.', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
		failed = True
	
	if failed == False:
		cmds.confirmDialog( title='Success', message='Vertex normals have been adjusted.\nSee results by selecting "Normals" - "Vertex Normal Edit Tool" ', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
