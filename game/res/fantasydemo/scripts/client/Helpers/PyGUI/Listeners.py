import weakref
	
_languageChangeListeners = []
_deviceListeners = []

def registerInputLangChangeListener( listener ):
	_languageChangeListeners.append( weakref.ref(listener) )
	
def registerDeviceListener( listener ):
	_deviceListeners.append( weakref.ref(listener) )

def handleInputLangChangeEvent():
	import GUI
	global _languageChangeListeners
	for listener in [ x() for  x in _languageChangeListeners if x() is not None ]:
		if hasattr( listener, 'handleInputLangChangeEvent' ):
			listener.handleInputLangChangeEvent()
	
	return True	
	
def onRecreateDevice():
	for listener in [ x() for  x in _deviceListeners if x() is not None ]:
		if hasattr( listener, 'onRecreateDevice' ):
			listener.onRecreateDevice()

