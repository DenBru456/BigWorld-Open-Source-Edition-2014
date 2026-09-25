from LogFile import errorLog
import AssetProcessorSystem
import ResMgr

# This class finds all TextGuiComponent <label> entries in .gui files, and
# converts the text there from base64 which is no longer supported, to UTF-8
class Base64ToUTF8:

	def __init__( self ):		
		self.description = "Base64 to UTF-8 Gui label Fix"


	def appliesTo( self ):
		return ("gui",)


	def process( self, dbEntry ):
		sect = ResMgr.openSection(dbEntry.name)
		if sect is None:
			return False
			
		# Convert old base64 <label> entries in TextGUIComponent sections to UTF-8
		fixed = False
		for (key,ds) in sect.items():
			if key == "TextGUIComponent":
				tds = ds["label"]
				if tds is not None:
					fixed = fixed | AssetProcessorSystem.convertBase64DataSection(tds)

		if fixed:
			sect.save()
	
		return fixed
