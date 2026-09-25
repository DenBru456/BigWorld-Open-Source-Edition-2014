import BigWorld
from Math import Vector3
import random

def getBotTalked():
	values = []
	for b in BigWorld.bots.values():
		values.append(b.player.botTalked)
	return values
		
BigWorld.addWatcher( "bots/botTalked", getBotTalked )


class Avatar( BigWorld.Entity ):
	
	COMBAT_RADIUS = 300
	
	def onBecomePlayer( self ):
		self.targetID = None
		self.dest = None
		self.clientApp.autoMove = False
		self.botTalked = 0
		
		self._randomTeleport()
		self.targetTimer = self.clientApp.addTimer( 5.0, self._chooseTarget, True )
		
	
	def onTick( self, curTime ):
		# If our target has gone out of range, forget em
		if self.targetID and \
			   not self.clientApp.entities.has_key( self.targetID ):
			self.targetID = None

		# If we haven't found anyone to target yet, look for em
		if self.targetID is None:
			self._chooseTarget()
			if self.targetID is None:
				return
		
		target = self.clientApp.entities[ self.targetID ]
		dist = Vector3( self._position() ).\
			   flatDistTo( Vector3( target.position ) )

		# If we're near enough to the target, start talking
		if dist < 8.0:

			if self.clientApp.isMoving:
				self.clientApp.stop()
			if target.botTalked < 10:
				self.cell.talkToOthers( self.targetID )
			else:
				self.targetID = None

		# If not, hunt em down
		elif dist > 12.0 and \
			 (not self.clientApp.isMoving or \
			  self.dest.flatDistTo( target.position ) > 25.0):
			self._moveTo( (target.position.x, 0, target.position.z) )


	def _moveTo( self, pos ):
		if pos:
			self.dest = Vector3( pos )
			self.clientApp.moveTo( self.dest )


	def _nearest( self, e1, e2 ):
		mypos = self._position()
		e1pos = e1.position
		e2pos = e2.position
		if (e1pos.x - mypos.x) ** 2 + (e1pos.z - mypos.z) ** 2 <= \
		   (e2pos.x - mypos.x) ** 2 + (e2pos.z - mypos.z) ** 2:
			return e1
		else:
			return e2

	def _position( self ): return self.clientApp.position


	def _randomTeleport( self ):
		if self.isDestroyed:
			clientApp = self.clientApp
			if clientApp:
				clientApp.delTimer( self.targetTimer )
			return
		self.clientApp.snapTo(
			(random.randint( -self.COMBAT_RADIUS, self.COMBAT_RADIUS ), 0,
			 random.randint( -self.COMBAT_RADIUS, self.COMBAT_RADIUS )) )

	
	def _chooseTarget( self ):
		if self.isDestroyed:
			clientApp = self.clientApp
			if clientApp:
				clientApp.delTimer( self.targetTimer )
			return
		candidates = [ e for e in self.clientApp.entities.values() \
					   if e.__class__ == Avatar and e.id != self.id and e.botTalked < 10 ]
		if candidates:
			tgt = reduce( self._nearest, candidates )
			self.targetID = tgt.id
			self.clientApp.faceTowards( tgt.position )
		else:
			self.targetID = None
