#!/usr/bin/python
"""
A script to generate graphs as accepted by the Patrol and ZigzigPatrol
movement controllers.  Not very efficient at all, but it doesn't really need to
be either.
"""

import os
import sys

try:
	sys.path.append(
		os.environ[ "MF_ROOT" ] +
			"/bigworld/tools/server/pycommon".replace( '/', os.sep ) )
except KeyError:
	print "Warning: MF_ROOT is not set"

from graph import *

def villages( n, worldradius, defaults={} ):

	g = Graph( defaults )

	# Create villages
	villages = [ Vertex.random( g, worldradius ) for x in xrange( n ) ]
	for v in villages:
		g.add( v )

	# Form minimum spanning tree
	cloud = [ villages.pop() ]
	while villages:

		# Find nearest node to the cloud
		nearest = None
		neardist = None
		for c in cloud:
			for v in villages:
				if nearest == None or c.distTo( v ) < neardist:
					nearest = (c,v)
					neardist = c.distTo( v )

		# Bring it into the cloud
		(c,v) = nearest
		c.connect( v ); v.connect( c )
		cloud.append( v )
		villages.remove( v )

	# Create graph
	return g

g = villages( 100, 10000 )
#g = villages( 10, 10000 )
print g.getXMLDocument().toprettyxml()
