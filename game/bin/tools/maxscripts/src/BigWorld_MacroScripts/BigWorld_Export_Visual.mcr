macroScript Export_Visual
	category:"BigWorld"
	toolTip:"Export BigWorld Visual"
	Icon:#("bigworld_icons", 14)
	
(	
	-- This version detects the bigworld export settings
	resPath = (getDir #export) + "/"
	exportLocation = getSaveFileName caption:"Choose location to export model" filename: resPath types:"Visual(*.visual)"
	
	function beginExport objectGroup exportVisualLocation exportSelected =
	(
		isAnimatedAsset = false
		isStaticWithNodesAsset = false	
		for i in objectGroup do
		(
			if i.position.isAnimated == true or i.rotation.isAnimated == true or i.scale.isAnimated == true then
			(
				isAnimatedAsset = true
			)
			for m in i.modifiers do
			(
				if classof m == skin or classof m == Morpher or classof m == Physique do
				(
					isAnimatedAsset = true
				)
			)
		)
		if isAnimatedAsset == true then
		(
			BWVisualSetting "mode" "animated" "allow_scale" true "bump_mapped" true
			exportFile exportVisualLocation selectedOnly:exportSelected
		)
		else -- not likely animated
		(
			for i in objectGroup do 
			(
				if matchpattern i.name pattern:( "HP_*") then -- static with nodes
				(
					isStaticWithNodesAsset = true
				)
			)
			if isStaticWithNodesAsset == true then
			(
				BWVisualSetting "mode" "static_with_nodes" "allow_scale" true "bump_mapped" true
				exportFile exportVisualLocation selectedOnly:exportSelected
			)
			else -- static
			(
				BWVisualSetting "mode" "static" "allow_scale" true "bump_mapped" true
				exportFile exportVisualLocation selectedOnly:exportSelected
			)
		)
	)
	
	numSelected = 0
	for i in selection do
	(
		numSelected += 1
	)
	
	if exportLocation != undefined then
	(
		-- strip away any .visual .primitive .model extension that the user may of selected within the getSave dialog
		if findString exportLocation ".model" != undefined then
		(
			extensionIndex = findString exportLocation ".model"
			exportLocation = substring exportLocation 1 (extensionIndex - 1)
		)
		if findString exportLocation ".visual" != undefined then
		(
			extensionIndex = findString exportLocation ".visual"
			exportLocation = substring exportLocation 1 (extensionIndex - 1)
		)
		if findString exportLocation ".primitives" != undefined then
		(
			extensionIndex = findString exportLocation ".primitives"
			exportLocation = substring exportLocation 1 (extensionIndex - 1)
		)
		if findString exportLocation ".visualsettings" != undefined then
		(
			extensionIndex = findString exportLocation ".visualsettings"
			exportLocation = substring exportLocation 1 (extensionIndex - 1)
		)
		if findString exportLocation ".thumbnail.jpg" != undefined then
		(
			extensionIndex = findString exportLocation ".thumbnail.jpg"
			exportLocation = substring exportLocation 1 (extensionIndex - 1)
		)
		
		exportVisualLocation = exportLocation + ".visual"
		visualSettings_url = exportLocation + ".visualsettings"
		if doesFileExist visualSettings_url then -- export the file using the visualSettings.xml settings
		(
			if numSelected >= 1 then
			(
				exportFile exportVisualLocation selectedOnly:true
			)
			else
			(
				exportFile exportVisualLocation selectedOnly:false
			)
		)
		else
		(
			if numSelected >= 1 then -- Allow for export selected. Will only export selected objects, if nothing selected will export all.
			(
				exportSelected = true
				objectGroup = selection
			)
			else
			(
				exportSelected = false
				objectGroup = objects
			)
			beginExport objectGroup exportVisualLocation exportSelected
		)
	)
	else
	(
		messagebox "Invalid export path, export cancelled"
	)
)