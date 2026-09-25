import os
import struct
import shutil
import time
ERROR = False
try:
	from PIL import Image
except ImportError:
	ERROR = True
	print "SpaceImageCreator: Import error, please install Python Imaging Library and try again"

# resolution of tile level n / resolution of tile level n - 1
TILE_DIVISION = 2

# min size for a tile in pixels
MIN_OUTPUT_IMG_SIZE = 512 

# final tile image quality
JPG_IMAGE_QUALITY = 75

#output folder name relative to space
OUTPUT_FOLDER_NAME = "tileset"

#temp folder name relative to space
TEMP_FOLDER_NAME = "temp"

# template for JSON metafile generated for/used by spaceviewer
JSON_TEMPLATE = """
{
	"dateGenerated": "%s",
	"tileSize": %d,
	"depth": %d,
	"worldBoundsOfRootTile": 
	{
		"minX": %d,
		"minY": %d,
		"maxX": %d,
		"maxY": %d
	},
	"worldBoundsOfSpaceGeometry": 
	{
		"minX": %d,
		"minY": %d,
		"maxX": %d,
		"maxY": %d
	}
}
"""


class PyProgressHandler:

	def __init__( self ):
		self.msg = ''
		self.steps = 0
		self.curStep = 0
	# __init__


	def print_progress( self ):
		if self.steps == 0:
			self.steps = 1
		progress = self.curStep * 100 / self.steps
		progressToDisplay = progress / 2
		dotText = '.' * progressToDisplay + ' ' * ( 50 - progressToDisplay )
		sys.stdout.write('%-50s%3d%%\r' % ('%s(%d/%d )%s' % ( self.msg,
		  self.curStep,
		  self.steps,
		  dotText ), progress ))
		sys.stdout.flush()
		if self.curStep >= self.steps:
			sys.stdout.write('\nFinished!\n')
	# print_progress


	def startProgress( self, msg, steps ):
		self.msg = msg
		self.steps = steps
		self.curStep = 0
		self.print_progress()
	# startProgress


	def progressStep( self, step ):
		self.curStep += step
		self.print_progress()
	# progressStep
	

	def stopProgress( self ):
		pass
	# stopProgress
	

	def isProgressCancelled( self ):
		pass
	# isProgressCancelled
	
# end class PyProgressHandler


if __name__ == '__main__':
	consoleMode = True
	progressMsgForSingleMap = 'Creating space map'
	progressMsgForLevelImages = 'Creating level images'
	pyProgressHandler = PyProgressHandler()
else:
	import WorldEditor
	import ResMgr
	consoleMode = False
	progressMsgForSingleMap = 'SCRIPT/PROGRESS_BAR_MSG/CREATING_SPACE_MAP'
	progressMsgForLevelImages = 'SCRIPT/PROGRESS_BAR_MSG/CREATING_LEVEL_IMAGES'
	pyProgressHandler = None


def isProgressCancelled():
	global consoleMode
	global pyProgressHandler
	if consoleMode:
		return pyProgressHandler.isProgressCancelled()
	WorldEditor.isProgressCancelled()
# isProgressCancelled


def progressStep( step ):
	if consoleMode:
		pyProgressHandler.progressStep( step )
	else:
		WorldEditor.progressStep( step )
# progressStep


def startProgress( msg, steps, needLocalization, canCancel ):
	if consoleMode:
		pyProgressHandler.startProgress( msg, steps )
	else:
		if needLocalization:
			msg = ResMgr.localise( msg )
		WorldEditor.startProgress( msg, steps, canCancel )
# startProgress


def stopProgress():
	if consoleMode:
		pyProgressHandler.stopProgress()
	else:
		WorldEditor.stopProgress()
# stopProgress


