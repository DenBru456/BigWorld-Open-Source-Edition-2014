
import BigWorld
import ItemBase

from Item import Item
from Food import Food
from Gadget import Gadget
from Staff import Staff
from Wield import Wield
from Axe import Axe

# This dictionary maps an old item type to the new item class and class subtype
oldItemTypeDict = {
	Item.STAFF_TYPE:			( Staff,	Staff.SNAKE ),
	Item.STAFF_TYPE_2:			( Staff,	Staff.LIGHTNING ),
	Item.DRUMSTICK_TYPE:		( Food,		Food.STRIFF_DRUMSTICK )	,
	Item.SPIDER_LEG_TYPE:		( Food,		Food.SPIDER_LEG )	,
	Item.BINOCULARS_TYPE:		( Gadget,	Gadget.BINOCULARS ),
	Item.SWORD_TYPE:			( Wield,	Wield.SWORD_BASTARD ),
	Item.SWORD_TYPE_2:			( Wield,	Wield.SWORD_BASTARD_MITHRIL ),
	Item.AXE_TYPE:				( Axe,		Wield.BATTLE_AXE ),
	Item.GOBLET_TYPE:			( Food,		Food.WINE_GOBLET ),
}

# This method returns information for this old-style item type
# The info is the class and the new-style item type
def lookupItem( itemType ):
	try:
		return oldItemTypeDict[ itemType ]
	except:
		return None

# ------------------------------------------------------------------------------
# Method: resolveIconName
# Description:
#	- returns the icon name for the item class if one exists
# ------------------------------------------------------------------------------
def resolveIconName( itemType ):
	methodName = "resolveIconName"
	itemTup = lookupItem( itemType )

	if itemTup == None:
		print methodName + "itemType: " + \
			str( itemType ) + " is not an item."
		return ""
	else:
		itemClass = itemTup[0]
		itemID = itemTup[1]

		if itemID in itemClass.guiIconNames.keys():
			return itemClass.guiIconNames[ itemID ]
		else:
			print methodName + "itemType: " + \
				str( itemID ) + " has no GUI Icon."
			return itemClass.guiIconNames[ itemClass.UNKNOWN_TYPE ]


# ------------------------------------------------------------------------------
# Method: newItem
# Description:
#	- Creates a new Item when supplied with an item type.
#	- The itemType supplied is the old-style item value. This method is for
#	  compatibility with the old-style code until new-style revolution takes
#	  over.
#	- Now if we have prerequisites, and the item constructor accepts them,
#	  we pass them in.  Support legacy constructor for now as well.
# ------------------------------------------------------------------------------
def newItem( itemType, prereqs = None ):
	r = lookupItem( itemType )
	if not r:
		#~ print "Item.newItem: lookup for", itemType, "failed"
		#~ import traceback
		#~ traceback.print_stack()
		return None
	return r[0]( r[1], prereqs )


# ------------------------------------------------------------------------------
# A Helper class to load an item in the loading thread.
#
# When the callbackFn is called, self.resourceRefs holds the necessary resources
# for the item's construction.
# ------------------------------------------------------------------------------
class LoadBG:
	def __init__( self, itemNo, callbackFn ):
		self.itemNo = itemNo
		self.resourceRefs = None
		self.itemTypeDict = lookupItem(itemNo)
		if not self.itemTypeDict:
			if callbackFn != None:
				callbackFn( self )
			return

		self.itemType = self.itemTypeDict[0]
		self.callbackFn = callbackFn
		if hasattr( self.itemType, "prerequisites" ):
			resourceList = tuple(set(self.itemType.prerequisites(itemNo)))
			BigWorld.loadResourceListBG( resourceList, self.onLoad, 128 )
		else:
			if self.callbackFn != None:
				self.callbackFn( self )
				self.callbackFn = None

	def onLoad( self, resourceRefs ):
		self.resourceRefs = resourceRefs
		if self.callbackFn != None:
			self.callbackFn( self )
			self.callbackFn = None


# ------------------------------------------------------------------------------
# A static method which is called to get a list of preload resources.
# ------------------------------------------------------------------------------
def Item_preload( list ):
	pass

def giveSwords():
	p = BigWorld.player()

	p.inventoryMgr.addItem( Item.SWORD_TYPE )
	p.inventoryMgr.addItem( Item.SWORD_TYPE_2 )

	p.inventoryWindow.updateInventory(
					p.inventoryItems,
					p.inventoryMgr.availableGoldPieces() )

def giveAll():
	p = BigWorld.player()

	p.inventoryMgr.addItem( Item.STAFF_TYPE )
	p.inventoryMgr.addItem( Item.STAFF_TYPE_2 )
	p.inventoryMgr.addItem( Item.DRUMSTICK_TYPE )
	p.inventoryMgr.addItem( Item.BINOCULARS_TYPE )
	p.inventoryMgr.addItem( Item.SWORD_TYPE )
	p.inventoryMgr.addItem( Item.SWORD_TYPE_2 )
	p.inventoryMgr.addItem( Item.AXE_TYPE )
	p.inventoryMgr.addItem( Item.GOBLET_TYPE )

	p.inventoryWindow.updateInventory(
					p.inventoryItems,
					p.inventoryMgr.availableGoldPieces() )

#Item.py
