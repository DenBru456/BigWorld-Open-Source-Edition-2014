macroScript Exit_Portal
	category:"BigWorld"
	toolTip:"Add Exit Portal"
	Icon:#("bigworld_icons", 2)
	
(
	-- BigWorld Add Portals
	-- 
	-- Version: 1.0
	-- Date: 2010
	-- Author: Adam Maxwell
	-- Website: http://www.bigworldtech.com
	-- Works on: MAX 2010
	--
	-- Description
	-- Search and prompt for BigWorld_MaterialLibrary.mat
	-- Assigns portal flags with single click
	-- Assigns a material based on portal flags
	-- Adjusts wire colour based on portal flags, for when material library is not loaded
	--
	-- ToDo:
	-- Check if portal is being assigned to sub object selection - is it a hull?
	-- if so give it only material name.
	-- Other:
	-- put import into bw folder
	--
	-- Known Bugs:
	-- None	
	
	include "BigWorld_Common.ms"
	
	hullObject = false
	subSelection = false
	global bw_hasSearchedMatLib
	bwMacroScriptsPath = (pathConfig.GetDir #usermacros)

	function MakePortal selected =
	(
		if stdPort == undefined do -- set all undefined to false
		(
			setUserProp selected "portal" "false"
			global stdPort = getUserProp selected "portal"
		)
		if heavPort == undefined do -- set all undefined to false
		(
			setUserProp selected "heaven" "false"
			global heavPort = getUserProp selected "heaven"
		)
		if exPort == undefined do -- set all undefined to false
		(
			setUserProp selected "exit" "false"
			global exPort = getUserProp selected "exit"
		)
			
		if findString selected.name "heaven_portal" != undefined do -- already has heaven_portal suffix, must test this before _portal
		(
			originalName = selected.name
			portalSuffixPos = findString selected.name "heaven_portal"
			newName = replace originalName portalSuffixPos  13 ""
			selected.name = newName
		)		
		
		if findString selected.name "_portal" != undefined do -- already has _portal suffix
		(
			originalName = selected.name
			portalSuffixPos = findString selected.name "_portal"
			newName = replace originalName portalSuffixPos  7 ""
			selected.name = newName
		)
		
		setUserProp selected "portal" "true"
		setUserProp selected "heaven" "false"
		setUserProp selected "exit" "true"
		
		-- new for collada, removing suffix _portal				
		selected.name = selected.name + "exit_portal"
		
		selected.material = currentMaterialLibrary["exit_portal"]
		selected.wirecolor = color 255 0 0
		
	)
	
	-- Loads BW material library
	if bw_hasSearchedMatLib == undefined then -- only ever load material library once
	(
		if loadMaterialLibrary "BigWorld_MaterialLibrary.mat" == false then 
		(
			messagebox "Please locate the BigWorld Material Library. \nTry bigworld/tools/maxscripts/resources/materiallibraries"		
			fileOpenMatLib()			
		)
		else
		(
			print "Found BigWorld Material Library"
		)
		bw_hasSearchedMatLib = true
	)
	
	
	-- Test if in sub object selection mode --
	
	if subobjectLevel == 4 do
	(
		subSelection = true
		if matchPattern $.name pattern:"*_hull" then
		(
			--print "Debug: Is _hull suffix"
			if classof $ == Editable_Mesh do
			(
				--print "Debug: Is Editable Mesh"
				if querybox "Portal materials can only be assigned to Hull's of Editable Poly.\nConvert to Editable Poly?" == true do
				(
					convertToPoly $
					subobjectLevel = 4
					-- NOW ASSIGN PORTAL
				)
			)
			
			if classof $ == Editable_Poly then
			(
				-- print "Debug: Is Edit Poly"
				id = ($.getmaterialindex true)
				faceMaterial = $.material[id].name -- Can crash if bigworld material library is missing the hull material 
				
				if faceMaterial == "exit_portal" then
				(
					print "material portal removed"
					$.material[id] = currentMaterialLibrary["hull_material"]
				)
				else
				(
					print "material portal added"
					$.material = currentMaterialLibrary["exit_portal"]
				)
			)
			else
			(
				print "Only objects of class Editable Poly can be assigned portal materials"
			)
		)	
		else
		(
			messagebox "When assigning portals to sub object selections, the object must be a custom hull"
		)
	)	
	
	
	if subobjectLevel == 1 or subobjectLevel == 2 or subobjectLevel == 3 or subobjectLevel == 5 do
	(
		subSelection = true
		messagebox "Only polygons of Editable Poly custom hulls can be assigned portal materials"
	)
	
	-- If not sub object selection
	if subobjectLevel == 0 or subSelection == false do
	(
		for i in 1 to selection.count do 
		(
			global stdPort = getUserProp selection[i] "portal"
			global heavPort = getUserProp selection[i] "heaven"
			global exPort = getUserProp selection[i] "exit"
			
			if stdPort == true and heavPort == false and exPort == true then -- is exit portal
			(
				setUserProp selection[i] "heaven" "false"
				setUserProp selection[i] "exit" "false"
				setUserProp selection[i] "portal" "false"
				
				-- new for collada, removing suffix exit_portal				
				originalName = selection[i].name
				portalSuffixPos = findString selection[i].name "exit_portal"
				newName = replace originalName portalSuffixPos 11 ""
				selection[i].name = newName
				
				selection[i].material = standard()
				selection[i].wirecolor = color 128 128 128
			)
			else
			(
				Case IsPlanar selection[i] of  
				(
					"Too many verts":
					(
						print selection[i].name + " has too many verts"
					)
					"Is planar":
					(
						MakePortal selection[i]
					)
					"Not geometry": messagebox "Only geometryClass objects can be assigned portal flags"
					"Not planar":
					(
						if querybox ("object " + selection[i].name + " is not planar. Portals must be planar. \nPlease read the content_creation.chm manual for extra information. \nFlag it anyway?") == true do
						(
							MakePortal selection[i]
						)
					)					
				)
			)
		)
	)
)