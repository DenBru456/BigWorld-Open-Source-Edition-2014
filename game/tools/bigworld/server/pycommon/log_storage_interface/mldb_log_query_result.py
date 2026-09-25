"""This file provides the general result processing from the PyQuery provided
by bwlog.so to the result format expected by the abstract log storage interface
layer."""

from base_log_query_result import BaseLogQueryResult

import logging
log = logging.getLogger( __name__ )

json = None
# simplejson is generally more comprehensive than the default json package,
# so try to rely on it by default.
try:
	import simplejson as json
except ImportError:
	try:
		import json
	except ImportError:
		log.warning( "No JSON module was loaded. "
			"Metadata will output as string" )


class MLDBLogQueryResult( BaseLogQueryResult ):

	def __init__( self, query, pyQueryResult ):
		BaseLogQueryResult.__init__( self )

		self._query = query
		self._translatePatts = self._query.getLogDB().translatePatts
		self._pyQueryResult = pyQueryResult


	#
	# Abstract function implementations - required by BaseLogQueryResult
	#

	def asDict( self ):
		message = self._pyQueryResult.format( self._query.filterMask )

		# Apply translation patterns if there are any
		if self._translatePatts:
			for patt, repl in self._translatePatts.iteritems():
				message = patt.sub( repl, message )

		metadata = self._pyQueryResult.metadata()
		if metadata and json:
			metadata = json.loads( metadata )

		return {
			'message': message,
			'metadata': metadata
		}

# MLDBLogQueryResult
