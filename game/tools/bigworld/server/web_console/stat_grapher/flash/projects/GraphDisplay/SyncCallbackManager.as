import mx.remoting.Service;
import mx.remoting.PendingCall;

import mx.rpc.RelayResponder;
import mx.rpc.ResultEvent;
import mx.rpc.FaultEvent;

/**
 * Callback manager. Includes Remoting callback.
 * Turns asynchronous functions (which get passed a callback
 * as a parameter) into synchronous functions.
 * Example usage:
 *
 *		var scm:SyncCallbackManager = new SyncCallbackManager();
 *		scm.setService( service );
 *		scm.remoteCall( this, receivePrefTree, errorHandler,
 *			"getPrefTree", "bwLogData1" );
 *		scm.remoteCall( this, receiveLogRange, errorHandler,
 *			"getLogRange", "bwLogData1" );
 *		scm.callOnFinish( this, "helloWorld" );
 *		scm.start();
 *
 * The strategy is basically to recurse through the "start()" method
 * until all queued function calls have been made.
 */

class SyncCallbackManager
{
	// Class variables
	// ========================================================================
	private var __pendingCallQueue:Array;

	private var __finalCallObj:Object;
	private var __finalCallFunc:String;
	private var __finalCallArgs:Array;

	private var __service:Service;
	private var __functionRepository:Object;

	// Class methods
	// ========================================================================
	public function SyncCallbackManager()
	{
		__pendingCallQueue = new Array();

		// This is really hacky and uses a "feature" which won't work in
		// Actionscript 3.0 - namely, that Actionscript 2.0 doesn't handle
		// closures properly. So functions that reference "this" will be
		// referencing the object it belongs to rather than the object
		// that created the function.
		__functionRepository = new Object();
		__functionRepository.localHandler = function()
		{
			this.handlerObj[this.responseHandlerName].apply(
					this.handlerObj, arguments );
			this.parent.onReceived( this );
		}

		__functionRepository.remoteHandler = function( re:ResultEvent )
		{
			this.handlerObj[this.responseHandlerName]( re.result );
			this.parent.onReceived( this );
		}

		__functionRepository.errorHandler = function( fe:FaultEvent )
		{
			this.handlerObj[this.errorHandlerName]( fe );
			this.parent.onReceived( this );
		}
	}

	/**
	 * Sets up a remoting call to the service which should have been
	 * already set by "setService"
	 *
	 * Arguments:
	 * 1) Object to which the handler functions belong
	 * 2) Response handler function
	 * 3) Error handler function
	 * 4) Function to call on the remote service (must be a string)
	 * 5) Arguments for the function (must be an array)
	 */
	public function remoteCall( handlerObj:Object, responseHandlerName:String,
			errorHandlerName:String, funcName:String, args:Array )
	{
		var callObj:Object = new Object();
		callObj.handlerObj = handlerObj;
		callObj.responseHandlerName = responseHandlerName;
		callObj.errorHandlerName = errorHandlerName;
		callObj.funcName = funcName;
		callObj.args = args;
		callObj.type = "remote";

		__pendingCallQueue.push( callObj );
	}

	/**
	 * Sets up a local function call which expects a callback function.
	 *
	 * Arguments:
	 * 1) Object to which the handler functions belong
	 * 2) Response handler function
	 * 3) Object to which the remote function belongs
	 * 4) Function to call
	 * 5) Arguments for the function (must be an array)
	 */
	public function localCall( handlerObj:Object, responseHandlerName:String,
			funcObj:Object, funcName:String, args:Array )
	{
		var callObj:Object = new Object();
		callObj.handlerObj = handlerObj;
		callObj.responseHandlerName = responseHandlerName;
		callObj.funcObj = funcObj;
		callObj.funcName = funcName;
		callObj.args = args;
		callObj.parent = this;
		callObj.type = "local";

		__pendingCallQueue.push( callObj );
	}

	/**
	 * Sets the service
	 */
	public function setService( service:Service )
	{
		__service = service;
	}

	/**
	 * Sets a function to call on completion of all callback handlers
	 */
	public function callOnFinish( targetObj:Object, func:String, args:Array )
	{
		__finalCallObj = targetObj;
		__finalCallFunc = func;
		__finalCallArgs = args;
	}

	/**
	 * MAIN FUNCTION
	 */
	public function start()
	{
		if (__pendingCallQueue.length > 0)
		{
			var callObj:Object = __pendingCallQueue.shift();

			// Give the object a reference back to us (the
			// SyncCallbackManager instance)
			callObj.parent = this;

			if (callObj.type == "local")
			{

				// Create callback function
				callObj.receiver = __functionRepository.localHandler;

				// Call the function!
				callObj.funcObj[callObj.funcName].apply(
					callObj.funcObj, callObj.args );
			}
			else if (callObj.type == "remote")
			{
				callObj.receiver = __functionRepository.remoteHandler;
				callObj.errorReceiver = __functionRepository.errorHandler;

				var pc:PendingCall =
					__service[callObj.funcName].apply( __service, callObj.args );
				pc.responder =
					new RelayResponder( callObj, "receiver", "errorReceiver" );
			}
		}
		else
		{
			__finalCallObj[__finalCallFunc].apply(
					__finalCallObj, __finalCallArgs );

			this.cleanUp();
		}
	}

	/**
	 * Basically does two things:
	 * 1) Unlinks all attributes of the object.
	 * 2) Recurses to handle the next pending queue.
	 */
	public function onReceived( obj:Object )
	{
		// Delete every attribute of object
		for (var i:String in obj)
		{
			delete obj[i];
		}

		this.start();
	}

	/**
	 * Unlinks function and object pointers just to prevent circular
	 * references.
	 */
	private function cleanUp()
	{
		delete __finalCallArgs;
		delete __finalCallObj;
		delete __finalCallFunc;
	}
}
