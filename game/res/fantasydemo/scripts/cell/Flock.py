"This module implements the Flock entity."

import BigWorld

import random
from math import sin, cos

# ------------------------------------------------------------------------------
# Section: class Flock
# ------------------------------------------------------------------------------

STATE_FLYING = 0
STATE_LANDING = 1

# The boids will pick a group of trees whose average position is
# closest to their flight centre.

ripperTrees = [
	(-42, 12, 265),
	(-40, 12, 278),
	(-46, 7, 296),
	(-48, 9, 297),
	(-54, 7, 290),
	(-64, 0, 284),
	(-52, 8, 348),
	(-50, 17, 359)
]

shantyTrees = [
	(-40, 9, 356),
	(-46, 9, 409),
	(-46, 9, 409),
	(-11, 10, 446),
	(17, 12, 445)
]

forestTrees = [
	(111.82, 14.00, 382),
	(112.24, 15.03, 426),
	(112.68, 14.00, 450),
	(86.08, 11.24, 383),
	(118.89, 14.00, 412),
	(124.20, 14.00, 401),
	(124.34, 14.92, 445),
	(103.98, 14.00, 382),
	(128.68, 14.00, 457),
	(139.95, 10.68, 445),
	(62.42, 14.00, 412),
	(140.70, 11.32, 423),
	(140.75, 14.80, 435),
	(140.94, 10.86, 411),
	(141.25, 14.00, 467),
	(57.56, 14.22, 425),
	(45.07, 16.50, 414),
	(43.00, 12.87, 418),
	(93.92, 14.00, 380),
	(109.14, 14.89, 409),
	(93.46, 14.00, 386),
	(110.55, 16.28, 456),
	(110.90, 14.00, 394),
	(87.39, 14.00, 438),
	(118.42, 11.05, 435),
	(78.61, 14.00, 446),
	(127.16, 14.14, 436),
	(96.15, 11.05, 445),
	(107.38, 14.96, 434),
	(85.79, 14.93, 424),
	(118.53, 14.00, 475),
	(80.73, 11.05, 464),
	(125.00, 14.00, 488),
	(77.41, 14.00, 456),
	(127.11, 14.00, 460),
	(75.01, 14.00, 424),
	(72.89, 14.88, 409),
	(72.40, 11.05, 465),
	(131.30, 15.47, 476),
	(133.11, 16.29, 481),
	(134.42, 14.00, 469),
	(134.53, 14.48, 434),
	(137.40, 14.05, 450),
	(64.53, 11.05, 464),
	(91.91, 11.05, 487),
	(111.40, 11.05, 481),
	(102.32, 15.09, 442),
	(102.40, 11.05, 479),
	(91.50, 15.24, 433),
	(112.87, 11.84, 404),
	(88.58, 11.05, 473),
	(115.37, 22.49, 440),
	(100.12, 15.21, 405),
	(85.77, 11.05, 491),
	(85.34, 14.00, 392),
	(84.82, 11.05, 446),
	(83.93, 11.05, 454),
	(119.42, 14.00, 390),
	(82.42, 15.13, 419),
	(77.80, 14.00, 390),
	(77.65, 14.00, 408),
	(77.11, 11.05, 488),
	(130.24, 14.96, 464),
	(130.63, 14.28, 425),
	(68.59, 14.00, 455),
	(68.15, 17.72, 400),
	(67.32, 14.00, 384),
	(58.08, 15.53, 387),
	(57.76, 13.77, 398),
	(106.12, 32.83, 420),
	(96.76, 14.00, 396),
	(109.37, 11.05, 475),
	(93.29, 13.37, 412),
	(111.01, 13.21, 458),
]

waterTrees = [
	(-203, 11.7, 18.6),
	(-206, 9.3, -5.3)
]

pathTrees = [
	(-20, 26, -14)
]

forestTrees = [
	(3.38, 46, 37),
	(-57, 25, 15.8)
]

# ringdemo
#treeGroups = [waterTrees, pathTrees, forestTrees]

# demo3city
#treeGroups = [ripperTrees, shantyTrees, forestTrees]

treeGroups = []

class Flock( BigWorld.Entity ):
	"A Flock entity."

	def __init__( self ):
		BigWorld.Entity.__init__( self )

		pos = self.position
		self.xorigin = pos[0]
		self.yorigin = pos[1]
		self.zorigin = pos[2]
#		self.setAoIRadius(20)
#		self.setAoIUpdates(1)
		self.stateChangeTime = BigWorld.time()
		self.treeGroup = self.pickTreeGroup()
		if self.state == STATE_FLYING:
			self.fly()

	def pickTreeGroup( self ):
		if len(treeGroups):
			distances = map(self.treeGroupDistanceSquared, treeGroups)
			return distances.index(min(distances))
		else:
			return -1

	def treeGroupDistanceSquared( self, group ):
		sum = reduce(lambda a, b: (a[0] + b[0], 0, a[2] + b[2]), group)
		dx = sum[0] / len(group) - self.position[0]
		dz = sum[2] / len(group) - self.position[2]
		return dx * dx + dz * dz

	def onTimer( self, timerID, userID ):
		assert( 1 or userID ) # Not used

		now = BigWorld.time()
		self.position = ( self.xorigin + 40 * sin(0.24 * now), \
					self.yorigin, self.zorigin + 45 * cos(0.27 * now) )

		if now - self.stateChangeTime >= self.maxFlightTime and \
			self.treeGroup != -1:
			self.land(self.findLandingPoint())
			self.cancel(timerID)

	def findLandingPoint( self ):
		group = treeGroups[self.treeGroup]
		index = random.randrange(len(group))
		return group[index]

	def land( self, position ):
		self.state = STATE_LANDING
		self.position = position
		self.stateChangeTime = BigWorld.time()

	def fly( self ):
		self.state = STATE_FLYING
		self.stateChangeTime = BigWorld.time()
		self.addTimer( 0, 0.1 )

#	def enterAoI( self, id ):
#		entity = BigWorld.entities[id]
#		if self.state == STATE_LANDING and entity.className == "Avatar":
#			self.fly()

#	def leaveAoI( self, id ):
#		pass

# Flock.py
