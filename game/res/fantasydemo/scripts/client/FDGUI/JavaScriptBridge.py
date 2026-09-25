# -*- coding: utf-8 -*-

import json

# Example of derived class

# class WebWindow( JavaScriptBridge ):
#
#	def _getJavaScriptEvaluateFunction( self ):
#		return self._getInternalBrowserScript().webPage.evaluateJavaScript
#
#	@exposedToJavaScript
#	def sendMsg( self, msg ):
#		print "sendMsg", msg


def exposedToJavaScript( f ):
	f.isExposedToJavaScript = True
	return f

class JavaScriptCaller( object ):
	def __init__( self, webPage ):
		self.webPage = webPage

	def __getattr__( self, fnName ):
		def fn( *args ):
			if self.webPage is None:
				return
			argsAsStr = ",".join( repr( arg ) for arg in args )
			script = "%s(%s)" % (fnName, argsAsStr)
			self.__dict__[ "webPage" ].executeJavascript( script, "" )
		return fn


class JavaScriptBridge( object ):
	def onStatusTextChange( self, event ):
		text = event.stringValue

		if text.startswith( "@BW:" ):
			self.invokeFromJavaScript( text[4:] )

		return True

	def invokeFromJavaScript( self, text ):
		args = json.loads( text )

		fn = getattr( self, args[0] )

		if hasattr( fn, "isExposedToJavaScript" ):
			fn( **args[1] )
		else:
			print "Unexpected function call which is not exposedToJavaScript"
		#call the invokation callback
		self.invokeCallback()

	@property
	def js( self ):
		#call the invokation callback
		self.invokeCallback()
		return JavaScriptCaller( self._getInternalBrowserScript().webPage )

	#callback called when calling javascript/flash or calling this from flash/javascript
	def invokeCallback( self ):
		pass

# JavaScriptBridge.py
