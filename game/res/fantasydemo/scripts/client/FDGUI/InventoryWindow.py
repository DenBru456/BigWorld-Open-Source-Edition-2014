
import FantasyDemo
import BigWorld
import GUI
import ResMgr

import ItemLoader
import Keys
import Inventory

import Cursor
from Helpers import PyGUI
from Helpers.PyGUI import Window, DraggableWindow, PyGUIEvent, PyGUIBase
from Helpers.PyGUI.DraggableComponent import DraggableComponent


DRAGGED_ITEM_GUI_FILE_PRECACHE = ResMgr.openSection( "gui/dragged_item.gui" )



class DraggedItem( DraggableWindow ):
	base = DraggableWindow
	factoryString="FDGUI.DraggedItem"

	def __init__( self, component ):
		DraggedItem.base.__init__( self, component )


	def handleMouseButtonEvent( self, comp, event ):
		if event.key == Keys.KEY_LEFTMOUSE and not event.isKeyDown():
			self.active( False )

		return DraggedItem.base.handleMouseButtonEvent( self, comp, event )


	@staticmethod
	def create( texture ):
		c = GUI.Window( texture )
		return DraggedItem( c ).component


class ItemDropRegion( PyGUIBase ):
	base = PyGUIBase
	factoryString="FDGUI.DraggedItem"

	def __init__( self, component ):
		ItemDropRegion.base.__init__( self, component )


	def handleDragEnterEvent( self, comp, dragged ):
		if isinstance( dragged.script, InventorySlot ):
			return True

		return False


	def handleDropEvent( self, comp, dropped ):
		assert isinstance( dropped.script, InventorySlot )
		if dropped.parent.script.inventoryMgr:
			dropped.parent.script.inventoryMgr.selectItem( dropped.script.item['serial'] )
			dropped.parent.script.inventoryMgr._entity._checkStowAndEquip()
			dropped.parent.script.inventoryMgr._entity.dropTry()
			return True

		return False


class InventorySlot( Window ):
	base = Window
	factoryString="FDGUI.InventorySlot"

	def __init__( self, component ):
		InventorySlot.base.__init__( self, component )
		self.slotNumber = None
		self.item = None
		self.initialPosition = self.component.position
		self.draggedItem = None


	def onSave( self, dataSection ):
		InventorySlot.base.onSave( self, dataSection )
		dataSection.writeInt( 'InventorySlot/slotNumber', self.slotNumber )


	def onLoad( self, dataSection ):
		InventorySlot.base.onLoad( self, dataSection )
		self.slotNumber = dataSection.readInt( 'InventorySlot/slotNumber' )


	def handleMouseClickEvent( self, component ):
		InventorySlot.base.handleMouseClickEvent( self, component )
		if self.item:
			FantasyDemo.rds.keyBindings.callActionByName( "SelectItem", serialNumber = self.item['serial'] )
			return True

		return False


	def handleDragStartEvent( self, comp ):
		if self.draggedItem:
			self.draggedItem.script.active( False )
			self.draggedItem = None

		if self.item != None:
			self.draggedItem = GUI.load("gui/dragged_item.gui")
			self.draggedItem.textureName = self.component.textureName
			cursorPosition = PyGUI.Utils.mouseScreenPosition()
			self.draggedItem.position = (cursorPosition[0], cursorPosition[1], 0.2)
			self.draggedItem.script.active( True )
			self.draggedItem.script.startDragging( GUI.mcursor().position )
			return True

		return False


	def handleDragEnterEvent( self, comp, dragged ):
		if not isinstance( dragged.script, InventorySlot ):
			return False

		return True


	def handleDragStopEvent( self, component ):
		if self.draggedItem:
			self.draggedItem.script.active( False )
			self.draggedItem = None

		return True


	def handleDropEvent( self, comp, dropped ):
		assert isinstance( dropped.script, InventorySlot )
		
		parentScript = self.component.parent.script
		droppedParentScript = dropped.parent.script

		if parentScript.inventoryMgr is droppedParentScript.inventoryMgr and parentScript.inventoryMgr != None:
			selfItem = self.item
			droppedItem = dropped.script.item
			self.setItem( droppedItem )
			dropped.script.setItem( selfItem )
			return True
		else:
			return parentScript.handleDropEvent( comp, dropped )


	def __str__( self ):
		return "InventorySlot(%s)" % self.slotNumber


	def setItem( self, item ):
		self.item = item
		if self.item:
			itemType = self.item['itemType']
			itemSerial  = self.item['serial']
			lockHandle = self.item['lockHandle']
			self.component.textureName = ItemLoader.resolveIconName( itemType )
		else:
			self.component.textureName = ""


	@staticmethod
	def create( texture ):
		c = GUI.Window( texture )
		return InventorySlot( c ).component


class InventoryWindow( DraggableWindow ):
	factoryString="FDGUI.InventoryWindow"

	def __init__( self, component ):
		self.itemsMovedEvent = lambda inventory: None
		self.inventoryMgr = None
		self.inventoryItems = None
		DraggableWindow.__init__( self, component )


	def __str__( self ):
		return "InventoryWindow(%s)" % self.inventoryMgr


	def onSave( self, dataSection ):
		DraggableWindow.onSave( self, dataSection )
		pass


	def onLoad( self, dataSection ):
		DraggableWindow.onLoad( self, dataSection )
		pass


	def handleDragEnterEvent( self, comp, dragged ):
		if isinstance( dragged.script, InventorySlot ):
			return True

		return DraggableWindow.handleDragEnterEvent( self, comp, dragged )


	def handleDropEvent( self, comp, dropped ):
		if not isinstance( dropped.script, InventorySlot ):
			return False

		if self.inventoryMgr != None and isinstance( dropped.parent.script, TraderWindow.TraderWindow ):
			traderWindow = dropped.parent.script
			itemIndex = traderWindow.inventoryItems.index( dropped.script.item )
			self.inventoryMgr._entity.onBuyItem( itemIndex )

			return True

		return DraggableWindow.handleDropEvent( self, comp, dropped )


	def onBound( self ):
		DraggableWindow.onBound( self )


	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )


	def active( self, show ):
		if self.isActive == show:
			return

		DraggableWindow.active( self, show )
		Cursor.showCursor( show )


	def updateInventory( self, inventoryItems, goldPieces = None ):
		self.inventoryItems = inventoryItems

		# Only display the items that are unlocked
		unlockedItems = [item for item in inventoryItems
			if item.lockHandle == Inventory.NOLOCK]

		if goldPieces != None:
			self.component.goldLable.text = '%7ig' % int( goldPieces )

		inventorySlots = dict( [(child.script.slotNumber, child)
			for name, child in self.component.children
				if isinstance( child.script, InventorySlot )] )

		items = dict( [ ( item['serial'], item )
			for item in unlockedItems] )


		placedItems = []

		for i in inventorySlots.values():
			if i.script.item and i.script.item['serial'] in items:
				i.script.setItem( items[ i.script.item['serial'] ] )
				placedItems.append( items[ i.script.item['serial'] ] )
			else:
				i.script.setItem( None )

		unplacedItems = [ i for i in unlockedItems if not i in placedItems ]
		emptySlots = [ i for i in inventorySlots.values() if not i.script.item ]

		for item in unplacedItems:
			if len( emptySlots ) > 0:
				emptySlots[0].script.setItem( item )
				del emptySlots[0]


	@staticmethod
	def create( texture ):
		c = GUI.Window( texture )
		return InventoryWindow( c ).component




import TraderWindow


