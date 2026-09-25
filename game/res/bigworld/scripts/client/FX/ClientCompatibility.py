#Stub out some fns used by the editor, for compatibility with the client

import BigWorld
if BigWorld.component == "editor":
	#Stub out addMat, delMat
	def addMat(a,b): return 0
	def delMat(a): return 0
	BigWorld.addMat = addMat
	BigWorld.delMat = delMat

	#Stub out Player
	def player(): return None
	BigWorld.player = player
