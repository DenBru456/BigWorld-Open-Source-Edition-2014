# Making a custom bsp
import maya.cmds as cmds
import bw_common as bwcommon

def main():
	# Need to get selection here as creating a shader networks screws with selection
	allSelectedObjects = cmds.ls( selection=True )
	
	bwcommon.bwCreateMaterial ( "BW_bspSG", "custom_bsp", 1, 0.5, 0, "bsp_bmp", "%BIGWORLD_RES_DIR%/helpers/maps/AID_BSP.bmp" )
	
	cmds.select( clear=True )
	for obj in allSelectedObjects:
		cmds.select( obj, add=True )
	
	for obj in allSelectedObjects:
		print obj
		if (obj.rfind( "_bsp" ) == -1): #_bsp not found in name
			newName = bwcommon.bwRename( obj, "bsp" ) # name appropriately  
			obj = cmds.rename( obj, newName )
			cmds.sets( obj, forceElement="BW_bspSG" )
		else: #_bsp was found!
			newName = bwcommon.bwRename(obj, "none") # name appropriately  
			obj = cmds.rename( obj, newName )
			cmds.sets( obj, forceElement="initialShadingGroup" )