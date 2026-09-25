import commands


def fileDescriptorsUsed( pid ):
	cmd = "ls /proc/%s/fd/ | wc -l" % pid
	count = int( commands.getstatusoutput( cmd  )[1] )
	return count - 2 # exclude '..' and '.'