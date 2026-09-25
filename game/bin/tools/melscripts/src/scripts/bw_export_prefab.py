# Export Prefab
import maya.cmds as cmds
import bw_common as bwcommon
from xml.dom.minidom import Document

MODEL_LAYER_SUFFIX = "_bw_model_layer"
SHELL_LAYER_SUFFIX = "_bw_shell_layer"
	
objectAndOffsetsList = []

#--------------------------------------------------
# Main Window
#--------------------------------------------------
def exportPrefabUI():
	global exportPrefabWin
	doesExist = cmds.window( 'exportPrefabWin', exists=True )
	if doesExist == False:
		exportPrefabWin = cmds.window( title="Export Prefab", width = 100, height = 100 )
		addUIWidgets()
	cmds.showWindow( exportPrefabWin )

#--------------------------------------------------
# Adds a slider and a button to the window
#--------------------------------------------------
def addUIWidgets():
	global exportShellsCB
	global prefabUrl
	global modelUrl
	global shellUrl
	prefabUrl = None
	modelUrl = None
	shellUrl = None
	cmds.columnLayout()
	cmds.iconTextButton( style='textOnly', label='Choose the location of your prefab file:' )
	cmds.button( label="Choose Prefab File Location", command="bw_export_prefab.getPrefabUrl()" )
	cmds.iconTextButton( style='textOnly', label='Choose the location of your Visual files (if applicable):' )
	cmds.button( label='Choose Models Export Location', command= "bw_export_prefab.getModelUrl()" )
	cmds.iconTextButton( style='textOnly', label='Choose the location of your Shell files (if applicable):' )
	cmds.button( label='Choose Shell Export Location', command= "bw_export_prefab.getShellUrl()" )
	cmds.button( label='Begin Export', command="bw_export_prefab.begin()" )
	cmds.button( label='Close', command=('cmds.deleteUI(\"' + exportPrefabWin + '\", window=True)') )

#--------------------------------------------------
# Gets the desired location of the Model File from User
#--------------------------------------------------
def getModelUrl():
	global modelUrl
	modelUrl = cmds.fileDialog2( fileFilter="Visual Files (*.visual)", dir=bwResPath, cap="Export BigWorld Asset to:", dialogStyle=2 )
	 
#--------------------------------------------------
# Gets the desired location of the Shell File from User
#--------------------------------------------------
def getShellUrl():
	global shellUrl
	shellUrl = cmds.fileDialog2( fileFilter="Visual Files (*.visual)", dir=bwResPath, cap="Export BigWorld Asset to:", dialogStyle=2 )
	 
#--------------------------------------------------
# Gets the location of the Prefab File from User
#--------------------------------------------------
def getPrefabUrl():
	global prefabUrl
	global prefabUrlFileExt
	prefabUrl = cmds.fileDialog2( fileFilter="Prefab (*.prefab)", dir=bwResPath, cap="Export prefab file to:", dialogStyle=2 )
	prefabUrlString = prefabUrl[0]
	prefabUrlFileExt = prefabUrlString[(prefabUrlString.rfind( "/" ) + 1):]

