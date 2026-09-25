-- BigWorld Common Functions

global bwCleanPath
fn bwCleanPath pathToClean = (
	pathToClean = pathConfig.normalizePath pathToClean
	pathToClean = pathConfig.convertPathToAbsolute pathToClean
	pathToClean = pathConfig.convertPathToLowerCase pathToClean				
	pathToClean = substituteString pathToClean "\\" "/"
	return pathToClean
)

-- NO LONGER WORKS AFTER DIRECTORY RESTRUCTURE, THERE IS NO BIGWORLD FOLDER
global bigWorldFolderDir
fn bigWorldFolderDir pluginPath = (	
	bwLoc = findString pluginPath "bigworld"	
	if bwLoc != undefined then (
		bwLoc -= 1
		bwDir = substring pluginPath 1 bwLoc
	) 
	else (
		bwDir = "" -- cannot pass undefined to getSavePath initialDir
	)
	return bwDir
)

global bigWorldResDir
fn bigWorldResDir pluginPath = (	
	-- pluginPath is "D:\adamm_perforce_workspace\2.current\game\bin\tools\exporter\3dsmax2013x64"
	-- there has to be a string crimp method somewhere.
	
	lengthOfString = pluginPath.count
	locationBinFolder = findstring pluginPath "\bin"
	remainingLength = (lengthOfString - locationBinFolder) + 1
	s1 = replace pluginPath locationBinFolder remainingLength ""
	resDir = s1 + "\\res"
	
	if resDir != undefined then (
	) 
	else (
		resDir = "" -- cannot pass undefined to getSavePath initialDir
	)
	return resDir
)

-- "tools" string should be stable between projects
global bwToolsFolderDir
fn bwToolsFolderDir pluginPath = (
	toolsLoc = findString pluginPath "tools"	
	if toolsLoc != undefined then (
		toolsLoc -= 1
		toolsDir = substring pluginPath 1 toolsLoc
	) 
	else (
		toolsDir = "" -- cannot pass undefined to getSavePath initialDir
	)
	return toolsDir
)

function convertCoordinateToBW maxCoordinate =
(
	ty = maxCoordinate[2]
	tz = maxCoordinate[3]
	maxCoordinate[3] = ty
	maxCoordinate[2] = tz
	bwCoordinate = maxCoordinate
	return bwCoordinate
)

fn convertToMeters inputToScale = 
(
	unitScale = units.SystemScale
	unitTypeScale = case units.SystemType of 
	(
		#Inches: 0.0254
		#Feet: 0.3048
		#Miles: 1609.344
		#Millimeters: 0.001
		#Centimeters: 0.01 
		#Meters: 1
		#Kilometers: 1000
	)
	scaleFactor = unitScale * unitTypeScale
	return inputToScale * scaleFactor
)

function cleanUpForPrinting dirtyString =
(
	cleanString = substituteString dirtyString "\"" "" -- remove quotes, does nothing
	cleanString = substituteString cleanString "[" ""
	cleanString = substituteString cleanString "]" ""
	cleanString = substituteString cleanString "," " "
	return cleanString
)