def mergeImage( imgList ):
	if len( imgList ) != ( TILE_DIVISION * TILE_DIVISION ):
		return None
	
	imgSize = None
	for img in imgList:
		if img != None:
			imgSize = img.size[0]
			break			
	if not imgSize:
		return None
		
	temp = imgSize
	minOutputImgSize = MIN_OUTPUT_IMG_SIZE
	while temp <= minOutputImgSize:
		temp = temp * TILE_DIVISION
	minOutputImgSize = temp
	
	mergeSize = ( imgSize * TILE_DIVISION, imgSize * TILE_DIVISION )
	thumbnailSize = mergeSize
	mergeImg = Image.new( 'RGB', mergeSize, 0 )	
	x = 0
	y = 0
	for img in imgList:
		if img != None:
			mergeImg.paste( img, ( x, y ) )
		if x + imgSize < mergeSize[0]:
			x += imgSize
		else:
			x = 0
			y += imgSize
		if y >= mergeSize[1]:
			break
	if thumbnailSize[0] > minOutputImgSize or thumbnailSize[1] > minOutputImgSize:
		thumbnailSize = ( minOutputImgSize, minOutputImgSize )

	mergeImg.thumbnail( thumbnailSize, Image.ANTIALIAS )
			
	return mergeImg	
# mergeImage
	
 
def getTileImage( fileList, imgSize, levelCnt, curLevel, outPutPath, ignoreCnt = 0, coordX = 0, coordY = 0, cancel = False ):
	if cancel:
		return None

	cnt = len( fileList )
	if curLevel == 0:
		if cnt != 1:
			return None
		
		img = None
		if os.path.exists( fileList[0] ):
			img = Image.open( fileList[0] )
		return img
	
	size = TILE_DIVISION ** curLevel
	halfSize = size / 2
	if cnt != size * size:
		return None

	imgList = []
	coordOffsetX = coordX * TILE_DIVISION
	coordOffsetY = coordY * TILE_DIVISION
	for x in range( 0, TILE_DIVISION ):
		for y in range( 0, TILE_DIVISION ):
			subFileList = []
			for pX in range( 0, halfSize ):
				for pY in range( 0, halfSize ):
					pos = ( x * halfSize + pX ) * size + ( y * halfSize + pY ) 
					subFileList.append( fileList[pos] )
			imgList.append( getTileImage( subFileList, imgSize, levelCnt, curLevel-1, outPutPath, ignoreCnt, coordOffsetX + x, coordOffsetY + y, isProgressCancelled() ) )

	imgMerge = None
	if len( imgList ):
		imgMerge = mergeImage( imgList )
		progressStep( 1 )
		if imgMerge:
			#save the image
			folderLevel = levelCnt - curLevel
			if curLevel >= ignoreCnt and folderLevel >= 0:
				imgPath = "%s/%s/%d/%d" % ( outPutPath, OUTPUT_FOLDER_NAME, folderLevel, coordY )
				imgFile = "%s/%d.jpg" % ( imgPath, coordX )
				if not os.path.exists( imgPath ):
					os.makedirs( imgPath )
					
				imgMerge.save( imgFile, quality = JPG_IMAGE_QUALITY )
			
	return imgMerge
# getTileImage


def convertImages( srcPath, desPath, deleteScr = False ):
	srcPath = srcPath.replace('\\', '/')
	if srcPath[-1] != '/':
		srcPath += '/'
	for parent, dirnames, filenames in os.walk( srcPath ):
		for filename in filenames:
			fileExt = filename.split('.')[-1]
			if fileExt.lower() == 'jpg':
				img = Image.open( os.path.join( parent, filename ))
				newFolder = parent.split( srcPath )[1]
				newFolder = os.path.join( desPath, parent.split( srcPath )[1])
				if not os.path.exists( newFolder ):
					os.makedirs( newFolder )
				img.save( os.path.join( newFolder, filename ), quality = JPG_IMAGE_QUALITY )

	if deleteScr:
		shutil.rmtree( srcPath, ignore_errors = True )
# convertImages

def calcLevelInfo( imgSize, xSize, ySize ):
	maxSize = ySize
	if xSize >= ySize:
		maxSize = xSize
		
	fixedSize = 1
	levelCnt = 0
	stitchCnt = 0
	ignoreLevelCount = 0
	
	while fixedSize < maxSize:
		fixedSize *= TILE_DIVISION
		levelCnt += 1
		if stitchCnt == 0:
			stitchCnt = ( levelCnt - 1 ) * TILE_DIVISION * TILE_DIVISION + 1
		else:
			stitchCnt = stitchCnt * TILE_DIVISION * TILE_DIVISION + 1
			
	outputImgSize = imgSize
	while outputImgSize <= MIN_OUTPUT_IMG_SIZE:
		ignoreLevelCount += 1
		outputImgSize *= TILE_DIVISION
		
			
	ret = [ fixedSize, levelCnt, stitchCnt, ignoreLevelCount, outputImgSize ]
	return ret
