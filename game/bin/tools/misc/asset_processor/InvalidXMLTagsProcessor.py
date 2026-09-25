import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
from LogFile import errorLog
from FileUtils import extractSectionsByName
from FileUtils import extractPath
from FileUtils import openSectionFromFolder

class InvalidXMLTagsProcessor:
	def __init__( self ):
		self.description = "Invalid XML Tags Fix"
		
	def appliesTo( self ):
		return ("model", "graph", "xml", "model", "visual", "chunk")		
												
	def process(self,dbEntry):
		dbEntrySection = dbEntry.section()
		changed = False
		
		# Sanitise blends in models:
		if dbEntry.name[-6:] == ".model":							
			animations = extractSectionsByName(dbEntrySection, "animation")
			for animation in animations:
				alphas = extractSectionsByName(animation, "alpha")
				for alpha in alphas:
					for child in alpha.values():
						thisChanged = child.cleanName()
						if thisChanged:
							changed = True
							
		# Sanitise graph UIDs:		
		if dbEntry.name[-6:] == ".graph": 
			thisChanged = self.cleanSections(dbEntrySection)
			if thisChanged:
				changed = True
				
		# Sanitise particle system names:
		if self.isParticleSystem(dbEntrySection):
			for child in dbEntrySection.values():
				thisChanged = child.cleanName()
				if thisChanged:
					changed = True

		# Look for any dodgy XML:
		if not self.validXML(dbEntrySection, True):
			errorLog.warningMsg("Possible invalid XML in %s" % (dbEntry.name))
	
		if changed: 
			dbEntrySection.save()
						
		return changed
		
	def cleanSections(self, section):
		changed = section.cleanName()
		for child in section.values():
			childChanged = self.cleanSections(child)
			if childChanged:
				changed = True
		return changed
		
	# This is a bit of a hack - there is currently no easy way of checking
	# whether a file is a particle system file!  Instead we use some general
	# hueristics
	def isParticleSystem(self, section):
		for child in section.values():
			if child.name == "seedTime":
				return True
			children = extractSectionsByName(child, "serialiseVersionData")
			if len(children) != 0:
				return True
			children = child.values()
			if len(children) != 0:
				child = children.pop(0)
				children = extractSectionsByName(child, "serialiseVersionData")
				if len(children) != 0:
					return True						
		return False
				
	def validXML(self, section, ignoreTopLevel):
		if not ignoreTopLevel:
			if not section.isNameClean():
				return False
		for child in section.values():
			if not self.validXML(child, False):
				return False
		return True
