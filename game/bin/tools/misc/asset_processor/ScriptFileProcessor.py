import os
import sys
x=sys.path
sys.path=x

import FileUtils

class ScriptFileProcessor:
	def __init__( self ):
		pass
		
	def buildDatabase(self, dbEntry):	
		# need to search for model and textures	
		bw_res_path = FileUtils.BW_RES_PATH
		try:
			f = open(bw_res_path+'/'+dbEntry.name,'r')
		except IOError:
			print "Failed to open %s" % (dbEntry.name,)
			return
			
		extensions = (".model",".tga",".bmp",".texanim",".jpg",".png",".dds")
			
		lines = f.readlines()
		for line in lines:
			line = line.replace('\'', '\"')
			for ext in extensions:
				if ext in line:
					words = line.split("\"")
					for word in words:
						if word[-len(ext):] == ext:
							dbEntry.addDependency( word )
		f.close()		
				
	def process(self,dbEntry):
		return True
		