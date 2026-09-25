from primitives import locallog

def checkLog( case, event, params, count ):
	output = locallog.grepLastServerLog( "eventListener: Event: %s: %s" % \
										(event, params ) )
	case.assertTrue( len( output ) > 0 and len( output.split( "\n" ) ) == count,
				"Event listener %s wasn't called" % event)
	
	output = locallog.grepLastServerLog( 
						"personalityCallback: Event: simple_space.%s: %s" % \
						( event, params ) )
	case.assertTrue( len( output ) > 0 and len( output.split( "\n" ) ) == count,
				"Callback %s called" % event)