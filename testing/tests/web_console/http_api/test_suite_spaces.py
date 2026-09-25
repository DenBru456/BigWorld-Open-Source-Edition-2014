import sys
import time

from test_common import *

from bwtest import log


# Test suite 4: testing space functionality

suite4 = TestSuite( 
		name = 'Test suite 4: testing spaces functionality',
		description = 'Will test all spaces functions',
		tags = [] )



# scenario 1: test running sv/api/spaces

class Scenario1( TestCase ):
	name = 'Test running sv/api/spaces'
	description = 'Will run sv/api/spaces and sanity check returned values.'
	tags = []


	def step0( self ):
		"""given server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run sv/api/spaces"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.spaceSpaces( limit=2, index=1 )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""check "spaceList" is present"""
		log.debug( 'returned json: %s' % self.context['json'] )
		assert 'spaceList' in self.context['json']

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 2: test running sv/get_space

class Scenario2( TestCase ):
	name = 'Test running sv/get_space'
	description = 'Will run sv/get_space and sanity check returned values.'
	tags = []


	def step0( self ):
		"""given server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run sv/get_space"""
		time.sleep( 1 )
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.spaceGetSpace( spaceId=config.WCAPI_SPACE, cellId=1 )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""check required items are present"""
		log.debug( "Returned json: %r" % self.context['json'] )

		required_sections = [
			'spaceBounds', 'mappings', 'gridResolution', 'selectedCell',
			'stats', 'root' ]

		for item in required_sections:
			if not item in self.context['json']:
				log.debug( "section %s not found in json" % item )
			assert item in self.context['json']

		stats = self.context['json']['stats']
		assert stats

		stats_req = [ 
			'minLoad', 'avgLoad', 'maxLoad', 'cellapps', 'cells' ]

		for item in stats_req:
			if not item in stats:
				log.debug( "section %s not found in stats" % item )
				assert False

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


# scenario 3: test running sv/get_entity_types

class Scenario3( TestCase ):
	name = 'Test running sv/get_entity_types'
	description = 'Will run sv/get_entity_types and sanity check returned values.'
	tags = []


	def step0( self ):
		"""given server is restarted"""
		assert( TestCommon.restartServer() )

	def step1( self ):
		"""run sv/get_entity_types"""
		w = StartWebConsoleAPI()
		self.context['code'], self.context['json'] = w.spaceGetEntityTypes( spaceId=config.WCAPI_SPACE )

	def step2( self ):
		"""check returned code is 200 (OK)"""
		assert( self.context['code'] == 200 )

	def step3( self ):
		"""check required items are present: json output"""
		assert len(self.context['json']) > 0

	def tearDown( self ):
		"""PostRun: shut down server"""
		assert( TestCommon.stopServer() )
		TestCommon.clean()


