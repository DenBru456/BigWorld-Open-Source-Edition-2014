from FileUtils import extractSectionsByName

class SpeedtreeNameFix( ):

	def __init__( self ):
		self.description = "Speedtree Name Fixer"
		self.nameChangeMap = {}
		base = "speedtree/"
		self.nameChangeMap[ base + "Conifers/Douglas Fir/DouglasFir_RT.spt" ] = base + "Conifers/douglas_fir/DouglasFir_RT.spt"
		self.nameChangeMap[ base + "Conifers/Douglas Fir Full/DouglasFir_RT_Full.spt" ] = base + "Conifers/douglas_fir_full/DouglasFir_RT_Full.spt"
		self.nameChangeMap[ base + "Broadleaves/Bradford Callery Pear/BradfordPear_RT_Fall.spt" ] = base + "Broadleaves/bradford_callery_pear/BradfordPear_RT_Fall.spt"
		self.nameChangeMap[ base + "Broadleaves/weeping willow2/weepingwillow_rt.spt" ] = base + "Broadleaves/weeping_willow2/weepingwillow_rt.spt"
		self.nameChangeMap[ base + "Palms_Cacti_Cycads/Suguaro Cactus/SaguaroCactus_RT.spt" ] = base + "Palms_Cacti_Cycads/suguaro_cactus/SaguaroCactus_RT.spt"
		self.nameChangeMap[ base + "shrubs_flowers/American Boxwood/AmericanBoxwood_RT.spt" ] = base + "shrubs_flowers/american_boxwood/AmericanBoxwood_RT.spt"

	def appliesTo( self ):
		return ("chunk")

	def processTreeSection( self, sect, dbEntry ):
		treeName = sect.readString( "spt" )
		if self.nameChangeMap.has_key( treeName ):
			sect.deleteSection( "spt" )
			sect.writeString( "spt", self.nameChangeMap[treeName] )
			return True
		return False
		
	def process( self, dbEntry ):
		ret = False
		dbEntrySection = dbEntry.section()
		if dbEntry.name[-7:] == "o.chunk":
			trees = extractSectionsByName(dbEntrySection,"speedtree")
			for tree in trees:				
				ret = self.processTreeSection(tree,dbEntry) or ret

		if ret: dbEntrySection.save()
		return ret