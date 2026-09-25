# Making an Heaven portal
# Has both Portal and Heaven Tag

import maya.cmds as cmds
import bw_common as bwcommon

def main():
	allSelectedObjects = cmds.ls( selection=True )
	
	bwcommon.bwCreateMaterial ( "BW_hportalSG", "heaven_portal", 0, 1.0, 0, "hportal_bmp", "%BIGWORLD_RES_DIR%/helpers/maps/AID_hportal.bmp" )
	
	cmds.select( clear=True )
	for obj in allSelectedObjects:
		cmds.select( obj, add=True )
	
	for obj in allSelectedObjects:
		if cmds.attributeQuery( 'Heaven', node=obj, exists=True ):  #if Attribute Heaven exists
			print ("object %s contains Heaven attribute"%obj )
			if cmds.getAttr( '%s.Heaven'%obj ) == True:  #if Attribute is True
				cmds.deleteAttr( '%s.Heaven'%obj )    #remove Attribute
				newName = bwcommon.bwRename( obj, "none" ) # name appropriately  
				obj = cmds.rename( obj, newName )
				cmds.sets( obj, forceElement="initialShadingGroup" )
				print ( "object %s has had its Heaven attribute removed"%obj )
				if cmds.attributeQuery( 'Portal', node=obj, exists=True ):    #Had Heaven, now removed, testing for Portal to remove
					cmds.deleteAttr( '%s.Portal'%obj )    #remove Attribute                        
					print ( "object %s has had a Portal attribute removed"%obj )
				if cmds.attributeQuery( 'Label', node=obj, exists=True ):    #Had Heaven, now removed, testing for Label to remove
					cmds.deleteAttr( '%s.Label'%obj )    #remove Attribute                        
					print ( "object %s has had A Label attribute removed"%obj )
			else:    #else Attribute exists but its false
				print ( "Attribute Portal exists on %s but its false. Setting it to True"%obj )
				cmds.setAttr( '%s.Heaven'%obj, True )
				newName = bwcommon.bwRename( obj, "heaven" ) # name appropriately
				obj = cmds.rename( obj, newName )
				cmds.sets( obj, forceElement="BW_hportalSG" );
				if cmds.attributeQuery( 'Portal', node=obj, exists=True ) == False: #if no Portal add one and set it true.
					print ( "object %s has No Portal attribute, going to add one"%obj )
					cmds.addAttr( obj, longName='Portal', at='bool' )
					cmds.setAttr( '%s.Portal'%obj, True )                    
				else:
					if cmds.getAttr( '%s.Portal'%obj ) == False:
						cmds.setAttr( '%s.Portal'%obj, True )                
				if cmds.attributeQuery( 'Label', node=obj, exists=True ) == False: #if no label add one.
					print ( "object %s has No Label attribute, going to add one"%obj )
					cmds.addAttr( obj, longName='Label', dataType='string' )                
		else:  #else has no Heaven Attribute so Add one and a Portal and a Label Attribute
			cmds.addAttr( obj, longName='Heaven', at='bool' )
			cmds.setAttr( '%s.Heaven'%obj, True )
			newName = bwcommon.bwRename( obj, "heaven" ) # name appropriately  
			obj = cmds.rename( obj, newName )
			cmds.sets( obj, forceElement="BW_hportalSG" );
			if cmds.attributeQuery( 'Portal', node=obj, exists=True ): # Test for portal attribute
				if cmds.getAttr( '%s.Heaven'%obj ) == False:  #Has portal but its false                
					cmds.setAttr( '%s.Portal'%obj, True )
			else: # Doesnt have a portal attribute so add one.
				cmds.addAttr( obj, longName='Portal', at='bool' )
				cmds.setAttr( '%s.Portal'%obj, True )            
			if cmds.attributeQuery( 'Label', node=obj, exists=True ) == False: # If it doenst have a Label
				cmds.addAttr( obj, longName='Label', dataType='string' )           
		if cmds.attributeQuery( 'Exit', node=obj, exists=True ):  #if Attribute Heaven exists
			print ( "object %s contains Exit attribute"%obj )
			cmds.deleteAttr( '%s.Exit'%obj )    #remove Attribute