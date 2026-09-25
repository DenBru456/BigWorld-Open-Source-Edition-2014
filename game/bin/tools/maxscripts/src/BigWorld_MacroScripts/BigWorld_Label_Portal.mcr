macroScript Label_Portal
	category:"BigWorld"
	toolTip:"Label a Portal"
	Icon:#("bigworld_icons", 8)
	
(
	-- BigWorld Label Portals
	-- 
	-- Version: 1.0
	-- Date: 2010
	-- Author: Adam Maxwell
	-- Website: http://www.bigworldtech.com
	-- Works on: MAX 2010
	--
	-- Description:
	-- Assigns a portal label to an existing portal by adding the User defined property
	-- label = label_name
	--
	-- ToDo:
	-- Display existing label name when label already exists. 
	--
	-- Known Bugs:
	-- None	
	
	function IsPortal selected = 
	(
		for i in 1 to selection.count do -- COUNTING TWICE!
		(
			
			global stdPort = getUserProp selection[i] "portal"
			global heavPort = getUserProp selection[i] "heaven"
			global exPort = getUserProp selection[i] "exit"
			
			if stdPort == true or heavPort == true or exPort == true then -- is some type of portal
			(		
				return True
			)
			else
			(
				messagebox "Portal Labels cannot be assigned to non portal objects. This object is not a portal."
				return False
			)
		)
	)	
	
	try(destroyDialog Name_HP)catch() -- needs testing
	rollout Name_Label "Portal Labeller" width:300
	(
		label label1 "Enter Portal Label"
		label label2 "\"label = \" prefix will be added automatically"
		edittext nameField ""		
		button okLabel "OK" 		
				
		on okLabel pressed do
		(
			if nameField.text == "" or (matchPattern nameField.text pattern:"label*") then
			(
				messagebox "Please enter a valid name, \n \"label =\" is added automatically"
			)
			else
			(
				setUserProp $ "label" nameField.text
			)
			destroyDialog Name_Label	
		)
	)
	
	-- Get the number of objects selected
	selectionCount = 0
	for i in 1 to selection.count do
	(
		selectionCount = selectionCount + 1
	)
		
	-- Test for single object selection or sub object selection
	if selectionCount == 1 then
	(
		global label = getUserProp $ "label"
		if label == "" or label == undefined then
		(		
			if subobjectLevel == 1 or subobjectLevel == 2 or subobjectLevel == 3 or subobjectLevel == 4 or subobjectLevel == 5 then
			(
				subSelection = true
				messagebox "Portal Labels cannot be assigned to sub objects, Use a separate portal object."
			)
			else -- A single object is selected
			(
				if IsPortal $ == true then
				(
					createDialog Name_Label
				)
				else -- The selected object is not a Portal
				(
					print "Object is not a portal"
				)
			)
		)
		else -- The portal is already labelled
		(
			print "The portal is already labelled"
						
			result = queryBox ("An exisint label was found with the value : " +label as string + "\nDo you want to remove this label") beep:false
			if result then 
			(
				setUserProp $ "label" ""
			)
		)
	)	
	else
	(
		messagebox "Zero or Multiple objects selected. \nPortal labels can only be added one at a time. Select a single portal and try again"
	)	
)