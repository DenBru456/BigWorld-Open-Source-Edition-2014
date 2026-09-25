import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
from FileUtils import extractSectionsByName
from FileUtils import stripExtension
from FileUtils import stripPath
from FileUtils import extractPath
from FileUtils import openSectionFromFolder
from MaterialSectionProcessorBase import MaterialSectionProcessorBase
from LogFile import errorLog


#Process a textureOrMFM section.
#returns (BOOL,FILENAME) where the results are:
#BOOL - true if this section is an MFM section
#		false if this section is a texture section
#FILENAME - either the .mfm or texture file name
def isTextureOrMFM(sect ):
	value = sect.asString
	
	#if the entry ends in .mfm, easy. it's an mfm
	if ".mfm" in value:
		return (True,value)
		
	#if not, then we first must check if an .mfm with
	#the same filename exists.
	value = stripExtension(value)+".mfm"	
	ds = ResMgr.openSection(value)
	if ds != None:
		return (True,value)
	else:
		return (False,sect.asString)
		

		
class VisualFileProcessor( MaterialSectionProcessorBase ):
	def __init__( self ):
		MaterialSectionProcessorBase.__init__( self )
		
		
	def buildDatabase(self,visualEntry):		
		sect = visualEntry.section()
		
		rss = extractSectionsByName(sect,"renderSet")
		for rs in rss:
			gs = extractSectionsByName(rs,"geometry")
			for g in gs:
				pgs = extractSectionsByName(g,"primitiveGroup")
				for pg in pgs:
					material = pg["material"]
					if material != None:
						self.processVisualMaterial(material,visualEntry)
						MaterialSectionProcessorBase.buildDatabase( self, material, visualEntry )					
						
						
	def processVisualMaterial(self,material,visualEntry):
		#first find mfm
		sect = material["mfm"]
		if sect != None:
			mfmSect = ResMgr.openSection(sect.asString)
			if mfmSect != None:
				#have to do this because all other files
				#are opened as direct children of the current
				#folder, and this affects the section name.
				(mfmSect,mfmPath) = openSectionFromFolder(sect.asString)
				#print "ADD MFM FROM VISUAL", mfmPath+"/"+mfmSect.name
				mfmPath = mfmPath.replace("\\","/")
				mfmName = mfmPath + "/" + mfmSect.name
				visualEntry.addDependency( mfmName )				
		else:
			#second find textureormfm
			sect = material["textureormfm"]
			if sect != None:
				(isMFM,filename) = isTextureOrMFM(sect)
				if isMFM:
					(mfmSect,mfmPath) = openSectionFromFolder(filename)
					#note - mfmSect guaranteed to exist after isTextureOrMFM call
					#print "ADD MFM FROM VISUAL", mfmPath+"/"+mfmSect.name
					mfmPath = mfmPath.replace("\\","/")
					mfmName = mfmPath + "/" + mfmSect.name
					visualEntry.addDependency( mfmPath + "/" + mfmSect.name )	
						
					
	def process(self,dbEntry):
		result = True
				
		#sect = ResMgr.openSection(dpEntry.name)
		#renderSets = extractSectionsByName(sect,"renderSet")
		#for rs in renderSets:
		#	nodes = extractSectionsByName(rs,"node")
			#renderSetSkinned = len(nodes) > 1
			#fileContext.skinned = renderSetSkinned
		#	geometries = extractSectionsByName(rs,"geometry")
		#	for g in geometries:
				#if renderSetSkinned != 0:
				#	if (not self.detectSkinning(g,path+sect.name)):
				#		return False
				#else:
				#	fileContext.skinned = 0
		#		primitiveGroups = extractSectionsByName(g,"primitiveGroup")
		#		for pg in primitiveGroups:					
		#			material = pg["material"]
		#			if material != None:
		#				fxs = extractSectionsByName(material,"fx")
		#				if len(fxs) > 1:
		#					errorLog.errorMsg("Visual file had more than one fx file")
		#			else:
		#				errorLog.errorMsg("Could not find material section in Visual")
		#				return False		
		return result


	#This method looks up the vertices file and looks at the vertex format,
	#simply to see whether the file is soft-skinned or hard-skinned.
	def detectSkinning(self,sect,filename):
		vertices = self.processVerticesName( sect.readString("vertices"),filename )
		ds = ResMgr.openSection(vertices)
		if ds != None:
			vertexFormat = ds.asBinary.split('\0',1)[0]
			#print "SKINNING : ", filename, vertices, vertexFormat
			#if vertexFormat in ("xyznuvi","xyznuvitb"):
			#	fileContext.skinned = 2
			#elif vertexFormat in ("xyznuviiiwwtb","xyznuviiiww"):
			#	fileContext.skinned = 1
			#else:
			#	fileContext.skinned = 0
		else:
			errorLog.errorMsg("Could not load vertices from file %s" % (vertices,))
			return False
		return True
		
		
	def processVerticesName(self,original,filename):
		#some vertices are fully qualified bin section path names.
		idx = original.find(".primitives")
		if idx != -1:
			#print "Fully Qualified Primitives", original
			return original
			
		#new vertices have no path information, they are relative
		#to the implicit primitives filename
		idx = original.find('/')
		if idx == -1:
			modified = extractPath(filename) + "/" + stripExtension(stripPath(filename)) + ".primitives/" + original
			#print "No Path Information Primitives", original, modified
			return modified
						
		#there is path information, but no mention of the ".primitives" file.
		#put the .primitives name in the right place.
		idx = original.find('.')
		if idx != -1:
			modified = original[:idx] + ".primitives/" + original[idx+1:]
			#print "Path Information But No Mention of Primitives", original, modified
			return modified