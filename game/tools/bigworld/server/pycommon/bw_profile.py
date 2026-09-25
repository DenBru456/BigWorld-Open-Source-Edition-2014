

_moduleLoaded = 0


def isAvailable():
	return _moduleLoaded


def _shouldUseProfiling():
	"""Report whether the environment has been setup requesting
	the use of Profiling"""

	import os
	envStatus = os.getenv( 'BW_WEB_CONSOLE_PROFILING', False )
	return bool( (envStatus) and (envStatus != "0") )
# _shouldUseProfiling


# Initialisation - Module loading functionality
if _shouldUseProfiling():
	try:
		import thread

		import bw_shared_object_path
		from _bw_profile import *

		_orig_start_new = thread.start_new_thread

		def bootstrap( func ):
			def newfunc( *args, **kwargs ):
				import _bw_profile
				result = None
				_bw_profile.__onThreadStart( getattr( func, '__name__', "Unknown" ) )
				try:
					result = func( *args, **kwargs )
				finally:
					_bw_profile.__onThreadEnd()
				return result
		
			return newfunc

		def hooked_start_new( func, *args, **kwargs ):
			return _orig_start_new( bootstrap( func ), *args, **kwargs )

		thread.start_new_thread = hooked_start_new


		class _BWProfileDumpState:
			"""This is an elegant way of not only keeping the enumerators consistent
			but also of handling unexpected modifications to the C++
			enumerators. If the expected values do not exist then an exception
			will prevent this module from loading"""
			try:
				INACTIVE=getJsonDumpStateValue( "JSON_DUMPING_INACTIVE" )
				ACTIVE=getJsonDumpStateValue( "JSON_DUMPING_ACTIVE" )
				COMPLETED=getJsonDumpStateValue( "JSON_DUMPING_COMPLETED" )
				FAILED=getJsonDumpStateValue( "JSON_DUMPING_FAILED" )
			except:
				# logging for this exception is handled by the _bw_profile module
				import sys
				sys.exit( 1 )
		# _BWProfileDumpState


		def getJsonDumpStatusInfo():
			"""@returns a dict containing:
			- statusText: display-friendly string indicating current dump status
			- isEnabled: profiler currently enabled as a boolean"""
			_dumpStatus = getJsonDumpState()

			if not isEnabled():
				_statusText = "Disabled"
			else:
				# when isEnabled() then INACTIVE means Enabled but not yet
				# dumping - ie. Pending
				_statusText = {
					_BWProfileDumpState.INACTIVE:	"Pending",
					_BWProfileDumpState.ACTIVE:		"Dumping",
					_BWProfileDumpState.COMPLETED:	"Completed",
					_BWProfileDumpState.FAILED:		"Failed"
				}.get( _dumpStatus,					"Unknown" )

			_isEnabled = 0
			if isEnabled():
				_isEnabled = 1

			_outputFilePath = ""
			if _isEnabled and _dumpStatus != _BWProfileDumpState.INACTIVE:
				_outputFilePath = getJsonOutputFilePath()

			return dict ( statusText = _statusText, isEnabled = _isEnabled,
				outputFilePath = _outputFilePath )
		# getJsonDumpStatusInfo


		_moduleLoaded = 1


	except Exception, ex:
		import logging

		logging.basicConfig()
		log = logging.getLogger( __name__ )
		log.error( "Unable to load bw_profile: %s\n", str( ex ) )

		import sys
		sys.exit( 1 )

else:
	"""This is a set of stubs to replace expected _bw_profile functions when
	not configured"""
	def enable():
		pass
	def isEnabled():
		return 0
	def tick():
		pass
	def startJsonDump():
		pass
	def setJsonDumpCount():
		pass
	def setJsonDumpDir():
		pass
	def getJsonDumpState():
		return 0
	def getJsonDumpStatusInfo():
		return dict( statusText = "Unknown", isActive = False )
	def getJsonOutputFilePath():
		return dict()
