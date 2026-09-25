import BigWorld, GUI, Keys
import ResMgr
import Utils

from PyGUIBase import PyGUIBase

ITEM_MARGIN = 0.05

# -------------------------------------------------------------------------
# This class implements a scrolling list of whatever gui items you please
# -------------------------------------------------------------------------
class ScrollingList( PyGUIBase ):

	factoryString="PyGUI.ScrollingList"

	def __init__( self, component ):
		PyGUIBase.__init__( self, component )
		self.selection = 0
		self.itemGuiName = ""
		self.itemGuiDS = None
		self.backFn = None
		self.budget = Utils.Budget( self.createItem, self.deleteItem )
		self.selectItemCallback = lambda x: None
		self.maxVisibleItems = 0
		self.totalHeightScreenClip = 0.0
		component.focus = True
		component.crossFocus = True

	def active( self, state ):
		if state == self.isActive:
			return
		PyGUIBase.active( self, state )
		self.selectItem( self.selection )

	#This method is required for page controls - the ScrollingList
	#works under a page control.
	def onSelect( self, pageControl ):
		pass

	#This method is called back by our gui Budget helper
	#This method returns a new component
	def createItem( self ):
		assert self.itemGuiDS is not None
		g = GUI.load( self.itemGuiDS )
		setattr( self.items, "m%d"%(len(self.items.children),), g)
		g.script.doLayout( self )
		return g

	#This method is called back by our gui Budget helper
	def deleteItem( self, c ):
		self.items.delChild(c)

	def setupItems( self, backFn, setupParams ):
		self.backFn = backFn

		oldidx = -1
		if self.selection < len( self.items.children ):
			oldidx = self.selection

		self.budget.balance( len(setupParams) )

		num = len( setupParams )
		for i in xrange( 0, num ):
			g=self.items.children[i][1]
			g.script.setup(setupParams[i], i)
			g.script.select(0)

		if num > 0:
			self.doLayout( None )
			if oldidx >= 0:
				self.selectItem( oldidx )

	def doLayout( self, parent ):
		PyGUIBase.doLayout( self, parent )
		
		# Start at the top of our parent Window component, moving down by the
		# height of each item.
		y = 1.0
		totalHeight = 0
		itemHeight = 0
		screenWidth = BigWorld.screenWidth()
		screenHeight = BigWorld.screenHeight()
		for discard, i in self.component.items.children:
			i.position.y = y
			thisItemHeight = i.script.adjustFont( screenWidth, screenHeight )
			if itemHeight == 0 and thisItemHeight != 0:
				itemHeight = thisItemHeight
			y = y - itemHeight - ITEM_MARGIN
			totalHeight += itemHeight + ITEM_MARGIN

		self.component.items.height = totalHeight

		# Convert total height into screen clip space, since the MatrixGUITransform 
		# transforms in screen clip space.
		heightMode = self.component.items.heightMode
		self.component.items.heightMode = "LEGACY"
		self.totalHeightScreenClip = float( self.component.items.height )
		self.component.items.heightMode = heightMode

		# Setup the maximum scrolling range
		self.items.script.maxScroll[1] = max(0, self.totalHeightScreenClip - self.heightInScreenClip())
		self.items.script.minScroll[1] = 0
		if self.items.script.maxScroll[1] == 0.0 and hasattr( self, 'scrollUp' ):
			self.scrollUp.visible = 0
			self.scrollDown.visible = 0

		self.maxVisibleItems = int(2.0 / itemHeight) if itemHeight > 0 else 1


	def heightInScreenClip( self ):
		heightMode = self.component.heightMode
		self.component.heightMode = "LEGACY"
		selfHeightClip = self.component.height
		self.component.heightMode = heightMode
		return selfHeightClip
		
	# -------------------------------------------------------------------------
	# This method returns true if the given index is selectable
	# -------------------------------------------------------------------------
	def canSelect( self, idx ):
		if idx < 0:
			return 0
		if idx >= len( self.items.children ):
			return 0
		return self.items.children[idx][1].script.canSelect()

	# -------------------------------------------------------------------------
	# Moves x items forward/back in the list. If target isnt selectable it will
	# select the nearst selectable item after it. It will loop back around if
	# the end of the list is encountered
	# -------------------------------------------------------------------------
	def moveSelection( self, dist ):
		self.selectItem( self.getSelectionOffset(dist) )
	
	# -------------------------------------------------------------------------
	# Scrolls the list the given number of items without changing 
	# the current selection. Will not allow scrolling past the end of the list.
	# -------------------------------------------------------------------------
	def scrollList( self, dist ):						
		self.items.script.scrollBy( 0, 0.1 * dist )
		
		#check for scroll arrows
		if hasattr( self, 'scrollUp' ):
			self.scrollUp.visible = self.items.script.canScrollUp()
			self.scrollDown.visible = self.items.script.canScrollDown()
		
	
	# -------------------------------------------------------------------------
	# Gets the selection index dist items away, taking into account some 
	# items may not be selectable.
	# -------------------------------------------------------------------------
	def getSelectionOffset( self, dist ):
		curIdx = self.selection
		
		if dist == 0:
			return curIdx
		
		newIdx = (curIdx + dist) % len( self.items.children )
		direction = -1 if dist < 0 else 1
		
		while not self.canSelect( newIdx ):
			newIdx = (newIdx + direction) % len( self.items.children )
			if newIdx == curIdx: # wrapped around to start, bail out.
				return newIdx
				
		return newIdx
		
	# -------------------------------------------------------------------------
	# This method should be called to safely select an item.
	# -------------------------------------------------------------------------
	def selectItem( self, idx = 0, bringIntoView=True, animate=True, forceReselect=False ):
		num = len( self.items.children )
		if num == 0 or (idx == self.selection and not forceReselect): 
			return

		oldIdx = self.selection

		if idx >= num:
			idx = num - 1
		if idx < 0:
			idx = 0
		self.selection = idx

		if oldIdx >= 0 and oldIdx < num:
			self.items.children[oldIdx][1].script.select(0)
		self.items.children[idx][1].script.select(1)
		
		if bringIntoView:
			self.checkSelectionVisible(animate)

		self.updateControlBar()

		try:
			self.selectItemCallback( idx )
		except Exception, e:
			print "ERROR: ScrollingList.selectItem callback", e

	def executeSelected( self, playSound = True ):
		BigWorld.playSound("ui/boop")
		entry = self.items.children[self.selection][1]
		i = entry.script.onSelect( self )
		self.updateControlBar()

	# -------------------------------------------------------------------------
	# This method updates the control bar based on the state of the currently
	# selected item.
	# -------------------------------------------------------------------------
	def updateControlBar( self ):
		pass

	# -------------------------------------------------------------------------
	#This method performs a scroll window check :
	#if we need to scroll the window to show the current selection, do so.
	#this method also shows/hides the scroll arrows.
	# -------------------------------------------------------------------------
	def checkSelectionVisible( self, animate = True ):
		if self.items.script.maxScroll[1] == 0.0:
			self.items.script.scrollTo(0, 0, animate)
			
			if hasattr( self, 'scrollUp' ):
				self.scrollUp.visible = 0
				self.scrollDown.visible = 0
			return

		self.scrollToItem( self.selection, animate )


	# -------------------------------------------------------------------------
	# Scrolls the list so the given index is visible (doesn't change selection)
	# -------------------------------------------------------------------------
	def scrollToItem( self, idx, animate = True ):
		# This is the actual position of the item
		itemHeight = (self.totalHeightScreenClip / len(self.component.items.children))
		itemScrollY = itemHeight * idx

		# Scroll only to get the item into view
		currentScroll = self.items.script.scroll[1]
		
		if itemScrollY < currentScroll + itemHeight:
			# scroll up 
			scrollTarget = itemScrollY - itemHeight 
		elif itemScrollY > currentScroll + self.heightInScreenClip() - itemHeight * 2.0: 
			# scroll down
			scrollTarget = itemScrollY - self.heightInScreenClip() + itemHeight * 2.0
		else:
			# don't scroll
			scrollTarget = currentScroll
		
		self.items.script.scrollTo(0, scrollTarget, animate)

		#check for scroll arrows
		if hasattr( self, 'scrollUp' ):
			self.scrollUp.visible = self.items.script.canScrollUp()
			self.scrollDown.visible = self.items.script.canScrollDown()


	# -------------------------------------------------------------------------
	# This method handles any list traversal key presses.
	# -------------------------------------------------------------------------
	def handleTraversalKeys( self, event ):
		if not event.isKeyDown():
			return False

		if event.key in [Keys.KEY_JOYDDOWN,Keys.KEY_DOWNARROW,Keys.KEY_S]:
			if len( self.items.children ) == 0:
				return True
			oidx = None
			idx = self.selection
			while idx != oidx:
				if oidx == None: oidx = idx
				idx += 1
				if idx >= len( self.items.children ):
					idx = 0
				if self.canSelect( idx ):
					self.selectItem( idx )
					break
			BigWorld.playSound("ui/tick")
			return True
		elif event.key in [Keys.KEY_JOYDUP,Keys.KEY_UPARROW,Keys.KEY_W]:
			if len( self.items.children ) == 0:
				return 1
			oidx = None
			idx = self.selection
			while idx != oidx:
				if oidx == None: oidx = idx
				idx -= 1
				if idx < 0:
					idx = len( self.items.children ) - 1
				if self.canSelect( idx ):
					self.selectItem( idx )
					break
			BigWorld.playSound("ui/tick")
			return True
		elif event.key == Keys.KEY_PGUP:
			dist = self.maxVisibleItems
			if self.selection - dist < 0:
				dist = self.selection
			self.moveSelection( -dist )
		elif event.key == Keys.KEY_PGDN:
			dist = self.maxVisibleItems
			if self.selection + dist >= len( self.items.children ):
				dist = len( self.items.children ) - self.selection - 1
			self.moveSelection( dist )
		elif event.key == Keys.KEY_HOME:
			self.selectItem(0)
		elif event.key == Keys.KEY_END:
			self.selectItem( len( self.items.children )-1 )

		return False

	# -------------------------------------------------------------------------
	# This method is called handles key events for the list.
	# -------------------------------------------------------------------------
	def handleKeyEvent( self, event ):
		key = event.key
	
		if ( event.isKeyDown() ):
			if self.handleTraversalKeys( event ):
				return True
			elif key == [Keys.KEY_JOYA] or (
					key in [ Keys.KEY_RETURN, Keys.KEY_NUMPADENTER ] and
					not BigWorld.isKeyDown( Keys.KEY_LALT ) and
					not BigWorld.isKeyDown( Keys.KEY_RALT )):
				if len( self.items.children ) == 0:
					return True
				# Sink further key events so that the new screen won't
				# get messages about this key-press.
				BigWorld.sinkKeyEvents( Keys.KEY_RETURN )
				BigWorld.sinkKeyEvents( Keys.KEY_NUMPADENTER )
				self.executeSelected()
				return 1
			elif key in [Keys.KEY_JOYB,Keys.KEY_JOYBACK,Keys.KEY_ESCAPE, \
					Keys.KEY_BACKSPACE]:
				if self.backFn != None:
					self.active( 0 )
					BigWorld.playSound("ui/boop")
					self.backFn()
					return 1
		
		return False
	

	def onLoad( self, section ):
		self.itemGuiName = section.readString( "itemGui", "")
		self.itemGuiDS = ResMgr.openSection( self.itemGuiName )
		assert self.itemGuiName != ""

	# -------------------------------------------------------------------------
	# This method is called just after the component loads.  Here we perform
	# a check to make sure we have a items area.
	# -------------------------------------------------------------------------
	def onBound( self ):
		PyGUIBase.onBound( self )
		try:
			self.items = self.component.items
		except AttributeError:
			print "the scrolling list should have a items area!!!"


		
