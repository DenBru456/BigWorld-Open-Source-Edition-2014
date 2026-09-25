"""
Log DB constants are used for both reading and writing logs, as well as any
tools which utilise the interface for either purpose.
"""

BACKEND_MLDB = "mldb"
BACKEND_MONGODB = "mongodb"
VALID_BACKENDS = ( BACKEND_MLDB, BACKEND_MONGODB )

# charsets
MLDB_CHARSET = 'utf-8'
MONGODB_CHARSET = 'utf-8'
