import ResMgr

SIZE_MODE_CLIP 		= 0
SIZE_MODE_PIXEL 	= 1
SIZE_MODE_LEGACY 	= 2


def fixDeprecatedSizeMode( section, name ):
	deprecatedName = name + "InClip"
	newName = name + "Mode"
	if section.has_key( deprecatedName ):
		oldValue = section.readBool( deprecatedName )
		section.deleteSection( deprecatedName )				
		newValue = SIZE_MODE_LEGACY if oldValue else SIZE_MODE_PIXEL
		section.writeInt( newName, newValue )
		return True
		
	return False


class DeprecatedGuiSizeModeFix:
	def __init__( self ):
		self.description = "Deprecated GUI Size Mode Fix"
		
		
	def appliesTo( self ):
		return ("gui",)
		
		
	def process( self, dbEntry ):
		sect = ResMgr.openSection(dbEntry.name)
		if sect is None:
			return False
			
		# Convert old widthRelative/heightRelative to widthMode/heightMode
		fixed = False
		for compSect in sect.values():
			fixedWidth = fixDeprecatedSizeMode( compSect, "width" )
			fixedHeight = fixDeprecatedSizeMode( compSect, "height" )
			
			fixed = fixed or fixedWidth or fixedHeight
			
		if fixed:
			sect.save()
	
		return fixed
		