import os, time, sys
try:
	import sqlite3 as sqlite
except:
	import sqlite #Work in 2.6 and 2.4
from bwtest import TestCase, config
from helpers.command import Command
from helpers.timer import runTimer
from primitives import WebConsoleAPI


class RestartWebConsole( TestCase ):
	
	
	name = "RestartWebConsole"
	tags = ["PRIORITY0"]
	description = "This test isn't really a test, but restarts web console on"\
				  " the specified machine to ensure that the other web console "\
				  "tests are run against a correct version of web-console"
	
	
	def setUp( self ):
		self.web_console_path = os.path.join( config.CLUSTER_BW_ROOT, 
										config.BIGWORLD_FOLDER,
										"tools/bigworld/server/web_console" )
		self.directory = os.path.dirname( os.path.abspath( __file__ )) 
		self.config_path = os.path.join( self.directory, "web_console.cfg" )
		self.db_file = "/tmp/web_console.sqlite"
		self.log_path = "/tmp/web_console.log"
		self.message_logger_path =  os.path.join( config.CLUSTER_BW_ROOT, 
											  config.BIGWORLD_FOLDER,
											  config.TOOLS_BINARY_FOLDER,
											  "message_logger" )
		self.ml_out_path = "/var/log/bigworld"
		self.ml_log_path = os.path.join( self.ml_out_path, "message_logger.log" )
		self.ml_config_path = "message_logger.conf"
		
	
	def tearDown( self ):
		pass
	
	
	def runTest( self ):
		#First kill any currently running web_console and message_logger commands
		cmd = Command()
		for process in ["start-web_console.py", "message_logger"]:
			cmd.call( 'ssh root@%s "ps ax|grep %s"' % (config.WCAPI_WCHOST, process ) )
			output = cmd.getLastOutput()[0]
			for line in output.split( "\n" ):
				if "grep" in line:
					continue
				pid = line.split()
				if pid == []:
					continue
				pid = int(pid[0])
				cmd.call( '-ssh root@%s "kill -9 %s"' % ( config.WCAPI_WCHOST, pid) )
		
		#Clean up SQLITE database and log files
		cmd.call( '-ssh root@%s "rm %s"' % \
								( config.WCAPI_WCHOST, self.db_file ) )
		cmd.call( '-ssh root@%s "rm %s"' % \
								( config.WCAPI_WCHOST, self.log_path ) )
		cmd.call( '-ssh root@%s "rm -rf %s"' % \
								( config.WCAPI_WCHOST, self.ml_out_path ) )
		
		cmd.call( '-ssh root@%s "mkdir -p %s"' % \
								( config.WCAPI_WCHOST, self.ml_out_path ) )
		cmd.call( '-ssh root@%s "cp %s %s"' % \
						( config.WCAPI_WCHOST,
						os.path.join( self.directory, self.ml_config_path ),
						os.path.join( self.ml_out_path, self.ml_config_path ) ) )
		#Start web_console
		cmd.call( 'ssh root@%s "python %s/start-web_console.py --daemon %s -o %s"' \
				% ( config.WCAPI_WCHOST, self.web_console_path, 
					self.config_path, self.log_path ) )
		#Start message_logger
		cmd.call( 'ssh root@%s "%s --daemon -o %s -e %s -c %s"'\
				% ( config.WCAPI_WCHOST, self.message_logger_path,
				self.ml_log_path, self.ml_log_path, 
				os.path.join( self.ml_out_path, self.ml_config_path ) ),
				waitForCompletion  = False, parallel = True )
		
		#Wait for WebConsole to be responding
		wcApi = WebConsoleAPI.WebConsoleAPI( user = "admin", passwd = "admin" )
		def checkWebConsoleIsUp():
			try:
				wcApi.poll( 1 )
			except:
				return False
			return True
		runTimer( checkWebConsoleIsUp, timeout = 20 )
		
		#Add user
		"""
		cmd.call( 'ssh root@%s "chmod 777 %s"' % ( config.WCAPI_WCHOST, self.db_file) )
		sys.path.append( self.web_console_path )
		turbogears.update_config( configfile=self.config_path, modulename="root.config" )
		hub = PackageHub("web_console")
		from web_console.common import model
		user = model.User(
				user_name = config.WCAPI_USER,
				password = config.WCAPI_PASS,
				serveruser = config.WCAPI_USER )
		groupObj = model.Group.by_group_name( "modify_all" )
		user.addGroup(groupObj)
		hub.commit()
		sys.path.pop()
		"""
		wcApi.addUser( config.WCAPI_USER, config.WCAPI_PASS )
		
		
		
		