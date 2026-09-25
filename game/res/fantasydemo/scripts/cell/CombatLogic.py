import random


# CombatLogic primary function
# attacker is the attacking entity,
# defender is the defending entity,
# and theMove is the move performed by the attacker

CL_HIT = 0
CL_DESPERATE = 1
CL_PARRY = 2
CL_MISS = 3

resultAnimTimes = {
	CL_HIT: 2,
	CL_DESPERATE: 2,
	CL_PARRY: 1,
	CL_MISS: 1,
	(1<<5) | 1: 1
}

hitResultStrings = {
	CL_HIT: "hit",
	CL_DESPERATE: "desperate parry",
	CL_PARRY: "parry",
	CL_MISS: "miss"
}

def parryChance(defender, move):
	return 70 * (defender.ccDefence / 100)
	#in proper version depends on specific move used and skill of defender

def strikeChance(move):
	return 70
	#in proper version depends on specific move used and skill of attacker

def desperateChance(defender, move):
	return 70 * ((defender.ccDefence + 50) / 150)

def breakChance(defender):
	return 50

def swing( attacker, defender, theMove ):
	# see if the 'attacker' is trying to break away
	if attacker.stance == 0:
		didBreak = random.randint(1,100)>breakChance(defender)
		print attacker.playerName, "attempts to break away from", \
			defender.playerName, "and", [ "fails", "succeeds" ][ didBreak ]
		return [ CL_MISS, (1<<5)|1 ][ didBreak ]

	# it's a normal attack then
	if random.randint(1,100)>strikeChance(theMove): hitResult = CL_MISS
	elif random.randint(1,100)<=parryChance(defender, theMove): hitResult = CL_PARRY
	elif random.randint(1,100)<=desperateChance(defender, theMove):
		hitResult = CL_DESPERATE
		defender.reduceDefence(10)
	else:
		hitResult = CL_HIT
		defender.reduceDefence(10)
		defender.closeHit(random.randint(10,25), attacker.id)

	print attacker.playerName, "attacks", defender.playerName, \
		"with a result of", hitResultStrings[ hitResult ]
	#returns the hit|parry|desperate parry|miss in 3 bits
	return (theMove << 3) | hitResult

# CombatLogic.py
