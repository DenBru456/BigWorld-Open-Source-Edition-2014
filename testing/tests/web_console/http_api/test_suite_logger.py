import sys

from test_common import *
from bwtest import log

suite3 = TestSuite(
		name = 'Test suite 3: testing logger functionality',
		description = 'Will test all logger functions',
		tags = [] )


# scenario 1: test running log/search

class Scenario1( TestCase ):
	name = 'Test running log/search'
	description = 'Will run log/search and sanity check returned values'
	tags = []


	def step0( self ):
		"""run logs/search"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.logsSearch()

	def step1( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step2( self ):
		"""check mandatory sections are present"""
		required_sections = [
			'users', 'hostnames', 'components', 'serverTimezone',
			'severities', 'output_columns', 'default_columns',
			'categories', 'message_sources', 'mlstatus',
			'defaultQuery' ]

		for item in required_sections:
			if not item in self.context['json']:
				log.debug( "section %s not found in json" % item )
				assert False

# scenario 2: test running log/fetchAsync

class Scenario2( TestCase ):
	name = 'Test running log/fetchAsync'
	description = 'Will run log/fetchAsync and sanity check returned values, and then run /poll to see the results.'
	tags = []


	def step0( self ):
		"""run logs/fetchAsync"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.logsFetchAsync()

	def step1( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step2( self ):
		"""check 'id' is present"""
		assert 'id' in self.context['json']
		self.context['pollId'] =  self.context['json']['id']
		assert self.context['pollId']

	def step3( self ):
		"""run /poll?id=<value>"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.poll( self.context['pollId'] )

	def step4( self ):
		"""and check that returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step5( self ):
		"""and returned json contains 'status' and 'updates' sections"""
		required_sections = [ 'status', 'updates' ]

		for item in required_sections:
			if not item in self.context['json']:
				log.debug( "section %s not found in json" % item )
				log.debug( "gotten json is %r" % self.context['json'] )
				assert False


# scenario 3: test running log/fetchAsync with all options

class Scenario3( TestCase ):
	name = 'Test running log/fetchAsync with all options'
	description = 'Will run log/fetchAsync and sanity check returned values, and then run /poll to see the results.'
	tags = []




	def step0( self ):
		"""run logs/fetchAsync with all parameters"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.logsFetchAsync( 
			args = {
				'limit': 10,
				'live': False, 
				'context': 1,
				'show': [ 'date', 'time', 'host' ], 
				'queryTime': 'now', 
				'period': 'forwards',
				'periodUnit': 'hours', 
				'periodValue': 1, 
				'endAddr': 50, 
				'host': config.CLUSTER_MACHINES[0], 
				'serveruser': config.WCAPI_USER, 
				'pid': 123, 
				'appid': 123, 
				'procs': [ 'cellapp', 'baseapp' ], 
				'source': [ 'C++' ],
				'category': [ 'Bots', 'Chunk' ],
				'severity': [ 'TRACE' ],
				'message': '123',
				'casesens': False,
				'regex': False,
				'negate_procs': True,
				'negate_severity': True,
				'negate_category': False,
				'negate_source': False,
				'negate_host': False, 
				'negate_serveruser': False,
				'negate_pid': True,
				'negate_appid': True,
				'negate_message': True 
			}
		)

	def step1( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step2( self ):
		"""check "id" is present"""
		assert 'id' in self.context['json']
		self.context['pollId'] =  self.context['json']['id']
		assert self.context['pollId']

	def step3( self ):
		"""run /poll?id=<value>"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.poll( self.context['pollId'] )

	def step4( self ):
		"""and check that returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step5( self ):
		"""and returned json contains 'status' and 'updates' sections"""
		required_sections = [ 'status', 'updates' ]

		for item in required_sections:
			if not item in self.context['json']:
				log.debug( "section %s not found in json" % item )
				assert False


