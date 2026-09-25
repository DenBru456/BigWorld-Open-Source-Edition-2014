"""
Utility methods for managing keybindings
"""

import BigWorld
import Keys
from functools import partial
from bwdebug import ERROR_MSG, INFO_MSG, TRACE_MSG

KEY_ALIAS_CONTROL 	= (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL)
KEY_ALIAS_ALT 		= (Keys.KEY_LALT, Keys.KEY_RALT)
KEY_ALIAS_SHIFT 	= (Keys.KEY_LSHIFT, Keys.KEY_RSHIFT)
KEY_ALIAS_WINDOWS	= (Keys.KEY_LWIN, Keys.KEY_RWIN)

keyAliases = {  "CONTROL": KEY_ALIAS_CONTROL,
				"ALT": KEY_ALIAS_ALT,
				"SHIFT": KEY_ALIAS_SHIFT,
				"WINDOWS": KEY_ALIAS_WINDOWS,
			 }


def _stringToKey( key ):
	if key in keyAliases:
		return keyAliases[key]
	else:
		return BigWorld.stringToKey( key )


def _keyToString( key ):
	try:
		return _reverseKeysLookup[ key ]
	except KeyError:
		return ""


def _isKeyDown( key ):
	if type(key) is tuple:
		for k in key:
			if BigWorld.isKeyDown(k):
				return True
	else:
		return BigWorld.isKeyDown(key)


def _keyInKeyList( key, keyList ):
	for k in keyList:
		if type(k) is tuple:
			return _keyInKeyList( key, k )
		elif k == key:
			return True
			
	return False


def BWKeyBindingAction( actionName, *args, **kargs ):

	def addActionName( actionName, actionFunction ):
		if not hasattr( actionFunction, "_BWKeyBindingActionNames" ):
			actionFunction._BWKeyBindingActionNames = []
		actionFunction._BWKeyBindingActionNames += [(actionName, args, kargs)]
		return actionFunction

	return partial( addActionName, actionName )


class BWActionHandler( object ):

	def __init__( self ):
		self.setupActionList()

	def setupActionList( self ):
		# Go though the members of the class that were set up as
		# key binding actions and "fix" them (make them point to the correct
		# function) and build a list of these.
		entityClass = self.__class__
		self.actionFunctions = {}
		for name, function in entityClass.__dict__.items():
			if hasattr( function, "_BWKeyBindingActionNames" ):
				actionNames = function._BWKeyBindingActionNames
				assert( callable( function ) )

				# Get the function from ourselves so we have a bound version
				function = getattr( self, name )
				for (actionName, args, kargs) in actionNames:
					self.actionFunctions[ actionName ] = partial( getattr( self, name ), *args, **kargs )


