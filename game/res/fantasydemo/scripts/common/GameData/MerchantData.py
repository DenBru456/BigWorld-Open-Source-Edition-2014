# This module contains constant data associated with the Merchant entity type.

import ResMgr
import AvatarModel
import ItemBase
import PresetModel

AVATAR_MODE_DATA = None
MERCHANT_ITEMS = None

def init():
	global AVATAR_MODEL_DATA
	global MERCHANT_ITEMS

	AVATAR_MODEL_DATA = AvatarModel.pack( PresetModel.load( ResMgr.openSection( 'scripts/data/merchant_model_data.xml' ) ) )

	MERCHANT_ITEMS = set([
							ItemBase.ItemBase.STAFF_TYPE,
							ItemBase.ItemBase.STAFF_TYPE_2,
							ItemBase.ItemBase.DRUMSTICK_TYPE,
							#ItemBase.ItemBase.SPIDER_LEG_TYPE,
							ItemBase.ItemBase.BINOCULARS_TYPE,
							ItemBase.ItemBase.SWORD_TYPE,
							ItemBase.ItemBase.SWORD_TYPE_2,
							ItemBase.ItemBase.AXE_TYPE,
							ItemBase.ItemBase.GOBLET_TYPE,
							])

MIN_STOCK = 1
MAX_STOCK = 1

init()
