macroScript Cue_Track
	category:"BigWorld"
	toolTip:"Add a Note Track"
	Icon:#("bigworld_icons", 5)
	
(	
	-- BigWorld Add Cue Track
	-- 
	-- Version: 1.0
	-- Date: 2010
	-- Author: Adam Maxwell
	-- Website: http://www.bigworld.com
	-- Works on: MAX 2010
	--
	-- Description:
	-- Adds a NoteTrack and key to the selected node at current frame
	-- User can choose between cue: and sound: 
	-- Prompts for input for the cue
	--
	-- Known Bugs:
	-- The track view doesnt zoom into the exact node containing the new note track.
	--
	-- To Do:
	-- Zoom and expand the note track in the dope sheet
	--
	-- Info:
	-- BigWorld reads note tracks applied to the root of a node. 
	-- It is essential that note tracks be added directly to a node. Note tracks added to the global scene or deep with a nodes parameters (such as its transforms or materials) will be ignored. 
	-- Types of note tracks available (cue:name, sound:name)
	
	global conjugatedName = ""
	
	try(destroyDialog EnterNoteData)catch() 
	rollout EnterNoteData "Enter Note Info" width:300
	(
		label label1 "Enter Note Track Information"
		label label2 "prefix types will be added automatically"
		radiobuttons noteType "Note Type:" labels:#("cue:", "sound:") columns:2 
		edittext nameField ""		
		button renameNote "OK"
		
		on renameNote pressed do
		(
			if nameField.text == "" or (matchPattern nameField.text pattern:"cue:*") or (matchPattern nameField.text pattern:"sound:*") then
			(
				messagebox "Please enter a valid name, \n prefix types are added automatically"
			)
			else
			(
				prefixType = ""
				case noteType.state of
				(
					1: prefixType = "cue:"
					2: prefixType = "sound:"
				)
				
				conjugatedName = prefixType + nameField.text				
				ntp1 = NoteTrack "PosNT1"
				
				if hasNoteTracks $ == true then -- Already has note track
				(
					noteTrackName = getNoteTrack $ 1
					NewKey = addNewNoteKey noteTrackName.keys sliderTime #select -- add key to existing note track at slider time
				)
				else -- Doesn't have notetrack. so add one. 
				(
					addNoteTrack $ ntp1 -- 
					newKey = addNewNoteKey ntp1.keys sliderTime #select 
				)
				newKey.value = conjugatedName
								
				macros.run "Track View" "LaunchDopeSheetEditor"
				trackviews.current.setFilter #keyableTracks #noteTracks
				trackviews.zoomSelected #noteTracks
				
				destroyDialog EnterNoteData			
			)			
		)		
	)
		
	selectionCount = 0
	for i in 1 to selection.count do
	(
		selectionCount = selectionCount + 1
	)
		
	if selectionCount == 1 then
	(
		createDialog EnterNoteData
	)	
	else
	(
		messagebox "Zero or Multiple objects selected. \nNote tracks must be added to a single node. \nChose an object to add a Note Track"
		pickObject prompt:"Select an object" select: true
		if $ != undefined then
		(
			createDialog EnterNoteData
		)
		else
		(
			messagebox "No object selected aborting BigWorld NoteTrack"
		)
	)	
)