class BWKeyBindings:

	def __init__( self ):
		self.actionsByBinding = {}
		self.actionsByName = {}
		self.handlers = []


	def readInDefaultKeyBindings( self, dataSection ):
		self.actionsByName = {}
		for actionDataSection in dataSection.values():
			actionBinding = _ActionBinding()
			actionBinding.readFromDataSection( actionDataSection )

			actionName = actionBinding.actionName
			self.actionsByName[ actionName ] = actionBinding


	def readInPreferenceKeyBindings( self, dataSection ):
		for actionDataSection in dataSection.values():
			actionBinding = _ActionBinding()
			actionBinding.readFromDataSection( actionDataSection )

			actionName = actionBinding.actionName
			if self.actionsByName.has_key( actionName ):
				self.actionsByName[ actionName ].addPreferenceKeyBindings( actionBinding )


	def writePreferenceKeyBindings( self, dataSection ):
		dataSection.deleteSection( "keyBindings" )
		dataSection.createSection( "keyBindings" )
		keyBindingsSection = dataSection._keyBindings
		for action in self.actionsByName.values():
			action.writePreferenceKeyBindings( keyBindingsSection )


	def addHandler( self, handler ):
		if not handler in self.handlers:
			self.handlers.append( handler )


	def removeHandler( self, handler ):
		if handler in self.handlers:
			self.handlers.remove( handler )


	# ------------------------------------------------------------------------------
	# Method: buildBindList
	# Description: Builds a list of down-key (keys that must all be held down in
	# order for a action to be called,) and a list of not-down keys (key
	# combinations that cannot also be down for the action to be called.)
	#
	# It accepts a list of pairs, consisting of a list and some other data type
	# (not important except for a not-equal comparison,) and returns a list of
	# triples, consisting of the down-key list, the not-down keys list, and the
	# data type.
	# ------------------------------------------------------------------------------
	def buildBindList( self ):
		self.actionsByBinding = {}
		for action in self.actionsByName.values():
			for binding in action.getBindings():
				if not self.actionsByBinding.has_key( binding ):
					self.actionsByBinding[ binding ] = []
				self.actionsByBinding[ binding ] += [action.actionName]

		# Clear our return list.
		self.bindList = []

		# For each pair in the list of down-keys, create the list of not-down keys.
		for downKeys, actionNames in self.actionsByBinding.items():
			notDownLists = []

			# Now go through all the other down-keys to find ambiguity.
			# A down-key combination is ambiguous if it is contained entirely
			# within another down-key combination, unless they both happen to refer
			# to the same actionNames.
			for otherDownKeys, otherActionNames in self.actionsByBinding.items():

				if actionNames != otherActionNames:
					containedEntirely = 1

					for key in downKeys:
						containedEntirely = containedEntirely and \
							key in otherDownKeys

					# Now if there is ambiguity, build a not-down list to
					# disambiguate the two key combinations.
					if containedEntirely:
						notDownList = []

						# The not-down list is formed from the list of all keys
						# pressed down in the second list which are not already in
						# the first list. This is equivalent to listing which keys
						# are not covered by the first list and making sure the
						# second list is not thusly satisfied.
						for otherKey in otherDownKeys:
							if otherKey not in downKeys:
								notDownList.append( otherKey )
						notDownLists.append( notDownList )

			# Add the triple to the return list.
			for actionName in actionNames:
				self.bindList.append( ( downKeys, notDownLists, actionName) )

		for entity in self.handlers:
			if getattr( entity, "onBindCallback", None):
				entity.onBindCallback( self )


	# ------------------------------------------------------------------------------
	# Method: printBindList
	# Description: Accepts a bind list (a triple consisting of a down-key list,
	# a not-down keys list, and a actionName,) and prints it.
	#
	# This method uses the BigWorld module in order to keep itself compatible
	# with the C++ values for the keys.
	# ------------------------------------------------------------------------------

	def printBindList( self ):
		bindListByName = {}
		for ( downKeys, notDownKeysList, actionName) in self.bindList:
			if bindListByName.has_key( actionName ):
				bindListByName[ actionName ] += [ (downKeys, notDownKeysList) ]
			else:
				bindListByName[ actionName ] = [ (downKeys, notDownKeysList) ]

		actionNames = sorted( bindListByName.keys() )
		for actionName in actionNames:
			for (downKeys, notDownKeysList) in bindListByName[ actionName ]:
				# Print the down-key list first.
				print actionName,":",
				for downKey in downKeys:
					print _keyToString( downKey ),
				#print "] {",

				# Print each not-down key list next.
				if len( notDownKeysList ) > 0:
					if len( notDownKeysList ) == 1:
						print "but not",
						for notDownKey in notDownKeysList[0]:
							print _keyToString( notDownKey ),
					else:
						print "but not any of {",
						for notDownKeys in notDownKeysList:
							print "[",
							for notDownKey in notDownKeys:
								print _keyToString( notDownKey ),
							print "]",
						print "}",
				print


	def getBindingsForAction( self, actionName ):
		if self.actionsByName.has_key( actionName ):
			return self.actionsByName[ actionName ].getBindings()
		else:
			return []


	def addBindingForAction( self, actionName, binding ):
		binding = tuple( sorted( binding ) )
		if not actionName in self.actionsByName:
			ERROR_MSG( "Action '%s' is unknown" % (actionName,) )
			return

		action = self.actionsByName[ actionName ]
		bindings = action.getBindings()
		if binding in bindings:
			ERROR_MSG( "Action '%s' already has the binding %s" % (actionName, binding) )
			return
		return action.addBinding( binding )


	def removeBindingForAction( self, actionName, binding ):
		binding = tuple( sorted( binding ) )
		if not actionName in self.actionsByName:
			ERROR_MSG( "Action '%s' is unknown" % (actionName,) )
			return

		action = self.actionsByName[ actionName ]
		bindings = action.getBindings()
		if binding not in bindings:
			ERROR_MSG( "Action '%s' does not have the binding %s" % (actionName, binding) )
			return
		return self.actionsByName[ actionName ].removeBinding( binding )


	def callActionByName( self, actionName, *args, **kargs ):
		# We have the action name. Go through the active handlers and
		# see who wants to handle it.
		for entity in reversed( self.handlers ):
			if entity.actionFunctions.has_key( actionName ):
				ret = entity.actionFunctions[ actionName ]( True, *args, **kargs )

				# Only keep going if the method returns False. Anything
				# else (i.e. None) will cause it to stop.
				if ret != False:
					break


	def callActionForKeyState( self, key ):
		for downKeys, upKeySets, actionName in self.bindList:
			if _keyInKeyList( key, downKeys ):
				okayToGo = 1
				for downKey in downKeys:
					okayToGo = okayToGo and _isKeyDown(downKey)
				if okayToGo:
					for upKeys in upKeySets:
						allDown = True
						for upKey in upKeys:
							allDown = allDown and _isKeyDown(upKey)
						okayToGo = okayToGo and not allDown

				# We have the action name. Go through the active handlers and
				# see who wants to handle it.
				for entity in reversed( self.handlers ):
					if entity.actionFunctions.has_key( actionName ):
						ret = entity.actionFunctions[ actionName ]( okayToGo )

						# Only keep going if the method returns False. Anything
						# else (i.e. None) will cause it to stop.
						if ret != False:
							break


	def getActionForKeyState( self, key ):
		for downKeys, upKeySets, actionName in self.bindList:
			if _keyInKeyList( key, downKeys ):
				okayToGo = 1
				for downKey in downKeys:
					okayToGo = okayToGo and _isKeyDown(downKey)
				if okayToGo:
					for upKeys in upKeySets:
						allDown = True
						for upKey in upKeys:
							allDown = allDown and _isKeyDown(upKey)
						okayToGo = okayToGo and not allDown

				if okayToGo:
					return actionName


