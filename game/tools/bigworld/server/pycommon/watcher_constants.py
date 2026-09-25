# Watcher protocol data types
TYPE_UNKNOWN    = 0
TYPE_INT        = 1
TYPE_UINT       = 2
TYPE_FLOAT      = 3
TYPE_BOOL       = 4
TYPE_STRING     = 5
TYPE_TUPLE      = 6
TYPE_TYPE       = 7

# Component types
CELL_APP = 0
BASE_APP = 1
SERVICE_APP = 2

def isValidComponent( componentType ):
	return componentType in ( CELL_APP,
		BASE_APP,
		SERVICE_APP
		)

# Exposure hints for watcher forwarding
EXPOSE_WITH_ENTITY = 0
EXPOSE_CELL_APPS = 1
EXPOSE_WITH_SPACE = 2
EXPOSE_LEAST_LOADED = 3
EXPOSE_LOCAL_ONLY = 4
EXPOSE_BASE_APPS = 5
EXPOSE_SERVICE_APPS = 6
EXPOSE_BASE_SERVICE_APPS = 7

def isValidExposure( exposureValue ):
	return exposureValue in ( EXPOSE_WITH_ENTITY,
		EXPOSE_CELL_APPS,
		EXPOSE_WITH_SPACE,
		EXPOSE_LEAST_LOADED,
		EXPOSE_LOCAL_ONLY,
		EXPOSE_BASE_APPS,
		EXPOSE_SERVICE_APPS,
		EXPOSE_BASE_SERVICE_APPS
		)

# watcher_constants.py
