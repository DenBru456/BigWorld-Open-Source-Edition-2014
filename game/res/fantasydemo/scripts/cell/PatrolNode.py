

import BigWorld
import random


class PatrolNode(BigWorld.UserDataObject):
	
	#-------------------------------------------------------------------------
	# Constructor
	#-------------------------------------------------------------------------
	
	def __init__(self):
		BigWorld.UserDataObject.__init__(self)

	#-------------------------------------------------------------------------
	# This method returns the guid of the next node from 'self', choosing
	# randomly using the 'importance' as a weight in the random calculations.
	# If no UDO is found, it returns the empty link ("","")
	#-------------------------------------------------------------------------
	
	def nextPatrolNodeByImportance( self, lastNode = None ):
		if len(self.patrolLinks) == 0:
			# no next node
			return None
		elif len(self.patrolLinks) == 1:
			# return the only node
			return self.patrolLinks[0]
		
		
		if lastNode in self.patrolLinks:
			if self.backtrackChance > random.uniform( 0, 1 ):
				return lastNode

		# find out the sum of all "importance" properties
		importanceSum = 0;
		nodeSet = set(self.patrolLinks) - set([lastNode])
		for node in nodeSet:
			if node != None:
				importanceSum += node.importance
		
		# get a random number between 0 and the sum of all "importance"
		# properties
		importanceRand = random.randint( 0, importanceSum-1 )
		# use the "importance" of each linked node to define a segment in
		# the range of 0 to "importanceSum". A node is selected if the
		# random number falls inside the node's segment.
		for node in nodeSet:
			if node != None:
				if importanceRand < node.importance:
					return node	# random number within node's segment, so return
				importanceRand -= node.importance	# move to next segment.
			
		# nothing found, so return nothing
		return None
