import socket

# From mercury.hpp
FLAG_HAS_REQUESTS			= 0x01
FLAGS_OF_BUNDLE				= 0x01
FLAG_HAS_ACKS				= 0x04
FLAG_ORDER_STRICT			= 0x08
FLAG_ORDER_CONTIGUOUS		= 0x10
FLAG_IS_RELIABLE			= 0x20
FLAG_IS_FRAGMENT			= 0x40
FLAG_HAS_SEQUENCE_NUMBER	= 0x80
FLAGS_OF_NUB				= 0xFC
FLAGS_OK                    = FLAGS_OF_BUNDLE | FLAGS_OF_NUB

# Changed case from original in mercury.hpp for python importing behaviour
kReplyMessageIdentifier = 0xFF

LOGIN_APP_PORT = 20013

LOCALHOST = socket.gethostbyname( socket.gethostname() )
