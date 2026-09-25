import mx.remoting.Service;
import mx.remoting.PendingCall;
import mx.rpc.RelayResponder;
import mx.rpc.ResultEvent;

import com.bigworldtech.BWUtils;

class TopMachineGraphController extends BaseGraphController
{
	// =========================================================================
	// Section: Members
	// =========================================================================

	/** Name of this controller. */
	public var __name:String = "Summary of all machines";

	/** The machine information, from IP to object:(ip, hostname). */
	private var __machineInfo:Object = null;

	/** The order of the machines, by their IP. */
	private var __machineOrder:Array = null;

	/** The date of a pending request, if any. */
	private var __lastInfoRequestTime:Number = null;

	/**
	 *	How long to wait for a pending request for machine info before another
	 *	request can be made again, in milliseconds.
	 */
	private static var INFO_REQUEST_TIMEOUT = 5000;

	// =========================================================================
	// Section: Methods
	// =========================================================================

	/**
	 *	Constructor.
	 */
	public function TopMachineGraphController()
	{
		super();
		__machineInfo = new Object();
		__machineOrder = new Array();
		__lastInfoRequestTime = null;
	}

	public function init():Void
	{
		//debug( "init" );
		this.requestMachineInfo();
	}

	public function getTitle():String
	{
		return __name;
	}

	private function requestMachineInfo( ips:Array ):Void
	{
		// If we had a request pending and haven't had a reply for 
		// less than 5 seconds, consider request still outstanding
		if (__lastInfoRequestTime != null && 
				getTimer() - __lastInfoRequestTime < INFO_REQUEST_TIMEOUT)
		{
			debug( "requestMachineInfo", 
				"Already waiting for requestMachineInfo response" );
			return;
		}
		__lastInfoRequestTime = getTimer();

		var startTime:Number = __currentTime - __currentRange;
		var endTime:Number = __currentTime;

		//debug( "requestMachineInfo",
		//	"StartTime: " + startTime + " endTime: " + endTime );
		
		var context:Object = null;
		__rcm.remoteCall( this, "receiveMachineInfo", "handleError", context,
			"requestMachineInfo", [__logName, startTime, endTime, ips] );
	}

	private function receiveMachineInfo( context:Object,
			machineList:Array ):Void
	{
		var now:Number = getTimer();
		//debug( "receiveMachineInfo", "took " +
		//	(now - __lastInfoRequestTime) + "ms" );

		__lastInfoRequestTime = null;

		// TODO: occasionally an empty list is returned from the backend
		// erroneously because the SQL query returns 0 rows, possibly due to
		// the machine statistics not being inserted into the database in time.
		// For now, ignore it.
		if (machineList.length == 0)
		{
			return;
		}

		var changed:Boolean = false;
		var oldMachineOrder:Array = __machineOrder;
		__machineOrder = new Array();

		var oldMachineIndices:Object = new Object();
		var newMachineIndices:Object = new Object();
		for (var i:Number = 0; i < oldMachineOrder.length; ++i)
		{
			oldMachineIndices[oldMachineOrder[i]] = i;
		}

		var machineNames:Array = new Array();
		for (var i:Number = 0; i < machineList.length; ++i)
		{
			machineNames.push( i + ":" + machineList[i].hostname );
			newMachineIndices[machineList[i].ip] = i;
		}
		//debug( "receiveMachineInfo", "machineList: " + machineNames );

		for (var i:Number = 0; i < machineList.length; ++i)
		{
			var newMachine:Object = machineList[i];
			if (oldMachineIndices[newMachine.ip] == undefined)
			{
				changed = true;
				__machineInfo[newMachine.ip] = newMachine;
				//debug( "receiveMachineInfo",
				//	"added: " + BWUtils.objectToString( newMachine ) );
			}
			__machineOrder.push( newMachine.ip );
		}

		for (var i:Number = 0; i < oldMachineOrder.length; ++i)
		{
			var oldMachine:Object = __machineInfo[oldMachineOrder[i]];
			if (newMachineIndices[oldMachine.ip] == undefined)
			{
				changed = true;
				delete __machineInfo[oldMachine.ip];
				//debug( "receiveMachineInfo",
				//	"removed: " + BWUtils.objectToString( oldMachine ) );
			}
		}

		if (changed)
		{
			recreateGraphs();
		}
	}

	/**
	 *
	 */
	public function willRegroup( maxGraphs:Number )
	{
		var numMachines:Number = this.getNumMachines();

		//debug( "willRegroup", "maxGraphs = " + maxGraphs +
		//	", numMachines = " + numMachines );

		if (maxGraphs == numMachines)
		{
			// We already have a nice number of graphs
			//debug( "willRegroup", "already optimal; false" );
			return false;
		}
		else if (maxGraphs < numMachines)
		{
			// Downsize (less graphs)
			//debug( "willRegroup", "downsizing; true" );
			return true;
		}
		else if (maxGraphs > numMachines)
		{
			// Upsize (more graphs)
			//debug( "willRegroup", "upsizing; true" );
			return true;
		}

		//debug( "willRegroup", "returning false" );
		return false;
	}

