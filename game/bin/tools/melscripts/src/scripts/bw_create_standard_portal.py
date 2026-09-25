# Making a standard portal
# Only has Portal = True flag
import maya.cmds as cmds
import bw_common as bwcommon

def main():
	allSelectedObjects = cmds.ls( selection=True )
	
	bwcommon.bwCreateMaterial ( "BW_sportalSG", "standard_portal", 0, 0, 1, "sportal_bmp", "%BIGWORLD_RES_DIR%/helpers/maps/AID_portal.bmp" )
	
	cmds.select( clear=True )
	for obj in allSelectedObjects:
		cmds.select( obj, add=True )
	
	for obj in allSelectedObjects:
		if cmds.attributeQuery( 'Portal', node=obj, exists=True ):  #if Attribute Portal exists
			print ( "object %s contains Portal attribute"%obj )
			if cmds.getAttr( '%s.Portal'%obj ) == True:  #if Attribute is True
				cmds.deleteAttr( '%s.Portal'%obj ) #remove Attribute            
				newName = bwcommon.bwRename( obj, "none" ) # name appropriately  
				obj = cmds.rename( obj, newName )
				cmds.sets( obj, forceElement="initialShadingGroup" )
				print ( "object %s has had its Portal attribute removed"%obj )
				if cmds.attributeQuery( 'Label', node=obj, exists=True ):    #Had Portal, now removed, testing for Label to remove
					print ( "object %s has had A Label attribute removed"%obj )
					cmds.deleteAttr( '%s.Label'%obj )    #remove Attribute                        
			else:    #else Attribute exists but its false
				print ( "Attribute Portal exists on %s but its false. Setting it to True"%obj )
				cmds.setAttr( '%s.Portal'%obj, True )
				newName = bwcommon.bwRename( obj, "portal" ) # name appropriately  
				obj = cmds.rename( obj, newName )
				cmds.sets( obj, forceElement="BW_sportalSG" )
				if cmds.attributeQuery( 'Label', node=obj, exists=True ) == False: #if no label add one.
					print ( "object %s has No Label attribute, going to add one"%obj )
					cmds.addAttr( obj, longName='Label', dataType='string' )
		else:    #else has no Portal Attribute
			cmds.addAttr( obj, longName='Portal', at='bool' )
			cmds.setAttr( '%s.Portal'%obj, True )
			newName = bwcommon.bwRename( obj, "portal" ) # name appropriately  
			obj = cmds.rename( obj, newName )
			cmds.sets( obj, forceElement="BW_sportalSG" )
			cmds.addAttr( obj, longName='Label', dataType='string' )                   
		if cmds.attributeQuery( 'Exit', node=obj, exists=True ):  #if Attribute Exit exists
			print ( "object %s contains Exit attribute"%obj )
			cmds.deleteAttr( '%s.Exit'%obj )    #remove Attribute
		if cmds.attributeQuery( 'Heaven', node=obj, exists=True ):  #if Attribute Heaven exists
			print ( "object %s contains Heaven attribute"%obj )
			cmds.deleteAttr( '%s.Heaven'%obj )    #remove Attribute