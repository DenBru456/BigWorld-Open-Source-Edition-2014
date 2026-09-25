# Making a custom hull
import maya.cmds as cmds
import bw_common as bwcommon

def main():
	allSelectedObjects = cmds.ls( selection=True )
	
	bwcommon.bwCreateMaterial( "BW_custom_hullSG", "custom_hull", 1, 0, 0.95, "hull_bmp", "%BIGWORLD_RES_DIR%/helpers/maps/AID_Hull.bmp" )
	
	#reinstantiate the selection, lost when material created
	cmds.select( clear=True )
	for obj in allSelectedObjects:
		cmds.select( obj, add=True )
	
	for obj in allSelectedObjects:
		print obj
		if (obj.rfind( "_hull" ) == -1): #_bsp not found in name
			newName = bwcommon.bwRename( obj, "hull" ) # name appropriately  
			obj = cmds.rename( obj, newName )
			cmds.sets( obj, forceElement="BW_custom_hullSG" )
		else: #_bsp was found!
			newName = bwcommon.bwRename( obj, "none") # name appropriately  
			obj = cmds.rename( obj, newName )
			cmds.sets( obj, forceElement="initialShadingGroup" )