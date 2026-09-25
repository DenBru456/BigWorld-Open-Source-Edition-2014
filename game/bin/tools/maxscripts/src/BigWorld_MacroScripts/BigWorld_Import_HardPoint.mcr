macroScript Import_HardPoint
	category:"BigWorld"
	toolTip:"Import Hard Point"
	Icon:#("bigworld_icons", 4)
	
(	
	-- BigWorld Import Hard Point
	-- Author: Adam Maxwell
	-- Website: http://www.bigworld.com
	-- Tested on: MAX 2010-13 
	--
	-- Description
	-- Imports a hard point model from /bigworld/tools/maxscripts/resources/hard_point/hard_point.fbx,
	-- if the file is not found it will prompt the user for file location
	-- If no or multiple objects are selected when the script is executed the HP will be placed in the scene root
	-- If a single object is selected the HP will be parented to that object and aligned to its position/rotation
	-- The imported HP is scaled to match the scenes system unit size. The HP model will always be ~ 20cm squared
	-- The HP model is coloured to represent the BW axis
	-- The script will ask for a name and append the prefix "HP_". Does not allow the name "", "HP_", HP_00"
	-- 
	-- Known Bugs:
	-- If an existing hard point in the scene is named "HP_00" nothing will be imported and the existing "HP_00" will be used. 
	--
	-- ToDo:
	-- Renamer should accept enter to close renamer
		
	include "BigWorld_Common.ms"
	
	attachToMe = "" -- The parent object to attach the HP too
	
	---------------------------
	-- FBX Import parameters --
	---------------------------	
	sysScaleAmount = 1 / units.SystemScale
	FbxImporterSetParam "ScaleFactor" sysScaleAmount -- Scale the incomming HP model to match scene units
	FbxImporterSetParam "mode" #merge
	FbxImporterSetParam "ScaleConversion" true -- This automatically scales between unit types, e.g. #feet -> #meters.
	
	----------------------------
	-- Renaming the HardPoint --
	----------------------------		
	try(destroyDialog Name_HP)catch() -- needs testing
	rollout Name_HP "Hard Point renamer" width:300
	(
		label label1 "Enter Hard Point name"
		label label2 "\"HP_\" prefix will be added automatically"
		edittext nameField ""		
		button renameHP "OK" 		
				
		on renameHP pressed do
		(
			if nameField.text == "" or (matchPattern nameField.text pattern:"HP_*") or (matchPattern nameField.text pattern:"00") then
			(
				messagebox "Please enter a valid name, \n \"HP_\" is added automatically" title:"Invalid Name"
			)
			else
			(
				$.name = "HP_" + nameField.text
			)
			destroyDialog Name_HP	
		)
	)
		
	-----------------------------------------	
	-- If one object selected store it  --
	-----------------------------------------
	if selection.count == 1 then
	(
		attachToMe = $
	)
	
	-----------------
	-- import file --
	-----------------	
	bwScriptsPath = (pathConfig.GetDir #usermacros)
	pathOfFile = ""
	failing = false
	
	-- get file from /bigworld/tools/maxscripts/resources/hard_point/hard_point.fbx, where it is copied to by installer	
	pluginPath = bwGetVisualPluginPath()
	-- returns this "D:\adamm_perforce_workspace\2.current\game\bin\tools\exporter\3dsmax2013x64\""
	
	
	-- NO LONGER USE BIGWORLD DIRECTORY SINCE DIRECTORY RESTRUCTURE
	--bwLoc = bigWorldFolderDir pluginPath
	--bwLoc = bwCleanPath bwLoc
	
	toolsLoc = bwToolsFolderDir pluginPath
	toolsLoc = bwCleanPath toolsLoc	
	--gives us "D:\adamm_perforce_workspace\2.current\game\bin\"
	
	hardPointURL = toolsLoc + "tools/maxscripts/src/import/hard_point.fbx"
	
	if importFile hardPointURL #noPrompt using:FBXIMP  == false then
	(
		messagebox "Cannot import Hard Point because file cannot be found. Please locate the file \"hard_point.fbx\"" title:"File not found"
		pathOfFile = getOpenFileName caption:"Select hard_point.fbx" \
		types:"FBX(*.FBX)|*.fbx*|"	filename: (bwScriptsPath + "hard_point.fbx")
		if pathOfFile != undefined then
		(			
			importFile (pathOfFile) #noPrompt using:FBXIMP			
		)
		else
		(
			messagebox ("hard_point.fbx was not found, import failed. \nhard_point.fbx should be located in bigworld/tools/maxscripts/resources/hard_point." +
				"\nTry reinstalling the scripts, or copy the HardPoint from the  bigworld/tools/maxscripts/src/import folder," +
				"\nor create your own hard_point.fbx at the expected location") title:"File not found"			
			failing = true
		)
	)
	
	-----------------------------------------------
	-- Attach HP to object attachToMe and Rename --
	-----------------------------------------------
	if failing != true do
	(
		select $HP_00
		-- The scale conversion done on import by scaleFactor and scaleConversion is retained in the HP which can result in some strange issues such as attachment scaling 
		-- and irregular HP helper size in max. So we collapse the Xform of the incomming object.
		resetxform $
		maxOps.CollapseNode $ true
		$HP_00.name = uniqueName "HP_" -- prevents cyclical hierarchy on script run twice before object renamed
		createdialog Name_HP 
		
		if attachToMe != "" then
		(
			$.parent = attachToMe
			$.transform = attachToMe.transform
			--	$.rotation = attachToMe.rotation -- redundant
			messageBox ("Hard Point attached and aligned to " + (attachToMe.name) + ". Please adjust accordingly") title:"Hard Point added"
		)
		else
		(
			messagebox "No parent object was selected. HP placed at origin" title:"No parent selected"
		)
		actionMan.executeAction 0 "310"  -- Tools: Zoom Extents Selected
	)
)
