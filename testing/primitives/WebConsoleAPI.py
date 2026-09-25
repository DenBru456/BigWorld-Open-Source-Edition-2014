"""Low-level Wrapper module to the REST API of WebConsole. Unless specifically
testing WebConsole, should use helpers.ClusterController. See API tab of 
WebConsole for a more complete documentation of this API
"""

import sys
import getpass

from simplejson import JSONEncoder

#sys.path.append( '../lib' )

import easyurlget
import xmlconf

from bwtest import config
from bwtest import log


def _readWebConsoleAPIConfig():
	config.WCAPI_USER = getpass.getuser()
	config.WCAPI_PASS = config.WCAPI_USER
	config.WCAPI_WCHOST = 'toolbox'
	config.WCAPI_WCPORT = '8080'
	config.WCAPI_SPACE = 2
		

	userConfigFile = config.TEST_ROOT + "/user_config/user_config.xml"
	
	try:
		success = xmlconf.readConf( userConfigFile, config,
			{ 
				'webConsoleAPI/user': 	 'WCAPI_USER',
				'webConsoleAPI/pass':	 'WCAPI_PASS',
				'webConsoleAPI/wchost':  'WCAPI_WCHOST',
				'webConsoleAPI/wcport':  'WCAPI_WCPORT',
				'webConsoleAPI/machine': 'WCAPI_MACHINE',
				'webConsoleAPI/space':   'WCAPI_SPACE'
			} )

	except IOError:
		log.error( "user_config/user_config.xml not found!" )
		return

	if not success:
		log.error( "Failed to parse user_config/user_config.xml!" )
		return

	#print "Configuration read from xml:\n"
	#print config.WCAPI_USER
	#print config.WCAPI_PASS
	#print config.WCAPI_WCHOST
	#print config.WCAPI_WCPORT
	#print config.WCAPI_SPACE
	

_readWebConsoleAPIConfig()

