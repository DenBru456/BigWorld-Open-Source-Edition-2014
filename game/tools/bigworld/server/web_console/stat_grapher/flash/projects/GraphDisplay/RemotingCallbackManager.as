import mx.remoting.Service;
import mx.remoting.PendingCall;

import mx.rpc.RelayResponder;
import mx.rpc.ResultEvent;
import mx.rpc.FaultEvent;

import com.bigworldtech.BWUtils;

/**
 * Remoting callback manager. Basically allows you to store context
 * data which is returned when making a flash remoting function call.
 *
 * Also performs checks on when queries time out.
 */

class RemotingCallbackManager
{
	// Class variables
	// ========================================================================
	private var __pendingCalls:Array;

	// Class methods
	private var __service:Service;
	private var __functionRepository:Object;

	public function RemotingCallbackManager()
	{
		__pendingCalls = new Array();
		__functionRepository = new Object();
		__functionRepository.remoteHandler = function( re:ResultEvent )
		{
			this.handlerObj[this.responseHandlerName]( this.context,
				re.result );
			this.parent.onReceived( this );
		}

		__functionRepository.errorHandler = function( fe:FaultEvent )
		{
			this.handlerObj[this.errorHandlerName]( this.context, fe );
			this.parent.onReceived( this );
		}
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "RemotingCallbackManager." + context;
		if (msg != undefined)
		{
			out += ": " + undefined;
		}
		BWUtils.log( out );
	}

	/**
	 * Sets the service
	 */
	public function setService( service:Service )
	{
		__service = service;
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
			errorHandlerName:String, context:Object,
			funcName:String, args:Array )
	{
		var callObj:Object = new Object();
		callObj.handlerObj = handlerObj;
		callObj.context = context;
		callObj.responseHandlerName = responseHandlerName;
		callObj.errorHandlerName = errorHandlerName;
		callObj.funcName = funcName;
		callObj.args = args;
		callObj.parent = this;
		callObj.receiver = __functionRepository.remoteHandler;
		callObj.errorReceiver = __functionRepository.errorHandler;

		__pendingCalls.push( callObj );

		var pc:PendingCall =
			__service[callObj.funcName].apply( __service, callObj.args );
		pc.responder =
			new RelayResponder( callObj, "receiver", "errorReceiver" );

	}

	public function onReceived( callObj:Object )
	{
		// Remove from array
		for (var i:Number = 0; i < __pendingCalls.length; ++i)
		{
			if (__pendingCalls[i] == callObj)
			{
				//debug( "onReceived", "Deleting callObj!" );
				__pendingCalls.splice( i, 1 );
				break;
			}
		}

		BWUtils.clearObject( callObj );
	}
}
