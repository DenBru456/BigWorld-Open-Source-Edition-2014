#!/usr/bin/env python

import logging
import os
import threading
from xml.dom import minidom

log = logging.getLogger( __name__ )


class Prefs( object ):

	OPEN_FILES = {}

	# A semaphore for making sure that no two threads can ever be in the
	# constructor at the same time.  A bit heavy handed, but ensures we only
	# have one XML object per file
	initSem = threading.Lock()

	def __init__( self, filename, rootname=None ):

		try:
			self.initSem.acquire()
			self.hasRootname = ( rootname != None )

			# If we've already got some prefs open, steal references to existing
			# XML objects and make sure we incref
			if not self.hasRootname:
				if self.OPEN_FILES.has_key( filename ):
					(prefs, refcount, sem) = self.OPEN_FILES[ filename ]
					self.doc = prefs.doc
					self.root = prefs.root
					self.filename = filename
					self.OPEN_FILES[ filename ] = (prefs, refcount+1, sem)
					return

			# This block is for reading existing prefs
			try:
				self.filename = filename
				self.doc = minidom.parse( filename )
				self.root = self.doc.firstChild
				self.purgeWhitespace()

			# If we can't, make a new prefs file
			except:
				self.doc = minidom.Document()
				if self.hasRootname:
					self.root = self.doc.createElement( rootname )
				else:
					self.root = self.doc.createElement( "prefs" )
				self.doc.appendChild( self.root )

			# Note that we've got the prefs open
			if not self.hasRootname:
				self.OPEN_FILES[ self.filename ] = (self, 1, threading.Semaphore())

		finally:
			self.initSem.release()

	def __del__( self ):

		if not self.hasRootname:
			(prefs, refcount, sem) = self.OPEN_FILES[ self.filename ]

			if refcount > 1:
				self.OPEN_FILES[ self.filename ] = (prefs, refcount-1, sem)
			else:
				self.save()
				del self.OPEN_FILES[ self.filename ]

	def save( self, filename=None ):
		if not filename:
			filename = self.filename
		open( filename, "w" ).write( self.doc.toprettyxml() )

	def getNode( self, path, create = False ):
		"""
		Returns the node associated with the path/to/element.  If create is True
		then intermediate nodes are created on the fly.
		"""

		node = self.root
		for tag in [t for t in os.path.split( path ) if t != ""]:
			parent = node
			node = self._getChildElement( node, tag )
			if node is None:
				if create:
					node = self.doc.createElement( tag )
					parent.appendChild( node )
				else:
					return None
		return node

	def _getChildElement( self, node, name ):
		for child in node.childNodes:
			if child.nodeType == child.ELEMENT_NODE and child.tagName == name:
				return child
		return None

	def _getChildText( self, node ):
		for child in node.childNodes:
			if child.nodeType == child.TEXT_NODE:
				return child.data.strip()
		return None

	def get( self, path, fatal = False ):
		node = self.getNode( path )
		if node is None:
			if fatal:
				log.critical( "XMLPrefs: Can't read %s from %s" % \
							  (path, self.filename) )
			else:
				return None
		else:
			return self._getChildText( node )

	def set( self, path, value ):
		"""
		Intermediate nodes will be created if they don't exist already.
		"""

		node = self.getNode( path, True )
		while len( node.childNodes ) > 0:
			node.removeChild( node.childNodes[0] )
		text = self.doc.createTextNode( str( value ) )
		node.appendChild( text )

	def getDoc( self ) :
		"""If you want to do anything other than basic att=val mappings, you're
		   going to have to manipulate the XML tree yourself.  I'm not going to
		   convert the tree to a hash because that means you can't have repeated
		   tag names."""
		return self.doc

	def getRoot( self ):
		return self.root

	def getSem( self ):
		"""Returns the semaphore for this prefs file.  If you are doing prefs
		   work with a threaded app where the prefs are modified in more than one
		   thread, you'll need this."""

		return self.OPEN_FILES[ self.filename ][2]

	def purgeWhitespace( self ):

		stack = [ self.root ]
		removeList = []

		while stack:
			node = stack.pop()
			for child in node.childNodes:
				if child.nodeType == child.TEXT_NODE and \
					   not child.data.strip():
					removeList.append( child )
				elif child.nodeType == child.TEXT_NODE:
					child.data = child.data.strip()
				elif child.hasChildNodes():
					stack.append( child )

		for node in removeList:
			node.parentNode.removeChild(node)
			node.unlink
