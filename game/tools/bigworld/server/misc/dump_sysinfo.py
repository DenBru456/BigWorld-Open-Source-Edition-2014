#!/usr/bin/env python

import os
import socket
import sys

import bwsetup; bwsetup.addPath( ".." )
from pycommon import util

def run( cmd, trailingspace ):
	print util.border( cmd )
	sys.stdout.flush()
	os.system( cmd )
	for i in xrange( trailingspace ):
		print
	sys.stdout.flush()

print util.border( socket.gethostname(), "=" )
print

run( "cat /proc/cpuinfo", 0 )
run( "cat /proc/meminfo", 1 )
run( "dmesg", 1 )
run( "/sbin/lspci -v", 0 )
