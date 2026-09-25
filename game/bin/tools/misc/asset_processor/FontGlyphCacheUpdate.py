from FileUtils import extractSectionsByName

class FontGlyphCacheUpdate( ):
	'''
		This AssetProcessor class upgrades font files from 1.9 to 2.0 format.
		It strips out the <generated> section, as fonts are now automatically
		generated.
		
		NOTE
		----
		If you have generated font files that you wish to retain (for example
		artist-generated fonts) then add them to the ignore list in the
		constructor below.
	'''
	def __init__( self ):
		self.description = "Font Glyph Cache Update"
		self.ignoreList = []
		self.ignoreList.append("system/fonts/fantasydemo.font")

	def appliesTo( self ):
		return ("font")
		
	def process( self, dbEntry ):
		changed = False
		dbEntrySection = dbEntry.section()
		if dbEntry.name not in self.ignoreList:
			if dbEntrySection.has_key( "generated" ):
				dbEntrySection.deleteSection( "generated" )
				creationSection = dbEntrySection["creation"]
				creationSection.deleteSection( "startChar" )
				creationSection.deleteSection( "endChar" )
				dbEntrySection.save()
				return True
		return False
