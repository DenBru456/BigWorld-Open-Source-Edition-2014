import mx.remoting.Service;
import mx.remoting.PendingCall;
import mx.rpc.RelayResponder;
import mx.rpc.ResultEvent;

import com.bigworldtech.BWUtils;

class EveryProcGraphController extends BaseGraphController
{
	// Class members
	// ========================================================================
	public var __name:String = "Summary for all processes";

	// What process type we graph
	private var __processType:String = null;

	// Dictionary of process ids -> process info
	private var __processInfo:Object = null;

	// The order of the processes as returned from the database
	private var __processOrder:Array = null;

	// A sort of mutex on making process info requests
	private var __lastInfoRequestTime:Number;

	// Milliseconds before the process info request
	// is considered timed out
	private static var INFO_REQUEST_TIMEOUT = 5000;

	// Public class methods (initialiser functions)
	// ========================================================================
	/**
	 *	Constructor
	 */
	public function EveryProcGraphController()
	{
		super();

		__processType = null;
		__processInfo = new Object();
		__processOrder = new Array();
		__lastInfoRequestTime = null;
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "EveryProcGraphController." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	public function getTitle():String
	{
		return __name;	
	}

	/**
	 *
	 */
	public function init()
	{
		debug( "init" );
		this.requestProcessInfo();
	}

	/**
	 *
	 */
	public function setParams( params:Object )
	{
		__processType = params.processType;

		//debug( "setParams", "Process type: " + __processType );

		__name = "Process summary for " + params.processType;
	}

	// Public class methods
	// ========================================================================
	/**
	 *
	 */
	public function constructGraphs()
	{
		//debug( "constructGraphs", "Max graphs is: " + __maxGraphs );

		var increment:Number = 0;
		var processesLeft = __processOrder.length;
		var placesLeft:Number = __maxGraphs;

		// fit n processes into m graphs where maybe n > m
		while (processesLeft > 0)
		{
			var startIndex:Number = __processOrder.length - processesLeft;
			increment = Math.ceil( processesLeft / placesLeft );

			var group:Object = new Object();
			group.items = new Array();

			var firstProcessDBID:String = __processOrder[startIndex];
			var lastProcessDBID:String =
				__processOrder[startIndex + increment - 1];
			group.firstName = __processInfo[firstProcessDBID].name;
			group.lastName = __processInfo[lastProcessDBID].name;

			//debug( "constructGraphs",
			//	(__maxGraphs - placesLeft) + ": " + group.firstName + "-" +
			//	group.lastName );

			for (var j:Number = 0; j < increment; ++j)
			{
				var processDBID:Object = __processOrder[startIndex + j];
				group.items.push( processDBID );
			}

			var graph:Graph = this.requestGraph( group, __processType );
			this.updateGraphName( graph.id );
			graph.setShowNumSummarised( false );

			__graphData[graph.id] = group;

			processesLeft -= increment;
			--placesLeft;
		}
	}

	/**
	 *
	 */
	public function willRegroup( maxGraphs:Number )
	{
		var numGraphs:Number = this.getNumGraphs();
		var numProcesses:Number = __processOrder.length;

		//debug( "willRegroup: ",
		//	"maxGraphs = " + maxGraphs +
		//	", numProcesses = " + numProcesses );

		if (maxGraphs == numProcesses)
		{
			// We already have a nice number of graphs
			//debug( "willRegroup", "already optimal" );
			return false;
		}
		else if (numProcesses > maxGraphs)
		{
			// Downsize (less graphs)
			//debug( "willRegroup", "downsizing" );
			return true;
		}
		else if (numProcesses < maxGraphs)
		{
			// Upsize (more graphs)
			//debug( "willRegroup", "upsizing" );
			return true;
		}

		//debug( "willRegroup", "returning false" );
		return false;
	}

	/**
	 *
	 */
	public function onDrillDown( drillDown:Object )
	{
		var graphId:Number = drillDown.graphId;
		var group:Object = __graphData[ graphId ];

		if (group.items.length == 1 and getNumGraphs() == 1)
		{
			debug( "drillDown", "can't drill down" );
		}
		else
		{
			/* Step 1: Generate new state */
			var state:GraphDisplayState = new GraphDisplayState(
				"Proc",
				{
					processType: __processType,
					processIds: __graphData[graphId].items
				} );

			/* Step 2: Tell the boss we want the new state */
			dispatchEvent({
				type: "onDrillDown",
				state: state
			});
		}
	}

	/**
	 *	This function is called at a regular interval. So here's where
	 *	we make extra server queries for new processes and stuff.
	 */
	public function pump()
	{
		this.requestProcessInfo();

		super.pump();
	}


	/**
	 *	Overridden from BaseGraphController so that all graphs get the same
	 *	selected statistic state.
	 */
	public function setSelectedStat( statId: String )
	{
		for (var graphId:String in this.__graphs)
		{
			var graph:Graph = __graphs[graphId];
			graph.setSelectedStat( statId );
		}
	}

	// Private methods
	// ========================================================================
	/**
	 *
	 */
	private function getNumGraphs()
	{
		var numGraphs:Number = 0;
		for (var i:String in this.__graphData)
		{
			++numGraphs;
		}

		return numGraphs;
	}

	/**
	 *
	 */
	private function addToGraph( newProc:Object )
	{
	}

	/**
	 *
	 */
	private function updateGraphName( graphId:Number )
	{
		var group:Object = __graphData[ graphId ];
		if (group.items.length == 1)
		{
			var processInfo = this.__processInfo[ group.items[0] ];
			__graphs[ graphId ].setText(
				processInfo.name + " (Host: " + processInfo.machine +
				", PID: " +
				processInfo.pid + ")" );
			__graphs[ graphId ].setShowNumSummarised( false );

			/*
			debug( "updateGraphName",
				"Single process: Name is: " +
				this.__processInfo[ group.items[0] ].name );
			*/
		}
		else
		{
			__graphs[ graphId ].setText(
				this.__processType + " " +
				group.firstName + "-" + group.lastName );
			__graphs[ graphId ].setShowNumSummarised( true );
		}
	}



	/**
	 *
	 */
	public function drillDown( graphId:Number )
	{
		var group:Object = __graphData[ graphId ];

		if (group.items.length == 1 and getNumGraphs() == 1)
		{
			debug( "drillDown", "can't drill down" );
		}
		else
		{
			// Step 1: Generate new state
			var state:GraphDisplayState = new GraphDisplayState(
				"Proc",
				{
					time: Math.round(__currentTime),
					processType: __processType,
					processIds: group.items
				}
			);

			// Step 2: Tell the boss we want the new state
			dispatchEvent({
				type: "onDrillDown",
				state: state
			});

			debug( "drillDown", "going down" );
		}
	}

	// Remote requests
	// ========================================================================

	/**
	 *
	 */
	private function makeRemoteRequestByTick( context:Object, graphId:Number,
		startTick:Number, endTick:Number, resolution:Number )
	{
		//debug( "makeRemoteRequestByTick" );

		var dbIds:Array = __graphData[graphId].items;

		__rcm.remoteCall( this, "receiveData", "handleError", context,
			"requestProcessStatistics", [__logName, __user, __processType, dbIds, startTick,
			endTick, resolution] );
	}

	/**
	 *
	 */
	private function makeRemoteRequestByTime( context:Object, graphId:Number,
		startTime:Number, endTime:Number, resolution:Number )
	{
		//debug( "makeRemoteRequestByTime" );

		var dbIds:Array = __graphData[graphId].items;

		__rcm.remoteCall( this, "receiveData", "handleError", context,
			"requestProcessStatisticsByTime", [__logName, __user, __processType, dbIds,
			startTime, endTime, resolution] );
	}

	/**
	 *
	 */
	private function requestProcessInfo()
	{
		// If we had a request pending and haven't had a reply for 
		// less than 5 seconds, consider request still outstanding
		if (__lastInfoRequestTime != null && 
				getTimer() - __lastInfoRequestTime < INFO_REQUEST_TIMEOUT)
		{
			debug( "requestProcessInfo", 
				"Already waiting for requestProcessInfo response" );
			return;
		}

		__lastInfoRequestTime = getTimer();

		var startTime:Number = __currentTime - __currentRange;
		var endTime:Number = __currentTime;

		__rcm.remoteCall( this, "receiveProcessInfo", "handleError", null,
			"requestProcessInfo", [__logName, __user, __processType,
			startTime, endTime ] );
	}

	// Receivers
	// ========================================================================

	/**
	 *
	 */
	private function receiveProcessInfo( context:Object, processList:Array )
	{
		//debug( "receiveProcessInfo" );
		__lastInfoRequestTime = null;

		__processOrder = new Array();

		var newProcessFound:Boolean = false;
		// Get new process info
		for (var i:Number = 0; i < processList.length; ++i)
		{
			// Add to process info
			var newProc:Object = processList[i];

			__processOrder.push( newProc.dbId );

			if (__processInfo[ newProc.dbId ] == undefined)
			{
				__processInfo[ newProc.dbId ] = newProc;
				newProcessFound = true;
			}
			//debug( "receiveProcessInfo",
			//	i + ":process " + __processInfo[__processOrder[i]].name +
			//	" (" + __processOrder[i] + ")" );
		}

		if (newProcessFound)
		{
			this.recreateGraphs();
		}
	}
}
