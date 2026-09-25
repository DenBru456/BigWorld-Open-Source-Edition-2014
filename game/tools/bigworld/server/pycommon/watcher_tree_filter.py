#!/usr/bin/env python
"""Support querying a range of watcher values specified by a path with
wildcards. Used by getmany.py and WebConsole"""

import messages
import watcher_constants
import logging

from watcher_data_message import WatcherDataMessage

log = logging.getLogger( __name__ )


class Error( Exception ):
	""" Superclass of various Watcher exceptions """
	pass
# end class Error


class BadPathError( Error ):

	def __init__( self, badPath, querySubPaths, process ):

		result = ""
		for p in querySubPaths:
			if badPath.startswith( p ):
				result += p
				badPath = badPath[ len(p) + 1: ]
				s = badPath.split( '/', 1 )

				if len(s) == 2:
					result += "/<%s>/" % s[0]
					badPath = s[1]

		self.badPath = badPath
		self.querySubPaths = querySubPaths
		self.process = process

		Error.__init__( self,
			"Unsuccessful watcher request to %s: %s" % (process.label(), result) )

# end class BadPathError


class QueryTooBigError( Error ):
	pass
# end class QueryTooBigError


class ResultsTooBigError( Error ):
	pass
# end class ResultsTooBigError


def _splitPath( path ):
	splitPaths = path.split( "/*" )

	# Strip leading '/' and handle the case of entries starting with '*'
	finalPaths = [""]
	for path in splitPaths:
		if path == '':
			finalPaths.append( path )
		elif path.startswith( '/' ):
			finalPaths.append( path[1:] )
		else:
			finalPaths.append( finalPaths.pop() + path )

	return finalPaths


def _createProcessKeys( processes ):
	keys = [process.label() for process in processes]

	# If not all unique
	if len( processes ) > len( set( processes ) ):
		keys = ["%s:%d" % (process.label(), process.pid)
				for process in processes ]

	return keys


# def writeTable( keySets, table, prefix = "" ):
# 	if prefix:
# 		print "Table:", prefix
#
# 	if len( keySets ) > 2:
# 		if prefix:
# 			prefix += '/'
#
# 		for key in keySets[0]:
# 			writeTable( keySets[1:], table[key], prefix + key )
# 			print
# 	else:
# 		stringTable = [[''] + keySets[ 0 ]]
#
# 		for y in keySets[1]:
# 			currentRow = [y]
# 			for x in keySets[0]:
# 				currentRow.append( str( table[x][y][1] ) )
# 			stringTable.append( currentRow )
#
# 		columnSizes = [max( len( s ) for s in col ) for col in stringTable]
#
# 		for i in range( len( stringTable[0] ) ):
# 			for j in range( len( stringTable ) ):
# 				if i == 0 or j == 0:
# 					fmt = "%-*s"
# 				else:
# 					fmt = "%*s"
# 				print fmt % (columnSizes[ j ], stringTable[ j ][ i ]),
# 			print


def _createLeaf( value ):
	return value[ 1 : 3 ]


def createDictTree( results, subPaths ):
	currSubPath = subPaths[0]
	remainingPaths = subPaths[1:]

	if results.has_key( currSubPath ):
		assert( len( results ) == 1 )
		leafValues = results[ currSubPath ]

		if not remainingPaths:
			if leafValues:
				return _createLeaf( leafValues[0] )
			else:
				return None
		else:
			assert( len( remainingPaths ) == 1 )
			assert( remainingPaths[-1] == '' )
			return dict( (value[0], _createLeaf( value ))
					for value in leafValues )

	partitionedResults = {}
	startLen = len( currSubPath ) + 1

	for path, value in results.items():
		assert( path.startswith( currSubPath ) )
		partitionKey, pathTail = path[startLen:].split( '/', 1 )

		partitionedResults.setdefault( partitionKey, {} )[ pathTail ] = value

	return dict( (key, createDictTree( value, remainingPaths ))
					for key, value in partitionedResults.items() )


def _createTreeForProcess( process, subPaths, tolerateMissingPaths = True ):

	paths = [""]

	if subPaths[-1] == '':
		querySubPaths = subPaths[:-1]
	else:
		querySubPaths = subPaths

	for subPath in querySubPaths:
		paths = [path + subPath for path in paths]

		try:
			batchResult = WatcherDataMessage.batchQuery( paths, [process] )
		except ValueError, e:
			raise QueryTooBigError(
					"%s.\nProcess = %s\nNum paths = %d\nFirst path = %s" %
						(e.message, process.label(), len( paths ), paths[0]) )

		try:
			procResults = batchResult[ process ]
		except KeyError:
			procResults = {}

		if len( paths ) > len( procResults ):
			for path in paths:
				if path not in procResults:
					raise ResultsTooBigError( "Results too big.\n"
							"Expected %d results from %s but received %d.\n"
							"For example, no result for %s." %
						(len(paths), process.label(), len( procResults ), path) )

		for oldPath in procResults.keys():
			for value in procResults[ oldPath ]:
				if value[2] == watcher_constants.TYPE_UNKNOWN:
					if not tolerateMissingPaths:
						raise BadPathError( value[0], querySubPaths, process )
					else:
						log.debug( "process '%s' has no value for path '%s'",
							process.label(), value[0] )

		paths = [oldPath + '/' + value[0] + '/'
					for oldPath in procResults.keys()
						for value in procResults[oldPath]]

	return createDictTree( procResults, subPaths )


def _createTree( processes, subPaths ):
	keys = _createProcessKeys( processes )

	# TODO: It would be better if all processes were done in parallel
	values = dict( (key, _createTreeForProcess( process, subPaths ))
				for (key, process) in zip( keys, processes ) )

	return FilteredWatcherTree( values, subPaths )


def isTreeATable( tree ):
	return len( set( tuple( x.keys() ) for x in tree.values() ) ) == 1


def printTreeAsTable( tree, depth ):
	if depth > 2 or \
			((depth == 2) and not isTreeATable( tree )):
		for key, value in tree.items():
			print key
			printTreeAsTable( value, depth - 1 )
			print
		return

	if depth == 2:
		keys1 = tree.keys()
		keys2 = tree.values()[0].keys()

		print '	'.join( [''] + keys2 )
		for key in keys1:
			print '	'.join( [key] + [str(value[0]) for value in tree[key].values()] )

	else:
		print '	'.join( tree.keys() )
		print '	'.join( (value and str( value[0] )) or "" for value in tree.values() )


class FilteredWatcherTree( object ):
	def __init__( self, values, subPaths ):
		self.values = values
		self.subPaths = subPaths

	def depth( self ):
		return len( self.subPaths )

	def write( self, outFile = None ):
		import sys
		if outFile:
			oldStdout = sys.stdout
			sys.stdout = outFile

		printTreeAsTable( self.values, self.depth() )

		if outFile:
			sys.stdout = oldStdout

	def __json__( self ):
		return self.__dict__


def getFilteredTree( path, processes ):
	subPaths = _splitPath( path )
	return _createTree( processes, subPaths )

# watcher_tree_filter.py
