-- Macroscript for verifying and correcting the scene resources against resouce paths in paths.xml
macroScript Verify_Paths
    category:"BigWorld"
    toolTip:"Verify Texture Paths"
    Icon:#("bigworld_icons", 17)
(
	if doesFileExist (pathConfig.appendPath (GetDir #userScripts) "BigWorld_Common.ms") then (
		fileIn "BigWorld_Common.ms" -- using fileIn seams to evaluate the  functions in the included file, whilst include does not - causing all sorts of undeclared problems
		--include "BigWorld_Common.ms"
		failing = False
	)
	else (
		messagebox "'Missing BigWorld_Common.ms, Please refer to the content creation manual for BigWorld MAXScript installation instructions" title:"File not found"
		failing = True
	)	
	
	struct BWVerifyPaths (
		listBoxOfTexturePaths = #(),
		fileNodes = #(),
		filesNeedingReview = #(),
		resPaths = #(),
		pluginPath = "",
		xmlPath = "",
		maxForm = "",
		verifyGui = "",
		CopyAllToButton = dotnetobject "button",
		CopySelToButton = dotnetobject "button",	
		CancelButton = dotnetobject "button",
		
		--@param silentSuccess is set to True when this function is called from the export process.
		--@param selection is set to True when in Export Selection mode. In this event we only consider fileTexture nodes connected to the current selection.
		fn onCreate failing:False silentSuccess:False selectedExport:False = (
			if failing == False then (
				this.pluginPath = bwGetVisualPluginPath()
				this.xmlPath = pathConfig.appendPath this.pluginPath "paths.xml"
				
				pathsManager = PathsXMLManager pathsXML: this.xmlPath pathsXMLDir: this.pluginPath
				this.resPaths = pathsManager.getArrayOfAbsPaths()		
				
				if selectedExport then (				
					this.fileNodes = (this.getFileTextureAttachedToObjects selection)					
				)
				else ( -- not export selected				
					this.fileNodes = this.getFileTextureAttachedToObjects objects
				)
				
				if not silentSuccess and (fileNodes.count == 0) then (
					messagebox "Objects to be exported do not have associated texture files" title:"No textures found"
					return undefined
				)
				
				for f in this.fileNodes do (
					texName = f.filename
					texName = bwCleanPath texName
					if not this.pathInResPaths texName then (
						if appendIfUnique this.filesNeedingReview texName then (
						)
					)
				)
				if this.filesNeedingReview.count > 0 then (
					this.verifyGui = this.gui()
				)
				if not silentSuccess and this.filesNeedingReview.count == 0 then (
					messagebox "All texture paths are in the res path" title:"Textures already in res path!"
				)
			)
		),
		b = onCreate(),		
			
		fn updateTextScrollList = (			
			this.listBoxOfTexturePaths.Items.Clear()
			for i in this.filesNeedingReview do
			(
				this.listBoxOfTexturePaths.Items.Add i
			)
		),
		
		-- @ sender.tag.value the dotnetEventHandler passes two default arguments, the first is the button itself.
		-- Use the buttons .tag value to store and pass the object because you cant pass args from EventHandlers or call this.CopyAll 		
		fn copyAll sender arg = (
			if sender.tag.value.filesNeedingReview.count == 0 then (
				return undefined -- shouldnt occur because gui should of closed if this occurs
			)
			
			fileNodesSubSet = #()
			for i = 1 to sender.tag.value.filesNeedingReview.count do (
				for f in sender.tag.value.fileNodes do (
					if bwCleanPath f.filename == bwCleanPath sender.tag.value.filesNeedingReview[i] then (
						append fileNodesSubSet f
					)
				)
			)
			sender.tag.value.doCopy fileNodesSubSet
		),

		fn copySelection sender arg = (
			selectedObjects = sender.tag.value.listBoxOfTexturePaths.SelectedItems			
			numberSelected = sender.tag.value.listBoxOfTexturePaths.SelectedItems.Count
			
			if numberSelected == 0 then (
				messagebox "Please select a texture to move" title:"Nothing selcted"
				return undefined
			)
			
			fileNodesSubSet = #()
			
			for i = 0 to numberSelected-1 do (
				for f in sender.tag.value.fileNodes do (
					cleanFileName = bwCleanPath f.filename
					if selectedObjects.Item[i] == cleanFileName do (
						append fileNodesSubSet f
					)
				)
			)
			sender.tag.value.doCopy fileNodesSubSet
		),

		-- this cancel exit is called when dotnet button is pressed
		fn cancelExitFromButton sender arg = (			
			sender.tag.value.maxForm.Close()
		),
		
		-- this cancel exit is called when the files to review is empty.
		fn cancelExit = (
			this.maxForm.Close()
		),

		fn gui = (			
			--Create DotNet Label for ListBox
			listBoxLabel = dotNetObject "label" --"system.windows.forms.label"
			listBoxLabel.text = "Review Texture File Locations"
			listBoxLabel.autoSize = true
			listBoxLabel.location = dotNetObject "System.Drawing.Point" 3 3
			
			--Create Copy All To Button		
			-- CopyAllToButton = dotNetObject "System.Windows.Forms.Button"  -- now a property of object
			CopyAllToButton.tag = dotnetmxsvalue this
			CopyAllToButton.text = "Copy All To"
			CopyAllToButton.size = dotNetObject "System.Drawing.Size" 165 30
			CopyAllToButton.location = dotNetObject "System.Drawing.Point" 5 120
			
			--Create Copy Sel. To
			--CopySelToButton = dotNetObject "System.Windows.Forms.Button"  -- now a property of object
			CopySelToButton.tag = dotnetmxsvalue this
			CopySelToButton.text = "Copy Sel. To"
			CopySelToButton.size = dotNetObject "System.Drawing.Size" 165 30
			CopySelToButton.location = dotNetObject "System.Drawing.Point" 175 120

			--Create Cancel Button
			-- CancelButton = dotNetObject "System.Windows.Forms.Button"  -- now a property of object
			CancelButton.tag = dotnetmxsvalue this
			CancelButton.text = "Cancel"
			CancelButton.size = dotNetObject "System.Drawing.Size" 165 30
			CancelButton.location = dotNetObject "System.Drawing.Point" 345 120

			--Create Dotnet ListBox
			this.listBoxOfTexturePaths = dotNetObject "System.Windows.Forms.ListBox" width:600 height:260			
			this.listBoxOfTexturePaths.SelectionMode = listBoxOfTexturePaths.SelectionMode.MultiExtended	
			this.listBoxOfTexturePaths.location = dotNetObject "System.Drawing.Point" 5 20
			this.listBoxOfTexturePaths.MinimumSize = dotNetObject "System.Drawing.Size" 500 100

			-- Populate the ListView			
			this.updateTextScrollList()
			
			--Create a DotNet Form
			-- global form = maxForm = dotNetObject "MaxCustomControls.MaxForm"
			this.maxForm = dotNetObject "MaxCustomControls.MaxForm"
			this.maxForm.text = "Review Texture File Locations"
			this.maxForm.AutoSize = true
			this.maxForm.AutoSizeMode = GrowOnly

			--Add the components to the form
			this.maxForm.controls.Add(listBoxLabel)
			this.maxForm.controls.Add(listBoxOfTexturePaths)
			this.maxForm.controls.Add(CopyAllToButton)
			this.maxForm.controls.Add(CopySelToButton)
			this.maxForm.controls.Add(CancelButton)
			this.maxForm.topmost = true
			this.maxForm.AutoScale = true
			
			--Event handler for button pressed
			dotNet.addEventHandler CopyAllToButton "click" copyAll
			dotNet.setLifetimeControl CopyAllToButton #dotNet
			
			--Event handler for button pressed
			dotNet.addEventHandler CopySelToButton "click" copySelection
			dotNet.setLifetimeControl CopySelToButton #dotNet
			
			--Event handler for button pressed
			dotNet.addEventHandler CancelButton "click" cancelExitFromButton
			dotNet.setLifetimeControl CancelButton #dotNet
			
			-- draw form
			this.maxForm.show()
		),
		
		fn pathInResPaths pathToTest = (
			pathToTest = bwCleanPath pathToTest
			for resPath in this.resPaths do (		
				if  findString pathToTest resPath == 1 then (
					return True
				)
			)
			return False
		),
		
-- 		fn bigWorldFolderDir = (
-- 			bwLoc = findString this.pluginPath "bigworld"
-- 			bwLoc -= 1
-- 			if bwLoc != undefined then (
-- 				bwDir = substring this.pluginPath 1 bwLoc
-- 			) 
-- 			else (
-- 				bwDir = "" -- cannot pass undefined to getSavePath initialDir (see getCopyDestinationDir)
-- 			)
-- 			return bwDir
-- 		),			
		
		fn getCopyDestinationDir = (
			resDir = bigWorldResDir pluginPath			
			destDir = getSavePath caption:"Select Resource Path For Copy Destination" initialDir: resDir 
			-- Handle dialog cancel
			if destDir == undefined or destDir == "" then (
				return undefined -- choose nothing for the save path
			)
			-- destDir = newpath
			if not this.pathInResPaths destDir then (		
				messagebox ("The destination dir: " + destDir as string + "\ndoes not exist within the resource paths specified in paths.xml.\n\nPlease select an appropriate destination or adjust your paths.xml.") title: "Bad Destination Dir"
				return undefined
			)	
			return destDir -- warning possibly not absolute
		),
		
		fn doCopy fileNodesSubSet = (
			destinationDir = this.getCopyDestinationDir()
			
			if destinationDir == undefined or not doesFileExist destinationDir then (
				-- messagebox already send in getCopyDestinationDir
				return undefined
			)
			
			for f in fileNodesSubSet do (
				-- The fileNodeSubSet (max material) can contain references to files that no longer exist.
				-- This tells the user that the material will be remapped but the file is missing
				if not doesFileExist f.filename then (
					messagebox ("Could not find texture for copy.\n" + f.filename as string + "\nThe material has been remapped to the destination") title:"Missing texture file!"
				)
				
				fBasename = filenameFromPath f.filename
				destFile = destinationDir + "\\" + fBasename
				
				-- Check to see if file exists and ask if OK to overwrite
				shouldCopy = True		
				if doesFileExist destFile then (
					result = yesNoCancelBox ("Do you want to overwrite the file " + destFile as string + "?") title:"Overwrite Files?"
					if result == #no or result == #cancel then (
						shouldCopy = False
					)			
				)
				
				-- Move the file 
				if shouldCopy then (
					fileToCopy = bwCleanPath f.filename
					copyFile fileToCopy destFile
				)
				
				absolutefFilename = bwCleanPath f.filename
				
				-- for every file needing review (the listbox) if the name is the same as the textureNode.filename then change the textureNode.filename to destFile 
				-- im pretty sure this first bit is superferlous because filesNeedingReview is unique
				for i in this.filesNeedingReview do (
					if i == absolutefFilename then (
						-- had to put this in because duplicate fileNodes would result in only one of them being remapped. 
						for g in fileNodesSubSet do (
							if g.fileName == f.fileName and f != g then (
								g.fileName = destFile		
							)
						)					
						f.filename = destFile
					)
				)
				
				-- Delete the item from fileNeedingReview
				index = findItem this.filesNeedingReview absolutefFilename
				if index > 0 then (
					this.filesNeedingReview = deleteItem this.filesNeedingReview index
				)
			)
				
			if this.filesNeedingReview.count == 0 then (
				this.cancelExit()
			)
			
			-- update the ListBox gui
			this.updateTextScrollList()
		),
		
		fn getFileTextureAttachedToObjects theObjects =(
			listfileNodes = #()
			for obj in theObjects do
			(
				join listfileNodes (getClassInstances bitmapTexture target:obj asTrackViewPick:off)
			)
			makeUniqueArray listfileNodes
			return listfileNodes
		)
	)
	
	bwVerifyPathsObject = BWVerifyPaths()	
)