#--------------------------------------------------
# Main function, begin export
#--------------------------------------------------
def begin():
	global prefabBoundingBox
	global exportShells
	global exportModels
	global modelUrlPath
	global modelUrlFile
	global shellUrlPath
	global shellUrlFile
	exportShells = False
	exportModels = False
	failing = True	
	
	# Ensure appropriate fields are filled out
	if prefabUrl != None:
		if modelUrl != None:
			exportModels = True
		if shellUrl != None:
			if shellUrl[0].find( "shells" ) == -1:
				cmds.confirmDialog( title='Exporting Shells to non shell folder!', message="Shells can only be exported to folder or subfolder named \"shells\"", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
			else:
				exportShells = True
		if exportModels or exportShells == True:
			#everything is ready
			failing = False
		else:
			cmds.confirmDialog( title='Export Location Undefined!', message="Please choose the location to export the models, or shells", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
	else:
		cmds.confirmDialog( title='Prefab File Location Undefined!', message="Please choose the location to create the Prefab file", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
	
	# Test if there are Layers with appropriate names (MODEL_LAYER_SUFFIX, SHELL_LAYER_SUFFIX)
	layers = cmds.ls( long=True, type='displayLayer' )
	if len( layers ) >= 1:
		for layer in layers[1:]:
			if (MODEL_LAYER_SUFFIX in layer) or (SHELL_LAYER_SUFFIX in layer):
				failing = False    	
	else:
		cmds.confirmDialog( title='There was nothing to export!', message="Please ensure you have your models on layers with suffix \"_bw_model_layer\",\nshells on layers with \"_bw_shell_layer\",\nand the appropriate export location chosen.", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )            	
		failing = True
	
	# Everything filled out correctly - Go	
	if failing == False:
		if exportModels == True:
			modelUrlString = modelUrl[0]
			modelUrlPath = modelUrlString[0:(modelUrlString.rfind( "/" ) + 1)]
			modelUrlFileExt = modelUrlString[(modelUrlString.rfind( "/" ) + 1):]
			modelUrlFile = modelUrlFileExt[0:(modelUrlFileExt.rfind( "." ))]
		if exportShells == True:
			shellUrlString = shellUrl[0]
			shellUrlPath = shellUrlString[0:(shellUrlString.rfind( "/" ) + 1)]
			shellUrlFileExt = shellUrlString[(shellUrlString.rfind( "/" ) + 1):]
			shellUrlFile = shellUrlFileExt[0:(shellUrlFileExt.rfind( "." ))]
			
		#Generate the bounding box for the entire prefab (all objects)
		prefabBoundingBox = generatePrefabBoundingBox()
		
		#Export Each layer and Add its name and bounding boxes to a List
		exportAllSceneTo() # Passing in the model URL and File Name so that it can be joined with layer name for the model name

#--------------------------------------------------
# Calculates BoundingBox for entire Prefab
#--------------------------------------------------
def generatePrefabBoundingBox():
	global bwCoordsPrefabBoundingBox
	#Select all mesh objects on shell or model layers
	layers = cmds.ls( long=True, type='displayLayer' )
	cmds.select( deselect=True )
	for layer in layers:
		if (MODEL_LAYER_SUFFIX in layer) or (SHELL_LAYER_SUFFIX in layer):
			nodesInLayer = cmds.editDisplayLayerMembers( layer, query=True )
			for node in nodesInLayer:
				cmds.select( node, add=True )
				
	allLayerObjects = cmds.ls( selection=True )
	allPolyLayerObjects = cmds.filterExpand( allLayerObjects, selectionMask=12 ) # Only select mesh type nodes
	
	#Create combiner object for prefab boundingbox calculation	
	combinerCreated = False
	deleteDuplicate = False
	for node in allPolyLayerObjects:
		if combinerCreated == True:
			tmpObj = cmds.duplicate( node, returnRootsOnly = True, name='TempObj' )
			cmds.select( tmpObj, r=True )
			cmds.select( tmpPrefabObjCombiner, tgl=True )
			tmpPrefabObjCombiner = cmds.rename( tmpPrefabObjCombiner, 'deleteMe' )
			tmpPrefabObjCombiner = cmds.polyUnite( tmpObj, tmpPrefabObjCombiner, ch=0, name="PrefabObjCombiner" )
			deleteDuplicate = True
			try: # Deleting a non existing node causes script break
				cmds.delete( 'TempObj' )
			except:
				pass
		else:
			tmpPrefabObjCombiner = cmds.duplicate( node, returnRootsOnly = True, name='PrefabObjCombiner' )
			combinerCreated = True
			
		if deleteDuplicate == True:
			try:
				cmds.delete( 'deleteMe' )
			except:
				pass
			
	# Calculate bounding box for entire prefab in maya coords
	prefabBoundingBox = list( cmds.polyEvaluate( tmpPrefabObjCombiner, boundingBox=True ) )
	prefabBoundingBox[0] = list( prefabBoundingBox[0] )
	prefabBoundingBox[1] = list( prefabBoundingBox[1] )
	prefabBoundingBox[2] = list( prefabBoundingBox[2] )
	try:
		cmds.delete( 'PrefabObjCombiner' )
	except:
		pass
	
	# Create a copy of the Prefab Bounding Box in BigWorld Coords (Z flipped)
	bwCoordsPrefabBoundingBox = bwcommon.convertCoordinateToBW( prefabBoundingBox )
	
	return prefabBoundingBox
  
#--------------------------------------------------
# Exporting each Layer as a single model
#--------------------------------------------------	
def exportAllSceneTo():
	global objectAndOffsetsList
	somethingExported = False
	failing = False
	objectAndOffsetsList = []
	# Get all objects on a layer
	layers = cmds.ls( long=True, type='displayLayer' )
	for layer in layers:
		if failing == False:
			if (MODEL_LAYER_SUFFIX in layer and exportModels == True) or (SHELL_LAYER_SUFFIX in layer and exportShells == True):
				somethingExported = True # This tests to ensure that something is exported. You can have modelSuffix layers and no modelUrl
				nodesInLayer = cmds.editDisplayLayerMembers( layer, query=True )
				allPolyLayerObjects = cmds.filterExpand( nodesInLayer, selectionMask=12 ) # Filter the list for mesh objects
				if allPolyLayerObjects != None: # Check that the layer is not empty
					# Find the export directory for this layer
					if MODEL_LAYER_SUFFIX in layer:
						resUrlPathFileLayer = modelUrlPath + modelUrlFile + "_" + layer + ".model"
					if SHELL_LAYER_SUFFIX in layer:
						resUrlPathFileLayer = shellUrlPath + shellUrlFile + "_" + layer + ".model"
					relativeResUrlPathFileLayer = resUrlPathFileLayer[resUrlPathFileLayer.rfind( "/res/" ) + 5:]
					
					# Generate the bounding box for the layer. Put info into list
					generateLayerBoundingBox( allPolyLayerObjects, relativeResUrlPathFileLayer )
					
					# Select everything on layer
					cmds.select( deselect=True )
					for node in allPolyLayerObjects:
						cmds.select( node, add=True )
						
					#Export each layer
					try:
						cmds.file( (bwResPath + "/" + relativeResUrlPathFileLayer), force=True, options="", type="BigWorldAsset", pr=True, exportSelected=True )
					except:
						cmds.confirmDialog( title='Exporters not installed!', message="Please refer to the content tools reference guide for exporter installation instructions", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
						failing = True
	
	if somethingExported == True: # Write the prefab file
		writeXML( prefabUrl, bwCoordsPrefabBoundingBox ) #Since both prefabUrl and bwCoordsPrefabBoundingBox is global do I need to pass it in ?	
	else:
		cmds.confirmDialog( title='There was nothing to export!', message="Please ensure you have your models on layers with suffix \"_bw_model_layer\",\nshells on layers with \"_bw_shell_layer\",\nand the appropriate export location chosen.", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )            	
#---------------------------------------------------------------------------
# Calculates BoundingBox for entire layer and creates object and bb list
#---------------------------------------------------------------------------
def generateLayerBoundingBox( allPolyLayerObjects, relativeResUrlPathFileLayer ):
	global objectAndOffsetsList
		
	#Create the combined Object to get BoundingBox for layer
	layerCombinerCreated = False
	deleteLayerDuplicate = False
	for node in allPolyLayerObjects:
		if layerCombinerCreated == True:
			tmpLayerObj = cmds.duplicate( node, returnRootsOnly = True, name = 'TempLayerObj' )
			cmds.select( tmpLayerObj, r=True )
			cmds.select( tmpLayerObjCombiner, tgl=True )
			tmpLayerObjCombiner = cmds.rename( tmpLayerObjCombiner, "LayerObjCombiner_deleteMe" )
			tmpLayerObjCombiner = cmds.polyUnite( tmpLayerObj, tmpLayerObjCombiner, ch=0, name="LayerObjCombiner" )
			deleteLayerDuplicate = True
			try:
				cmds.delete( 'TempLayerObj' )
			except:
				pass
		else:
			tmpLayerObjCombiner = cmds.duplicate( node, returnRootsOnly = True, n="LayerObjCombiner" ) #Duplicate the object to create the initial object combiner.
			layerCombinerCreated = True
		
		# Delete one of the Layer object combiners. 
		if deleteLayerDuplicate == True:
			try:
				cmds.delete( 'LayerObjCombiner_deleteMe' )
			except:
				pass
	
	# Determine its local boundingbox (used for shells only), make mutable
	worldLayerBoundingBox = list( cmds.polyEvaluate(tmpLayerObjCombiner, boundingBox=True) )
	worldLayerBoundingBox[0] = list( worldLayerBoundingBox[0] )
	worldLayerBoundingBox[1] = list( worldLayerBoundingBox[1] )
	worldLayerBoundingBox[2] = list( worldLayerBoundingBox[2] )	
	
	bwCoordWorldLayerBoundingBox = bwcommon.convertCoordinateToBW( worldLayerBoundingBox )
	
	# Set the tempLayerObjCombiner objects pivot to its BBMin, This is the position of the layer (object) relative to the prefab.
	# It is used as the offset position and will also be the layer(objects) Min BB (BB in prefab is local to the prefab).
	cmds.move( worldLayerBoundingBox[0][0],worldLayerBoundingBox[1][0],worldLayerBoundingBox[2][0], tmpLayerObjCombiner[0]+'.scalePivot', tmpLayerObjCombiner[0]+'.rotatePivot', worldSpace=True )
	
	# Delete the final Layer object combiners.
	try:
		cmds.delete( "LayerObjCombiner" )
	except:
		pass
	
	#Set the pivots of all Objects to be at the min point of the Layers BoundingBox
	for node in allPolyLayerObjects:
		cmds.move( worldLayerBoundingBox[0][0],worldLayerBoundingBox[1][0],worldLayerBoundingBox[2][0], node+'.scalePivot', node+'.rotatePivot', worldSpace=True )
		cmds.move( 0,0,0, node, rotatePivotRelative=True )
	
	# Write the Layers Path and Min / Max bounding box to list
	objectAndOffsetsList.append( relativeResUrlPathFileLayer )
	
	# Append offset
	offsetX = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[0][0] )
	objectAndOffsetsList.append( offsetX )
	offsetY = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[1][0] )
	objectAndOffsetsList.append( offsetY )
	offsetZ = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[2][0] )
	objectAndOffsetsList.append( offsetZ )
	
	# Append layer (object) MinBB
	layerBoundingBoxMinX = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[0][0] )
	objectAndOffsetsList.append( layerBoundingBoxMinX )
	layerBoundingBoxMinY = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[1][0] )
	objectAndOffsetsList.append( layerBoundingBoxMinY )
	layerBoundingBoxMinZ = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[2][0] ) 
	objectAndOffsetsList.append( layerBoundingBoxMinZ )

	# Append layer (object) MinBB	
	layerBoundingBoxMaxX = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[0][1] )
	objectAndOffsetsList.append( layerBoundingBoxMaxX )
	layerBoundingBoxMaxY = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[1][1] )
	objectAndOffsetsList.append( layerBoundingBoxMaxY )
	layerBoundingBoxMaxZ = bwcommon.convertToMeters( bwCoordWorldLayerBoundingBox[2][1] )
	objectAndOffsetsList.append( layerBoundingBoxMaxZ )

