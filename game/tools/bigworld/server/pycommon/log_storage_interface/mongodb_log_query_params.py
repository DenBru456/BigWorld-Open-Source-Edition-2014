import pymongo
import re
import datetime
from dateutil import tz

from base_log_query_params import BaseLogQueryParams
from pycommon.exceptions import QueryParamException
from log_reader_constants import SERVER_STARTUP_STRING, QUERY_TO_BEGINNING, \
	QUERY_TO_PRESENT, QUERY_BEGINNING_OF_LOGS, QUERY_NOW
from iterable import iterable


def _negateParam( paramToNegate ):
	return ( paramToNegate[0], { '$nin': paramToNegate[1][ '$in' ] } )
# _negateParam


class MongoDBLogQueryParams( BaseLogQueryParams ):

	# The processing order of parameters. This is necessary because python 2.4
	# does not have an OrderedDict.
	# TODO: Change to OrderedDict after all dev environments have moved to 2.6+
	# python
	ORDERED_VALID_PARAMS = [
		"start",
		"end",
		"period",
		"host",
		"pid",
		"appid",
		"procs",
		"severities",
		"message",
		"exclude",
		"casesens",
		"source",
		"categories",
		"metadata_key",
		"metadata_value",
		"negate_procs",
		"negate_severity",
		"negate_category",
		"negate_source",
		"negate_host",
		"negate_pid",
		"negate_appid",
		"negate_metadata_key",
		"negate_metadata_value",
	]

	def __init__( self, logReader, query, params ):
		BaseLogQueryParams.__init__( self )

		self.PROCESS_PARAM_FUNCS = {
			'start': 			self._convertStartTime,
			'end': 				self._convertEndTime,
			'period':			self._convertPeriod,
			'host': 			self._convertHost,
			'pid':				self._convertPid,
			'appid': 			self._convertAppId,
			'procs': 			self._convertProcs,
			'severities': 		self._convertSeverities,
			'message': 			self._convertMessage,
			'exclude': 			self._convertExclude,
			'casesens': 		self._convertCaseSensitivity,
			'source': 			self._convertSource,
			'categories':		self._convertCategories,
			'metadata_key':		self._convertMetadata,

			# 'None' process functions have the end result of not copying across
			# to the new param list at all. These parameters are only used for
			# processing internally to this layer.
			'metadata_value':			None, # handled by self._convertMetadata
			"negate_procs":				None,
			"negate_severity":			None,
			"negate_category":			None,
			"negate_source":			None,
			"negate_host":				None,
			"negate_pid":				None,
			"negate_appid":				None,
			"negate_metadata_key":		None,
			"negate_metadata_value":	None,
			"interpolate":				None,
		}

		self._logReader = logReader
		self._query = query
		self.params = {}
		self._abstractParams = {}

		self._setParams( params )
	# __init__


	def _setParams( self, parameters ):
		self._abstractParams = dict( parameters )

		# server user is not needed in the query parameters.
		if 'serveruser' in self._abstractParams:
			del self._abstractParams[ 'serveruser' ]

		# interpolate has no meaning in MongoDB (but if it is provided it is not
		# erroneous, we can simply ignore it)
		if "interpolate" in self._abstractParams:
			del self._abstractParams[ 'interpolate' ]

		# If message or exclude are '', remove them, otherwise MongoDB will
		# attempt to match an empty string
		if ('message' in self._abstractParams) and \
				(self._abstractParams[ 'message' ] == ''):
			del self._abstractParams[ 'message' ]
		if ('exclude' in self._abstractParams) and \
				(self._abstractParams[ 'exclude' ] == ''):
			del self._abstractParams[ 'exclude' ]


		# If neither message nor exclude are present, delete casesens
		if (not 'message' in self._abstractParams) and \
				(not 'exclude' in self._abstractParams) and \
				('casesens' in self._abstractParams):
			del self._abstractParams[ 'casesens' ]


		# appid and pid are set to zero when no filter is set. Remove them so
		# MongoDB does not attempt to match value 0.
		if ('pid' in self._abstractParams) and \
				(self._abstractParams[ 'pid' ] == 0):
			del self._abstractParams[ 'pid' ]
		if ('appid' in self._abstractParams) and \
				(self._abstractParams[ 'appid' ] == 0):
			del self._abstractParams[ 'appid' ]

		# translate is not needed in the query parameters.
		if 'translate' in self._abstractParams:
			del self._abstractParams[ 'translate' ]


		self._validateMetadataParams( self._abstractParams )


		# Validate every passed-in parameter first.
		#
		# This may seem like a roundabout way of doing things but it ensures
		# that we haven't been passed a parameter that is not in the valid list,
		# but still accomplishes conversion in the correct order.
		for item in self._abstractParams.items():
			if item[0] not in self.ORDERED_VALID_PARAMS:
				raise QueryParamException(
					"MongoDBLogQueryParam: Invalid parameter: %s" % item[0] )

		# Now copy or convert the values across in order (order is important)
		for paramName in self.ORDERED_VALID_PARAMS:
			if paramName in self._abstractParams.keys():
				try:
					# Test to see if the current parameter is in the list of
					# params to convert
					processFunc = self.PROCESS_PARAM_FUNCS[ paramName ]

					# Param is in the list to convert. Only if it has a valid
					# function then call the function. If function type is
					# "None" the the param will not be converted or copied to
					# the new DB params
					if processFunc:
						# Call the conversion function
						convertedItem = processFunc( self._abstractParams[ paramName ] )
						if convertedItem:
							self.params[ convertedItem[0] ] = convertedItem[1]
					# else conversion is "None", do not copy over
				except KeyError:
					# Not in the list of conversions. Do a straight copy of the
					# param name and value.
					self.params[ paramName ] = self._abstractParams[ paramName ]
	# setParams


	def resetTimeParam( self, dateObj, counter, queryDirection, contains ):
		"""
		Reset the time parameter.
		"""

		if queryDirection == pymongo.ASCENDING:
			direction = '$gt'
		else:
			direction = '$lt'

		includesDirection = direction
		if contains:
			includesDirection += 'e'

		self.params[ '$or' ] = [
			{ 'ts': dateObj, 'cnt': { includesDirection: counter } },
			{ 'ts': { direction: dateObj } }
		]

		# Need to make sure this is updated to remove any other time-related
		# query parameters that have been added:
		self.params.pop( 'ts', None )

	# resetTimeParam


	def _validateMetadataParams( self, abstractParams ):
		# negate_metadata_key is only possible if a key exists and has no value
		if (('negate_metadata_key' in abstractParams) and \
				(abstractParams['negate_metadata_key'])) and \
				(('metadata_value' in abstractParams) or \
				('metadata_key' not in abstractParams)):

			raise QueryParamException(
				"Unable to negate metadata key, requires metadata_key "
				"and must not have metadata_value",
				paramName = 'negate_metadata_key',
				paramValue = abstractParams[ 'negate_metadata_key' ] )


		# negate_metadata_value is only possible when a value and key exist
		if (('negate_metadata_value' in abstractParams) and \
				(abstractParams['negate_metadata_value'])) and \
				('metadata_key' not in abstractParams):

			raise QueryParamException(
				"Unable to negate metadata value, requires both metadata_key "
				"and metadata_value",
				paramName = 'negate_metadata_value',
				paramValue = abstractParams[ 'negate_metadata_value' ] )


		# metadata_value is only possible when a key exists
		if 'metadata_value' in abstractParams and \
				'metadata_key' not in abstractParams:

			raise QueryParamException(
				"metadata_value requires a metadata_key",
				paramName = 'metadata_value',
				paramValue = abstractParams[ 'metadata_value' ] )

	# _validateMetadataParams


	def _convertStartTime( self, startTimeParam ):

		# Could be 'server startup x', 'beginning of logs', 'now' or a time.
		# Query date range greater than provided start time or converted 
		# startup time.
		if isinstance( startTimeParam, basestring ) and \
			(SERVER_STARTUP_STRING in startTimeParam):

			if startTimeParam == SERVER_STARTUP_STRING:
				datetimeParam = self._logReader.getLastServerStartupDateTime(
													self._query.serverUser )
				if datetimeParam is None:
					# Do not add a $gte parameter at all if there are no
					# startups. This will start from beginning of logs.
					return None
			else:
				try:
					startupNumber = \
						int( startTimeParam[ startTimeParam.rindex(' ')+1: ] )
				except ValueError:
					raise QueryParamException(
							"Invalid startup '%s'." % startTimeParam,
							paramName = 'start', paramValue = startTimeParam )

				try:
					datetimeParam = self._logReader.getServerStartupDateTime(
						self._query.serverUser, startupNumber )

					if datetimeParam is None:
						return None

				except KeyError:
					# No startups available. Go back to beginning
					return None

		elif startTimeParam == QUERY_BEGINNING_OF_LOGS:
			# Get the time of first log in database. This would be useful when
			# qeury from beginning of logs and specify forwards
			datetimeParam = self._query.getLogBeginningTime()

			if not datetimeParam:
				return None

		elif startTimeParam == QUERY_NOW:

			datetimeParam = datetime.datetime.now().replace(
				tzinfo = tz.tzlocal() ).astimezone( tz.tzutc() ) \
				.replace(tzinfo = None)

		else:

			# Number of seconds since epoch. Convert to datetime
			datetimeParam = datetime.datetime.fromtimestamp(
				float( startTimeParam ) ) \
				.replace( tzinfo = tz.tzlocal() ).astimezone( tz.tzutc() ) \
				.replace( tzinfo = None )

		return ( 'ts', { '$gte': datetimeParam } )

	# convertStartTime


	def _convertEndTime( self, endTimeParam ):

		# If time param already exists, add less than end time to it
		datetimeParam = \
				datetime.datetime.fromtimestamp( float( endTimeParam ) ) \
				.replace( tzinfo = tz.tzlocal() ).astimezone( tz.tzutc() ) \
				.replace(tzinfo = None)

		# 'ts' may have already been set by convertStartTime
		if 'ts' in self.params:
			# append to the existing parameter and return that
			self.params[ 'ts' ][ '$lte' ] = datetimeParam
			return ( 'ts', self.params[ 'ts' ] )

		else:
			return ( 'ts', { '$lte': datetimeParam } )
	# convertEndTime


	def _convertPeriod( self, periodValue ):
		# Adjust time param's $gte and $lte fields based on period passed in
		# Can be 'to present' 'to beginning' or +- a number of seconds.
		# If blank, assume querying all logs.

		if periodValue == QUERY_TO_PRESENT:

			if 'ts' in self.params:
				if '$gte' in self.params[ 'ts' ]:
					self._query.parentQuery.querySort = pymongo.ASCENDING
					if '$lte' in self.params[ 'ts' ]:
						del self.params[ 'ts' ][ '$lte' ]
				else:
					del self.params[ 'ts' ]

		elif periodValue == QUERY_TO_BEGINNING:

			self._query.parentQuery.querySort = pymongo.DESCENDING
			if 'ts' in self.params:
				if '$gte' in self.params[ 'ts' ]:
					self.params[ 'ts' ][ '$lte' ] = \
							self.params[ 'ts' ][ '$gte' ]
					del self.params[ 'ts' ][ '$gte' ]

		else:
			isEitherSide = ( periodValue[0] not in '+-' )

			startTime = self.params[ 'ts' ][ '$gte' ]
			periodValue = float( periodValue )

			timeDelta = datetime.timedelta(	seconds = periodValue )

			if isEitherSide:
				endTime = startTime + timeDelta
				startTime = startTime - timeDelta

			elif periodValue < 0:
				self._query.parentQuery.querySort = pymongo.DESCENDING

				endTime = startTime
				startTime = startTime + timeDelta

			else:
				self._query.parentQuery.querySort = pymongo.ASCENDING

				endTime = startTime + timeDelta

			self.params[ 'ts' ][ '$gte' ] = startTime
			self.params[ 'ts' ][ '$lte' ] = endTime
	# convertPeriod


	def _convertHost( self, hostnames ):

		# Passed in as name, need IP for query
		hostnameIps = []

		hostnamesMap = dict( (x, y) for (y, x) in \
				self._query.hostnames.items() )

		for h in iterable( hostnames ):
			try:
				hostnameIps.append( hostnamesMap[ h ] )
			except KeyError:
				# Not a big deal. This hostname may be recored by other 
				# Message Logger not by this one.
				pass

		param = ( 'host', { '$in': hostnameIps } )

		try:
			if self._abstractParams[ 'negate_host' ]:
				param = _negateParam( param )
		except KeyError:
			pass

		return param
	# convertHost


	def _convertPid( self, pidParam ):

		pidList = [ int( p ) for p in iterable( pidParam ) ]
		param = ( 'pid', { '$in': pidList } )

		try:
			if self._abstractParams[ 'negate_pid' ]:
				param = _negateParam( param )
		except KeyError:
			pass


		return param
	# convertPid


	def _convertAppId( self, appIdParam ):

		appIdList = [ int( a ) for a in iterable( appIdParam ) ]
		# Include entries with no AppId
		appIdList.append( 0 )
		param = ( 'aid', { '$in': appIdList } )

		try:
			if self._abstractParams[ 'negate_appid' ]:
				# Remove the 0 AppId added above when negating
				param[1][ '$in' ].pop()
				param = _negateParam( param )
		except KeyError:
			pass

		return param
	# convertAppId


	def _convertProcs( self, processes ):

		# Passed as names. Get list of components and resolve for list of IDs.
		componentIds = []
		componentsMap = dict(( x, y) for (y, x) in self._query.components.items() )

		for p in iterable( processes ):
			try:
				componentIds.append( componentsMap[ p ] )
			except KeyError:
				# Not a big deal. This process type may be recored by other 
				# Message Logger not by this one.
				pass

		param = ( 'cpt', { '$in': componentIds } )

		try:
			if self._abstractParams[ 'negate_procs' ]:
				param = _negateParam( param )
		except KeyError:
			pass

		return param
	# convertProcs


	def _convertSeverities( self, severities ):

		# Passed as names. Get list of severities and resolve for list of IDs.
		severityIds = []
		severitiesMap = dict( (x, y) for (y, x) in \
				self._query.severities.items() )

		for s in iterable( severities ):
			# If there's a mismatch between different databases, ignore it
			# for this database, rather than fail completely.
			if s in severitiesMap:
				severityIds.append( severitiesMap[ s ] )

		param = ( 'svt', { '$in': severityIds } )

		try:
			if self._abstractParams[ 'negate_severity' ]:
				param = _negateParam( param )
		except KeyError:
			pass

		return param
	# convertSeverities


	def _convertMessage( self, messageParam ):
		# Passed in as regex pattern. Add to existing msg param if it exists.
		if 'msg' in self.params:
			self.params[ 'msg' ][ '$in' ] = [ re.compile( messageParam ) ]
			return ( 'msg', self.params[ 'msg' ] )
		else:
			return( 'msg', { '$in': [ re.compile( messageParam ) ] } )
	# convertMessage


	def _convertExclude( self, excludeParam ):
		# An exclusion regex pattern. Add to existing msg param if it exists.
		if 'msg' in self.params:
			self.params[ 'msg' ][ '$nin' ] = [ re.compile( excludeParam ) ]
			return ( 'msg', self.params[ 'msg' ] )
		else:
			return ( 'msg', { '$nin': [ re.compile( excludeParam ) ] } )
	# convertExclude


	def _convertCaseSensitivity( self, caseSenseParam ):
		# Recompile msg param regexes with case insensitivity flag
		if not caseSenseParam and 'msg' in self.params:
			msgParam = self.params[ 'msg' ]
			if '$in' in msgParam:
				msgParam[ '$in' ] = [ re.compile(
						msgParam[ '$in' ][0].pattern, re.IGNORECASE ) ]
			if '$nin' in msgParam:
				msgParam[ '$nin' ] = [ re.compile(
						msgParam[ '$nin' ][0].pattern, re.IGNORECASE ) ]

			return ( 'msg', msgParam )
	# convertCaseSensitivity


	def _convertSource( self, sources ):

		# Passed as names. Get list of sources and resolve for list of IDs.
		sourceIds = []
		sourcesMap = dict( (x.lower(), y) for (y, x) in
						self._query.sources.items() )

		for s in iterable( sources ):
			# If there's a mismatch between different databases, ignore it
			# for this database, rather than fail completely.
			if s.lower() in sourcesMap:
				sourceIds.append( sourcesMap[ s.lower() ] )

		param = ( 'src', { '$in': sourceIds } )

		try:
			if self._abstractParams[ 'negate_source' ]:
				param = _negateParam( param )
		except KeyError:
			pass

		return param
	# convertSources


	def _convertCategories( self, categories ):

		# Passed as names. Get list of categories and resolve for list of IDs.
		categoryIds = []
		categoriesMap = dict( (x, y) for (y, x) in \
				self._query.categories.items() )

		for c in iterable( categories ):
			try:
				categoryIds.append( categoriesMap[ c ] )
			except KeyError:
				pass

		param = ( 'ctg', { '$in': categoryIds } )

		try:
			if self._abstractParams[ 'negate_category' ]:
				param = _negateParam( param )
		except KeyError:
			pass

		return param
	# convertCategories


	def _convertMetadata( self, metadataKey ):

		# Pre-validation of metadata key combinations occur in _setParams

		# If value has been set, add a full filter,
		# Else add as $exists.
		if 'metadata_value' in self._abstractParams:

			metadataValue = self._abstractParams[ 'metadata_value' ]
			param = ( 'md.' + metadataKey, metadataValue )

			try:
				if self._abstractParams[ 'negate_metadata_value' ]:
					param = ( 'md.' + metadataKey,
							{ '$exists': True, '$ne': metadataValue } )
			except KeyError:
				pass

		else:

			param = ( 'md.' + metadataKey, { '$exists': True } )

			try:
				if self._abstractParams[ 'negate_metadata_key' ]:
					param = ( 'md.' + metadataKey, { '$exists':
						not self._abstractParams[ 'negate_metadata_key' ] } )
			except KeyError:
				pass

		return param
	# convertMetadata


# MongoDBLogQueryParams
