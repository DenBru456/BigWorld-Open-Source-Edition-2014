macroScript Prefab_Assembler
	category:"BigWorld"
	toolTip:"Prefab Assembler"
	Icon:#("bigworld_icons", 13)
(
	-- BigWorld Prefab_Assembler
	-- 
	-- Version: 1.0
	-- Date: 2011
	-- Author: Adam Maxwell
	-- Website: http://www.bigworldtech.com
	-- Tested with: MAX 2011 
	--
	-- Description
	-- Exports all unhidden geometry class objects on layers with special suffix and assembles them into a .prefab for placement in WorldEditor
	
	include "BigWorld_Common.ms"
	
	global MODEL_LAYER_SUFFIX = "_bw_model_layer"
	global SHELL_LAYER_SUFFIX = "_bw_shell_layer"
	
	dotnet.loadAssembly "system.xml.dll"
	xml=dotNetObject "system.xml.xmlDocument"
	
	failing = false
	exportModelLocation = undefined
	exportShellLocation = undefined
	prefab_url = undefined
	enableExportButtonSwitch1 = false
	enableExportButtonSwitch2 = false
	objectListAndOffsets_url = undefined
	cleanAllBBoxMinString = undefined
	cleanAllBBoxMaxString = undefined
	
	rollout BigWorldPrefabAssembler "BigWorld Prefab Assembler" width:320
	(		
		function generatePrefabBoundingBox objectGroup = -- Will be called once with all objects in scene to create prefab bounding box, then once for each layer
		(			
			combinerCreated = false
			tmpObjCombiner = undefined
			for obj in objectGroup do -- Create duplicate object and attach all objects to it for prefab bounding box calculation
			(				
				if combinerCreated == true then 
				(
					tmpObj = copy obj
					attach tmpObjCombiner tmpObj					
				)
				else
				(
					tmpObjCombiner = copy obj
					convertToMesh tmpObjCombiner
					combinerCreated = true					
				)
			)			
			-- process boundiing box information			
			boundingBoxMin = tmpObjCombiner.min
			maxUnitsBoundingBoxMin = tmpObjCombiner.min
			tmpBBMin = convertToMeters boundingBoxMin -- unit and system scale fixes
			boundingBoxMin = convertCoordinateToBW tmpBBMin -- BW and Max have different coord sys, swap Y and Z
			formattedBBoxMin = formattedPrint boundingBoxMin format:".6f" -- prefab files use 6 decimal places
			
			boundingBoxMax = tmpObjCombiner.max
			tmpBBMax = convertToMeters boundingBoxMax -- unit and system scale fixes
			boundingBoxMax = convertCoordinateToBW tmpBBMax -- BW and Max have different coord sys, swap Y and Z
			formattedBBoxMax = formattedPrint boundingBoxMax format:".6f" -- prefab files use 6 decimal places
			cleanBBoxMinString = cleanUpForPrinting formattedBBoxMin -- remove [ " , etc.
			cleanBBoxMaxString = cleanUpForPrinting formattedBBoxMax
			
			-- Store the boundingbox information for writing to xml
			cleanAllBBoxMinString = cleanBBoxMinString
			cleanAllBBoxMaxString = cleanBBoxMaxString			
			
			delete tmpObjCombiner
			
			return maxUnitsBoundingBoxMin  -- Return the min bbox of the combined objects in layer to
		)
		
		function generateLayerBoundingBox objectGroup objectListAndOffsets = -- Will be called once with all objects in scene to create prefab bounding box, then once for each layer
		(			
			combinerCreated = false
			tmpObjCombiner = undefined
			for obj in objectGroup do -- Create duplicate object and attach all objects to it for prefab bounding box calculation
			(				
				if combinerCreated == true then 
				(
					tmpObj = copy obj
					attach tmpObjCombiner tmpObj					
				)
				else
				(
					tmpObjCombiner = copy obj
					convertToMesh tmpObjCombiner
					combinerCreated = true					
				)
			)			
			-- process boundiing box information			
			boundingBoxMin = tmpObjCombiner.min
			maxUnitsBoundingBoxMin = tmpObjCombiner.min
			tmpBBMin = convertToMeters boundingBoxMin -- unit and system scale fixes
			boundingBoxMin = convertCoordinateToBW tmpBBMin -- BW and Max have different coord sys, swap Y and Z
			formattedBBoxMin = formattedPrint boundingBoxMin format:".6f" -- prefab files use 6 decimal places
			
			boundingBoxMax = tmpObjCombiner.max
			tmpBBMax = convertToMeters boundingBoxMax -- unit and system scale fixes
			boundingBoxMax = convertCoordinateToBW tmpBBMax -- BW and Max have different coord sys, swap Y and Z
			formattedBBoxMax = formattedPrint boundingBoxMax format:".6f" -- prefab files use 6 decimal places
			cleanBBoxMinString = cleanUpForPrinting formattedBBoxMin -- remove [ " , etc.
			cleanBBoxMaxString = cleanUpForPrinting formattedBBoxMax
			
			-- Write out the layers info to the objectListAndOffsets file
			format (cleanBBoxMinString + "\n") to: objectListAndOffsets -- this is the objects position.
			format (cleanBBoxMinString + "\n") to: objectListAndOffsets -- this is the objects min bbox
			format (cleanBBoxMaxString + "\n") to: objectListAndOffsets 			
			
			delete tmpObjCombiner
			
			return maxUnitsBoundingBoxMin  -- Return the min bbox of the combined objects in layer to
		)		
		
		function WriteXML prefab_url boundingBoxMin boundingBoxMax =
		(
			-- root parent tag
			rootName = filenameFromPath prefab_url
			root = xml.CreateElement rootName
			xml.AppendChild root
			
			-- chunks tag
			chunks = xml.CreateElement "chunks"
			root.AppendChild chunks
			
			-- item tag
			items = xml.CreateElement "items"
			root.AppendChild items
			
			local f = openFile objectListAndOffsets_url mode:"r"
			
			chunk_i = 0
			while not eof f do
			(
				model_url = readLine f
				modelTransform = readLine f
				BBMin = readLine f
				BBMax = readLine f
				
				-- exporting Shells				
				if matchpattern model_url pattern:("*" + SHELL_LAYER_SUFFIX + "*") then 
				(				
					-- -- -- add chunk0 to chunks
					tmpChunkNo = ("chunk" + chunk_i as string +".chunk")
					chunkNo = xml.CreateElement tmpChunkNo
					chunks.AppendChild chunkNo
					
					-- -- -- -- add shell to chunkNo
					shellTag = xml.CreateElement "shell"
					chunkNo.AppendChild shellTag
					
					-- -- -- -- -- editorOnly tag to shellTag
					editorOnly = xml.CreateElement "editorOnly"
					shellTag.AppendChild editorOnly
					
					-- -- -- -- -- metaData tag to shell Tag
					metaData = xml.CreateElement "metaData"
					shellTag.AppendChild metaData
					
					-- -- -- resource tag, sets the location of the .model file
					resource = xml.CreateElement "resource"
					shellTag.AppendChild resource 
					resource.InnerText = ("\t" + model_url + "\t")
					
					-- -- -- transform tag
					transformTag = xml.CreateElement "transform"
					shellTag.AppendChild transformTag
					
					-- -- -- reflectionVisible tag
					reflectionVisible = xml.CreateElement "reflectionVisible"
					shellTag.AppendChild reflectionVisible
					reflectionVisible.InnerText = "\tfalse\t" 
					
					-- -- -- prefab transform tag
					prefabTransform = xml.CreateElement "transform"
					chunkNo.AppendChild prefabTransform	
					
					-- -- -- shell boundingBox tag
					boundingBoxTag = xml.CreateElement "boundingBox"
					chunkNo.AppendChild boundingBoxTag
					
					-- -- -- -- min tag
					minTag = xml.CreateElement "min"
					boundingBoxTag.AppendChild minTag
					minTag.InnerText = ("\t" + BBMin as string + "\t")
					
					-- -- -- -- max tag
					maxTag = xml.CreateElement "max"
					boundingBoxTag.AppendChild maxTag
					maxTag.InnerText = ("\t" + BBMax as string + "\t")	
					
					chunk_i = chunk_i + 1
				)
				else if matchpattern model_url pattern:("*" + MODEL_LAYER_SUFFIX + "*") then -- non shell objects
				(						
					-- -- -- model tag
					model = xml.CreateElement "model"
					items.AppendChild model
					
					-- -- -- editorOnly tag
					editorOnly = xml.CreateElement "editorOnly"
					model.AppendChild editorOnly

					-- -- -- metaData tag
					metaData = xml.CreateElement "metaData"
					model.AppendChild editorOnly

					-- -- -- resource tag, sets the location of the .model file
					resource = xml.CreateElement "resource"
					model.AppendChild resource 
					resource.InnerText = ("\t" + model_url + "\t")	
					
					-- -- -- transform tag
					transformTag = xml.CreateElement "transform"
					model.AppendChild transformTag		
					
					-- -- -- reflectionVisible tag
					reflectionVisible = xml.CreateElement "reflectionVisible"
					model.AppendChild reflectionVisible
					reflectionVisible.InnerText = "\tfalse\t" 
					
					-- -- -- prefab transform tag
					prefabTransform = xml.CreateElement "prefabTransform"
					model.AppendChild prefabTransform				
				)
				
				-- Children of editorOnly
				-- -- -- -- hidden tag
				hidden = xml.CreateElement "hidden"
				editorOnly.AppendChild hidden
				hidden.InnerText = "\tfalse\t"
				
				-- -- -- -- frozen tag
				frozen = xml.CreateElement "frozen"
				editorOnly.AppendChild frozen
				frozen.InnerText = "\tfalse\t"
				
				-- -- -- -- castShadow tag
				castShadow = xml.CreateElement "castShadow"
				editorOnly.AppendChild castShadow
				castShadow.InnerText = "\ttrue\t"
				
				-- Children of transformTag
				-- -- -- -- transform rows
				row0 = xml.CreateElement "row0"
				transformTag.AppendChild row0
				row0.InnerText = "\t1.000000 0.000000 0.000000\t" 
				
				row1 = xml.CreateElement "row1"
				transformTag.AppendChild row1
				row1.InnerText = "\t0.000000 1.000000 0.000000\t" 
				
				row2 = xml.CreateElement "row2"
				transformTag.AppendChild row2
				row2.InnerText = "\t0.000000 0.000000 1.000000\t" 
				
				row3 = xml.CreateElement "row3"
				transformTag.AppendChild row3
				row3.InnerText = "\t0.000000 0.000000 0.000000\t" 
				
				-- Children of prefab transform tag
				-- -- -- -- prefab transform rows
				row0 = xml.CreateElement "row0"
				prefabTransform.AppendChild row0
				row0.InnerText = "\t1.000000 0.000000 0.000000\t" 
				
				row1 = xml.CreateElement "row1"
				prefabTransform.AppendChild row1
				row1.InnerText = "\t0.000000 1.000000 0.000000\t" 
				
				row2 = xml.CreateElement "row2"
				prefabTransform.AppendChild row2
				row2.InnerText = "\t0.000000 0.000000 1.000000\t" 
				
				row3 = xml.CreateElement "row3"
				prefabTransform.AppendChild row3
				row3.InnerText = ("\t" + modelTransform as string + "\t")
			)
			
			-- -- boundingBox tag
			boundingBox = xml.CreateElement "boundingBox"
			root.AppendChild boundingBox
			
			-- -- -- min tag
			minTag = xml.CreateElement "min"
			boundingBox.AppendChild minTag
			minTag.InnerText = ("\t" + boundingBoxMin as string + "\t")
			
			-- -- -- max tag
			maxTag = xml.CreateElement "max"
			boundingBox.AppendChild maxTag
			maxTag.InnerText = ("\t" + boundingBoxMax as string + "\t")
			
			-- -- snaps tag
			snaps = xml.CreateElement "snaps"
			root.AppendChild snaps
				
			-- -- -- min tag
			positionTag = xml.CreateElement "position"
			snaps.AppendChild positionTag
			positionTag.InnerText = "\t0.000000 0.000000 1.000000\t"
			
			-- -- -- max tag
			angleTag = xml.CreateElement "angle"
			snaps.AppendChild angleTag
			angleTag.InnerText = "\t0.000000\t"
			
			xml.save prefab_url
			close f
		)
		
		function exportAllSceneTo exportLocation =
 		(			
			-- Create a file listing all exported objects and their offests
			local isGeometry = false
			tempDir = getDir #temp -- 3dsMax LocalSettings Temp
			objectListAndOffsets_url = tempDir + "\list_and_offsets.txt"
			try deleteFile objectListAndOffsets_url -- remove file if it exists from previous prefab export
			catch
			(
				messagebox ("Unable to delete previous object list. \nPlease manually remove file " + objectListAndOffsets_url as string)
				global failing = true
			)
			objectListAndOffsets = createFile objectListAndOffsets_url
			objectListAndOffsets = openFile objectListAndOffsets_url mode:"a"	-- file used to save out group offsets for export.
			
			totalLayers = LayerManager.count - 1	-- because we start with layer 0 not 1
			if totalLayers >= 2 then -- Cannot export from default layer
			(
				for i = 0 to totalLayers do					
				(					
					layerName = (LayerManager.getLayer i).name --gives access to layer properties
					if (matchpattern layerName pattern:("*" + MODEL_LAYER_SUFFIX)) or (matchpattern layerName pattern:("*" + SHELL_LAYER_SUFFIX)) then
					(						
						deselect selection
						currentLayer = layerManager.getLayer i
						objectArray = #()
						currentLayer.select true
						
						for obj in selection do -- only select unhidden objects geometry class objects -- THIS DOESNT WORK.
						(
							if (obj.isNodeHidden == false and superClassOf obj == GeometryClass) do
							(
								append objectArray obj
							)
						)	
						
						if objectArray.count == 0 then -- Checking for empty layers
						(
							if i != 0 do
							(
								layerName = (LayerManager.getLayer i).name --gives access to layer properties
								messagebox ("An empty layer " + layerName + " was found, nothing exported for this layer")
							)
						)
						else -- > 1 layer. Objects selected
						(
							if i == 0 then -- default (0) layer should have nothing in it, dont want warning for that layer
							(
								messagebox ("Objects were found on default layer 0, these objects were ignored. \nPlease read the content creation manual or the Aditional Help on BigWorld Maxscripts")
							)
							else -- there are > 1 layer; > 1 objects; and its not layer 0. 
							(
								layerName = (LayerManager.getLayer i).name --gives access to layer properties
								
								if matchpattern layerName pattern:("*" + MODEL_LAYER_SUFFIX) then
								(										
									export_url = exportModelLocation + "\\" + layerName + ".visual"									
								)
								else if matchpattern layerName pattern:("*" + SHELL_LAYER_SUFFIX) then
								(
									export_url = exportShellLocation + "\\" + layerName + ".visual"
								)
								
								model_url = substituteString export_url ".visual" ".model"
								
								-- for writing to .prefab file
								-- Strip out all url before "\res\" because path is relative to paths.xml path
								relativeStartPos = (findString model_url "\\res\\" + 5)
								relativePathModel_url = substring model_url relativeStartPos -1
								relativePathModel_url = substituteString relativePathModel_url "\\" "/" -- swap \ for /
								format (relativePathModel_url + "\n") to: objectListAndOffsets -- write name of layer to file list
								
								-- set each object in layer pivot to its min so that subsequent bounding box calculation is correct
								
								for obj in objectArray do
								(								
									obj.pivot = obj.min							
								)
								
								LayerMin = generateLayerBoundingBox objectArray objectListAndOffsets --  write out position, and bouding box min max for this layer
								
								-- Move the whole layer selection to the origin, relative to its position so that it has a handle within its bbox
								for obj in objectArray do
								(								
									newPos = obj.pos - LayerMin
									obj.pos = newPos
								)							
								exportFile export_url noPrompt:true selectedOnly:true							
							)
						)
					)
					else
					(
						messagebox ("A layer without either suffix \"_bw_model_layer\" or \"_bw_shell_layer\" was found. All objects on this layer will be ignored.")
					)
				)
			)
			else
			(
				messagebox ("There is only 1 (default) layer, this script requires individual models to be placed on layers.\nPlease read the content creation manual or the Aditional Help on BigWorld Maxscripts")
			)			
			close objectListAndOffsets
		)
		
		label label1 "Exports each layer to a separate model file,"
		label label2 "and then assembles the models as a prefab"
		
		group "Export models to:"
		(
			label label4 "Export location must be defined in paths.xml"
			button chooseModelExportPath "Choose Export Path" width:240 height:30 enabled:true
		)	
		
		group "Export shells to:"
		(
			label label5 "Export location must be a subfolder of \"shells\""
			label label6 "Export location must be defined in paths.xml"
			button chooseShellExportPath "Choose Export Path" width:240 height:30 enabled:true
		)
		
		group "Save prefab file to:"
		(
			label label7 "Prefab should be saved to a location defined in paths.xml"
			button prefabName "Save Prefab file" width:240 height:30 enabled:true
		)		
		
		button beginExport "Export (Warning: Please save first)" width:240 height:40 enabled:false
		
		-- Get the model export location
		on chooseModelExportPath pressed do 
		(
			exportModelLocation = getSavePath caption:"Choose location to export models" initialDir: (getDir #export)
			if exportModelLocation != undefined then
			(
				chooseModelExportPath.text=exportModelLocation
				enableExportButtonSwitch1 = true
				if ((enableExportButtonSwitch1 == true or enableExportButtonSwitch2 == true) and enableExportButtonSwitch3 == true) do beginExport.enabled=true
			)
			else
			(
				-- Debug do nothing
			)
		)
		
		-- Get the shell export location
		on chooseShellExportPath pressed do 
		(
			exportShellLocation = getSavePath caption:"Choose location to export models" initialDir: (getDir #export)
			if exportShellLocation != undefined then
			(
				chooseShellExportPath.text=exportShellLocation
				enableExportButtonSwitch2 = true
				if ((enableExportButtonSwitch1 == true or enableExportButtonSwitch2 == true) and enableExportButtonSwitch3 == true) do beginExport.enabled=true
			)
			else
			(
				-- Debug do nothing
			)
		)		
		
		-- Get the prefab name and location 
		on prefabName pressed do
		(				
			prefab_url = getSaveFileName caption:"Save prefab file to: " filename:((getDir #export) + "/") types:"Prefab(*.prefab)"
			if prefab_url != undefined then
			(
				if not matchPattern prefab_url pattern:"*.prefab" do -- the save dialog sometimes returns non .prefab suffixed paths/file
				(
					tempName = prefab_url
					prefab_url = tempName + ".prefab"
				)
				enableExportButtonSwitch3 = true -- enable export switch
				prefabName.text = prefab_url
				if ((enableExportButtonSwitch1 == true or enableExportButtonSwitch2 == true) and enableExportButtonSwitch3 == true) do beginExport.enabled=true
			)
			else
			(
				messagebox "No prefab location chosen"
			)
		)
		
		-- Test if model, shell url are set when appropriate layers are present
		on beginExport pressed do
		(		
			totalLayers = LayerManager.count - 1	-- because we start with layer 0 not 1
			for i = 0 to totalLayers do
			(
				layerName = (LayerManager.getLayer i).name				
				if (matchpattern layerName pattern:("*" + MODEL_LAYER_SUFFIX + "*") and (exportModelLocation == undefined)) then
				(					
					failing = true
				)
				if (matchpattern layerName pattern:("*" + SHELL_LAYER_SUFFIX + "*") and (exportShellLocation == undefined)) then 
				(				
					failing = true
				)
			)
			if failing == true then
			(
				messagebox "Field \"export models to:\" or \"export shells to:\" is not defined"
			)
			
			-- Ensure that the shells are going into a shells directory
			if exportShellLocation != undefined do
			(
				if findString exportShellLocation "\\shells" == undefined do -- exporting to a shells directory. 
				(
					messagebox "Shells must be exported to a \"shells\" folder"
					failing = true
				)
			)
			
			if failing == false do
			(	
				onlyUnhiddenGeo = #()				
				for obj in objects do -- Create an array of unhidden geometryClass objects to calculate prefab bounding box with.
				(
					if obj.isNodeHidden == false do
					(
						if superClassOf obj == GeometryClass do
						(
							append onlyUnhiddenGeo obj
						)
					)
				)
				
				generatePrefabBoundingBox onlyUnhiddenGeo
				
				exportAllSceneTo exportLocation
				
				WriteXML prefab_url cleanAllBBoxMinString cleanAllBBoxMaxString
			)
			
			if failing == true then
			(
				messagebox "Errors were encountered along the way"
				destroydialog BigWorldPrefabAssembler
			)
			else
			(
				messagebox "Export and Prefab generation complete"
				destroydialog BigWorldPrefabAssembler
			)
		)			
	)
	createdialog BigWorldPrefabAssembler
)