	public function constructGraphs():Void
	{
		//debug( "constructGraphs", "Max graphs is: " + __maxGraphs );
		var increment:Number = 0;
		var machinesLeft:Number = this.getNumMachines();
		var placesLeft:Number = __maxGraphs;

		// fit n machines into m graphs where maybe n > m

		while (machinesLeft > 0)
		{
			var startIndex:Number = this.getNumMachines() - machinesLeft;

			// how many graphs to lay down in this iteration
			increment = Math.ceil( machinesLeft / placesLeft );

			var group:Object = new Object();
			group.items = new Array();

			var firstMachineIP:String = __machineOrder[startIndex];
			var lastMachineIP:String =
				__machineOrder[startIndex + increment - 1];
			group.firstName = __machineInfo[firstMachineIP].hostname;
			group.lastName = __machineInfo[lastMachineIP].hostname;

			for (var j:Number = 0; j < increment; ++j)
			{
				var machineInfo:Object =
					__machineInfo[__machineOrder[startIndex + j]];
				group.items.push( machineInfo );
			}
			
			var graph:Graph = this.requestGraph( group, "machine" );
			this.updateGraphName( graph.id );

			//debug( "recreateGraphs", "graph.id = " + graph.id +
			//	", group: " + group.firstName +
			//	" - " + group.lastName );

			machinesLeft -= increment;
			--placesLeft;
		}


	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = getTimer() + ": TopMachineGraphController." + context;
		if (msg != null or msg != undefined)
		{
			out += ": " + msg;
		}
		trace( out );
	}

	private function getNumMachines():Number
	{
		return __machineOrder.length;
	}

	private function updateGraphName( graphID:Number )
	{
		var group:Object = __graphData[graphID];
		var graph:Graph = __graphs[graphID];
		if (group.items.length == 1)
		{
			graph.setText( group.items[0].hostname +
				" (" + group.items[0].ip + ")" );
			graph.setShowNumSummarised( false );
		}
		else
		{
			graph.setText( group.firstName + " - " +
				group.lastName );
			graph.setShowNumSummarised( true );
		}
	}

	public function setParams( params:Object ):Void
	{
		//debug( "setParams: " + BWUtils.objectToString( params ) );

	}
	public function drillDown( id:Object ):Void
	{
		//debug( "drillDown" );
	}

	private function onDrillDown( drillDown:Object ):Void
	{
		//debug( "onDrillDown" );

		var graphID:Number = drillDown.graphId;
		var group:Object = __graphData[ graphID ];
		//debug( "onDrillDown", "group: " + BWUtils.objectToString( group ) );

		if (group.items.length == 1 and getNumMachines() == 1)
		{
			debug( "onDrillDown", "can't drill down" );
		}
		else
		{
			var state:GraphDisplayState = new GraphDisplayState(
				"Machine", { machines: group.items } );
			dispatchEvent( {
				type: 	"onDrillDown",
				state:	state
			} );
		}
	}

	private function kill():Void
	{
		//debug( "kill" );
	}

	public function pump()
	{
		//debug( "pump" );
		this.requestMachineInfo();
		super.pump();
	}

	public function setSelectedStat( statId:String ):Void
	{
		for (var graphID:String in __graphs)
		{
			__graphs[graphID].setSelectedStat( statId );
		}
	}

	private function makeRemoteRequestByTick( context:Object, graphID:Number,
			startTick:Number, endTick:Number, resolution:Number ):Void
	{
		//debug( "makeRemoteRequestByTick" );
		//debug( "makeRemoteRequestByTick: Start: " + startTick + " End: " + endTick +
		//	" Log end time: " + __logEndTime + " Graph ID: " + graphID );

		var ips:Array = new Array();
		for( var i:Number = 0; i < __graphData[graphID].items.length; ++i)
		{
			ips.push( __graphData[graphID].items[i].ip );
		}

		// __rcm.remoteCall -- do something here to request the machine
		// statistics
		__rcm.remoteCall( this, "receiveData", "errorHandler", context,
			"requestMachineStatistics",
			[__logName, ips, startTick, endTick, resolution] );

	}

	private function makeRemoteRequestByTime( context:Object, graphID:Number,
			startTime:Number, endTime:Number, resolution:Number ):Void
	{
		//debug( "makeRemoteRequestByTime" );
		//debug( "makeRemoteRequestByTime: Start: " + startTime + " End: " + endTime +
		//	" Log end time: " + __logEndTime + " Graph ID: " + graphID );

		var ips:Array = new Array();
		for( var i:Number = 0; i < __graphData[graphID].items.length; ++i)
		{
			ips.push( __graphData[graphID].items[i].ip );
		}

		// __rcm.remoteCall -- do something here to request the machine
		// statistics
		__rcm.remoteCall( this, "receiveData", "errorHandler", context,
			"requestMachineStatisticsByTime",
			[__logName, ips, startTime, endTime, resolution] );
	}

	private function printGroups()
	{
		for (var graphId:String in __graphData)
		{
			debug("GraphID: " + graphId );

			for (var i:Number = 0; i < __graphData[graphId].items.length; i++)
			{	
				debug("    IP: " + __graphData[graphId].items[i].ip);
			}
		}
	}
}
