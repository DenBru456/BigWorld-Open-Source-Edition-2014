
# common definitions, should read from config file later
PORT = 8168
BACKLOG = 5
MAX_MESSAGE_LENGTH = 1024
LOG_FORMAT = "%(asctime)s %(levelname)-6s %(message)s"

# BWLock command bytes, copied from
# src/tools/worldeditor/project/world_editord_connection.cpp
BWLOCKCOMMAND_INVALID 			= '\0'
BWLOCKCOMMAND_CONNECT 			= 'C'
BWLOCKCOMMAND_SETUSER 			= 'A'
BWLOCKCOMMAND_SETSPACE 			= 'S'
BWLOCKCOMMAND_LOCK 				= 'L'
BWLOCKNOTIFY_LOCK				= 'l'
BWLOCKCOMMAND_UNLOCK 			= 'U'
BWLOCKNOTIFY_UNLOCK				= 'u'
BWLOCKCOMMAND_GETSTATUS 		= 'G'

BWLOCKFLAG_SUCCESS 				= '\0'

# class definitions
class Rect:	# not the same as Win32 RECT, since our right and bottom are
			# inclusive

	def __init__( self, left, top, right, bottom ):
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom


	def valid( self ):
		return self.left <= self.right and self.top <= self.bottom


	def isIn( self, x, y ):
		return self.left <= x and x <= self.right and \
			self.top <= y and y <= self.bottom


	def intersect( self, other ):
		if self.isIn( other.left, other.top ) or \
				self.isIn( other.right, other.top ):
			return 1
		if self.isIn( other.left, other.bottom ) or \
				self.isIn( other.right, other.bottom ):
			return 1
		if other.isIn( self.left, self.top ) or \
				other.isIn( self.right, self.top ):
			return 1
		if other.isIn( self.left, self.bottom ) or \
				other.isIn( self.right, self.bottom ):
			return 1
		return 0


	def __repr__( self ):
		return '%d %d %d %d' % ( self.left, self.top, self.right, self.bottom )


	def __eval__( self, str ):
		values = str.split()
		if len( values ) != 4:
			raise Exception, "Format Error in Rect::__eval__"
		self.left = int( values[ 0 ] )
		self.top = int( values[ 1 ] )
		self.right = int( values[ 2 ] )
		self.bottom = int( values[ 3 ] )


	def __eq__( self, other ):
		return repr( self ) == repr( other )
