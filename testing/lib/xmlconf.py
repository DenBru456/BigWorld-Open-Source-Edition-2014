from xml.dom.minidom import parse


def readConf( fileName, confTarget, configPaths, rootTag = 'root' ):
		
	ret = False

	doc = parse( fileName )

	if doc is None:
		return ret

	root = None
	for child in doc.childNodes:
		if child.nodeName == rootTag:
			root = child

	if root is None:
		return ret

	foundPaths = {}

	for child in root.childNodes:
		_parseConfig( child, child.nodeName, foundPaths, configPaths )


	for path in foundPaths.keys():
		val = foundPaths[ path ]
		if len( val ) < 2:
			# take single value out of array
			val = val[ 0 ]
		if type( confTarget ) == dict:
			confTarget[ configPaths[ path ] ] = val
		else:
			setattr( confTarget, configPaths[ path ], val )

	return True
		
def _parseConfig( node, path, pathsToSet, configPaths ):

	for child in node.childNodes:
		curPath = path + '/' + child.nodeName
	
		for name in configPaths.keys():
				
			if curPath == name + '/#text':
				value = child.data.strip()
				if name in pathsToSet:
					pathsToSet[ name ].append( value )
				else:
					pathsToSet[ name ] = [ value ]


		if child.nodeType == child.ELEMENT_NODE:
			_parseConfig( child, curPath, pathsToSet, configPaths )

