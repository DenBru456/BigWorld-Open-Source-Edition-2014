import os
import time

from bwtest import TestCase, config
from primitives import manual, locallog
from helpers.cluster import ClusterController, ClusterControllerError
from helpers.timer import runTimer, TimerError
from template_reader import TemplateReader

class OnRestoreClientTest( TestCase ):
	
	
	name = "onRestoreClient test"
	description = "Semi-automated test that tests the functionality"\
				  " of on_restore_client using SDL client BWClient and Bots"
	tags = ["WIP", "MANUAL"]
	
	
	def setUp( self ):
		self.assertTrue( manual.input_passfail( """
		This test requires you to apply a patch to your 
		client and server source trees.
		Please apply the patch found at %s and 
		re-compile the server and SDL client.

		You will also need to have a functioning BWClient 
		but it doesn't need to be re-compiled.
		""" % os.path.join( config.TEST_ROOT, "tests", "fault_tolerance", 
						"TEST-Generate-controlled-CellApp-restore.patch"  ) ) )
		
		
		self._cc = ClusterController( config.CLUSTER_BW_ROOT 
											+ "/game/res/fantasydemo" )
		xmlPath = config.TEST_ROOT + \
				"/tests/fault_tolerance/on_restore_client_layout.xml"
		self._cc.start( 
			layoutXML = TemplateReader( xmlPath, machine=self._cc._machines[0] ) )
		self._cc.startProc( "bots" )
		self.lastBotsLogLength = 0
		
		
	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()
		
	
	def getAndCheckProxyIDs( self ):
		snippet = """
		ret = {}
		for id, obj in BigWorld.entities.items():
			if "Avatar" in obj.__class__.__name__:
				if obj.isBot():
					ret["b"] = id
				elif obj.basePlayerName.startswith("SDLClient"):
					ret["s"] = id
				else:
					ret["c"] = id
		srvtest.finish(ret)
		"""

		ids = self._cc.sendAndCallOnApp( "baseapp", 1, snippet )
		ret = self.findCellAppId(ids)
		while not ret:
			manual.input_yesno( """
			Please move the SDLClient and BWClient so that 
			they are on the same cell as the bot""" )
			ret = self.findCellAppId(ids)
		return ret
		

	def findCellAppId( self, ids):
		while True:
			for cellApp in self._cc.getWatcherData( "cellApps", "cellappmgr", None).getChildren():
				procOrd = cellApp.getChild( "id" ).value
				entities = self._cc.getWatcherData( "entities", "cellapp", procOrd )
				cellIds = []
				foundSeat = None
				for ent in entities:
					entityId = int( ent.name )
					entityType = ent.getChild( "type" ).value
					entityHaunts = ent.getChild( "haunts" ).value
					if entityHaunts and int( entityHaunts ) == -1:
						continue
					if entityId in ids.values():
						cellIds.append(entityType)
					if entityType == "Seat" and not foundSeat:
						foundSeat = entityId
				if foundSeat and len( cellIds ) == len( ids ):
					if "v" not in ids: ids["v"] = foundSeat
					return procOrd, ids
			else:
				return False


	def checkFragsOnCellApp( self, cellAppId,  ids ):
		frags = {}
		checkOnCellapp = """
ids = {ids}
c = BigWorld.entities[ids['c']]
b = BigWorld.entities[ids['b']]
s = BigWorld.entities[ids['s']]
v = BigWorld.entities[ids['v']]
srvtest.assertTrue( c.isReal() )
srvtest.assertTrue( b.isReal() )
srvtest.assertTrue( s.isReal() )
srvtest.assertTrue( v.isReal() )
srvtest.finish( (c.frags, b.frags, s.frags) )
"""
		
		frags['c'], frags['b'], frags['s'] = self._cc.sendAndCallOnApp( "cellapp", 
												cellAppId, checkOnCellapp, ids = ids )
		return frags
	
	def generateCellAppCrash( self, order, expectedRollBack, 
							ids, frags, cellAppId, additionalCommands = "" ):
		expectedMessages = ""
		fragCommands = ""
		for proxy in order:
			expectedMessages += "Avatar.set_frags: set_frags( %s ): %s=>%s\n"\
							% (ids[proxy], frags[proxy], frags[proxy]+1)
			expectedMessages += "AvatarGameLogic( %s )::set_frags: %s => %s\n"\
							% (ids[proxy], frags[proxy], frags[proxy]+1)
		if expectedRollBack == "s":
			expectedMessages += "AvatarGameLogic( %s )::reset_frags: %s => %s\n"\
							% (ids['s'], frags['s']+1, frags['s'])
			expectedMessages += "AvatarGameLogic( %s )::set_frags: %s => %s\n"\
							% (ids['s'], frags['s']+1, frags['s'])
		elif expectedRollBack == 'c':
			expectedMessages += "Avatar.reset_frags: reset_frags( %s ): %s=>%s\n"\
							% (ids['c'], frags['c']+1, frags['c'])
			expectedMessages += "Avatar.set_frags: set_frags( %s ): %s=>%s\n"\
								% (ids['c'], frags['c']+1, frags['c'])
			
		
		self.assertTrue( manual.input_yesno( """
The test will now generate a cellapp crash on restore.  Make sure you can see
both your SDLclient window and BWClient window.
Expected result:
All entities should disappear and reappear on both clients.
The following messages should appear in DebugView:
%s

Ready to continue?
""" % expectedMessages ) )
		
		snippet = "ids = {ids}\n"
		for proxy in order:
			snippet += "%s = BigWorld.entities[ ids['%s']]\n" % (proxy, proxy)
		snippet += additionalCommands
		for proxy in order:
			snippet += "%s.frags += 1\n" % proxy

		try:
			self._cc.sendAndCallOnApp( "cellapp", cellAppId, snippet, ids = ids )
		except ClusterControllerError:
			pass
		
		try:
			runTimer( self._cc._checkForCoreDumps, 
							lambda res: res == ["cellapp"],
							expectedFailures = ['cellapp'] )
		except TimerError:
			self.fail( "CellApp did not crash as expected." )
		
		self._cc.startProc( "cellapp", 1 )
		
	
	def checkFragsOnBotsAndClient( self, ids, frags, expectedBotMessages ):
		snippet = """
		ids = {ids}
		frags = {frags}
		c = BigWorld.bots.values()[0].entities[ ids['c'] ]
		b = BigWorld.bots.values()[0].entities[ ids['b'] ]
		s = BigWorld.bots.values()[0].entities[ ids['s'] ]
		srvtest.assertTrue( c.frags == frags['c'])
		srvtest.assertTrue( b.frags == frags['b'] )
		srvtest.assertTrue( s.frags == frags['s'] )
		srvtest.finish()
		"""

		self._cc.sendAndCallOnApp( "bots", snippet = snippet,
								   ids = ids, 
								   frags = frags)
		out = locallog.grepLastServerLog( "set_frags", process = "Bots", \
										 ).split( "\n" )
		
		self.assertTrue( len(out) in [x + self.lastBotsLogLength 
											for x in expectedBotMessages], 
						"Didn't find expected messages on bots")
		self.lastBotsLogLength = len(out)
		pythonCommand = """
		c = BigWorld.entities[%s]
		b = BigWorld.entities[%s]
		s = BigWorld.entities[%s]
		c.frags; b.frags; s.frags
		""" % (ids['c'], ids['b'], ids['s'])

		self.assertTrue( manual.input_passfail("""
		As a final test, input the following command in your BWclient's python console"
		%s
		Expected result:
		%s 
		%s
		%s
		""" % ( pythonCommand, frags['c'], frags['b'], frags['s'] ) ) )
		
		
	def step1( self ):
		"""Client-controlled entities on the ground"""
		
		loginPort = self._cc.getWatcherValue( "nubExternal/address", 
											  "loginapp" ).split(':')[1]
		self.assertTrue( manual.input_passfail( """
		Please connect an SDL client and a BigWorld client to the server at
		%s:%s
		Make sure you also have DeubgView open.
		""" % (self._cc._machines[0], loginPort ) ) )
		
		cellAppId, ids = self.getAndCheckProxyIDs()	
		
		snippet = """
		pos = BigWorld.entities[%s].position
		srvtest.finish( ( pos.x, pos.y, pos.z ) )
		""" % ids['s']
		
		x, y, z = self._cc.sendAndCallOnApp( "cellapp", cellAppId, snippet )
		self._cc.bots.add( 1 )
		
		
		snippet = """
		import Math
		BigWorld.bots.values()[0].stop()
		BigWorld.bots.values()[0].snapTo( Math.Vector3( %s, %s, %s ) )
		srvtest.finish()
		""" % ( x, y, z )
		self._cc.sendAndCallOnApp( "bots", snippet = snippet )

		for order, expectedRollBack in [(['c', 'b', 's'], 's'), 
										(['s', 'c', 'b'], 'b'), 
										(['b', 's', 'c'], 'c')]:
			cellAppId, ids = self.getAndCheckProxyIDs()	
		
			frags = self.checkFragsOnCellApp(cellAppId, ids)
		
			self.generateCellAppCrash(order, expectedRollBack, 
									ids, frags, cellAppId)
			
			cellAppId, ids = self.findCellAppId( ids )
			newfrags = self.checkFragsOnCellApp(cellAppId, ids)

			for proxy in order:
				if proxy == expectedRollBack:
					self.assertTrue( newfrags[proxy] == frags[proxy], 
						"Frags did not roll back as expected." )
				else:
					self.assertTrue( 
						newfrags[proxy] in [frags[proxy], frags[proxy] + 1], 
						"Frags returned  unexpected value" )
		
			self.assertTrue( manual.input_passfail("""
			Did you see the expected behavior?	
			""") )
			
			self.checkFragsOnBotsAndClient( ids, newfrags, [3, 5] )
			
		
		
	def step2( self ):
		"""Client-controlled entities on vehicles"""
		self.assertTrue( manual.input_passfail("""
		Please move your BWClient avatar to a moving platform on the 
		same cell as you are currently on.
		"""))
		
		cellAppId, ids = self.getAndCheckProxyIDs()	
		frags = self.checkFragsOnCellApp(cellAppId, ids)
		
		order = ['c']
		expectedRollBack = 'c'
		self.generateCellAppCrash(order, expectedRollBack, ids, frags, cellAppId)
		
		cellAppId, ids = self.getAndCheckProxyIDs()	
		newfrags = self.checkFragsOnCellApp(cellAppId, ids)

		self.assertTrue( manual.input_passfail("""
		Did you see the expected behavior?	
		""") )

		for proxy in order:
			if proxy == expectedRollBack:
				self.assertTrue( newfrags[proxy] == frags[proxy], 
					"Frags did not roll back as expected." )
			else:
				self.assertTrue( 
					newfrags[proxy] in [frags[proxy], frags[proxy] + 1], 
					"Frags returned  unexpected value" )
		
		self.checkFragsOnBotsAndClient( ids, newfrags, [1] )
		self.assertTrue( manual.input_passfail( """
		Please return the BWClient to its original position.
		""" ) )


	def step3( self ):
		"""Server-controlled entities on the ground"""
		
		for order, expectedRollBack in [( ['b', 's'], 'b'), (['s', 'b'], 's')]:
			cellAppId, ids = self.getAndCheckProxyIDs()	
			frags = self.checkFragsOnCellApp(cellAppId, ids)
			
			snippet = ""
			for proxy in order:
				snippet += "%s = BigWorld.entities[ %s ]\n" % (proxy, ids[proxy])
				snippet += "%s.controlledBy = None\n" % proxy
			snippet += "srvtest.finish()\n"
			self._cc.sendAndCallOnApp( "cellapp", cellAppId, snippet )
			time.sleep( 30 )
			
			self.generateCellAppCrash(order, expectedRollBack, ids, frags, cellAppId)
		
			cellAppId, ids = self.getAndCheckProxyIDs()	
			newfrags = self.checkFragsOnCellApp(cellAppId, ids)
			
			self.assertTrue( manual.input_passfail("""
			Did you see the expected behavior?	
			""") )
			
			for proxy in order:
				if proxy == expectedRollBack:
					self.assertTrue( newfrags[proxy] == frags[proxy], 
									"Frags did not roll back as expected." )
				elif proxy == 'c':
					self.assertTrue( newfrags[proxy] == frags[proxy]+1, 
									"Frags rolled back on client unexpectedly." )
				else:
					self.assertTrue( 
							newfrags[proxy] in [frags[proxy], frags[proxy] + 1], 
							"Frags returned  unexpected value" )
			self.checkFragsOnBotsAndClient( ids, newfrags, [2, 4] )
			
	
	def step4( self ):
		"""Server-controlled entities on vehicles"""
		
		for order, expectedRollBack in [( ['b', 's'], 'b'), (['s', 'b'], 's')]:
			cellAppId, ids = self.getAndCheckProxyIDs()	
			frags = self.checkFragsOnCellApp(cellAppId, ids)
			
			snippet = ""
			for proxy in order:
				snippet += "%s = BigWorld.entities[ %s ]\n" % (proxy, ids[proxy])
				snippet += "%s.controlledBy = None\n" % proxy
				snippet += "%s.boardVehicle( %s )\n" % ( proxy, ids['v'] )
				snippet += "srvtest.assertTrue( %s.vehicle is not None )\n" % proxy
			snippet += "srvtest.finish()\n"
			self._cc.sendAndCallOnApp( "cellapp", cellAppId, snippet )
			time.sleep( 30 )
			
			self.generateCellAppCrash(order, expectedRollBack, ids, frags, cellAppId)
		
			cellAppId, ids = self.getAndCheckProxyIDs()	
			newfrags = self.checkFragsOnCellApp(cellAppId, ids)
			
			self.assertTrue( manual.input_passfail("""
			Did you see the expected behavior?	
			""") )
			
			for proxy in order:
				if proxy == expectedRollBack:
					self.assertTrue( newfrags[proxy] == frags[proxy], 
									"Frags did not roll back as expected." )
				elif proxy == 'c':
					self.assertTrue( newfrags[proxy] == frags[proxy]+1, 
									"Frags rolled back on client unexpectedly." )
				else:
					self.assertTrue( 
							newfrags[proxy] in [frags[proxy], frags[proxy] + 1], 
							"Frags returned  unexpected value" )
			self.checkFragsOnBotsAndClient( ids, newfrags, [2, 4] )
	
	
	def step5( self ):
		"""Server-controlled entities on vehicles with board-vehicle rollback"""
		
		for order, expectedRollBack in [( ['b', 's'], 'b'), (['s', 'b'], 's')]:
			cellAppId, ids = self.getAndCheckProxyIDs()	
			frags = self.checkFragsOnCellApp(cellAppId, ids)
			
			snippet = ""
			additionalCommands = ""
			for proxy in order:
				snippet += "%s = BigWorld.entities[ %s ]\n" % (proxy, ids[proxy])
				snippet += "%s.controlledBy = None\n" % proxy
				snippet += "if %s.vehicle is not None: "\
							"%s.alightVehicle( %s )\n" % ( proxy, proxy, ids['v'] )
				snippet += "srvtest.assertTrue( %s.vehicle is not None )\n" % proxy
				additionalCommands += "%s.boardVehicle( %s )\n"  % ( proxy, ids['v'] )
			snippet += "srvtest.finish()\n"
			self._cc.sendAndCallOnApp( "cellapp", cellAppId, snippet )
			time.sleep( 30 )
			
			self.generateCellAppCrash(order, expectedRollBack, 
									ids, frags, cellAppId, additionalCommands )
		
			cellAppId, ids = self.getAndCheckProxyIDs()	
			newfrags = self.checkFragsOnCellApp(cellAppId, ids)
			
			snippet = """
			%s = BigWorld.entities[ %s ]
			srvtest.assertTrue( %s.vehicle is not None )		
			""" % ( expectedRollBack, ids[expectedRollBack], expectedRollBack )
			self._cc.sendAndCallOnApp( "cellapp", cellAppId, snippet)

			self.assertTrue( manual.input_passfail("""
			Did you see the expected behavior?	
			""") )
			
			for proxy in order:
				if proxy == expectedRollBack:
					self.assertTrue( newfrags[proxy] == frags[proxy], 
									"Frags did not roll back as expected." )
				elif proxy == 'c':
					self.assertTrue( newfrags[proxy] == frags[proxy]+1, 
									"Frags rolled back on client unexpectedly." )
				else:
					self.assertTrue( 
							newfrags[proxy] in [frags[proxy], frags[proxy] + 1], 
							"Frags returned  unexpected value" )
			
			self.checkFragsOnBotsAndClient( ids, newfrags, [2, 4] )
	
	
	def step6( self ):
		"""Server-controlled entities on vehicles with alight-vehicle rollback"""
		
		for order, expectedRollBack in [( ['b', 's'], 'b'), (['s', 'b'], 's')]:
			cellAppId, ids = self.getAndCheckProxyIDs()	
			frags = self.checkFragsOnCellApp(cellAppId, ids)
			snippet = ""
			additionalCommands = ""
			
			for proxy in order:
				snippet += "%s = BigWorld.entities[ %s ]\n" % (proxy, ids[proxy])
				snippet += "%s.controlledBy = None\n" % proxy
				snippet += "if %s.vehicle is None: "\
							"%s.boardVehicle( %s )\n" % ( proxy, proxy, ids['v'] )
				snippet += "srvtest.assertTrue( %s.vehicle is not None )\n" % proxy
				additionalCommands += "%s.alightVehicle()\n"  % proxy
			
			snippet += "srvtest.finish()\n"
			self._cc.sendAndCallOnApp( "cellapp", cellAppId, snippet )
			time.sleep( 30 )
			self.generateCellAppCrash(order, expectedRollBack, 
									ids, frags, cellAppId, additionalCommands )
			cellAppId, ids = self.getAndCheckProxyIDs()	
			newfrags = self.checkFragsOnCellApp(cellAppId, ids)
			
			snippet = """
			%s = BigWorld.entities[ %s ]
			srvtest.assertFalse( %s.vehicle is not None )		
			""" % ( expectedRollBack, ids[expectedRollBack], expectedRollBack )
			self._cc.sendAndCallOnApp( "cellapp", cellAppId, snippet)
			self.assertTrue( manual.input_passfail("""
			Did you see the expected behavior?	
			""") )
			
			for proxy in order:
				if proxy == expectedRollBack:
					self.assertTrue( newfrags[proxy] == frags[proxy], 
									"Frags did not roll back as expected." )
				elif proxy == 'c':
					self.assertTrue( newfrags[proxy] == frags[proxy]+1, 
									"Frags rolled back on client unexpectedly." )
				else:
					self.assertTrue( 
							newfrags[proxy] in [frags[proxy], frags[proxy] + 1], 
							"Frags returned  unexpected value" )
			
			self.checkFragsOnBotsAndClient( ids, newfrags, [2, 4] )
