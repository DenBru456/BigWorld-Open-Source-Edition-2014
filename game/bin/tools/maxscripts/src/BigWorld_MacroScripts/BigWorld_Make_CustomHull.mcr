macroScript Make_Hull
	category:"BigWorld"
	toolTip:"Convert to Custom Hull"
	Icon:#("bigworld_icons", 7)
	
(	
	-- BigWorld Make Custom Hull
	-- 
	-- Version: 1.0
	-- Date: 2010
	-- Author: Adam Maxwell
	-- Website: http://www.bigworldtech.com
	-- Works on: MAX 2010
	--
	-- Description
	-- Appends the suffix "_hull" to an object, labelling it a custom hull on BW export
	-- Applies a recognisable material to the hull object
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
		
		if matchPattern selection[i].name pattern:"*_hull" then
		(
			print "Removing hull flag"		
			originalName = selection[i].name
			hullSuffixPos = findString selection[i].name "_hull"
			newName = replace originalName hullSuffixPos 5 ""
			selection[i].name = newName
						
			selection[i].material = standard()
			selection[i].wirecolor = color 128 128 128			
		)
		else
		(	
			if superClassOf selection[i] == GeometryClass then
			(
				print "Adding hull flag"
				convertToPoly(selection[i]) -- This is required to assign portal materials in add portal scripts
				tempName = selection[i].name
				selection[i].name = tempName + "_hull"			
			
				selection[i].material = currentMaterialLibrary["Hull_material"]
				selection[i].wirecolor = color 255 0 128
			)
			else
			(
				messagebox "object " + selection[i].name + " is not a geometry class object \nOnly geometry class objects can be labelled as custom hulls"
			)				
		)
	)
)
