# ------------------------------------------------------------------------------
# Repository for miscellaneous client side helper functions
# ------------------------------------------------------------------------------

import BigWorld

def entitiesFromChunk( sectionName ):
	import ResMgr
	sects = ResMgr.openSection( sectionName )
	if sects != None:
		for sect in sects.values():
			if sect.name == "entity":
				type = sect.readString( "type" )
				pos = sect.readVector3( "transform/row3" )
				dict = {}
				for props in sect["properties"].values():
					try:
						dict[str(props.name)] = eval(props.asString)
					except:
						dict[str(props.name)] = props.asString
				#~ print type
				#~ print str(pos)
				#~ print str(dict)
				BigWorld.createEntity(type, BigWorld.player().spaceID, 0, pos, (0,0,0), dict)
