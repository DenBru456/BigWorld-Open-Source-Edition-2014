import BigWorld


class DroppedItem( BigWorld.Entity ):
	'''Plays the role of a collectible item dropped on the ground (cell-side).
	'''
	DESTROY_TIMER	=  0
	UNLINK_TIMER   =  1	
	UNLINK_TIMEOUT =  10


	def __init__( self ):
		BigWorld.Entity.__init__( self )

		if self.timeToLive != 0:
			self.addTimer( self.timeToLive, 0, DroppedItem.DESTROY_TIMER )

		# unset the ownerID so that clients getting this entity some time 
		# after it's dropped don't play the drop animation on its owner
		self.addTimer( DroppedItem.UNLINK_TIMEOUT, 0, DroppedItem.UNLINK_TIMER )


	def pickUpRequest( self, whomID ):
		'''Returns true if item can be picked. Sets the pickerID to 
		the Entity who requested it for the first time this is called.
		Also set a destroy timer to remove the item from the world. 
		Between the first call and the time of destruction, this 
		method will return false.
		Params:
			whomID			id of entity requesting to pick up item
		'''
		try:
			if self.pickerID == 0:
				picker = BigWorld.entities[ whomID ]
				picker.base.pickUpResponse( True, self.id, self.classType )
				self.addTimer( 5, 0, DroppedItem.DESTROY_TIMER )
				self.pickerID = whomID
			else:
				picker = BigWorld.entities[ whomID ]
				picker.base.pickUpResponse( False, self.id, 0 )
		except KeyError:
			errorMsg = 'pickUpRequest: request from unknown entity: %d'
			print errorMsg % whomID


	def onTimer( self, timerId, userId ):		
		'''Timer event handler.
		'''
		# destrou this item (has been picked up)
		if ( userId == DroppedItem.DESTROY_TIMER ):
			self.destroy()
		# unlink this item from dropper (has been dropped)
		elif ( userId == DroppedItem.UNLINK_TIMER ):
			self.dropperID = 0

# DroppedItem.py
