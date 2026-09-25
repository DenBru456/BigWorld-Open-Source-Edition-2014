import socket as socketmodule
import struct
import select

# Max recv buf size as given by /proc/sys/net/core/rmem_max on Linux, or 16
# megs on Windows
try:
	RMEM_MAX = int( open( "/proc/sys/net/core/rmem_max" ).read() )
except:
	RMEM_MAX = 16 * 1024 * 1024

def socket( flags = "", family = socketmodule.AF_INET,
			type = socketmodule.SOCK_DGRAM ):
	s = socketmodule.socket( family, type )
	if "b" in flags:
		s.setsockopt( socketmodule.SOL_SOCKET, socketmodule.SO_BROADCAST, 1 )
	if "m" in flags:
		s.setsockopt( socketmodule.SOL_SOCKET, socketmodule.SO_RCVBUF,
					  RMEM_MAX )
	return s

def recvAll( sock, timeout, bufsize = RMEM_MAX ):
	replies = []
	ready = select.select( [sock], [], [], timeout )[0]
	while ready:
		replies.append( sock.recvfrom( bufsize ) )
		ready = select.select( [sock], [], [], timeout )[0]
	return replies

def joinMulticastGroup( sock, multicastAddr ):
	mreq = struct.pack( "!4s4s", socketmodule.inet_aton( multicastAddr ),
						socketmodule.inet_aton( sock.getsockname()[0] ) )
	sock.setsockopt( socketmodule.SOL_IP, socketmodule.IP_ADD_MEMBERSHIP, mreq )


def getInterfaceAddress( ifname ):
	"""
	Get the IP address of the named interface.
	"""

	import fcntl

	s = socketmodule.socket( socketmodule.AF_INET, socketmodule.SOCK_DGRAM )
	return socketmodule.inet_ntoa( fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack( "256s", ifname[:15] ) )[20:24] )