#calcLevelInfo
			
def createSpaceLevelImageInternal( path, imgSize, xSize, ySize, levelInfo ):
	result = False
	if ERROR or len( levelInfo ) != 5:
		return result
		
	fileList = []
	imgPath = "%s/%s" % ( path, TEMP_FOLDER_NAME )
	
	
	fixedSize = levelInfo[0]
	levelCnt = levelInfo[1]
	stitchCnt = levelInfo[2]
	ignoreLevelCount = levelInfo[3]
	
	startProgress( progressMsgForLevelImages, stitchCnt, True, True )
	
	if levelCnt > ignoreLevelCount:
		#clear destination path
		destPath = "%s/%s" %( path, OUTPUT_FOLDER_NAME )
		shutil.rmtree( destPath, ignore_errors = True )
		
		topLevelPath = "%s/%d/" % ( destPath, levelCnt )
		if os.path.exists( topLevelPath ):
			shutil.rmtree( topLevelPath, ignore_errors = True );
		
		for x in range( 0, fixedSize ):
			for y in range( 0, fixedSize ):
				fileList.append( "%s/%d/%d.jpg" % ( imgPath, y, x ) )
		
		getTileImage( fileList, imgSize, levelCnt, levelCnt, path, ignoreCnt = ignoreLevelCount )
		
		if not os.path.exists( topLevelPath ) and ignoreLevelCount == 0:
			os.makedirs( topLevelPath )
			convertImages( imgPath, topLevelPath, True )
			
		result = True
	else:
		WorldEditor.addCommentaryMsg( "`SCRIPT/SPACEIMAGECREATOR_PY/IMAGE_SIZE_TOO_SMALL", 2 )
		result = False
	
	if os.path.exists( imgPath ):
		shutil.rmtree( imgPath, ignore_errors = True )
		
	stopProgress()
		
	return result
#createSpaceLevelImageInternal
	
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   create tileset.json metainfo file
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def createJsonFile( 
		path, xSize, ySize, pixelsPerMetre, 
		topLeftGridPosX, topLeftGridPosY, blockSize, levelInfo ):
		
	if len( levelInfo ) != 5:
		return False
		
	outputPath = "%s/%s" % (path, OUTPUT_FOLDER_NAME)
	if not os.path.exists( outputPath ):
		return False
		
	# world coordinate system is cartesian; tile coordinate system 
	# uses north-west point of space as its origin.
	north = ( topLeftGridPosY + 1 ) * blockSize
	west = topLeftGridPosX * blockSize
	worldWidth = xSize * blockSize
	worldHeight = ySize * blockSize
	
	tilesetDepth = levelInfo[ 1 ] - levelInfo[ 3 ]
	tileImgSize = levelInfo[ 4 ]
	fixedSize = levelInfo[ 0 ]
	
	# rootTileWorldWidth = imgSize * (TILE_DIVISION ** levelCnt) / xSize
	# rootTileWorldHeight = rootTileWorldWidth * ySize / xSize
	rootTileWorldWidth = fixedSize * blockSize
	
	# bounding rect of root tile (including backfill)
	rootTileWorldRect = {
		"minX": west,
		"maxX": west + rootTileWorldWidth,
		"minY": north - rootTileWorldWidth,
		"maxY": north
	}
	
	# bounding rect of actual space geometry
	worldRect = {
		"minX": west,
		"maxX": west + worldWidth,
		"minY": north - worldHeight,
		"maxY": north
	}
	
	# javascript date format, eg: "Thu Aug 30 2012 13:53:44 GMT+1000"
	dateGenerated = time.strftime( "%a %b %d %Y %X GMT%z" )
	
	jsonFile = file( "%s/%s/tileset.json" % (path, OUTPUT_FOLDER_NAME), 'w' )
	
	json = JSON_TEMPLATE % (
		dateGenerated,
		tileImgSize,
		tilesetDepth,
		rootTileWorldRect[ 'minX' ],
		rootTileWorldRect[ 'minY' ],
		rootTileWorldRect[ 'maxX' ],
		rootTileWorldRect[ 'maxY' ],
		worldRect[ 'minX' ],
		worldRect[ 'minY' ],
		worldRect[ 'maxX' ],
		worldRect[ 'maxY' ],
	)
	jsonFile.write( json )
	jsonFile.close()
	
	return True