function IsPlanar selectedObject =
(	
	-- Description:
	-- Tests if an objects verts are coplanar by
	-- Create array of verts, Use vert 1 and every other vert to create an array of edges
	-- Cross product of edge 1 and i normalized then compared with each other, if same then planar
	-- Note: discards verts too close together, discards edge vectors that are the normalized same
	
	global AngleDivergence = 0.98 -- filter tolerance angle between two edges (1 = same edge, 0 = perpendicular edge, i.e 1 is more sensitive)
	global VertTolerance = 0.01 -- filter tolerence distance between verts
	global VertThreshold = 15 -- maximum number of verts in object before prompt continue
	global filteringUsed = false -- switched if vert tolerance or edge tolerance is used
	
	global vertCount
	global hasSearchedMatLib -- was persistent
	global vertArray = #()
	global filteredVertArray = #()
	global edgeArray = #()
	global normalArray = #()
	global filteredEdgeArray = #()
	bwMacroScriptsPath = (pathConfig.GetDir #usermacros)
	
	if superClassOf selectedObject == GeometryClass then
	(
		----------------------------
		--------Vert Array-------
		----------------------------
		
		for vertEx in selectedObject.mesh.verts do 
		(
			append vertArray vertEx.pos
		)
		
		-- Vert number threshold
		vertCountOK = true
		if vertArray.count > VertThreshold then
		(
			vertCountOK = querybox (selectedObject.name + " contains more than the usual number of vertices for a typical portal.\nAre you sure you want to continue?")
		)
		
		if vertCountOK == true then
		(
			------------------------------------
			--Remove verts close to vert 1--
			------------------------------------
			
			vertArrayLength = vertArray.count
			append filteredVertArray vertArray[1] -- we are comparing everything to vertArray[1], it cannot be filtered out
			for i = 2 to vertArrayLength do 
			(
				if length (vertArray[1] - vertArray[i]) > VertTolerance then
				(
					append filteredVertArray vertArray[i]
				)
				else
				(
					filteringUsed = true 
				)
			)
			
			-----------------------------
			--CREATE EDGE ARRAY--
			-----------------------------
		
			-- Create array of edge vectors
			vertArrayLength = filteredVertArray.count
			for i = 2 to vertArrayLength do 
			(
				newEdge = filteredVertArray[i] - filteredVertArray[1]
				append edgeArray newEdge
			)
			
			-------------------------------------
			--CREATE Filtered Edge Array --
			-------------------------------------
			
			edgeArrayLength = edgeArray.count
			append filteredEdgeArray edgeArray[1] -- not filtering 1, because all others are compared to 1
			
			for i = 2 to edgeArrayLength do 
			(
				-- Discard same vector edges by dot prodcut. if the dot product is ~ 1 then the angle between them is 0
				norm_1 = normalize(edgeArray[1])
				norm_i = normalize(edgeArray[i])
				if dot norm_1 norm_i > AngleDivergence then
				(
					-- print "An edge was filtered"
				)
				else
				(
					append filteredEdgeArray edgeArray[i]
				)
			)
			
			-------------------------------------
			--CREATE NormCROSS ARRAY--
			-------------------------------------
			
			filteredEdgeArrayLength = filteredEdgeArray.count
			for i = 2 to filteredEdgeArrayLength do
			(
				crossProd = cross filteredEdgeArray[1] filteredEdgeArray[i]
				newNormalVector = normalize crossProd
				append normalArray newNormalVector
			)
			
			-----------------------------
			--Compare Normal Array--
			-----------------------------
			
			normalArrayLength = NormalArray.count
			for i = 2 to normalArrayLength do
			(
				if normalArray[1] != normalArray[i] do
				(
					failCase = "Not planar"
					return failCase 
				)
			)
			if filteringUsed == true do
			(
				messagebox "Some vertices were ignored during coplanar testing because they were too close to each other, portal may fail"
			)
			failCase = "Is planar"
			return failCase
		)
		else -- vertCount OK
		(
			failCase = "Too many verts"
			return failCase
		)
	)
	else -- Is geometry
	(
		failCase = "Not geometry"
		return failCase
	)	
)

-- Should try to run this before the export visual script to test for installed exporters
-- APPEARS TO WORK AFTER DIRECTORY RESTRUCTURE
global bwGetVisualPluginPath
fn bwGetVisualPluginPath =
(
	if ((maxVersion())[1] < 12000 ) then -- before max 2010 plugin paths were stored in plugin.ini in User Appdata
	(		
		pluginIniLoc = getDir #maxData + "Plugin.ini"	
	)
	else -- max 2010 or greater should write to plugin.UserSettings.ini in User Appdata
	(
		pluginIniLoc = getDir #maxData + "Plugin.UserSettings.ini"
	)	
	bwExporterLoc = getIniSetting pluginIniLoc "Directories" "BigWorld"	
	
	if bwExporterLoc == "" then
	(
		messagebox "No BigWorld path found in System Paths - 3rd Party Plugins. Please ensure plugins are correctly installed."
	)
	else
	(		
		print ("Found BigWorld Plugin Location " + bwExporterLoc as string)
	)
	return bwExporterLoc -- Returns something like "F:\adamm_perforce_workspace\2.current\bigworld\tools\exporter\3dsmax2013x64\"
)

global PathsXMLManager
struct PathsXMLManager (
	--dotnet.loadAssembly "system.xml.dll",
	xmlDoc=dotNetObject "system.xml.xmlDocument",
	paths = #(),
	pathsXML = "",
	pathsXMLDir = "",
	dirty = False,
	fn onCreate = (
		
		if doesFileExist this.pathsXML then 
		(
			--Load the XML File
			this.xmlDoc.load this.pathsXML
			--Check for root element
			docEle = this.xmlDoc.documentElement
			
			-- if root exists then continue
			if docEle!=undefined and docEle.name == "root" then
			(
				--recurseXML docEle
				this.recurseXML docEle
			)
		)
	),
	b = onCreate(),
	
	-- read in all XML elements
	fn recurseXml ele = (	
		for i = 0 to ele.childNodes.count-1 do
		(
			if ele.ChildNodes.itemOf[i].name == "Path" do (
				append this.paths ele.ChildNodes.itemOf[i].InnerText
			)			
			recurseXml ele.ChildNodes.itemOf[i]			
		)
	),
	
	fn getArrayOfPaths = (
		return this.paths
	),
	
	fn makePathAbs pathToConvert = (
		if pathConfig.isAbsolutePath pathToConvert then (
			-- Make sure that the path contains a disk drive. Default to same
			-- drive as the plugin if path starts with /.			
			if pathToConvert[1] == "\\" or pathToConvert[1] == "/" then	(
				pathToConvert = substring this.pathsXMLDir 1 3 + pathToConvert
			)
		)
		else ( -- relative path
			pathToConvert = pathConfig.convertPathToAbsolute (pathConfig.appendPath this.pathsXMLDir pathToConvert)
		)
		return (pathToConvert = substituteString pathToConvert "\\" "/")
	),
	
	fn makePathRel pathToConvert = (
		-- expects an absolute path
		relativeToPath = this.normAbsPath this.pathsXMLDir
		pathToConvert = pathConfig.convertPathToRelativeTo pathToConvert relativeToPath
		pathToConvert = substituteString pathToConvert "\\" "/"
		return pathToconvert		
	),
	
	fn normAbsPath pathToConvert = (
		pathToConvert = this.makePathAbs pathToconvert
		pathToConvert = pathConfig.convertPathToLowerCase pathToConvert
		pathToConvert = substituteString pathToConvert "\\" "/"
		return pathToConvert
	),
	
	fn getArrayOfAbsPaths = (
		-- return map(lambda x: self.normAbsPath(x), self.getArrayOfPaths())
		absPathArray = #()		
		for i in this.getArrayOfPaths() do	(
			x = this.normAbsPath i
			absPathArray = append absPathArray x
		)		
		return absPathArray
	),

	fn isPathUnique pathToTest = (
		tempAbsPathArray = this.getArrayOfAbsPaths()
		if (findItem tempAbsPathArray (this.normAbsPath pathToTest)) == 0 then (
			return true -- item IS unique
		)
		else(
			return false -- item is NOT unique
		)
	),
	
	fn addPath newPath = (
		if this.isPathUnique newPath then (
			append this.paths newPath
			this.dirty = True
		)
	),
	
	fn removePath pathToRem = (
		normPath = this.normAbsPath pathToRem
		numPaths = this.paths.count
		for i = 1 to numPaths do (
			normP = this.normAbsPath this.paths[i] -- this is meant to be the test path
			if normPath == normP do (
				this.paths = deleteItem this.paths i
				this.dirty = true
				exit
			)
		)
	),
	
	fn modifyPath oldPath newPath = (
		normOldPath = this.normAbsPath oldPath
		numPaths = this.paths.count
		for i = 1 to numPaths do (
			normP = this.normAbsPath this.paths[i]
			if normP == normOldPath do (
				this.paths[i] = newPath
				this.dirty = true
			)			
		)
	),
	
	fn toggleAbsRelPath pathToToggle = (
		normPath = this.normAbsPath pathToToggle
		numPaths = this.paths.count
		for i=1 to numPaths do (
			normP = this.normAbsPath this.paths[i]
			if normP == normPath then (
				if pathConfig.isAbsolutePath pathToToggle then (
					lowerNormPDrive = toLower normP[1]
					lowerXMLDirDrive = toLower this.pathsXMLDir[1] -- if its same drive
					if lowerNormPDrive == lowerXMLDirDrive then (
						this.paths[i] = this.makePathRel normPath
					)
					else (
						messagebox "Paths on different drives to the BigWorld visual plugin cannot be made relative." title:"Path on different drive"
					)					
				)
				else ( -- its relative, not absolute
					this.paths[i] = this.makePathAbs normPath
				)
				this.dirty = true 
			)
		)
	),
	
	fn dump = (
		print this.paths
		print this.pathsXML
		print pathsXMLDir
	),
	
	fn write = (
		if this.dirty == true then (
			-- Write Parent root Tag
			rootEle = this.xmlDoc.documentElement
			
			-- get the root of xmlDoc to clear it
			rootEle.RemoveAll()
			
			-- Write Paths tag
			pathsTag = this.xmlDoc.CreateElement "Paths"
			rootEle.AppendChild pathsTag
			
			for obj in this.paths do
			(
				-- Writing the Boxattachment tag
				pathTag = this.xmlDoc.CreateElement "Path"
				pathsTag.AppendChild pathTag
				
				-- Writing the path string				
				pathTag.InnerText = obj
			)
			
			-- clean it up for getFileAttribute function
			--cleanStringLiteralPath = substituteString this.pathsXML "\\" "\\\\"			
			
			-- does file exist is failing
			if doesFileExist this.pathsXML == false do (
				messagebox ("PathsXMLManager cannot find file\n" + this.pathsXML)
			)
				
			if getFileAttribute this.pathsXML #readOnly == true then (
				pathsIsReadOnly = true				
				messagebox "Cannot write to paths.xml. The file is read only." title:"Read only file"
			)
			else (
				pathsIsReadOnly = false
				this.xmlDoc.save this.pathsXML
				this.dirty = false
			)			
		)
		return pathsIsReadOnly
	)	
)