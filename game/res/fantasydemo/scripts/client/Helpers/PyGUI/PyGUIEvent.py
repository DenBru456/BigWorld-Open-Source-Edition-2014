
def PyGUIEvent( componentName, eventName, *args, **kargs ):
	"""
		@PyGUIEvent decorator.
		
		Note: If you override a function that is marked with this decorator
		in the base class, the derived class function is not required to be
		decorated. If you do decorate both, the event handler will be called
		twice.
	"""
	from functools import partial

	def addEvent( componentName, eventName, args, kargs, eventFunction ):
		if not hasattr( eventFunction, "_PyGUIEventHandler" ):
			eventFunction._PyGUIEventHandler = []
		eventFunction._PyGUIEventHandler += [(componentName, eventName, args, kargs)]
		return eventFunction

	return partial( addEvent, componentName, eventName, args, kargs )