class _ActionBinding:

	def __init__( self ):
		self.actionName = ''
		self.bindings = ()
		self.defaultBindings = ()


	def readFromDataSection( self, dataSection ):
		self.actionName = dataSection._name.asString
		for key, value in dataSection.items():
			if key == 'keys':
				keys = value.asString.split()
				keys = [ _stringToKey( key ) for key in keys ]

				if 0 in keys:
					ERROR_MSG( "Action '%s' is bound to one more more invalid keys" % (self.actionName,) )

				if len(keys) > 0:
					self.bindings += (tuple( sorted(keys) ),)

		self.defaultBindings = self.bindings


	def addPreferenceKeyBindings( self, preferenceBindings ):
		# If any bindings are read in from the preference file, they completely
		# replace the bindings for this action. To keep both the default set plus
		# new bindings, the preference bindings must list the union.
		assert( self.actionName == preferenceBindings.actionName )

		newBindings = sorted( preferenceBindings.getBindings() )
		if newBindings != sorted( self.defaultBindings ):
			self.bindings = tuple( newBindings )


	def writePreferenceKeyBindings( self, dataSection ):
		# Check if the bindings are different to the default bindings
		if sorted( self.bindings ) != sorted( self.defaultBindings ):
			newDataSection = dataSection.createSection( "action" )
			newDataSection.writeString( 'name', self.actionName )
			for binding in self.bindings:
				bindingString = ''
				for key in binding:
					bindingString += _reverseKeysLookup[ key ] + ' '
				newDataSection.writeStrings( 'keys', (bindingString.strip(),) )


	def addBinding( self, binding ):
		assert( binding not in self.bindings )
		self.bindings += (tuple(binding),)


	def removeBinding( self, binding ):
		assert( binding in self.bindings )
		newBindings = list( self.bindings )
		newBindings.remove( binding )
		self.bindings = tuple( newBindings )


	def getBindings( self ):
		return self.bindings



_reverseKeysLookup = {}

def _buildReverseKeysLookup():

	preferredSynonyms = ( \
			'NONE',
			'LEFTMOUSE',
			'RIGHTMOUSE',
			'MIDDLEMOUSE',
		)

	for name in preferredSynonyms:
		value = BigWorld.stringToKey( name )
		if value != 0 or name == 'NONE': # The value for KEY_NONE is 0
			_reverseKeysLookup[ value ] = name
		else:
			TRACE_MSG( 'Synonym "%s" is missing from BigWorld''s key list' % (name,) )

	for name in Keys.__dict__.keys():
		# We use BigWorld.stringToKey as it's the subset of keys that we're interested in
		value = BigWorld.stringToKey( name[4:] )
		if value == 0:
			continue

		if _reverseKeysLookup.has_key( value ):
			if _reverseKeysLookup[ value ] not in preferredSynonyms:
				TRACE_MSG( 'Unexpected synonym for "%s": "%s"' % \
					(_reverseKeysLookup[ value ], BigWorld.keyToString( value ),) )
		else:
			_reverseKeysLookup[ value ] = BigWorld.keyToString( value )

	for aliasName, aliasKeys in keyAliases.iteritems():
		_reverseKeysLookup[ aliasKeys ] = aliasName

_buildReverseKeysLookup()
