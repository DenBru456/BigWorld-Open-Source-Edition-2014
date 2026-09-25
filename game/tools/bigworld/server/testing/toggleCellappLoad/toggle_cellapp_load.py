#!/usr/bin/env python

import os
import sys
import optparse
import time
import operator

# BigWorld includes
try:
	sys.path.append(
			"../../pycommon".replace( '/', os.sep ) )
except KeyError:
	print "Warning: pycommon directory is not exist."
	sys.exit( 1 )

import cluster
import uid as uidmodule
import util

TEST_TICK_TIME = 10			# Detect process status interval time (second).
CPU_LOAD_DIFFERENCE = 0.1	# The difference between cellapps load when reaching
							# load balance.

# Test parameters for seting services
class TestParameter:
	def __init__( self, path, newVal, type = None, oldVal = None):
		self.path = path
		self.newVal = newVal
		self.oldVal = oldVal
		self.type = type

parCellAppMgr = TestParameter( path = "numCells", newVal = "1", oldVal = None)

parCellApp = [
	TestParameter( path = "config/demoLoadBalancing",
						newVal = "true", oldVal = "false"),
	TestParameter( path = "config/demoNumEntitiesPerCell",
					newVal = "1000", oldVal = "100")]

class BalanceTester( object ):
	# Initialize testing parameters
	def __init__( self, iTime, uerid = None ):
		self.iRunTime = int(iTime) * 60
		self.uid = uidmodule.getuid( uerid )
		self.cluster = cluster.cache.get( uid = self.uid )
		self.cellmgr = None
		self.originalCellApps = set()
		self.cellApps = set()
		self.retiring = None

		# Get processes.
		for proc in self.cluster.getProcs():
			if proc.label() == "cellappmgr":
				self.cellmgr = proc
			if proc.name == "cellapp":
				self.originalCellApps.add( proc )

		# Checking whether services run normally.
		if self.cellmgr == None:
			print "Cellappmgr is not running."
			sys.exit( 1 )

		if len( self.originalCellApps ) < 2:
			print "Must be have more than two cellapps for this test."
			sys.exit( 1 )

		self.cellApps = self.originalCellApps

	# Restore system original parameters.
	def restore( self ):
		self.initTestParas( True )

	# Set process watcher data
	def initWatcherData( self, proc, para, restore = False):
		if not proc:
			print "Process is none."
			return

		if restore:
			if para.oldVal == None:
				return
			newVal = para.oldVal
		else:
			para.oldVal = proc.getWatcherValue( para.path )
			newVal = para.newVal

		status = proc.setWatcherValue( para.path, newVal )

		if not status:
			print "Update %s watcher data[%s] fail." % (proc.label(), para.path)

	# Setup common balance test values.
	def initTestParas( self, restore = False ):
		for proc in self.cellApps:
			self.initWatcherData( proc, parCellApp[0], restore )

	# Checking whether cellapps crash or death.
	def checkCellApps( self ):
		mesg = ""
		for proc in self.originalCellApps:
			status = False
			for p in self.cellApps:
				if p.id == proc.id:
					status = True
					break
			if status == False:
				mesg += "%s is death.\n" % proc.label()

		if not mesg == "":
			print mesg

		return mesg

	def averageLoad( self ):
		for proc in self.cellApps:
			proc.setWatcherValue( parCellApp[1].path, parCellApp[1].oldVal )
		self.retiring = False
		print "Make cellapps load normally."

	def retireCellApp( self ):
		for proc in self.cellApps:
			proc.setWatcherValue( parCellApp[1].path, parCellApp[1].newVal )
		self.retiring = True
		print "Make cellapps retired."

	# Check cellapps retire status.
	# return: True=already retired   False=retiring
	def checkRetireStatus( self ):
		if self.retiring == False:
			return False

		# It is load balancing when:
		# numCells - 3(numNormalCells) >= numCellApps - 1
		num = self.cellmgr.getWatcherValue( parCellAppMgr.path )
		if ( num - 2 ) >=  len(self.cellApps) :
			return False
		return True

	# Check whether cellapp reaching load balance.
	# return: True=No False=Yes
	def checkLoadDifference( self ):
		cellApp0Load = 0
		i = 0

		for proc in self.cellApps:
			load = proc.getWatcherValue( "load" )
			# If get watcher data error, don't compare them.
			if load == None:
				return True
			load = float(load)
			if i == 0:
				cellApp0Load = load
				i += 1
				continue

			if abs(load - cellApp0Load) > CPU_LOAD_DIFFERENCE:
				return True
			i += 1

		return False

	def checkClusterBalance( self ):
		if self.checkRetireStatus():
			self.averageLoad()
		else:
			if not self.retiring and not self.checkLoadDifference():
				self.retireCellApp()

	# Run test
	def run( self ):
		self.initTestParas()

		while True:
			if not self.refresh():
				break
			self.checkClusterBalance()
			self.printCPUload()
			time.sleep(TEST_TICK_TIME)
			self.iRunTime -= TEST_TICK_TIME
			if self.iRunTime <= 0:
				print "Testing is over."
				break

		# Restore original value.
		self.initTestParas( True )
		return self.checkCellApps()

	# Refresh cluster information
	def refresh( self ):
		# Get CPU load
		self.cluster = cluster.cache.get( uid = self.uid )
		self.cellApps = self.cluster.getProcs( name="cellapp" )
		self.cellApps.sort(key=operator.attrgetter('id'))
		if( len(self.cellApps) < 2 ):
			print "CellApp number is %d, test stoping." % len(self.cellApps)
			return False
		return True

	# Print cellapps CPU load
	def printCPUload( self ):
		strOut = ""
		for proc in self.cellApps:
			strOut += "%s: %.2f\t" % (proc.label(), proc.load)
		print strOut

if __name__ == "__main__":
	util.setUpBasicCleanLogging()

	opt = optparse.OptionParser()
	opt.add_option( "-u", dest = "uid", default = None,
					help = "specify the UID or username to work with" )
	opt.add_option( "-t", dest = "runTime", default = 1,
					help = "set tool running time(minute, default=1) for testing." )
	opt.add_option( "-r", "--restore", dest = "restore", action = "store_true",
					help = "restore original system parameters." )
	opt.add_option( "-e", dest = "email", default = None,
				help = "the email which be sent when meet error." )
	options, args = opt.parse_args()

	if options.runTime <= 0:
		print "Invalid running time."
		sys.exit( 1 )

	tester = BalanceTester( options.runTime, options.uid )

	if options.restore:
		tester.restore()
		sys.exit( 0 )

	errorMesg = tester.run()
	if errorMesg != "" and options.email != None:
		import socket
		cmd = "echo \"%s\" | mail -s \"[%s] cellapps load balancing test failed.\" %s" \
			% (errorMesg, socket.gethostname(), options.email)
		os.system(cmd)
	sys.exit( 0 )
