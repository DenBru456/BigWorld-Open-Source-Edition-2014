# TODO: Document this file and its classes and methods

from base_log_query_result import BaseLogQueryResult

from dateutil import tz


# convert tz module-wide to prevent having to perform lookups on every log line
tzlocal = tz.tzlocal()
tzutc = tz.tzutc()

class MongoDBLogQueryResult( BaseLogQueryResult ):

	def __init__( self, query, dbEntry, maxHostnamesLen = 0 ):
		BaseLogQueryResult.__init__( self )

		self._dbEntry = dbEntry
		self._query = query
		self._maxHostnamesLen = maxHostnamesLen


	#
	# Abstract function implementations - required by BaseLogQueryResult
	#

	def asDict( self ):
		return self._processLogLine( self._dbEntry )
	# asDict


	#
	# MongoDB-only implementation functions (not required at abstraction layer).
	#

	# Convert raw mongo document to data ready for display.
	def _processLogLine( self, dbEntry ):
		logLine = u''

		# reduce the number of lookups
		query = self._query
		columnFilter = self._query.parentQuery.columnFilter
		logStorageCharset = self._query.logReader.getCharset()
		previous = False

		if ('date' in columnFilter) or ('time' in columnFilter):
			dateTimeString = MongoDBLogQueryResult.dateTimeToString(
					dbEntry[ 'ts' ], columnFilter )
			logLine += dateTimeString + " "
			previous = True


		if 'host' in columnFilter:
			if previous:
				logLine += " "

			if 'host' in dbEntry:
				# host column is int32 in mongodb, but convert it to int again
				# because it happened to be float once in BWT-29001
				hostnameString = query.hostnames[ int( dbEntry[ 'host' ] ) ]
			else:
				hostnameString = ""
			logLine += "%-*s" % (self._maxHostnamesLen, hostnameString)
			previous = True


		if 'serveruser' in columnFilter:
			if previous:
				logLine += " "
			logLine += "%-10s" % query.serverUser
			previous = True


		if 'pid' in columnFilter:
			if previous:
				logLine += " "

			if 'pid' in dbEntry:
				pidStr = str( dbEntry[ 'pid' ] )
			else:
				pidStr = ""

			logLine += "%-5s" % pidStr
			previous = True


		if 'process' in columnFilter:
			if previous:
				logLine += " "

			if 'cpt' in dbEntry:
				component = query.components[ dbEntry[ 'cpt' ] ]
			else:
				component = ""

			logLine += "%-10s" % component
			previous = True


		if 'appid' in columnFilter:
			if previous:
				logLine += " "

			appIdStr = ""
			if 'aid' in dbEntry:
				appId = dbEntry[ 'aid' ]
				if appId != 0:
					appIdStr = str( appId )
				elif 'host' in dbEntry and 'pid' in dbEntry \
							and 'cpt' in dbEntry:
					appId = self._query.findAppID( dbEntry[ 'host' ],
										dbEntry[ 'pid' ], dbEntry[ 'cpt' ] )
					if appId != 0:
						appIdStr = str( appId )

			logLine += "%-3s" % appIdStr
			previous = True


		if 'source' in columnFilter:
			if previous:
				logLine += " "

			if 'src' in dbEntry:
				source = query.sources[ dbEntry[ 'src' ] ]
			else:
				source = ""

			logLine += "%-6s" % source
			previous = True


		if 'severity' in columnFilter:
			if previous:
				logLine += " "

			if 'svt' in dbEntry:
				severity = query.severities[ dbEntry[ 'svt' ] ]
			else:
				severity = ""

			logLine += "%-8s" % severity
			previous = True


		# Used to align loglines containing newline characters underneath each
		# other, in the same way bwlog.so does for MLDB
		messageColumn = len( logLine )

		if ('category' in columnFilter) and ('ctg' in dbEntry):
			if previous:
				logLine += " "

			categoryString = query.categories[ dbEntry[ 'ctg' ] ].strip()
			if categoryString:
				logLine += '[' + query.categories[ dbEntry[ 'ctg' ] ] + ']'
				previous = True
			else:
				previous = False


		# forced encoding required here otherwise python attempts to treat
		# logLine as ascii later on (eg. when appending)
		logLine = logLine.encode( logStorageCharset )


		if ('message' in columnFilter) and ('msg' in dbEntry):
			if previous:
				logLine += " "

			# To get a clean log message, strip whitespace from the end, as some
			# messages may or may not have newline chars. A newline will always
			# be reappended to the end of the log output regardless of whether
			# this field is displayed of not.
			messageText = dbEntry[ 'msg' ]
			messageLines = [ a.rstrip() \
							for a in messageText.rstrip().split("\n") ]

			if messageLines:
				# forced encoding here is necessary because higher level
				# functions default to ascii codec
				logLine += messageLines[0].encode( logStorageCharset )

				# Perform alignment of subsequent loglines, as bwlog.so does
				if len( messageLines ) > 1:
					extraLines = [ "%-*s" % (messageColumn, a) \
									for a in messageLines [1:] ]
					for line in extraLines:
						logLine += line.encode( logStorageCharset )


		# Regardless of what fields were displayed, always include a newline on
		# the end of the message to maintain backwards compatibility
		logLine += "\n"

		metadata = None
		if logLine != '':
			if ('md' in dbEntry) and (len( dbEntry[ 'md' ] ) > 0):
				metadata = dbEntry[ 'md' ]


		if self._query.translatePatts:
			for patt, repl in self._query.translatePatts.iteritems():
				logLine = patt.sub( repl, logLine )

		return {
			'message': logLine,
			'metadata': metadata
		}
	# processLogLine


	def processSummaryDisplay( self, summarizedColumns ):
		"""
		MongoDB-only implementation functions(not required at abstraction layer)
		Convert raw mongo document to data ready for summary display
		param:
			summarizedColumns: the summary display columns
		return:
			tuple contains dictionary of the summary display columns and the
			text string of the values
		"""
		group = {}

		# reduce the number of lookups
		query = self._query
		logStorageCharset = self._query.logReader.getCharset()

		if 'time' in summarizedColumns:
			timeString = MongoDBLogQueryResult.dateTimeToString(
					self._dbEntry[ 'ts' ], 'time' )

			group[ 'time' ] = timeString


		if 'host' in summarizedColumns:
			if 'host' in self._dbEntry:
				# host column is int32 in mongodb, but convert it to int again
				# because it happened to be float once in BWT-29001
				hostnameString = query.hostnames[ int( \
												self._dbEntry[ 'host' ] ) ]
			else:
				hostnameString = ""
			group[ 'host' ] = "%-*s" % (self._maxHostnamesLen, hostnameString)


		if 'username' in summarizedColumns:
			group[ 'username' ] = "%-10s" % query.serverUser


		if 'pid' in summarizedColumns:
			if 'pid' in self._dbEntry:
				pidStr = str( self._dbEntry[ 'pid' ] )
			else:
				pidStr = ""

			group[ 'pid' ] = "%-5s" % pidStr


		if 'component' in summarizedColumns:
			if 'cpt' in self._dbEntry:
				component = query.components[ self._dbEntry[ 'cpt' ] ]
			else:
				component = ""

			group[ 'component' ] = "%-10s" % component


		if 'appid' in summarizedColumns:
			appIdStr = ""
			if 'aid' in self._dbEntry:
				appId = self._dbEntry[ 'aid' ]
				if appId != 0:
					appIdStr = str( appId )
				elif 'host' in self._dbEntry and 'pid' in self._dbEntry \
							and 'cpt' in self._dbEntry:
					appId = self._query.findAppID( self._dbEntry[ 'host' ],
								self._dbEntry[ 'pid' ], self._dbEntry[ 'cpt' ] )
					if appId != 0:
						appIdStr = str( appId )

			group[ 'appid' ] = "%-3s" % appIdStr


		if 'severity' in summarizedColumns:
			if 'svt' in self._dbEntry:
				severity = query.severities[ self._dbEntry[ 'svt' ] ]
			else:
				severity = ""

			group[ 'severity' ] = "%-8s" % severity


		if ('message' in summarizedColumns) and ('msg' in self._dbEntry):
			# To get a clean log message, strip whitespace from the end, as some
			# messages may or may not have newline chars. A newline will always
			# be reappended to the end of the log output regardless of whether
			# this field is displayed of not.
			messageText = self._dbEntry[ 'msg' ]
			messageLines = [ a.rstrip() \
							for a in messageText.rstrip().split( "\n" ) ]

			group[ 'message' ] = ""

			if messageLines:
				for line in messageLines:
					group[ 'message' ] += line

		for key, value in group.items():
			group[ key ] = value.encode( logStorageCharset )

		return group, ' '.join( group.values() )
	# processSummaryDisplay


	@classmethod
	def dateTimeToString( cls, timeStampField, columnFilter = None ):
		dateTimeString = ""
		dateTimeFormat = ""

		showDate = (not columnFilter) or ('date' in columnFilter)
		showTime = (not columnFilter) or ('time' in columnFilter)

		if showDate:
			dateTimeFormat += "%a %d %b %Y"

		if showTime:
			if dateTimeFormat:
				dateTimeFormat += " "
			dateTimeFormat += "%T.%f"

		dateTimeString = timeStampField.replace( tzinfo = tzutc ) \
							.astimezone( tzlocal ) \
							.strftime( dateTimeFormat )

		if showTime:
			# strip microseconds
			dateTimeString = dateTimeString[:-3]

		return dateTimeString
	# dateTimeToString

# MongoDBLogQueryResult
