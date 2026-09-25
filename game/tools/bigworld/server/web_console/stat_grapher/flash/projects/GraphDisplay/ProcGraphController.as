import mx.remoting.Service;
import mx.remoting.PendingCall;

import mx.rpc.RelayResponder;

import com.bigworldtech.BWUtils;
/**
 *	This class displays statistics graphs for individual processes within a
 *	process type.
 */
class ProcGraphController extends EveryProcGraphController
{
	// Class members
	// ========================================================================
	// What process type we graph
	private var __processType:String = null;

	// Dictionary of process ids -> process info
	private var __processInfo:Object = null;

	// List of process ids we're specifically graphing
	private var __processIds:Array = null;

	// Public class methods (initialiser functions)
	// ========================================================================
	/**
	 *	Constructor
	 */
	public function ProcGraphController()
	{
		super();

		__processType = null;
		__processInfo = new Object();

		//debug( "(constructor)", "initialised" );
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "ProcGraphController." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	public function getTitle()
	{
		return "Summary for " + __processIds.length + " " + __processType + "s";
	}

	/**
	 *
	 */
	public function setParams( params:Object )
	{
		__processType = params.processType;
		__processIds = params.processIds;
	}

	// Remote requests
	// ========================================================================

	/**
	 *
	 */
	private function requestProcessInfo()
	{
		var startTime:Number = __currentTime - __currentRange;
		var endTime:Number = __currentTime;

		__rcm.remoteCall( this, "receiveProcessInfo", "handleError", null,
			"requestProcessInfo", [__logName, __user, __processType,
			startTime, endTime, __processIds] );
	}
}
