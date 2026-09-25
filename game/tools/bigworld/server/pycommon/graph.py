"""
Library to read and write graphs compatible with the Patrol movement controller.
"""

import random
import math
from xml.dom import minidom

# Convert a hash into an XML node
def hash2XMLNode( hash, name, doc ):

	root = doc.createElement( name )
	for k, v in hash.items():
		el = doc.createElement( k )
		el.appendChild( doc.createTextNode( v ) )
		root.appendChild( el )
	return root

class Vec3:
	def __init__( self, x, y, z ):
		self.x = x
		self.y = y
		self.z = z

	def __str__( self ):
		return "%d %d %d" % (self.x, self.y, self.z)

	def distTo( self, v ):
		return math.sqrt( (self.x - v.x) ** 2 +
						  (self.y - v.y) ** 2 +
						  (self.z - v.z) ** 2 )

	def scale( self, x ):
		self.x *= x
		self.y *= x
		self.z *= x

class Vertex:

	ID = 0

	def getID( self ): id = self.ID; self.ID += 1; return str( id )
	getID = classmethod( getID )

	def __init__( self, graph, pos, attributes={} ):

		self.pos = pos
		self.ns = []
		self.graph = graph

		# ID's should be strings
		if attributes.has_key( "name" ):
			self.name = str( attributes[ "name" ] )
			del attributes[ "name" ]
		else:
			self.name = str( Vertex.ID ); Vertex.ID += 1;

		self.attributes = attributes

	def connect( self, v ):
		if v not in self.ns:
			self.ns.append( v )

	def getXMLNode( self, doc ):
		"""Create an XML node as part of the given XML document."""

		# Create element with attributes
		atts = self.attributes.copy()
		atts[ "name" ] = self.name
		atts[ "pos" ] = str( self.pos )
		root = hash2XMLNode( atts, "node", doc )

		# Add edges into the element
		edges = doc.createElement( "edges" )
		root.appendChild( edges )
		for n in self.ns:
			edge = doc.createElement( "edge" )
			edge.appendChild( doc.createTextNode( n.name ) )
			edges.appendChild( edge )

		return root

	def random( graph, radius ):
		return Vertex( graph, Vec3( random.randint( -radius, radius ),
									0,
									random.randint( -radius, radius ) ) )

	def distTo( self, other ): return self.pos.distTo( other.pos )

	def getRadius( self ):

		if self.attributes.has_key( "radius" ):
			return float( self.attributes[ "radius" ] )
		else:
			return float( self.graph.defaults[ "radius" ] )

	random = staticmethod( random )

class Graph:

	DEFAULTS = { "radius": 200,
				 "minStay": 10,
				 "maxStay": 30,
				 "minSpeed": 6,
				 "maxSpeed": 8 }

	def __init__( self, defaults, vertices=None, resetIDs=False ):
		self.vs = {}
		self.defaults = defaults

		# Insert mandatory defaults if not given
		for k, v in self.DEFAULTS.items():
			if not defaults.has_key( k ):
				defaults[ k ] = str( v )

		if resetIDs:
			Vertex.ID = 0

		if vertices:
			for v in vertices:
				self.add( v )

	def parse( self, filename ):
		"""Parse an XML graph file and create a graph from it."""

		doc = minidom.parse( filename )
		root = doc.childNodes[0]
		defaultsNode = root.getElementsByTagName( "nodeDefaults" )[0]
		nodes = root.getElementsByTagName( "nodes" )[0]

		# Macro to filter out non-element nodes
		def getChildElements( node ):
			return filter( lambda n: n.nodeType == n.ELEMENT_NODE,
						   node.childNodes )

		# Convert unicode string to ascii
		def u2a( us ):
			if type( us ) == type( u'' ):
				return us.encode( "utf-8" )
			else:
				return us

		# Recursively change all text in the node tree to ascii
		def node2ascii( node ):

			if node.nodeType == node.ELEMENT_NODE:
				node.tagName = u2a( node.tagName )
			elif node.nodeType == node.TEXT_NODE:
				node.data = u2a( node.data )

			for child in node.childNodes:
				node2ascii( child )

		node2ascii( root )

		# Create hash of options for nodeDefaults
		self.defaults = {}
		for opt in getChildElements( defaultsNode ):
			self.defaults[ opt.tagName ] = opt.firstChild.data.strip()

		# Create graph object
		g = Graph( self.defaults, None, True )

		# A map from node name to a list of it's neighbours' names.
		connections = {}

		# Parse nodes
		for node in getChildElements( nodes ):

			# Get the position
			posNode = node.getElementsByTagName( "pos" )[0]
			pos = map( lambda s: int( s ),
					   posNode.firstChild.data.strip().split( " " ) )
			pos = Vec3( *pos )
			node.removeChild( posNode )

			# Try to get the name
			try:
				nameNode = node.getElementsByTagName( "name" )[0]
				name = nameNode.firstChild.data.strip()
				node.removeChild( nameNode )
			except:
				name = str( Vertex.ID )

			# Get the edges
			connections[ name ] = []
			edgesNode = node.getElementsByTagName( "edges" )[0]
			for edgeNode in getChildElements( edgesNode ):
				connections[ name ].append( edgeNode.firstChild.data.strip() )
			node.removeChild( edgesNode )

			# Put name and all other attributes in a hash
			otheratts = { "name": name }
			for att in getChildElements( node ):
				otheratts[ att.tagName ] = att.firstChild.data.strip()

			# Create Vertex object and add to the graph
			g.add( Vertex( self, pos, otheratts ) )

			# Every time we create a Node the ID magically goes up
			Vertex.ID += 1

		# Link nodes as required
		for fromname in connections.keys():
			for toname in connections[ fromname ]:
				g.vs[ fromname ].connect( g.vs[ toname ] )

		return g

	parse = classmethod( parse )

	def add( self, v ):
		self.vs[ v.name ] = v

	def combine( g1, g2 ):
		g3 = Graph()
		for k,v in g1.vs.items():
			g3.vs[ k ] = v
		for k,v in g2.vs.items():
			g3.vs[ k ] = v
		return g3

	combine = staticmethod( combine )

	def scale( self, scale ):
		"""Scale all positions and radii using the same algorithm as
		   patrol_graph.cpp."""

		# Scale positions
		for v in self.vs.values():
			v.pos.scale( scale )

		# Macro to scale a float-string
		def scaleStr( scale, s ):
			return str( float( s ) * scale )

		self.defaults[ "radius" ] = scaleStr( scale,
											  self.defaults[ "radius" ] )
		scaleRoot = math.sqrt( scale )
		for v in self.vs.values():
			if v.attributes.has_key( "radius" ):
				v.attributes[ "radius" ] = scaleStr( scaleRoot,
													 v.attributes[ "radius" ] )

	def getXMLDocument( self ):

		# Create document and root
		doc = minidom.Document()
		root = doc.createElement( "waypoints" )
		doc.appendChild( root )

		# Put in defaults section
		root.appendChild( hash2XMLNode( self.defaults, "nodeDefaults", doc ) )

		# Makes nodes section
		nodes = doc.createElement( "nodes" ); root.appendChild( nodes );
		for node in self.vs.values():
			nodes.appendChild( node.getXMLNode( doc ) )

		return doc

