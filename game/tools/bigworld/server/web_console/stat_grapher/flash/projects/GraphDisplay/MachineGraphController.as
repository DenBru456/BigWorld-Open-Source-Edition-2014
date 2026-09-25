import mx.remoting.Service;
import mx.remoting.PendingCall;
import mx.rpc.RelayResponder;
import mx.rpc.ResultEvent;

import com.bigworldtech.BWUtils;

/**
 *	This controller graphs a specific subset of the available machines.
 */
class MachineGraphController extends TopMachineGraphController
{
	/** The machine IPs we are specifically graphing. */
	private var __machineIPs:Array = null;

	/**
	 *	Constructor.
	 */
	public function MachineGraphController()
	{
		super();

		__machineIPs = new Array();
	}

	public function getTitle():String
	{
		if (__machineIPs.length == 1)
		{
			return "Graph for machine (" + __machineIPs[0] + ")";
		}
		else
		{
			return "Summary for " + __machineIPs.length + " machines";
		}
	}

	public function setParams( params:Object )
	{
		BWUtils.clearArray( __machineIPs );
		for (var i:Number = 0; i < params.machines.length; ++i)
		{
			var machineInfo:Object = params.machines[i];
			__machineIPs.push( machineInfo.ip );
		}
	}

	private static function debug( context:String, msg:String )
	{
		var out:String = getTimer() + ": MachineGraphController." + context;
		if (msg != null or msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	public function requestMachineInfo()
	{
		super.requestMachineInfo( __machineIPs );
	}
}
