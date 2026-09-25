-- Macroscript for modifying BigWorld resource paths in paths.xml

macroScript Edit_Paths
    category:"BigWorld"
    toolTip:"Edit Paths XML"
    Icon:#("bigworld_icons", 16)
(
    dotnet.loadAssembly "system.xml.dll"
	
	if doesFileExist (pathConfig.appendPath (GetDir #userScripts) "BigWorld_Common.ms") then (
		fileIn "BigWorld_Common.ms" -- using fileIn seams to evaluate the  functions in the included file, whilst include does not - causing all sorts of undeclared problems
		--include "BigWorld_Common.ms"
		failing = False
	)
	else (
		messagebox "'Missing BigWorld_Common.ms, Please refer to the content creation manual for BigWorld MAXScript installation instructions" title:"File not found"
		failing = True
	)	
	
	struct BWEditPaths (
		
		maxForm = "",
		AddButton = dotnetobject "button",
		RemButton = dotnetobject "button",
		ModButton = dotnetobject "button",
		ToggleAbsRelButton = dotnetobject "button",
		SaveExitButton = dotnetobject "button",
		CancelButton = dotnetobject "button",
		pluginPath = "",
		xmlPath = "",
		pathsManager = "",
		listBoxOfPaths = "",
		maxForm = "",
		
		fn onCreate =
		(			
			if failing == false then (				
				this.pluginPath = bwGetVisualPluginPath()			
				this.xmlPath = pathConfig.appendPath this.pluginPath "paths.xml"				
					
				if this.pluginPath != "" then (-- The plugin.ini or plugin.UserSettings.ini does have a bw tag
					failing = false					
					this.pathsManager = PathsXMLManager pathsXML: this.xmlPath pathsXMLDir: this.pluginPath -- might want to make this a property?
					this.gui()
				)
				else (
					failing = true
				)
			)
		),
		b = onCreate(),
		
		fn updateTextScrollList = (
			paths = this.pathsManager.paths
			this.listBoxOfPaths.Items.Clear()
			for i in paths do
			(
				this.listBoxOfPaths.Items.Add i
			)
		),
		
		-- @ sender.tag.value the dotnetEventHandler passes two default arguments, the first is the button itself.
		-- Use the buttons .tag value to store and pass the object because you cant pass args from EventHandlers or call this.Somefunction
		-- should use global function bigWorldResDir to get default starting directory
		fn addPath sender arg = (
			-- why doesnt this.pluginPath work... 			
			--http://forums.cgsociety.org/archive/index.php/t-819223.html
			--http://forums.cgsociety.org/archive/index.php/t-1089936.html
			
			newPath = getSavePath caption:"Select Resource Path to Add"--  initialDir: resDir
			if newPath == undefined then -- Cancel button sets bwFolderLocation to undefined
			(
				messageBox "You have not chosen a path to add" title:"No path selected"
			)
			else (
				sender.tag.value.pathsManager.addPath newPath
				sender.tag.value.updateTextScrollList()
			)
		),

		fn removePath sender arg =
		(
			selectedPath = sender.tag.value.listBoxOfPaths.SelectedItem
			if selectedPath == undefined then (
				messageBox "You have not chosen a path to remove" title:"No path selected"
			)
			else(
				areYouSure = yesNoCancelBox "Are you sure you want to remove the path:" title:"Confirm Remove"
				if areYouSure == #yes then (
					sender.tag.value.pathsManager.removePath selectedPath
					sender.tag.value.updateTextScrollList()
				)
			)
		),

		fn modifyPath sender arg =
		(
			selectedModifyPath = sender.tag.value.listBoxOfPaths.SelectedItem        
			if selectedModifyPath == undefined then (
				messageBox "You have not chosen a path to modify" title:"No path selected"
			)
			else (
				originalText = selectedModifyPath				
				newPath = getSavePath caption:"Select Resource Path to Add" initialDir: originalText
				if newPath == undefined then (
				)
				else (
					sender.tag.value.pathsManager.modifyPath originalText newPath
					sender.tag.value.updateTextScrollList()
				)
			)
		),

		fn toggleAbsRel sender arg =
		(
			selectedPath = sender.tag.value.listBoxOfPaths.SelectedItem
			if selectedPath == undefined then (
				messageBox "You have not chosen a path to modify" title:"No path selected"
			)
			else (
				sender.tag.value.pathsManager.toggleAbsRelPath selectedPath
				sender.tag.value.updateTextScrollList()
			)
		),

		fn saveAndExit sender arg =
		(
			-- THIS IS RETURNING TRUE.. STRANGE TRUE EXPECTED AS FAIL
			pathsWasReadOnly = sender.tag.value.pathsManager.write()
			if pathsWasReadOnly == true then ( -- messagebox handled in pathsManager
			)
			else
			(
				bwRestartMax = yesNoCancelBox "The BigWorld Visual Plugin requires a restart of 3DSMax in order to use changes made to paths.xml.\nWould you like to quit 3DSMax?" title: "Quit 3dsMax?"
			)
			sender.tag.value.maxForm.Close()
			if bwRestartMax == #yes then (
				quitMax()
			)
		),
		
		fn cancelExit sender arg =
		(
			sender.tag.value.maxForm.Close() -- called from event handler passes object via button tag value
			--maxForm.Close()
		),
		
		fn gui = (
			StringForPathUrlLabel = "Filename: "+ this.xmlPath  -- can just use plugin path + paths.xml
			
			--Create DotNet Label
			PathUrlLabel = dotNetObject "label" --"system.windows.forms.label"
			PathUrlLabel.text = StringForPathUrlLabel
			PathUrlLabel.autoSize = true
			PathUrlLabel.location = dotNetObject "System.Drawing.Point" 3 3
			
			--Create Add Button
			-- AddButton = dotNetObject "System.Windows.Forms.Button" -- now a struct property
			AddButton.tag = dotnetmxsvalue this
			AddButton.text = "Add"
			AddButton.size = dotNetObject "System.Drawing.Size" 120 30
			AddButton.location = dotNetObject "System.Drawing.Point" 5 120
			
			--Create Remove Sel. Button
			-- RemButton = dotNetObject "System.Windows.Forms.Button"  -- now a struct property
			RemButton.tag = dotnetmxsvalue this
			RemButton.text = "Remove Sel."
			RemButton.size = dotNetObject "System.Drawing.Size" 120 30
			RemButton.location = dotNetObject "System.Drawing.Point" 130 120
			
			--Create Modify Sel. Button
			--ModButton = dotNetObject "System.Windows.Forms.Button" -- now a struct property
			ModButton.tag = dotnetmxsvalue this
			ModButton.text = "Modify Sel."
			ModButton.size = dotNetObject "System.Drawing.Size" 120 30
			ModButton.location = dotNetObject "System.Drawing.Point" 255 120
			
			--Create Modify Sel. Button
			--ToggleAbsRelButton = dotNetObject "System.Windows.Forms.Button" -- now a struct property
			ToggleAbsRelButton.tag = dotnetmxsvalue this
			ToggleAbsRelButton.text = "Toggle Sel. Abs/Rel"
			ToggleAbsRelButton.size = dotNetObject "System.Drawing.Size" 120 30
			ToggleAbsRelButton.location = dotNetObject "System.Drawing.Point" 380 120
			
			--Create Save and Exit Button
			--SaveExitButton = dotNetObject "System.Windows.Forms.Button" -- now a struct property
			SaveExitButton.tag = dotnetmxsvalue this
			SaveExitButton.text = "Save and Exit"
			SaveExitButton.size = dotNetObject "System.Drawing.Size" 245 30
			SaveExitButton.location = dotNetObject "System.Drawing.Point" 5 155
			
			--Create Cancel Button
			-- CancelButton = dotNetObject "System.Windows.Forms.Button" -- now a struct property
			CancelButton.tag = dotnetmxsvalue this
			CancelButton.text = "Cancel"
			CancelButton.size = dotNetObject "System.Drawing.Size" 245 30
			CancelButton.location = dotNetObject "System.Drawing.Point" 255 155

			--Create Dotnet ListBox
			this.listBoxOfPaths = dotNetObject "System.Windows.Forms.ListBox" width:600 height:260

			--dotNetControl listBoxOfPaths "System.Windows.Forms.ListBox" width:640 height:260
			this.listBoxOfPaths.location = dotNetObject "System.Drawing.Point" 5 20
			this.listBoxOfPaths.MinimumSize = dotNetObject "System.Drawing.Size" 500 100

			-- Populate the ListView			
			this.updateTextScrollList()
			
			--Create a DotNet Form
			this.maxForm = dotNetObject "MaxCustomControls.MaxForm"
			this.maxForm.text = "Modify Resource Paths"
			this.maxForm.AutoSize = true
			this.maxForm.AutoSizeMode = GrowOnly

			--Add the components to the form
			this.maxForm.controls.Add(PathUrlLabel)
			this.maxForm.controls.Add(listBoxOfPaths)
			this.maxForm.controls.Add(AddButton)
			this.maxForm.controls.Add(RemButton)
			this.maxForm.controls.Add(ModButton)
			this.maxForm.controls.Add(ToggleAbsRelButton)
			this.maxForm.controls.Add(SaveExitButton)
			this.maxForm.controls.Add(CancelButton)
			this.maxForm.topmost = true
			this.maxForm.AutoScale = true

			--Event handler for button pressed		
			dotNet.addEventHandler AddButton "click" addPath
			dotNet.setLifetimeControl AddButton #dotNet
			
			--Event handler for button pressed
			dotNet.addEventHandler RemButton "click" removePath
			dotNet.setLifetimeControl RemButton #dotNet
			
			--Event handler for button pressed
			dotNet.addEventHandler ModButton "click" modifyPath
			dotNet.setLifetimeControl ModButton #dotNet
			
			--Event handler for button pressed
			dotNet.addEventHandler ToggleAbsRelButton "click" toggleAbsRel
			dotNet.setLifetimeControl ToggleAbsRelButton #dotNet
			
			--Event handler for button pressed
			dotNet.addEventHandler SaveExitButton "click" saveAndExit
			dotNet.setLifetimeControl SaveExitButton #dotNet
			
			--Event handler for button pressed
			dotNet.addEventHandler CancelButton "click" cancelExit
			dotNet.setLifetimeControl CancelButton #dotNet
			-- draw form
			maxForm.show()
		)		
	) -- struct end
	
    --bwEditPathsObject = bwEditPaths() myVar:0.
	bwEditPathsObject = bwEditPaths pluginPath:""
)