def writeXML( prefabUrl, bwCoordsPrefabBoundingBox ):
	# Xml File location
	myfile = open( prefabUrl[0], 'w' )
	
	# Create the minidom document
	doc = Document()
	
	# Create the <creature_collider> root element
	root = doc.createElement( prefabUrlFileExt )
	doc.appendChild( root )
	
	# chunks tag
	chunks = doc.createElement( "chunks" )
	root.appendChild( chunks )
	
	# item tag
	items = doc.createElement( "items" )
	root.appendChild( items )
	
	# Calculate how many shells / objects there are. There are 10 elements for each object
	# name, ofsetx,y,z, bbMin, bbMax 
	numObjects = len( objectAndOffsetsList ) / 10
	
	chunk_i = 0
	object_index = 0
	for i in range( numObjects ):
		# exporting Shells
		if SHELL_LAYER_SUFFIX in objectAndOffsetsList[object_index]:
			# Add chunk0 to chunks
			tmpChunkNo = ( "chunk" + str( chunk_i ) + ".chunk" )
			chunkNo = doc.createElement( tmpChunkNo )
			chunks.appendChild( chunkNo )
			
			# Add shell to chunkNo
			shellTag = doc.createElement( "shell" )
			chunkNo.appendChild( shellTag )
			
			# EditorOnly tag to shellTag
			editorOnly = doc.createElement( "editorOnly" )
			shellTag.appendChild( editorOnly )
			
			# MetaData tag to shell Tag
			metaData = doc.createElement( "metaData" )
			shellTag.appendChild( metaData )
			
			# Resource tag, sets the location of the .model file
			resource = doc.createElement( "resource" )
			shellTag.appendChild( resource )
			
			# Text URL of the exported model files
			resourceText = doc.createTextNode( objectAndOffsetsList[object_index] )
			resource.appendChild( resourceText )
			
			# Transform tag
			transformTag = doc.createElement( "transform" )
			shellTag.appendChild( transformTag )
			#the children of this tag are outside this if
			
			# ReflectionVisible tag
			reflectionVisible = doc.createElement( "reflectionVisible" )
			shellTag.appendChild( reflectionVisible )
			
			# ReflectionVisible tag text
			reflectionVisibleText = doc.createTextNode( "false" ) 
			reflectionVisible.appendChild( reflectionVisibleText )
			
			# Prefab transform tag
			prefabTransform = doc.createElement( "transform" )
			chunkNo.appendChild( prefabTransform )
			# The Children of prefab transform tag are outside this if
			
			# shell boundingBox tag
			boundingBoxTag = doc.createElement( "boundingBox" )
			chunkNo.appendChild( boundingBoxTag )
			
			# Min tag
			minTag = doc.createElement( "min" )
			boundingBoxTag.appendChild( minTag )
			
			# Min tag text
			minTagText = doc.createTextNode( str( objectAndOffsetsList[object_index + 4] ) + " " + str( objectAndOffsetsList[object_index + 6] ) + " " + str( objectAndOffsetsList[object_index + 8] ) )
			minTag.appendChild( minTagText )
			
			# Max tag
			maxTag = doc.createElement( "max" )
			boundingBoxTag.appendChild( maxTag )
			
			#Max tag text
			maxTagText = doc.createTextNode( str( objectAndOffsetsList[object_index + 5] ) + " " + str( objectAndOffsetsList[object_index + 7] ) + " " + str( objectAndOffsetsList[object_index + 9] ) )
			maxTag.appendChild( maxTagText )
			
		elif MODEL_LAYER_SUFFIX in objectAndOffsetsList[object_index]:
			# Note, <items> (non shells ) do not use the boundingbox information
			# model tag
			model = doc.createElement( "model" )
			items.appendChild( model )
			
			# editorOnly tag
			editorOnly = doc.createElement( "editorOnly" )
			model.appendChild( editorOnly )
			
			# metaData tag
			metaData = doc.createElement( "metaData" )
			model.appendChild( metaData )
			
			# Resource tag, sets the location of the .model file
			resource = doc.createElement( "resource" )
			model.appendChild( resource )
			
			# Resource tag text
			resourceText = doc.createTextNode( objectAndOffsetsList[object_index] )
			resource.appendChild( resourceText )
			
			#transform tag
			transformTag = doc.createElement( "transform" )
			model.appendChild( transformTag )
			# The Children of transform tag are outside this if
			
			#reflectionVisible tag
			reflectionVisible = doc.createElement( "reflectionVisible" )
			model.appendChild( reflectionVisible )
			
			#reflectionVisible Text tag
			reflectionVisibleText = doc.createTextNode( "false" )
			reflectionVisible.appendChild( reflectionVisibleText )
			
			#prefab transform tag
			prefabTransform = doc.createElement( "prefabTransform" )
			model.appendChild( prefabTransform )
			# The Children of prefab transform tag are outside this if
		
		# Children of editorOnly
		# Hidden tag
		hidden = doc.createElement( "hidden" )
		editorOnly.appendChild( hidden )
		
		# Hitten text
		hiddenText = doc.createTextNode( "false" )
		hidden.appendChild( hiddenText )
		
		# Frozen tag
		frozen = doc.createElement( "frozen" )
		editorOnly.appendChild( frozen )
		
		# Frozen text
		frozenText = doc.createTextNode( "false" )
		frozen.appendChild( frozenText )
		
		# castShadow tag
		castShadow = doc.createElement( "castShadow" )
		editorOnly.appendChild( castShadow )
		
		# castShadow text  
		castShadowText = doc.createTextNode( "true" )
		castShadow.appendChild( castShadowText )
		
		# Children of transformTag
		# transform rows
		row0 = doc.createElement( "row0" )
		transformTag.appendChild( row0 )
		
		row0Text = doc.createTextNode( "1.000000 0.000000 0.000000" )
		row0.appendChild( row0Text )
		
		row1 = doc.createElement( "row1" )
		transformTag.appendChild( row1 )
		
		row1Text = doc.createTextNode( "0.000000 1.000000 0.000000" )
		row1.appendChild( row1Text )
		
		row2 = doc.createElement( "row2" )
		transformTag.appendChild( row2 )
		
		row2Text = doc.createTextNode( "0.000000 0.000000 1.000000" )
		row2.appendChild( row2Text )
		
		row3 = doc.createElement( "row3" )
		transformTag.appendChild( row3 )
		
		row3Text = doc.createTextNode( "0.000000 0.000000 0.000000" )
		row3.appendChild( row3Text )
		
		# Children of prefab transform tag
		# prefab transform rows
		row0 = doc.createElement( "row0" )
		prefabTransform.appendChild( row0 )
		
		row0Text = doc.createTextNode( "1.000000 0.000000 0.000000" )
		row0.appendChild( row0Text )
		
		row1 = doc.createElement( "row1" )
		prefabTransform.appendChild( row1 )
		
		row1Text = doc.createTextNode( "0.000000 1.000000 0.000000" )
		row1.appendChild( row1Text )
		
		row2 = doc.createElement( "row2" )
		prefabTransform.appendChild( row2 )
		
		row2Text = doc.createTextNode( "0.000000 0.000000 1.000000" )
		row2.appendChild( row2Text )
		
		row3 = doc.createElement( "row3" )
		prefabTransform.appendChild( row3 )
		
		row3Text = doc.createTextNode( str( objectAndOffsetsList[object_index + 1] ) + " " + str( objectAndOffsetsList[object_index + 2] ) + " " + str( objectAndOffsetsList[object_index + 3] ) )
		row3.appendChild( row3Text )
		
		# object_index
		object_index += 10
	
	# Common parameters for both <item> and <chunk> tags
	# boundingBox for entire prefab tag
	boundingBox = doc.createElement( "boundingBox" )
	root.appendChild( boundingBox )
	
	# min tag
	minTag = doc.createElement( "min" )
	boundingBox.appendChild( minTag )
	
	# min tag text
	minTagText = doc.createTextNode( str( bwCoordsPrefabBoundingBox[0][0] ) + " " + str( bwCoordsPrefabBoundingBox[1][0] ) + " " + str( bwCoordsPrefabBoundingBox[2][0] ) )
	minTag.appendChild( minTagText )
	
	# max tag
	maxTag = doc.createElement( "max" )
	boundingBox.appendChild( maxTag )
	
	# max tag text
	maxTagText = doc.createTextNode( str( bwCoordsPrefabBoundingBox[0][1] ) + " " + str( bwCoordsPrefabBoundingBox[1][1] ) + " " + str( bwCoordsPrefabBoundingBox[2][1] ) )
	maxTag.appendChild( maxTagText )
	
	# snaps tag
	snaps = doc.createElement( "snaps" )
	root.appendChild( snaps )
	
	# Children of snaps tag	
	# positionmin tag
	positionTag = doc.createElement( "position" )
	snaps.appendChild( positionTag )
	
	positionTagText = doc.createTextNode( "0.000000 0.000000 1.000000" )
	positionTag.appendChild( positionTagText )
	
	# angle tag
	angleTag = doc.createElement( "angle" )
	snaps.appendChild( angleTag )
	
	angleTagText = doc.createTextNode( "0.000000" )
	angleTag.appendChild( angleTagText )
	
	xmlString = doc.toprettyxml( indent="  " )
	
	#remove the xml version tag generated by minidom
	cleanXmlString = xmlString.lstrip( "<?xml version=\"1.0\" ?>" )
	cleanXmlString = cleanXmlString.lstrip( "\n" )
	myfile.write( cleanXmlString )
	
	#Close the file
	myfile.close()

# STARTS HERE
def main():
	global bwResPath # Has to be global because command 'string' wont pass it
	bwResPathExists = True
	bwResPath = cmds.workspace( fre="BigWorldAsset" )
	if len( bwResPath ) == 0:
		bwResPathExists = False
	if bwResPathExists == True:
		exportPrefabUI()
	else:
		cmds.confirmDialog( title='Project Location BigWorldAsset not defined!', message="Please refer to the content tools reference guide for instructions on how to set up the BigWorldAsset Project location", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
