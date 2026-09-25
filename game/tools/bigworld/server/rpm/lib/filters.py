import logging
import subprocess

import sys

log = logging.getLogger( 'filters' )

class Filters( object ):
	def __init__( self ):
		self._map = {}

	def add( self, line ):
		try:
			filename, cmd = line.split( None, 1 )
			assert( cmd[0] == '|')
			cmd = cmd[1:]

			self._map.setdefault( filename, [] ).append( cmd )
		except:
			print "Invalid filter arg -", line

	def get( self, dstPattern ):
		return FilterList( self._map.get( dstPattern, [] ) )


class FilterList( object ):
	def __init__( self, filters ):
		self.filters = filters

	def run( self, dst, macroExpander ):
		isOkay = True

		for filter in self.filters:
			inFile = open( dst, 'r' )
			inLines = inFile.readlines()
			inFile.close()

			cmd = macroExpander.expand( filter )

			p = subprocess.Popen( cmd, shell=True,
					stdin=subprocess.PIPE, stdout=open( dst, 'w' ) )

			for line in inLines:
				p.stdin.write( line )

			p.stdin.close()
			if p.wait() != 0:
				log.error( 'Failed to run "%s" on %s' %
						(cmd, dst) )
				isOkay = False

		return isOkay

# filters.py
