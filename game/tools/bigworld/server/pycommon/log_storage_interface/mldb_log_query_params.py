# TODO: Document this file and its classes and methods

import re
import time

# Local modules
from base_log_query_params import BaseLogQueryParams
from log_db_constants import MLDB_CHARSET
from log_reader_constants import PRE_INTERPOLATE, POST_INTERPOLATE, \
	DONT_INTERPOLATE, SERVER_STARTUP_STRING
from iterable import iterable

import bwsetup
bwsetup.addPath( "../.." )

# Other modules
import pycommon.bwlog as bwlog_module
from pycommon.exceptions import QueryParamException

_bwlog = bwlog_module._bwlog

# map abstract constants to bwlog constants
# TODO: Could be done better.
INTERPOLATE_MAP = {
	PRE_INTERPOLATE: _bwlog.PRE_INTERPOLATE,
	POST_INTERPOLATE: _bwlog.POST_INTERPOLATE,
	DONT_INTERPOLATE: _bwlog.DONT_INTERPOLATE,
}

import logging
log = logging.getLogger( __name__ )

class MLDBLogQueryParams( BaseLogQueryParams ):

	# The processing order of parameters. This is necessary because python 2.4
	# does not have an OrderedDict.
	# TODO: Change to OrderedDict after all dev environments have moved to 2.6+
	# python
	ORDERED_VALID_PARAMS = [
		"uid",
		"serveruser",
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
		"interpolate",
		"translate",
		"casesens",
		"context",
		"source",
		"categories",
		"negate_procs",
		"negate_severity",
		"negate_category",
		"negate_source",
		"negate_host",
		"negate_pid",
		"negate_appid",
	]


	# Not supported parameters for MLDB, only supported in MongoDB
	NOT_SUPPORTED_PARAMS_MLDB = [
		"metadata_key",
		"metadata_value",
		"negate_metadata_key",
		"negate_metadata_value",
	]

	def __init__( self, logQuery, params ):
		BaseLogQueryParams.__init__( self )

		self.PROCESS_PARAM_FUNCS = {
			# IMPORTANT: IN ORDER OF CONVERSION
			"serveruser":		self._convertServerUserToUID,
			"start":			self._convertStartTime,
			"end":				_convertEndTime,
			"procs":			self._convertProcsToMask,
			"severities":		self._convertSeveritiesToMask,
			"interpolate":		_convertInterpolateToBWLogValue,
			"source":			self._convertSourcesToMask,
			"categories":		self._convertCategoriesToMask,

			# 'None' process functions have the end result of not copying across
			# to the bwlog param list at all. These parameters are only used for
			# processing internally to this layer.
			"negate_procs":		None,
			"negate_severity":	None,
			"negate_category":	None,
			"negate_source":	None,
			"translate":		None,
		}


		# Defaults
		self.queryParams = {}
		self._originalParams = {}

		# Arguments
		self._logQuery = logQuery
		self._setParams( params )
	# __init__


	def _setParams( self, params ):
		self._originalParams = params

		# Validate every passed-in parameter first.
		#
		# This may seem like a roundabout way of doing things but it ensures
		# that we haven't been passed a parameter that is not in the valid list,
		# but still accomplishes conversion in the correct order.
		for item in params.items():
			if item[0] in self.NOT_SUPPORTED_PARAMS_MLDB:
				raise QueryParamException(
						"MLDBLogQueryParam: Not supported parameter: %s"
						% item[0] )
			elif item[0] not in self.ORDERED_VALID_PARAMS:
				raise QueryParamException(
						"MLDBLogQueryParam: Invalid parameter: %s" % item[0] )

		# Now copy or convert the values across in order (order is important)
		for paramName in self.ORDERED_VALID_PARAMS:
			if paramName in params.keys():
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
						convertedItem = processFunc( params[ paramName ] )
						if convertedItem:
							self.queryParams[ convertedItem[0] ] = convertedItem[1]
					# else conversion is "None", do not copy over
				except KeyError:
					# Not in the list of conversions. Do a straight copy of the
					# param name and value.
					self.queryParams[ paramName ] = params[ paramName ]
	# validateParams


	def getOriginalParamValue( self, paramName ):
		return self._originalParams.get( paramName, None )


	def getParamValue( self, paramName ):
		return self.queryParams.get( paramName, None )


	def _convertServerUserToUID( self, serveruser ):
		usermap = self._logQuery.getLogDB().getUsers()
		if serveruser not in usermap:
			raise QueryParamException(
					"Server user '%s' does not have any logs." % serveruser,
					paramName = 'serveruser', paramValue = serveruser )

		uid = usermap[ serveruser ]
		return ('uid', uid )
	# _convertServerUserToUID


	def _convertStartTime( self, startTime ):
		### param: startTime
		# If an event has been requested for the start time, calculate it

		if (type( startTime ) != str) and (type( startTime ) != unicode):
			try:
				self.queryParams[ "start" ] = float( startTime )
			except ValueError:
				raise QueryParamException(
						"Invalid start time '%s'." % startTime,
						paramName = "start", paramValue = startTime )
		else:

			# Look for "server startup" string
			if startTime.startswith( SERVER_STARTUP_STRING ):

				# Look for "server startup <n>"
				if len( startTime ) > len( SERVER_STARTUP_STRING ):
					startRegex = re.search( SERVER_STARTUP_STRING + " (\d+)",
											startTime )
					try:
						startupNumber, = startRegex.groups()
						startupNumber = int( startupNumber )
					except:
						raise QueryParamException(
								"Invalid startup '%s'." % startTime,
								paramName = 'start', paramValue = startTime )

					startups = self._logQuery.getLogDB().getUserLog(
							self.queryParams[ 'uid' ] ).getAllServerStartups()

					try:
						self.queryParams[ "startaddr" ] = \
								startups[ startupNumber ][1]
					except ( KeyError, IndexError ):
						raise QueryParamException(
							"Server startup '%d' not found." % startupNumber,
							paramName = 'start', paramValue = startTime )

					if startupNumber < len( startups ) - 1:
						self.queryParams[ "endaddr" ] = \
								startups[ startupNumber + 1 ][1]


				# Only "server startup" was provided. Get the last server
				# startup.
				else:
					lastStartup = self._logQuery.getLogDB().getUserLog(
						self.queryParams[ 'uid' ] ).getLastServerStartup()

					if lastStartup:
						self.queryParams[ 'start' ] = lastStartup[ 'entry' ].getTime()
					else:
						log.warning( "No server startup in log, starting from "
									"beginning" )
						self.queryParams[ "start" ] = _bwlog.LOG_BEGIN

			elif startTime == "now":
				self.queryParams[ "start" ] = time.time()

			elif startTime.startswith( 'beginning' ):
				self.queryParams[ "start" ] = _bwlog.LOG_BEGIN

			else:
				# fallback to a float conversion
				try:
					self.queryParams[ "start" ] = float( startTime )
				except ValueError, ex:
					raise QueryParamException(
							"Invalid start time '%s'." % startTime,
							paramName = "start", paramValue = startTime )
		return None
	# _convertStartTime


	def _convertProcsToMask( self, procs ):
		### param 'procs' -- filter by process type
		cnames = self._logQuery.getLogDB().getComponentNames()
		cnames = list( name.lower() for name in cnames )

		mask = 0
		for p in iterable( procs ):
			try:
				mask |= (1 << cnames.index( p.lower() ))
			except ValueError:
				raise QueryParamException(
						"Unknown process type '%s'" % p,
						paramName = 'procs', paramValue = p )

		if self._originalParams.has_key( 'negate_procs' ):
			mask = ~mask

		return ('procs', mask)
	# _convertProcsToMask


	def _convertSeveritiesToMask( self, severities ):
		### param 'severity' -- filter by log message severity
		mask = 0
		for s in iterable( severities ):
			i = _bwlog.SEVERITY_LEVELS.get( s )
			if i >= 0:
				mask |= (1 << i)
			else:
				raise QueryParamException(
					"Unknown severity '%s'" % s,
					paramName = 'severity', paramValue = s )

		if self._originalParams.has_key( 'negate_severity' ):
			mask = ~mask

		self.queryParams['severities'] = mask
		return ('severities', mask)
	# _convertSeveritiesToMask


	def _convertCategoriesToMask( self, categories ):
		### param 'category' -- filter by log message category
		categorySet = set()
		knownCategories = set( self._logQuery.getLogDB().getCategoryNames() )

		negate_category = self._originalParams.get( 'negate_category', False )
		charset = MLDB_CHARSET

		if negate_category:
			categorySet = knownCategories

			for cat in iterable( categories ):
				cat = cat.strip().encode( charset )

				try:
					categorySet.remove( cat )
				except KeyError:
					raise QueryParamException(
						"Unknown category '%s'" % cat,
						paramName = 'category', paramValue = cat )
		else:
			for cat in iterable( categories ):
				cat = cat.strip().encode( charset )
				if cat in knownCategories:
					categorySet.add( cat )
				else:
					raise QueryParamException(
						"Unknown category '%s'" % cat,
						paramName = 'category', paramValue = cat )

		return ('categories', tuple( categorySet ))
	# _convertCategoriesToMask


	def _convertSourcesToMask( self, sources ):
		### param 'source' -- filter by message source (c++ | python)
		mask = 0

		# case insensitive match for backwards compatibility
		CODE_SOURCE_TYPES = {}
		for sourceName, level in _bwlog.DebugMessageSource.iteritems():
			CODE_SOURCE_TYPES[ sourceName.lower() ] = level

		for sourceType in iterable( sources ):
			try:
				i = CODE_SOURCE_TYPES[ sourceType.lower() ]
			except KeyError:
				raise QueryParamException(
					"Unknown message source '%s'" % sourceType,
					paramName = 'source', paramValue = sourceType )
			if i >= 0:
				mask |= (1 << i)
			else:
				raise QueryParamException(
					"Unknown message source '%s'" % sourceType,
					paramName = 'source', paramValue = sourceType )

		if self._originalParams.has_key( 'negate_source' ):
			mask = ~mask

		return ('source', mask)
	# _convertSourcesToMask


def _convertEndTime( endTime ):
	try:
		endTime = float( endTime )
	except ValueError:
		raise QueryParamException(
				"Invalid end time '%s'." % endTime,
				paramName = "end", paramValue = endTime )
	return ('end', endTime )


def _convertInterpolateToBWLogValue( interpolateValue ):
	convertedValue = INTERPOLATE_MAP[ interpolateValue ]
	return ('interpolate', convertedValue)


# MLDBLogQueryParams