class WebConsoleAPI:
	"""Wrapper class to the WebConsole REST API
	"""

	def __init__( self, user = config.WCAPI_USER, 
			passwd = config.WCAPI_PASS, 
			wc_server = config.WCAPI_WCHOST, 
			wc_srvport = config.WCAPI_WCPORT ):
		"""Constructor. All parameters default to configuration in user_config.xml
		@param user: WebConsole user
		@param passwd: WebConsole password
		@param wc_server: Hostname of WebConsole instance
		@param wc_srvport: Port number of WebConsole instance
		"""

		wc_srvport = int( wc_srvport )
		self.user = user
		self.passwd = passwd
		self.wc_server = wc_server
		self.wc_srvport = wc_srvport

		self.httpBase = {
			'CC':		'http://%s:%r/cc/'%( wc_server, wc_srvport ),
			'Watcher': 	'http://%s:%r/watchers/'%( wc_server, wc_srvport ),
			'Log': 		'http://%s:%r/log/'%( wc_server, wc_srvport ),
			'Space':	'http://%s:%r/sv/'%( wc_server, wc_srvport ),
			'Commands':	'http://%s:%r/commands/'%( wc_server, wc_srvport ),
			'Console':	'http://%s:%r/console/'%( wc_server, wc_srvport ),
			'Profiler':	'http://%s:%r/profiler/'%( wc_server, wc_srvport ),
			'root':		'http://%s:%r/'%( wc_server, wc_srvport ),
			'admin':	'http://%s:%r/admin/'%( wc_server, wc_srvport ),
		}

	def _get( self, url, params={} ):
		return easyurlget.get( self.httpBase['CC'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects=False )

	def _getWatcher( self, url, params={} ):
		return easyurlget.get( self.httpBase['Watcher'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects=False )

	def _getLog( self, url, params={} ):
		return easyurlget.get( self.httpBase['Log'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects=False )

	def _getPoll( self, url, params={} ):
		return easyurlget.get( self.httpBase['root'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects=False )

	def _getSpace( self, url, params={} ):
		return easyurlget.get( self.httpBase['Space'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects=False )

	def _getCommands( self, url, params={} ):
		return easyurlget.get( self.httpBase['Commands'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects=False )

	def _getConsole( self, url, params={} ):
		return easyurlget.get( self.httpBase['Console'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects=False )

	def _getProfiler( self, url, params={} ):
		return easyurlget.get( self.httpBase['Profiler'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects = False )
	
	def _getAdmin( self, url, params={} ):
		return easyurlget.get( self.httpBase['admin'] + url,
				auth = ( self.user, self.passwd ),
				headers = {'Accept': 'application/json'},
				params = params, allow_redirects = False )


	def _ret( self, response ):
		return response.status_code, response.json()
	
	def addUser( self, user, password ):
		"""Call WebConsole admin add user.  Current credentials MUST be admin
		@param user: Username to add
		@param password: Password to add
		"""	
		r = self._getAdmin("edit", 
						params = { 	'action': 'add',
									'username': user,
									'pass1': password,
									'pass2': password,
									'serveruser': user,
									'group': 'modify_all' 
								})

	def startServer( self, machine ):
		"""Call WebConsole doStart
		@param machine: Name of machine to start server on
		"""
		log.info( "Starting Server via WebConsoleAPI on machine "
				  "%s for user %s" % ( machine, self.user ) )

		r = self._get( 'doStart',
				params = { 'mode' : 'single', 
						   'machine': machine, 
					       'user': self.user } )

		return self._ret(r)


	def stopServer( self ):
		"""Call WebConsole stop
		"""
		
		log.info( "Stopping Server via WebConsoleAPI for user %s" % self.user )

		r = self._get( 'stop' )
		return self._ret(r)


	def restartServer( self ):
		"""Call WebConsole restart
		"""
		
		log.info( "Restarting Server via WebConsoleAPI "
				  "for user %s" % self.user )

		r = self._get( 'restart' )
		return self._ret(r)


	def startProcess( self, machine, procname, count ):
		"""Call WebConsole startproc
		@param machine: Name of machine to start process on
		@param procname: Type of process to start eg. 'baseapp'
		@param count: Number of processes to start
		"""
		
		log.info( "Starting %r process(es) %s via WebConsoleAPI"
				  " on machine %s for user %s" % \
					( count, procname, machine, self.user) )

		r = self._get( 'startproc',
					params = { 'count' : count, 
								'machine': machine, 
								'pname': procname, 
								'user': self.user } )

		return r.status_code, None


	def stopProcess( self, machine, pid ):
		"""Call WebConsole stopproc
		@param machine: Name of machine to stop process on
		@param pid: Process ID to stop
		"""

		log.info( "Stopping process %r via WebConsoleAPI "
				  "on machine %s for user %s" % \
				(pid, machine, self.user) )

		r = self._get( 'stopproc',
					params = { 'machine': machine, 'pid': pid } )

		return r.status_code, None


	def retireApp( self, machine, pid ):
		"""Call WebCOnsole retireApp
		@param machine: Name of machine to retire process on
		@param pid: Process ID to retire
		"""
		log.info( "Retiring App %r via WebConsoleAPI "
				  "on machine %s for user %s" % \
					(pid, machine, self.user) )

		r = self._get( 'retireApp',
					params = { 'machine': machine, 'pid': pid } )

		return r.status_code, None



	def killProc( self, machine, pid, sig ):
		"""Call WebConsole killproc
		@param machine: Name of machine to kill process on
		@param pid: Process ID to kill
		@param sig: Signal to send, eg. SIGKILL, SIGINT
		"""

		log.info( "Killing process %r via WebConsoleAPI "
				  "on machine %s for user %s" % \
					(pid, machine, self.user) )

		r = self._get( 'killproc',
					params = { 'machine': machine, 'pid': pid, 'signal': sig } )

		return r.status_code, None

	def usersFlush( self ):
		"""Call WebConsole usersFlush
		"""
		r = self._get( 'usersFlush' );
		return r.status_code, None


	def getProcs( self, user, machine=None ):
		"""Call WebConsole getProcs
		@param user: Name of user
		@param machine: Machine to filter by. Default None
		"""
		log.info( "Retrieving process list via WebConsoleAPI "
				  "on machine %s for user %s" % \
					(machine, self.user) )

		params = {}
		if user:
			params['user'] = user
		if machine:
			params['machine'] = machine


		r = self._get( 'getProcs',
					params = params )

		return self._ret(r)


	def getMachines( self, includeTagInfo=False ):
		"""Call WebConsole getMachines
		@param includeTagInfo: Include tags parameter
		"""

		log.info( "Getting machines via WebConsole" )

		if includeTagInfo:
			r = self._get( 'getMachines',
					params = { 'tags': int(includeTagInfo) } )
		else:
			r = self._get( 'getMachines' )

		return self._ret(r)


	def getUsers( self, includeInactive=False ):
		"""Call WebConsole getUsers
		@param includeInactive: Include inactive users
		"""

		log.info( "Getting users via WebConsole" )

		if includeInactive:
			r = self._get( 'getUsers',
					params = { 'inactive': int(includeInactive) } )
		else:
			r = self._get( 'getUsers' )

		return self._ret(r)


	def coredumps( self, user ):
		"""Call WebConsole coredumps
		@param user: Name of user to get dumps for
		"""

		log.info( "Getting core dumps via WebConsole "
				  "for user %s" % (self.user) )

		r = self._get( 'coredumps',
				params = { 'user': user } )
		return self._ret(r)


	def layouts( self ):
		"""Call WebConsole layouts
		"""
		log.info( "Getting layouts via WebConsole "
				  "for user %s" % (self.user) )

		r = self._get( 'layouts' );
		return self._ret(r)


	def watchersGetFilteredTree( self, processes, path ):
		"""Call WebConsole Watchers filtered/get_filter
		@param processes: String filtering processes
		@param path: Path expression to filter on
		"""

		log.info( "Running WebConsoleAPI/getFilteredTree "
				  "with path '%s' on processes %r for user %s" % \
					(path, processes, self.user) )

		r = self._getWatcher( 'filtered/get_filtered_tree',
				params = { 'path': path, 'processes': processes } )
		return self._ret(r)


	def watchersShow( self, machine, pid, path ):
		"""Call WebConsole Watchers tree/show
		@param machine: Name of machine to get watchers from
		@param pid: Process ID to get watchers from
		@param path: Path to watcher 
		"""

		log.info( "Reading watcher %s:%s via WebConsoleAPI "
				  "on machine %s for user %s" % \
					(pid, path, machine, self.user) )

		r = self._getWatcher( 'tree/show',
				params = { 'machine' : machine, 'path': path, 'pid': pid } )
		return self._ret(r)


	def watchersEdit( self, machine, pid, path, datatype, newval ):
		"""Call WebConsole Watchers tree/edit
		@param machine: Name of machine to get watchers from
		@param pid: Process ID to get watchers from
		@param path: Path to watcher 
		@param datatype: Type of data
		@param newval: New value to set watcher to
		"""

		log.info( "Setting watcher at %s:%s to '%r' via "
				  "WebConsoleAPI on machine %s for user %s" % \
					(pid, path, newval, machine, self.user) )

		r = self._getWatcher( 'tree/edit',
				params = { 'dataType' : datatype, 
							'machine' : machine, 
							'newval' : newval, 
							'path': path, 
							'pid': pid } )

		return r.status_code, None


	def logsSearch( self ):
		"""Call WebConsole logs search.
		"""

		log.info( "Getting log config via WebConsole" )

		r = self._getLog( 'search' )
		return self._ret(r)


	def logsFetchAsync( self, args=None ):
		"""Call WebConsole logs fetchAsync
		@param args: Set of JSON arguments to filter the logs
		"""

		r = self._getLog( 'fetchAsync', args )
		log.info( "FetchAsync returns: %r, %s" % ( r.status_code, r.json() ) )
		return self._ret(r)


	def poll( self, id ):
		"""Call WebConsole poll
		@param id: ID of async task 
		"""

		r = self._getPoll( 'poll', { "id": id } )
		return self._ret(r)

	
	def spaceSpaces( self, limit, index ):
		"""Call WebConsole Spaces api/spaces
		@param limit: Max number of spaces to return
		@param index: Index of the first space in return list
		"""

		log.info( "Getting spaces via WebConsole for user %s" % (self.user) )

		r = self._getSpace( 'api/spaces', 
							{ "index": index, "limit": limit } )
		return self._ret(r)

	def spaceGetSpace( self, spaceId, cellId=None ):
		"""Call WebConsole get_spaces
		@param spaceId: ID of the space
		@param cellId: Optional ID of cell within the space
		"""

		log.info( "Getting space info for space %r via "
				  "WebConsole for user %s" % \
					(spaceId, self.user) )

		if cellId:
			r = self._getSpace( 'get_space', 
								{ "space": spaceId, "cell": cellId } )
		else:
			r = self._getSpace( 'get_space', { "space": spaceId } )
		return self._ret(r)


	def spaceGetEntityTypes( self, spaceId ):
		"""Call WebConsole Spaces get_entity_types
		@param spaceId: ID of the space
		"""
		log.info( "Getting entities in space for space %r via "
				  "WebConsole for user %s" % \
					(spaceId, self.user) )

		r = self._getSpace( 'get_entity_types', { "space": spaceId } )
		return self._ret(r)

	
	def commandsGetScripts( self, type, category="" ):
		"""Call WebConsole Commands getScripts
		@param type: type of commands to retrieve, eg. 'watcher' and 'db'
		@param category: category of commands to retrieve. Default '' for all
		"""
		
		log.info( "Getting callable watcher list via "
				  "WebConsole, type=%s, category=%s" % \
					(type, category) )

		r = self._getCommands( 'getscripts', 
								{ "type": type, "category": category } )
		return self._ret(r)


	def commandsScriptInfo( self, id ):
		"""Call WebConsole Commands scriptinfo
		@param id: ID of the command
		"""

		log.info( "Getting callable watcher info via "
				  "WebConsole, id=%r" % (id) )

		r = self._getCommands( 'scriptinfo', { "id": id } )
		return self._ret(r)


	def commandsExecuteScript( self, id, args, runType ):
		"""Call WebConsole Commands executeScript
		@param id: ID of the command
		@param args: Arguments to the script.
		@param runType: Method by which the command will be run, eg 'all' or 'any'
		"""
		encodedArgs= JSONEncoder().encode(args)

		log.info( "Calling watcher via WebConsole, id=%r, encodedArgs='%s'" % \
				(id, encodedArgs) )

		r = self._getCommands( 'executescript', 
								{ "id": id, 
								  "args": encodedArgs, 
								  "runType": runType } )
		return self._ret(r)


	def consoleProcessRequest( self, line, host, port ):
		"""Call WebConsole Consoles process_request
		@param line: Line of Python to execute
		@param host: Hostname of target machine 
		@param port: Python console port
		"""

		log.info( "Running single line python via "
				  "WebConsole, line='%s', to %s:%r" % \
					(line, host, port) )

		r = self._getConsole( 'process_request', 
								{ "line": line, 
								  "host": host, 
								  "port": port } )
		return self._ret(r)


	def consoleProcessMultilineRequest( self, block, host, port ):
		"""Call WebConsole Consoles process_multiline_request
		@param block: Block of Python to execute
		@param host: Hostname of target machine 
		@param port: Python console port
		"""

		log.info( "Running block python code via "
				  "WebConsole, block='%s', to %s:%r" % \
					(block, host, port) )

		r = self._getConsole( 'process_multiline_request', 
								{ "block": block, 
								  "host": host, 
								  "port": port } )
		return self._ret(r)


	def profilerRequest( self, endpoint, params ):
		"""Call a profiler endpoint

		@param endpoint: The profiler endpoint
		@param params: Dictionary of parameters to add to the URL
		"""
		return self._ret( self._getProfiler( endpoint, params ) )

	def rawRequest( self, endpoint, params ):
		"""Call a raw endpoint. Primarily for testing bad URLs.

		@param endpoint: The endpoint
		@param params: Dictionary of parameters to add to the URL
		"""
		return self._ret( self._getPoll( endpoint, params ) )
