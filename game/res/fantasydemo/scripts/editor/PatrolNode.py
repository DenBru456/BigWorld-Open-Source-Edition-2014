
# Importing WorldEditor to use linking functions
import WorldEditor
import WorldEditorDirector


# name of the patrol path link property
PATROL_PROP_NAME = "patrolLinks"


class PatrolNode:

	# return the patrol node model
	def modelName( self, props ):
		try:
			return "resources/models/station.model"
		except:
			return "helpers/props/standin.model"


	# patrol nodes always show the "+" gizmo
	def showAddGizmo( self, propName, thisInfo ):
		return True
		
		
	# patrol nodes linking conditions
	def canLink( self, propName, thisInfo, otherInfo ):
		thisProps = thisInfo["properties"]
		otherProps = otherInfo["properties"]
		
		if propName != PATROL_PROP_NAME and propName[0:len(PATROL_PROP_NAME) + 1] != PATROL_PROP_NAME + "[":
			# only one link to the "patrolLinks" link property, or an array
			# item such as "patrolLinks[0]".
			return False
		elif thisProps[PATROL_PROP_NAME].__contains__( ( otherInfo["guid"], otherInfo["chunk"] ) ):
			# only one link per PatrolNode
			return False
		elif otherInfo["type"] != thisInfo["type"]:
			# can only link to PatrolNode type
			return False
			
		return True


	# after cloning a single patrol node, it should link to the previous one.
	def postClone( self, thisInfo, otherInfo ):
		if WorldEditorDirector.bd.itemTool.functor.script.selection.size > 1:
			# only link to the previous one if only cloning one patrol node
			return
		
		WorldEditor.udoCreateLink( otherInfo["guid"], otherInfo["chunk"], thisInfo["guid"], thisInfo["chunk"], PATROL_PROP_NAME )
		
		return True


	# helper method to remove empty links
	def removeEmptyLinks( self, links ):
		emptyLink = ("","")
		while links.__contains__( emptyLink ):
			links.remove( emptyLink )
		
		
	# when a node is deleted, other nodes must be relinked
	def onDeleteObject( self, nodeInfo ):
		links = nodeInfo["properties"][ PATROL_PROP_NAME ]
		backLinks = nodeInfo["backLinks"]
		self.removeEmptyLinks( links )
		self.removeEmptyLinks( backLinks )
		
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
			WorldEditor.udoCreateLink( relinkNode[0], relinkNode[1], link[0], link[1], PATROL_PROP_NAME )
		
		# Relinking incomming links (BackLinks)
		for backlink in backLinks[backLinksBegin:]:
			WorldEditor.udoCreateLink( backlink[0], backlink[1], relinkNode[0], relinkNode[1], PATROL_PROP_NAME )
			
		# No need to add barrier here, since WorldEditor will add a barrier anyway


	# called to get extra context menu commands from the script
	def onStartLinkMenu( self, startInfo, endInfo ):
		# we should localise these strings
		return ( "",
			"`SCRIPT/PATROL_NODE_PY/SPLIT_LINK",
			"",
			"`SCRIPT/PATROL_NODE_PY/SWAP_LINK_DIRECTION",
			"`SCRIPT/PATROL_NODE_PY/BOTH_DIRECTIONS",
			"",
			"`SCRIPT/PATROL_NODE_PY/SWAP_LINK_DIRECTION_RUN_OF_LINKS",
			"`SCRIPT/PATROL_NODE_PY/BOTH_DIRECTIONS_RUN_OF_LINKS" )
	
	
	# called when one of the extra context menu commands is clicked
	def onEndLinkMenu( self, command, startInfo, endInfo ):
		if command == 0:
			self.splitLink( startInfo, endInfo )
		elif command == 1:
			self.swapLink( startInfo, endInfo )
		elif command == 2:
			self.bothDirLink( startInfo, endInfo )
		elif command == 3:
			self.swapLinksRun( startInfo, endInfo )
		elif command == 4:
			self.bothDirLinksRun( startInfo, endInfo )
		else:
			WorldEditor.addCommentaryMsg( "PatrolNode: received unknown command " + str(command) + ".", 0 )
			
			
	# split a link, creating a new node in the middle
	def splitLink( self, startInfo, endInfo ):
		startProps = startInfo["properties"]
		endProps = endInfo["properties"]
		
		# find out whether the nodes are linked in one or both directions
		startToEndLink = False
		endToStartLink = False
		if startProps[PATROL_PROP_NAME].__contains__( ( endInfo["guid"], endInfo["chunk"] ) ):
			startToEndLink = True
		if endProps[PATROL_PROP_NAME].__contains__( ( startInfo["guid"], startInfo["chunk"] ) ):
			endToStartLink = True
		
		# create new node
		snapToTerrain = 1
		AIR_THRESHOLD = 1.0
		startMin = ( startInfo["position"][0], startInfo["position"][1] - AIR_THRESHOLD, startInfo["position"][2] )
		startMax = ( startInfo["position"][0], startInfo["position"][1] + AIR_THRESHOLD, startInfo["position"][2] )
		endMin = ( endInfo["position"][0], endInfo["position"][1] - AIR_THRESHOLD, endInfo["position"][2] )
		endMax = ( endInfo["position"][0], endInfo["position"][1] + AIR_THRESHOLD, endInfo["position"][2] )
		if WorldEditor.terrainCollide( startMax, startMin ) < 0.0 or WorldEditor.terrainCollide( endMax, endMin ) < 0.0:
			# one of the link's end points is in the air, so don't snap to terrain
			snapToTerrain = 0
			
		midPoint = ( (startInfo["position"][0] + endInfo["position"][0])/2.0,
					 (startInfo["position"][1] + endInfo["position"][1])/2.0,
					 (startInfo["position"][2] + endInfo["position"][2])/2.0 )
		newInfo = WorldEditor.udoCreateAtPosition( startInfo["guid"], startInfo["chunk"], midPoint, snapToTerrain )
		newProps = newInfo["properties"]
		
		# delete old links
		WorldEditor.udoDeleteLinks( startInfo["guid"], startInfo["chunk"], endInfo["guid"], endInfo["chunk"] )
		
		# relink
		if startToEndLink:
			WorldEditor.udoCreateLink( startInfo["guid"], startInfo["chunk"], newInfo["guid"], newInfo["chunk"], PATROL_PROP_NAME )
			WorldEditor.udoCreateLink( newInfo["guid"], newInfo["chunk"], endInfo["guid"], endInfo["chunk"], PATROL_PROP_NAME )
			
		if endToStartLink:
			WorldEditor.udoCreateLink( endInfo["guid"], endInfo["chunk"], newInfo["guid"], newInfo["chunk"], PATROL_PROP_NAME )
			WorldEditor.udoCreateLink( newInfo["guid"], newInfo["chunk"], startInfo["guid"], startInfo["chunk"], PATROL_PROP_NAME )
			
		WorldEditor.addUndoBarrier( "Split link" )
	
	
	# swap the direction of the link
	def swapLink( self, startInfo, endInfo ):
		startProps = startInfo["properties"]
		
		# find out whether the nodes are linked in one or both directions
		startToEndLink = False
		if startProps[PATROL_PROP_NAME].__contains__( ( endInfo["guid"], endInfo["chunk"] ) ):
			startToEndLink = True
			
		WorldEditor.udoDeleteLinks( startInfo["guid"], startInfo["chunk"], endInfo["guid"], endInfo["chunk"] )
		
		if startToEndLink:
			WorldEditor.udoCreateLink( endInfo["guid"], endInfo["chunk"], startInfo["guid"], startInfo["chunk"], PATROL_PROP_NAME )
		else:
			WorldEditor.udoCreateLink( startInfo["guid"], startInfo["chunk"], endInfo["guid"], endInfo["chunk"], PATROL_PROP_NAME )

		WorldEditor.addUndoBarrier( "Swap link direction" )

	# set the link direction to enable traversing both ways
	def bothDirLink( self, startInfo, endInfo ):
		WorldEditor.udoCreateLink( startInfo["guid"], startInfo["chunk"], endInfo["guid"], endInfo["chunk"], PATROL_PROP_NAME )
		WorldEditor.udoCreateLink( endInfo["guid"], endInfo["chunk"], startInfo["guid"], startInfo["chunk"], PATROL_PROP_NAME )

		WorldEditor.addUndoBarrier( "Create links in both directions" )


	# swap the direction of the link
	def swapLinksRun( self, startInfo, endInfo ):
		newDir = "START_END"
		if startInfo["properties"][PATROL_PROP_NAME].__contains__( ( endInfo["guid"], endInfo["chunk"] ) ):
			newDir = "END_START"
			
		self.changeDir( startInfo, endInfo, newDir )
		
		WorldEditor.addUndoBarrier( "Swap direction of links (run of links)" )


	# set the link direction to enable traversing both ways
	def bothDirLinksRun( self, startInfo, endInfo ):
		self.changeDir( startInfo, endInfo, "BOTH" )
		
		WorldEditor.addUndoBarrier( "Create links in both directions (run of links)" )


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
				links = curInfo["properties"][PATROL_PROP_NAME]
				self.removeEmptyLinks( links )
				numLinks = len(links)
				if links.__contains__( ( lastInfo["guid"], lastInfo["chunk"] ) ):
					numLinks -= 1

				backLinks = curInfo["backLinks"]
				self.removeEmptyLinks( backLinks )
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
				WorldEditor.udoCreateLink( id1, chunk1, id2, chunk2, PATROL_PROP_NAME )
				
			if newDir == "END_START" or newDir == "BOTH":
				WorldEditor.udoCreateLink( id2, chunk2, id1, chunk1, PATROL_PROP_NAME )
			
			







