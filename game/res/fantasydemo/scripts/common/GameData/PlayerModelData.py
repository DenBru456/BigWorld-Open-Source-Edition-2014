'''The module contains data about available player models and their posible
customisations. All models and their customisations (dyes etc.) are required
to be present in the AvatarModelData module.
'''

import ResMgr
import AvatarModelData
import CustomisableModel
import PresetModels
import DefaultModel

PLAYER_MODELS = None

def init():
	global PLAYER_MODELS
	global PRESET_MODELS
	global DEFAULT_MODEL

	modelData = ResMgr.openSection( "scripts/data/player_model_data.xml" )
	PLAYER_MODELS = CustomisableModel.load( modelData )
	PRESET_MODELS = PresetModels.load( modelData )
	DEFAULT_MODEL = DefaultModel.load( modelData )

init()
