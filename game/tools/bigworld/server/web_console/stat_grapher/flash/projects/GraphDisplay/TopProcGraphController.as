import mx.remoting.Service;
import mx.remoting.PendingCall;
import mx.rpc.RelayResponder;
import mx.rpc.ResultEvent;

import com.bigworldtech.BWUtils;

class TopProcGraphController extends BaseGraphController
{
	// Class members
	// ========================================================================
	public var __name:String = "Summary of processes";

	// Public class methods (initialiser functions)
	// ========================================================================
	/**
	 *	Constructor
	 */
	public function TopProcGraphController()
	{
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "TopProcGraphController." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	/**
	 *
	 */
	public function init()
	{
		//debug( "init" );
		this.recreateGraphs();
	}

	/**
	 * Returns the title
	 */
	public function getTitle():String
	{
		return __name;
	}

	/**
	 *
	 */
	public function setParams( params:Object )
	{
	}

	// Public class methods
	// ========================================================================

	/**
	 * Overriding setCurrentTime for special case title naming when
	 * no statistics available
	 */
	public function setCurrentTime( time:Number )
	{
		super.setCurrentTime( time );

		for (var i:String in __graphs)
		{
			updateGraphName( i );
		}
	}

	/**
	 * Sets the current name. Called whenever it might have changed
	 */
	public function updateGraphName( graphId:Number )
	{
		var graph:Graph = __graphs[graphId];

		var numSummarised:Number = graph.getNumSummarised();
		var processType:String = __graphData[graphId];

		//debug( "updateGraphName", "Num summarised for "
		//		+ processType + " is: " + numSummarised );


		if (numSummarised == 0 or numSummarised == null)
		{
			graph.setText( "No " + processType + "s");
			graph.setShowNumSummarised( false );
		}
		else if (numSummarised == 1)
		{
			graph.setText( processType );
			graph.setShowNumSummarised( false );
		}
		else
		{
			graph.setText( "Summary for " + numSummarised + 
				" " + processType + "s" );
			graph.setShowNumSummarised( false );
		}
	}

	/**
	 *
	 */
	public function constructGraphs()
	{
		for (var i:String in __prefTree.procPrefs)
		{
			if (i == "ServiceApp" and this.getShowServiceApps() == false)
			{
				continue;
			}
			
			//debug( "constructGraphs", "Creating graph for " + i );
			var graph:Graph = this.requestGraph( i, i );

			var id:Number = graph.id;
			this.updateGraphName( id );

			//debug( "recreateGraph",
			//	"Request new graph: id=" + id +
			//	", data=" + __graphData[ id ] );
		}
	}

	/**
	 *
	 */
	public function onDrillDown( drillDown:Object )
	{
		var id:Number = drillDown.graphId;

		/* Step 1: Generate new state */
		var state:GraphDisplayState = new GraphDisplayState(
			"EveryProc", { processType: __graphData[id] } );

		/* Step 2: Tell the boss we want the new state */
		dispatchEvent({
			type: "onDrillDown",
			state: state
		});
	}


	// Private functions
	// ========================================================================
	/**
	 * Update graph name on drawing new stats
	 */
	private function onDrawStats( drawStatEvent:Object )
	{
		super.onDrawStats( drawStatEvent );

		for (var i:String in __graphs)
		{
			this.updateGraphName( i );
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
		var category:String = __graphData[ graphId ];

		__rcm.remoteCall( this, "receiveData", "handleError", context,
			"requestProcessStatistics", [ __logName, __user, category, null, startTick,
			endTick, resolution] );
	}

	/**
	 *
	 */
	private function makeRemoteRequestByTime( context:Object, graphId:Number,
		startTime:Number, endTime:Number, resolution:Number )
	{
		var category:String = __graphData[ graphId ];

		__rcm.remoteCall( this, "receiveData", "handleError", context,
			"requestProcessStatisticsByTime", [ __logName, __user, category, null,
			startTime, endTime, resolution] );
	}
}
