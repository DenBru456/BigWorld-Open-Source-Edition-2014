
# Importing WorldEditor to use linking functions
import WorldEditor
import re


# name of the patrol path link property
LINK_PROP_NAME = "links"


class PlatformNode:

	linkPropertyRE = re.compile( "^links$|^links\[\d+\]$" )

	# return the patrol node model
	def modelName( self, props ):
		try:
			if props['waitTime'] > 0:			
				return "resources/models/floating_platform_stop.model"
			else:
				return "resources/models/floating_platform_node.model"
		except:
			return "helpers/props/standin.model"


	# patrol nodes always show the "+" gizmo
	def showAddGizmo( self, propName, thisInfo ):
		return True


	# patrol nodes linking conditions
	def canLink( self, propName, thisInfo, otherInfo ):
		if PlatformNode.linkPropertyRE.match( propName ):
			if otherInfo["type"] != thisInfo["type"]:
				return False	# PlatformNode to PlatformNode only
			elif ( thisInfo["guid"], thisInfo["chunk"] ) in otherInfo["properties"]["links"]:
				return False	# no backlinks
			elif ( otherInfo["guid"], otherInfo["chunk"] ) in thisInfo["properties"]["links"]:
				return False	# single links only
		else:
			return False


	# helper method to remove empty links
	def cleanupEmptyLinks( self, links ):
		emptyLink = ("","")
		while links.__contains__( emptyLink ):
			links.remove( emptyLink )


	# when a node is deleted, other nodes must be relinked
	def onDeleteObject( self, nodeInfo ):
		links = nodeInfo["properties"][ LINK_PROP_NAME ]
		backLinks = nodeInfo["backLinks"]
		self.cleanupEmptyLinks( links )
		self.cleanupEmptyLinks( backLinks )

		relinkNode = None
		linksBegin = 0
		backLinksBegin = 0
		if len( links ) > 0:
			# relink everything to the first outgoing node
			relinkNode = links[0]
			linksBegin = 1
		elif len( backLinks ) > 0:			
			# relink everything to the first incomming node
			relinkNode = backLinks[0]
			backLinksBegin = 1
		else:
			return	# nothing to do!

		# Relinking outgoing links
		for link in links[linksBegin:]:
			WorldEditor.udoCreateLink( relinkNode[0], relinkNode[1], link[0], link[1], LINK_PROP_NAME )

		# Relinking incomming links (BackLinks)
		for backlink in backLinks[backLinksBegin:]:
			WorldEditor.udoCreateLink( backlink[0], backlink[1], relinkNode[0], relinkNode[1], LINK_PROP_NAME )

		WorldEditor.addUndoBarrier( "Relink after deleting PatrolNode" )


	# called to get extra context menu commands from the script
	def onStartLinkMenu( self, startInfo, endInfo ):
		# we should localise these strings
		return ("`SCRIPT/PLATFORM_NODE_PY/SPLIT_LINK",
				"",
				"`SCRIPT/PLATFORM_NODE_PY/SWAP_LINK_DIRECTION",
				"`SCRIPT/PLATFORM_NODE_PY/SWAP_LINK_DIRECTION_RUN_OF_LINKS" )


	# called when one of the extra context menu commands is clicked
	def onEndLinkMenu( self, command, startInfo, endInfo ):
		if command == 0:
			self.splitLink( startInfo, endInfo )
		elif command == 1:
			self.swapLink( startInfo, endInfo )
		elif command == 2:
			self.swapLinksRun( startInfo, endInfo )
		else:
			WorldEditor.addCommentaryMsg( "PatrolNode: received unknown command " + str(command) + ".", 0 )


	# split a link, creating a new node in the middle
	def splitLink( self, startInfo, endInfo ):
		startProps = startInfo["properties"]
		endProps = endInfo["properties"]

		# find out whether the nodes are linked in one or both directions
		startToEndLink = False
		endToStartLink = False
		if ( endInfo["guid"], endInfo["chunk"] ) in startProps[LINK_PROP_NAME]:
			startToEndLink = True
		if ( startInfo["guid"], startInfo["chunk"] ) in endProps[LINK_PROP_NAME]:
			endToStartLink = True

		# create new node
		midPoint = ( (startInfo["position"][0] + endInfo["position"][0])/2.0,
					 (startInfo["position"][1] + endInfo["position"][1])/2.0,
					 (startInfo["position"][2] + endInfo["position"][2])/2.0 )
		newInfo = WorldEditor.udoCreateAtPosition( startInfo["guid"], startInfo["chunk"], midPoint, False )
		newProps = newInfo["properties"]

		# delete old links
		WorldEditor.udoDeleteLinks( startInfo["guid"], startInfo["chunk"], endInfo["guid"], endInfo["chunk"] )

		# relink
		if startToEndLink:
			WorldEditor.udoCreateLink( startInfo["guid"], startInfo["chunk"], newInfo["guid"], newInfo["chunk"], LINK_PROP_NAME )
			WorldEditor.udoCreateLink( newInfo["guid"], newInfo["chunk"], endInfo["guid"], endInfo["chunk"], LINK_PROP_NAME )

		if endToStartLink:
			WorldEditor.udoCreateLink( endInfo["guid"], endInfo["chunk"], newInfo["guid"], newInfo["chunk"], LINK_PROP_NAME )
			WorldEditor.udoCreateLink( newInfo["guid"], newInfo["chunk"], startInfo["guid"], startInfo["chunk"], LINK_PROP_NAME )
			
		WorldEditor.addUndoBarrier( "Split link" )


	# swap the direction of the link
	def swapLink( self, startInfo, endInfo ):
		startProps = startInfo["properties"]
		
		# find out whether the nodes are linked in one or both directions
		startToEndLink = False
		if startProps[LINK_PROP_NAME].__contains__( ( endInfo["guid"], endInfo["chunk"] ) ):
			startToEndLink = True
			
		WorldEditor.udoDeleteLinks( startInfo["guid"], startInfo["chunk"], endInfo["guid"], endInfo["chunk"] )
		
		if startToEndLink:
			WorldEditor.udoCreateLink( endInfo["guid"], endInfo["chunk"], startInfo["guid"], startInfo["chunk"], LINK_PROP_NAME )
		else:
			WorldEditor.udoCreateLink( startInfo["guid"], startInfo["chunk"], endInfo["guid"], endInfo["chunk"], LINK_PROP_NAME )

		WorldEditor.addUndoBarrier( "Swap link direction" )


	# swap the direction of the link
	def swapLinksRun( self, startInfo, endInfo ):
		newDir = "START_END"
		if ( endInfo["guid"], endInfo["chunk"] ) in startInfo["properties"][LINK_PROP_NAME]:
			newDir = "END_START"

		self.changeDir( startInfo, endInfo, newDir )

		WorldEditor.addUndoBarrier( "Swap direction of links (run of links)" )


	# internal method to change the direction of all traversable links
	def changeDir( self, startInfo, endInfo, newDir ):
		# follow links and store them in resultLinks
		resultLinks = []
		for dir in [ "forward", "backward" ]:
			# this loop has two iterations: one for following links from start
			# to end, and one for following links from end to start.
			lastInfo = startInfo
			curInfo = endInfo
			skipFirstOne = False
			if dir == "backward":
				lastInfo = endInfo
				curInfo = startInfo
				skipFirstOne = True # skips the first link, proccessed in "forward"

			while curInfo != None:
				# Loop for following links.
				if skipFirstOne:
					skipFirstOne = False # skip this one
				else:
					# add the link to the result, or break if we hit a link that
					# is in the results already to avoid infinite loops.
					startEnd = ( ( lastInfo["guid"], lastInfo["chunk"] ), ( curInfo["guid"], curInfo["chunk"] ) )
					endStart = ( ( curInfo["guid"], curInfo["chunk"] ), ( lastInfo["guid"], lastInfo["chunk"] ) )
					if resultLinks.__contains__( startEnd ) or resultLinks.__contains__( endStart ):
						break

					if dir == "forward":
						resultLinks.append( startEnd );
					else:
						resultLinks.append( endStart );

				# find the next node
				links = curInfo["properties"][LINK_PROP_NAME]
				self.cleanupEmptyLinks( links )
				numLinks = len(links)
				if links.__contains__( ( lastInfo["guid"], lastInfo["chunk"] ) ):
					numLinks -= 1

				backLinks = curInfo["backLinks"]
				self.cleanupEmptyLinks( backLinks )
				numBackLinks = len(backLinks)
				if backLinks.__contains__( ( lastInfo["guid"], lastInfo["chunk"] ) ):
					numBackLinks -= 1

				if numLinks == 1:
					# there's a outgoing link, so use it.
					nextNode = links[0];
					if nextNode == ( lastInfo["guid"], lastInfo["chunk"] ):
						# The first link is to the lastInfo, so there must be
						# two links, and our next node must be in the second.
						nextNode = links[1];

					lastInfo = curInfo
					curInfo = WorldEditor.udoGet( nextNode[0], nextNode[1] );

				elif numBackLinks == 1:
					# no outgoing links, but there's a backlink, so use it.
					nextNode = backLinks[0];
					if nextNode == ( lastInfo["guid"], lastInfo["chunk"] ):
						# The first link is to the lastInfo, so there must be
						# two links, and our next node must be in the second.
						nextNode = backLinks[1];

					lastInfo = curInfo
					curInfo = WorldEditor.udoGet( nextNode[0], nextNode[1] );

				else:
					# no suitable links so break.
					break

		# do the actual operation on the found links
		for link in resultLinks:
			id1 = link[0][0]
			chunk1 = link[0][1]
			id2 = link[1][0]
			chunk2 = link[1][1]

			WorldEditor.udoDeleteLinks( id1, chunk1, id2, chunk2 )

			if newDir == "START_END" or newDir == "BOTH":
				WorldEditor.udoCreateLink( id1, chunk1, id2, chunk2, LINK_PROP_NAME )

			if newDir == "END_START" or newDir == "BOTH":
				WorldEditor.udoCreateLink( id2, chunk2, id1, chunk1, LINK_PROP_NAME )







