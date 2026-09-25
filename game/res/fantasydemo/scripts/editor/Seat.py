from GameData import SeatData

class Seat:
	def modelName( self, props ):
		return SeatData.modelNames[ props[ "seatType" ] ]

	def getEnums_seatType( self ):
		l = []
		for (id,name) in SeatData.editorDisplayNames.items():
			l.append( (id,name) )
		return tuple(l)	

# Seat.py
