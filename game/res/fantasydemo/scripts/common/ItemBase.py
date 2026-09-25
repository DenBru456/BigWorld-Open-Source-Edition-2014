"""This module implements the BaseItem class."""


"""
The items list:
2		STAFF_TYPE				Staff.STAFF_SNAKE
3		STAFF_TYPE_2			Staff.STAFF_LIGHTNING
4		DRUMSTICK_TYPE			Food.STRIFF_DRUMSTICK 
5		SPIDER_LEG_TYPE			Foog.SPIDER_LEG
6		BINOCULARS_TYPE			Gadget.BINOCULARS
7		SWORD_TYPE				Wield.SWORD_BASTARD
9		SWORD_TYPE_2			Wield.SWORD_BASTARD_MITHRIL
10		AXE_TYPE				Axe.AXE
17		GOBLET_TYPE				Food.WINE_GOBLET
"""

# ------------------------------------------------------------------------------
# Class ItemBase:
# ------------------------------------------------------------------------------

class ItemBase:
	'''Enumerates all item type in the game.
	'''
	NONE_TYPE				= -1
	STAFF_TYPE				=  2
	STAFF_TYPE_2			=  3
	DRUMSTICK_TYPE			=  4
	SPIDER_LEG_TYPE			=  5
	BINOCULARS_TYPE			=  6
	SWORD_TYPE				=  7
	SWORD_TYPE_2			=  9
	AXE_TYPE				=  10
	GOBLET_TYPE				=  17

	ITEM_PRICES = {
		STAFF_TYPE			:  20,
		STAFF_TYPE_2		:  19,
		DRUMSTICK_TYPE		:  5,
		SPIDER_LEG_TYPE		:  8,
		BINOCULARS_TYPE		:  10,
		SWORD_TYPE			:  17,
		SWORD_TYPE_2		:  19,
		AXE_TYPE			:  10,
		GOBLET_TYPE			:  7,
	}


def price( itemType ):
	'''Returns price of item of given type.
	'''
	return ItemBase.ITEM_PRICES[ itemType ]

#ItemBase.py
