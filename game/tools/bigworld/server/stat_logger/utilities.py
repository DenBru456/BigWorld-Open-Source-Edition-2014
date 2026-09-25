from xml.dom import minidom, Node
import time
import struct, socket

# Utility functions
# ============================================

# Creates unique database compatible names
class DbNamer:
	def __init__( self ):
		self.usedNames = {}
		self.prefix = ""
	def makeName( self, name ):
		return self.prefix + self._generateName( name )
	def addUsed( self, used ):
		self.usedNames[ used ] = True
	def setPrefix( self, prefix ):
		self.prefix = prefix

	def _generateName( self, name ):
		baseName = self._convertToDBName( name )
		dbName = baseName
		# Make sure the name is unique
		i = 1
		while self.usedNames.has_key( dbName ):
			dbName = baseName + str(i)
			i += 1

		# Add it to the dictionary
		self.usedNames[ dbName ] = True
		return dbName

	def _convertToDBName( self, name ):
		"""
		Convert names to db-friendly names.
		'Number in AOI' => number_in_aoi
		"""
		if name == "":
			return ""
		chars = list(name)
		#chars[0] = chars[0].lower()
		prevChar = True
		i = 0
		while i < len(chars):
			if chars[i] == ' ':
				chars[i] = '_'
				i += 1
			elif not chars[i].isalnum():
				del chars[i]
				prevChar = False
			else:
#				if not prevChar:
#					chars[i] = chars[i].upper()
				prevChar = True
				i += 1
		out = "".join(chars).lower()
		return out

def stringToBool( string ):
	return string.lower == "true"

# Given a floating point timestamp,
# return an integer timestamp (second resolution)
def convertFloatTime( time ):
	#seconds = int( time )
	#milliseconds = int((time % 1) * 1000)
	#return (seconds, milliseconds)
	return round(time * 1000)

# Converts a millisecond resolution long integer timestamp
# into a second resolution
def convertLongTime( time ):
	return time / 1000.0

# Given a timestamp, return the appropriate format
def formatTime( t ):
	if type(t) == long or type(t) == int:
		return time.strftime( "%d %b %Y, %H:%M:%S", time.localtime( int(t) ) )
	elif type(t) == tuple and len(t) == 2:
		return time.strftime( "%d %b %Y, %H:%M:%S", time.localtime( t[0] ) ) +\
			".%.3d" % (t[1])
	else:
		return t

# Converts an string IP address into the integer representation
def ipToInt( ip):
	return struct.unpack('I',socket.inet_aton(ip))[0]

# Converts an integer IP address into the string representation
def intToIp( n ):
	return socket.inet_ntoa(struct.pack('I',n))

# XML Utility functions
# ==========================================================

# Given an XML node (using minidom, although all DOM compatible
# Python node classes should work), find a child node with a
# certain name
def xmlFindChildElement( node, name ):
	for child in node.childNodes:
		if child.nodeType == Node.ELEMENT_NODE and child.nodeName == name:
			return child
	return None

# Given an XML Element node, parse all the attribute/value pairs
# into a dictionary
# e.g. <cat id="1", name="World"></cat>
# not used anymore
def xmlNodeAttributesToDict( node ):
	nodeDict = {}
	for i in range( node.attributes.length ):
		attribute = node.attributes.item(i)
		nodeDict[ attribute.name ] = attribute.value

	return nodeDict

def xmlNodeToDict( node ):
	nodeDict = {}
	for child in node.childNodes:
		if child.nodeType == Node.ELEMENT_NODE:
			nodeDict[ child.tagName ] = ""
			for grandchild in child.childNodes:
				if grandchild.nodeType == Node.TEXT_NODE:
					nodeDict[ child.tagName ] = grandchild.data.strip()
					break
	return nodeDict

def xmlAddValue( doc, node, name, value ):
	nameNode = doc.createElement( name )
	valueNode = doc.createTextNode( str(value) )
	nameNode.appendChild( valueNode )
	node.appendChild( nameNode )

def xmlAddComment( doc, node, comment ):
	commentNode = doc.createComment( comment )
	node.appendChild( commentNode )

# Maps a list in XML to a function
# - listName is the tagname of the list node
# - tagName is the tagname of each xml list element node
# - function is the function to be called
#
def xmlMapList( node, listName, tagName, function ):
	resultList = []
	listNode = xmlFindChildElement( node, listName )
	if listNode:
		for child in listNode.childNodes:
			if child.nodeType == Node.ELEMENT_NODE and \
					child.tagName == tagName:
				resultList.append( function( child ) )
	return resultList



# This is gonna slow things down, but we don't write xml that often
# so it's ok.
# This function basically changes the xml writer around a bit so that
# element nodes containing a single text nodes are printed on one line
# e.g.
# <hello>
#     world
# </hello>
# becomes
# <hello>world</hello>
def xmlModifyWriter():
	def element_writexml(self, writer, indent="", addindent="", newl=""):
		# indent = current indentation
		# addindent = indentation to add to higher levels
		# newl = newline string
		writer.write(indent+"<" + self.tagName)

		attrs = self._get_attributes()
		a_names = attrs.keys()
		a_names.sort()

		for a_name in a_names:
			writer.write(" %s=\"" % a_name)
			minidom._write_data(writer, attrs[a_name].value)
			writer.write("\"")
		if self.childNodes:
			#writer.write(">%s"%(newl))
			writer.write(">")
			if len(self.childNodes) == 1 and \
					self.childNodes[0].nodeType == Node.TEXT_NODE:
				self.childNodes[0].writexml(writer)
				writer.write("</%s>%s" % (self.tagName,newl))
			else:
				writer.write( newl )
				for node in self.childNodes:
					node.writexml(writer,indent+addindent,addindent,newl)
				writer.write("%s</%s>%s" % (indent,self.tagName,newl))
		else:
			writer.write("/>%s"%(newl))

	def text_writexml( self, writer, indent="", addindent="", newl="" ):
		#minidom._write_data(writer, "%s%s%s"%(indent, self.data, newl))
		minidom._write_data(writer, "%s"%(self.data))

	minidom.Element.writexml = element_writexml


def getOrdinalSuffix( num ):
	"""
	Return the ordinal suffix for the given number, e.g. "th", "st", etc.

	@param num:		the number to give the ordinal suffix for
	"""
	if (num / 10) % 10 == 1:
		return "th"
	elif num % 10 == 1:
		return "st"
	elif (num % 10) == 2:
		return "nd"
	elif (num % 10) == 3:
		return "rd"
	else:
		return "th"

