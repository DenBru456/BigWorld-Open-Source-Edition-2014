macroScript Export_Animation
	category:"BigWorld"
	toolTip:"Export BigWorld Animation"
	Icon:#("bigworld_icons", 15)
	
(	
	-- This version detects the bigworld export settings
	resPath = (getDir #export) + "/"
	exportLocation = getSaveFileName caption:"Choose location to export model" filename: resPath types:"Animation(*.animation)"
	
	function beginExport objectGroup exportAnimationLocation exportSelected =
	(	
		isAllowScale = false
		isMorph = false
		isNoteTrack = false
		for i in objectGroup do
		(
			if i.scale.isAnimated == true then
			(
				isAllowScale = true
			)
			for m in i.modifiers do
			(
				if classof m == Morpher do
				(
					isMorph = true
				)
			)
			if hasNoteTracks i == true then
			(
				isNoteTrack = true
			)
		)
		BWAnimationSetting "allow_scale" isAllowScale "morph" isMorph "cue_track" isNoteTrack
		exportFile exportAnimationLocation selectedOnly:exportSelected
	)	
	
	numSelected = 0
	for i in selection do
	(
		numSelected += 1
	)
	
	if exportLocation != undefined then
	(
		-- strip away a .animation or .animationsettings extension that the user may of selected within the getSave dialog
		if findString exportLocation ".animation" != undefined then
		(
			extensionIndex = findString exportLocation ".animation"
			exportLocation = substring exportLocation 1 (extensionIndex - 1)
		)
		
		exportAnimationLocation = exportLocation + ".animation"
		animationSettings_url = exportLocation + ".animationsettings"
		if doesFileExist animationSettings_url then -- export the file using the animationsettings.xml settings
		(
			if numSelected >= 1 then
			(
				exportFile exportAnimationLocation selectedOnly:true
			)
			else
			(
				exportFile exportAnimationLocation selectedOnly:false
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
			beginExport objectGroup exportAnimationLocation exportSelected
		)
	)
	else
	(
		messagebox "Invalid export path, export cancelled"
	)
)