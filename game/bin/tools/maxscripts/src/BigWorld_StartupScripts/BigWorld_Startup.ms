
	-- BigWorld Startup Scripts
	-- 
	-- Author: Adam Maxwell
	-- Website: http://www.bigworldtech.com
	-- Works on: MAX 2010/11
	--
	-- Description
	-- Search for and load BigWorld_MaterialLibrary.mat
	-- Define BigWorld_Batch_Export to be used with bigworld_batch_export.py script
	
global bw_hasSearchedMatLib	
-- Loads BW material library
if bw_hasSearchedMatLib == undefined then -- only ever load material library once
(
	if loadMaterialLibrary "BigWorld_MaterialLibrary.mat" == false then 
	(
		print "Did not find BigWorld Material Library"
	)
	else
	(
		print "Found BigWorld Material Library"
		bw_hasSearchedMatLib = true
	)
)

function WriteToLog text logfilestring =
(	
	logfilestream = openFile logfilestring mode:"a"
	format( text ) to: logfilestream
	close logfilestream
)

function BigWorld_Load_Export_WriteLog source_url dest_url logfilestring =
(	
	loadMaxFile source_url quiet:true useFileUnits:true
	-- Testing output value of exportFile
	numSelected = 0
	for i in selection do
	(
		numSelected += 1
	)
	if numSelected >= 1 then --Objects selected due to file open persistant callback scripts
	(
		if (exportFile dest_url #noPrompt selectedOnly:true) == true then
		(
			WriteToLog ("SUCCESSFULLY exported " + source_url + " to: " + dest_url + "\n\n") logfilestring
		)
		else
		(
			WriteToLog ("FAILED to export " + source_url + " to: " + dest_url + "\n\n") logfilestring
		)
	)
	else -- Nothing selected
	(
		if (exportFile dest_url #noPrompt) == true then
		(
			WriteToLog ("SUCCESSFULLY exported " + source_url + " to: " + dest_url + "\n\n" ) logfilestring
		)
		else
		(
			WriteToLog ("FAILED to export " + source_url + " to: " + dest_url + "\n\n") logfilestring
		)
	)
)

function Set_BigWorld_Setting bwFolderLocation =
(
	while (mapPaths.count() > 0) do
	(
		mapPaths.delete 1;
	)
	
	bwShaderLocation = bwFolderLocation + "\\res\\bigworld\\shaders\std_effects"
	bwHelperMaps = bwFolderLocation + "\\bin\\tools\\maxscripts\\src\helper_maps"
	bwMaterialLibraries = bwFolderLocation + "\\bin\\tools\\maxscripts\\src\materiallibraries"
	
	mapPaths.add bwShaderLocation
	mapPaths.add bwHelperMaps
	mapPaths.add bwMaterialLibraries
	
	local bwExportFolderVer = ""
	local maxVersionNumber
	
	maxVersionNumber = (maxVersion())[1]
	
	-- Convert maxVersion number to a meaningful number and pad it with zeros
	maxVersionNumberConverted = ((maxVersionNumber/1000) - 2)
	maxVersionNumberConverted = formattedPrint maxVersionNumberConverted format:"02d" as string
	
	bwExportFolderVer = ("\3dsmax20" + maxVersionNumberConverted)
	
	if is64bitApplication() then
	(
		bwExportFolderVer = bwExportFolderVer + "x64"
	)
	
	bwExporterLocation = bwFolderLocation + "\\bin\\tools\\exporter" + bwExportFolderVer
	pluginIniLoc = getDir #maxData + "Plugin.UserSettings.ini"
	
	setINISetting pluginIniLoc "Directories" "BigWorld" bwExporterLocation
)

function BigWorld_Batch_Export maxfileList overw logfilestring projectFolder =
(
	-- set the tests folder as a working directory in 3dsmax
	pathConfig.setCurrentProjectFolder projectFolder
	
	local f = openFile maxfileList mode:"r"
	while not eof f do 
	(
		source_url = readLine f
		dest_url = readLine f
		WriteToLog( dest_url + "\n") logfilestring
		if overw == 1 then --overwrite is true
		(
			if doesFileExist dest_url == true then
			(
				if deleteFile dest_url == true then -- Can't force an export overwrite without a prompt, have to delete file
				(
					BigWorld_Load_Export_WriteLog source_url dest_url logfilestring
				)
				else
				(
					WriteToLog ("FAILED to export " + source_url + " to: " + dest_url + " because ") logfilestring
					WriteToLog (dest_url + " could not be deleted \n\n") logfilestring
				)
			)
			else -- file doesnt exist
			(
				BigWorld_Load_Export_WriteLog source_url dest_url logfilestring
			)
		)
		else -- overwrite is false
		(
			if doesFileExist dest_url then
			(
				WriteToLog ("FAILED to export " + source_url + " to: " + dest_url + " because\n") logfilestring
				WriteToLog (dest_url + " already exists\n\n") logfilestring
			)
			else
			(
				BigWorld_Load_Export_WriteLog source_url dest_url logfilestring
			)
		)
		resetMaxFile #noPrompt
	)
	close f
)