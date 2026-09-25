#!/usr/bin/env python

import watcher_constants as Constants

class Forwarding( object ):

	def __init__( self ):
		pass

	@staticmethod
	def forwardPaths( version ):
		paths = {}

		from process import Version

		if version < Version(2, 6, 0):
			# EXPOSE_ALL == EXPOSE_CELL_APPS
			paths[ Constants.EXPOSE_CELL_APPS ] =			\
				"forwardTo/all"
		else:
			paths[ Constants.EXPOSE_CELL_APPS ] =			\
				"forwardTo/cellApps"
			paths[ Constants.EXPOSE_BASE_APPS ] =			\
				"forwardTo/baseApps"
			paths[ Constants.EXPOSE_SERVICE_APPS ] =		\
				"forwardTo/serviceApps"
			paths[ Constants.EXPOSE_BASE_SERVICE_APPS ] =	\
				"forwardTo/baseServiceApps"

		paths[ Constants.EXPOSE_WITH_ENTITY ] =				\
			"forwardTo/withEntity"
		paths[ Constants.EXPOSE_WITH_SPACE ] =				\
			"forwardTo/withSpace"
		paths[ Constants.EXPOSE_LEAST_LOADED ] =			\
			"forwardTo/leastLoaded"
		paths[ Constants.EXPOSE_LOCAL_ONLY ] =				\
			""

		return paths

	@staticmethod
	def runTypeHintToWatcherPath( runType, version ):
		try:
			return Forwarding.forwardPaths( version )[ int(runType) ]
		except:
			raise TypeError( "Unable to map '%s' to a known forwarding path." \
							% str(runType) )

# watcher.py
