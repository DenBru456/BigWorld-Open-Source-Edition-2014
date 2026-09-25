macroScript Make_BSP
	category:"BigWorld"
	toolTip:"Convert to BSP"
	Icon:#("bigworld_icons", 6)
	
(	
	-- BigWorld Make BSP
	-- 
	-- Version: 1.0
	-- Date: 2010
	-- Author: Adam Maxwell
	-- Website: http://www.bigworldtech.com
	-- Works on: MAX 2010
	--
	-- Description
	-- Appends the suffix "_bsp" to an object, labelling it a BSP on BW export
	-- Applies a recognisable material to the BSP object
	--	
	-- Known Bugs:
	-- None	
		
	global bw_hasSearchedMatLib
	bwMacroScriptsPath = (pathConfig.GetDir #usermacros)
		
	-- Loads BW material library
	if bw_hasSearchedMatLib == undefined then -- only ever load material library once
	(
		if loadMaterialLibrary "BigWorld_MaterialLibrary.mat" == false then 
		(
			messagebox "Please locate the BigWorld Material Library\nTry bigworld/tools/maxscripts/resources/materiallibraries"				
			fileOpenMatLib()			
		)
		else
		(
			print "Found BigWorld Material Library"
		)
		bw_hasSearchedMatLib = true
	)
	
	for i in 1 to selection.count do 
	(
		
		if matchPattern selection[i].name pattern:"*_bsp" then
		(
			print "Removing BSP flag"		
			originalName = selection[i].name
			bspSuffixPos = findString selection[i].name "_bsp"
			newName = replace originalName bspSuffixPos 4 ""
			selection[i].name = newName
						
			selection[i].material = standard()
			selection[i].wirecolor = color 128 128 128			
		)
		else
		(	
			if superClassOf selection[i] == GeometryClass then
			(
				print "Adding BSP flag"
				tempName = selection[i].name
				selection[i].name = tempName + "_bsp"			
			
				selection[i].material = currentMaterialLibrary["bsp_material"]
				selection[i].wirecolor = color 0 0 255
			)
			else
			(
				messagebox "object " + selection[i].name + " is not a geometry class object \nOnly geometry class objects can be labelled as a bsp"
			)
		)
	)
)