#createJsonFile	

def createSpaceLevelImage( 
		path, imgSize, xSize, ySize, pixelsPerMetre, 
		topLeftGridPosX, topLeftGridPosY, blockSize ):
	if ERROR:
		return False
	
	createImagesResult = False
	createJsonFileResult = False
	result = False
	levelInfo = calcLevelInfo( imgSize, xSize, ySize );
	createImagesResult = createSpaceLevelImageInternal( path, imgSize, xSize, ySize, levelInfo )
	if createImagesResult:
		createJsonFileResult = createJsonFile( path, xSize, ySize, pixelsPerMetre, topLeftGridPosX, topLeftGridPosY, blockSize, levelInfo )

	return createImagesResult and createJsonFileResult;
#createSpaceLevelImage

def createSpaceSingleMap( path, imgSize, xSize, ySize, outputWidth, outputHeight ):
	if ERROR:
		return False
		
	eachWidth = outputWidth / xSize
	eachHeight = outputHeight / ySize
	if eachWidth > imgSize:
		eachWidth = imgSize
	if eachHeight > imgSize:
		eachHeight = imgSize
	#fix the result image size
	outputWidth = eachWidth * xSize
	outputHeight = eachHeight * ySize

	startProgress( progressMsgForSingleMap, xSize * ySize, True, False )
	mergeImg = Image.new( 'RGB', ( outputWidth, outputHeight ), 0 )
	for x in range( 0, ySize ):
		for y in range( 0, xSize ):
			imgPath = "%s/%s/%d/%d.jpg" % ( path, TEMP_FOLDER_NAME, y, x )
			img = Image.open( imgPath )
			img.thumbnail( ( eachWidth, eachHeight ), Image.ANTIALIAS )
			mergeImg.paste( img, ( y * eachWidth, x * eachHeight ) )
			progressStep( 1 )

	stopProgress()
	shutil.rmtree( "%s/%s" % ( path, TEMP_FOLDER_NAME ), ignore_errors = True )
	mergeImg.save( "%s/map.jpg" % path, quality = JPG_IMAGE_QUALITY )
	return True
# createSpaceSingleMap


def error():
	return ERROR
# error


def startFromConsole():
	usage = """
usage: 
	create single map image:
	
		%prog -s imagesFolderPath imageSize horizTilesCount verticleTilesCount outImageWidth outImageHeight
	
	create multi-level images:
	
		%prog -l imagesFolderPath imageSize horizTilesCount verticleTilesCount pixelsPerMetre topLeftGridPosX topLeftGridPosY blockSize

"""
	args = sys.argv[1:]
	if len( args ) <= 0:
		print usage
		return
	imgType = args[0]
	if imgType.lower() == '-s' and len( args ) == 7:
		path = args[1]
		imgSize = int( args[2] )
		xSize = int( args[3] )
		ySize = int( args[4] )
		outputWidth = int( args[5] )
		outputHeight = int( args[6] )
		createSpaceSingleMap( path, imgSize, xSize, ySize, outputWidth, outputHeight )
	elif imgType.lower() == '-l' and len( args ) == 9:
		path = args[1]
		imgSize = int( args[2] )
		xSize = int( args[3] )
		ySize = int( args[4] )
		pixelsPerMetre = float( args[5] )
		topLeftGridPosX = int( args[6] )
		topLeftGridPosY = int( args[7] )
		blockSize = int( args[8] )
		createSpaceLevelImage( path, imgSize, xSize, ySize, pixelsPerMetre, topLeftGridPosX, topLeftGridPosY, blockSize )
	else:
		print usage
# startFromConsole


if __name__ == '__main__':
	import sys
	startFromConsole()

# SpaceImageCreator.py	
