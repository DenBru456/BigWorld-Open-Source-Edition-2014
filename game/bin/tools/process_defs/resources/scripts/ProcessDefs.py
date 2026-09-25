import pprint
import sys

def process( description ):
	entityDescriptions = description[ "entityTypes" ]

	print "Digest:", description[ "constants" ][ "digest" ]
	print "Entity types:"
	pprint.pprint( entityDescriptions )

	print "\n\nMethods that have return values:"
	for entity in entityDescriptions:
		for method in entity[ "baseMethods" ]:
			if method.has_key( "returnValues" ):
				print "  %s.%s" % (entity[ "name" ], method[ "name" ])

	print "argv:", sys.argv

	return True

# ProcessDefs.py
