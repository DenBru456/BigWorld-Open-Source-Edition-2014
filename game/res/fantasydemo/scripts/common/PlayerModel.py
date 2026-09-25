from GameData import PlayerModelData
import AvatarModel
import random
import re

def modelListToCharacterClassString( models ):
	"""
	Return a string identifying what character class the given model list
	represents, e.g. ranger or warrior.

	@param models 	The list of resource paths pointing to models that
					are composed into a particular character class's
					in-game avatar.
	"""
	charClass = None

	# Just pick the first model in the list, and extract the path component
	# after characters/avatars
	if len( models ) > 0:
		matches = re.search( r'characters/avatars/([^/]+)/', models[0] )
		if matches:
			charClass = matches.group( 1 )

	# If we don't have one, try an NPC model
	if charClass is None:
		if len( models ) > 0:
			matches = re.search( r'characters/npc/([^/]+)/', models[0] )
			if matches:
				charClass = matches.group( 1 )

	# Fallback
	if charClass is None:
		charClass = "(unknown)"

	return charClass


def defaultPlayerModel():
	return PlayerModelData.DEFAULT_MODEL

def randomPlayerModel( realm=None ):
	filteredModels = PlayerModelData.PLAYER_MODELS
	if realm is not None:
		filteredModels = [ x for x in filteredModels if x.realm == realm ]
		
	if len(filteredModels) == 0:
		print "ERROR: randomPlayerModel - no player models available for realm '%s'." % realm
		filteredModels = PlayerModelData.PLAYER_MODELS

	baseModel = random.choice( filteredModels )
	return baseModel.createInstanceWithRandomCustomisations()


def reCustomisePlayerModel( unpackedAvatarModel ):
	for model in PlayerModelData.PLAYER_MODELS:
		if set( model.models ).issubset( set( unpackedAvatarModel['models'] ) ):
			return model.createInstanceWithRandomCustomisations()
	assert "source model is not a player model. ['%s']" % "', '".join( unpackedAvatarModel['models'] )



# This is a temporary solution until the character customisation screen is
# implemented.
def nextPresetModel( oldAvatarModel ):
	models = PlayerModelData.PRESET_MODELS
	if oldAvatarModel in models:
		return models[(models.index( oldAvatarModel ) + 1) % len(models)]
	else:
		return models[0]

def previousPresetModel( oldAvatarModel ):
	models = PlayerModelData.PRESET_MODELS
	if oldAvatarModel in models:
		return models[models.index( oldAvatarModel ) - 1]
	else:
		return models[0]


# PlayerModel.py
