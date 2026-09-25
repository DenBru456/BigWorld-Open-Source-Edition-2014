#!/usr/bin/env python
"""   Query machines running bwmachined for their [Groups] tags.

   Query <tag>.  Passing no arguments is the same as passing --all.  If
   machines are specified but no tag is given, either --all or --list must be
   passed.

   Command Options:
    -a,--all:       Show all tag categories and values on selected machines
    -l,--list:      Show all tag categories on selected machines."""


if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-a", "--all", action = "store_true" )
	sopt.add_option( "-l", "--list", action = "store_true" )

	return sopt


def getUsageStr():
	return "querytags [tag] [<machines>]"


def getHelpStr():
	return __doc__


def run( args, env ):
	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	status = True

	# No machines / tags specified  OR --all
	if not parsedArgs or options.all:
		cat = None
		machineFilters = parsedArgs

	# Displaying all tag names on the machine(s)
	elif options.list:
		cat = ""
		machineFilters = parsedArgs

	# A tag name has been specified
	else:
		cat = parsedArgs[ 0 ]
		machineFilters = parsedArgs[1:]

	machines = env.getSelectedMachines( machineFilters )

	# Query the necessary machines for their tags. Results are stored
	# in the cluster object which we then use to display
	env.getCluster().queryTags( cat, machines )


	tagsFound = False
	# Displaying all tags
	if options.all or cat is None:
		for m in machines:
			for cc, tags in m.tags.items():
				env.info( "%-20s %s" % ("%s/%s:" % (m.name, cc),
									" ".join( tags )) )
				tagsFound = True

	# Displaying list of categories
	elif options.list or cat == "":
		for m in machines:
			if m.tags:
				env.info( "%-10s %s" % (m.name+":", " ".join( m.tags.keys() )) )
				tagsFound = True

	# Displaying specific categories
	else:
		for m in machines:
			if m.tags.has_key( cat ):
				env.info( "%-10s %s" % (m.name+":", " ".join( m.tags[ cat ] )) )
				tagsFound = True

	if not tagsFound:
		env.error( "Tag '%s' not found" % cat )
		status = False

	return status


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# querytags.py
