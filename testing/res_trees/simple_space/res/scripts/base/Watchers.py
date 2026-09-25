import BigWorld
from bwdecorators import functionWatcher, functionWatcherParameter


@functionWatcher( "command/baseServiceApps",
		BigWorld.EXPOSE_BASE_SERVICE_APPS,
		"BaseApps and ServiceApps Function Watcher" )
def baseServiceApps():
	return "baseServiceApps"


@functionWatcher( "command/baseApps",
		BigWorld.EXPOSE_BASE_APPS,
		"BaseApps Function Watcher" )
def baseApps():
	return "baseApps"


@functionWatcher( "command/serviceApps",
		BigWorld.EXPOSE_SERVICE_APPS,
		"ServiceApps Function Watcher" )
def serviceApps():
	return "serviceApps"


@functionWatcher( "command/leastLoaded",
		BigWorld.EXPOSE_LEAST_LOADED,
		"Least Loaded BaseApp Function Watcher" )
def leastLoaded():
	return "leastLoaded"
