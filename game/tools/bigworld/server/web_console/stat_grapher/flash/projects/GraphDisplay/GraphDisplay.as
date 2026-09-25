import mx.remoting.Service;
import mx.remoting.PendingCall;

import mx.rpc.RelayResponder;
import mx.rpc.FaultEvent;
import mx.rpc.ResultEvent;

import com.bigworldtech.BWUtils;
import BaseGraphController;

class GraphDisplay extends MovieClip
{
	// Visual related variables
	// ========================================================================
	private var __currentMaxGraphs:Number = 0;
	private var __graphPadding:Number;
	private var __graphs:Array;
	private static var ___minGraphWidth:Number = 300;
	private static var ___minGraphHeight:Number = 200;
	private var __width:Number;
	private var __height:Number;

	// Internal logic variables
	// ========================================================================
	// Log identification
	public var __logName:String;
	public var __user:String = null;

	// Pump interval identifier
	public var __interval:Number = null;
	public var __intervalDuration:Number = null;

	// Remote service object
	private var __service:Service;

	// Graph states
	private var __parentStateList:Array;
	private var __currentState:Object;

	// Graph controller
	//private var __graphController:BaseGraphController;
	private var __graphController:Object = null;
	private var __prefTree:Object = null;
	private var __displayPrefs:Object = null;
	private var __nextGraphID = 0;

	// Initial volatile state (only used once in init, then it's unused)
	private var __initialVolatileState:Object = new Object();


	// The last time we sent stats
	private var __lastGetStatsTime:Number = null;

	// Minimum time in milliseconds between sending stats
	private static var MIN_GETSTATS_TIME:Number = 200;

	// Internal components (movieclips, textfields)
	// ========================================================================
	// Bounding box instance
	private var _mcBoundingBox:MovieClip;

	// Misc
	// ========================================================================
	// Functions automatically defined by Listener
	private var dispatchEvent:Function;
	public var addEventListener:Function;
	public var removeEventListener:Function;

	// Event listener functions to hook into Graph Controllers
	private var __graphControllerEvents:Array;

	// For all graphs created, the desired points per view range
	private var __desiredPointsPerView:Number = 50;

	// Public methods
	// ========================================================================
	/**
	 * Constructor
	 */
	public function GraphDisplay()
	{
		// Initialise logic
		__graphs = new Array();
		__graphControllerEvents =
			[ "onKillGraphs",
			"onDrillDown",
			"onDrillUp",
			"onSnapToEnd",
			"onChangeTime",
			"onChangeRange",
			"onGraphSelected",
			"onDrawStats",
			"onReceiveLogRange"
			];
		//this.initState( this.defaultGraphDisplayState() );

		// Initialise display
		this.initDisplay();
		this.doResize();

		// Initialise event dispatch framework
		mx.events.EventDispatcher.initialize( this );
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "GraphDisplay." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	/**
	 * Initialise display related variables
	 */
	public function initDisplay()
	{
		// Retrieve width from scaled bounding box
		__width = this._width;
		__height = this._height;

		// Hide bounding box
		_mcBoundingBox._visible = false;
		_mcBoundingBox._width = 0;
		_mcBoundingBox._height = 0;

		// Enforce default zoom
		this._xscale = 100;
		this._yscale = 100;

		// Other general inits
		__graphPadding = 5;


		__initialVolatileState.currentTime = null;
		__initialVolatileState.currentRange = 60000;
		__initialVolatileState.snapToEnd = true;
		__initialVolatileState.logStartTime = null;
		__initialVolatileState.logEndTime = null;

	}

	/**
	 * Initialise graph controller states
	 */
	public function initState( state:GraphDisplayState )
	{
		/* TODO: doesn't appear to be used
		var graphStates:Array;
		if (stateString != undefined)
		{
			graphStates = GraphDisplayState.arrayFromString( stateString );
		}

		var numParentStates:Number = graphStates.length - 1;
		__parentStateList = new Array();

		for (var i:Number = 0; i < numParentStates; ++i)
		{
			__parentStateList.push( graphStates[i] );
		}
		__currentState = graphStates[graphStates.length - 1];
		*/

		__parentStateList = new Array();
		__currentState = state;
	}

	/**
	 * Main entry point to get graphing started
	 */
	public function go()
	{
		//debug( "go", "Log name is: " + __logName );

		// Initialise from server
		var scm:SyncCallbackManager = new SyncCallbackManager();
		scm.setService( __service );

		scm.remoteCall(this, "receivePrefTree", "handleError",
				"requestPrefTree", [__logName]);

		scm.remoteCall(this, "receiveDisplayPrefs", "handleError",
				"requestDisplayPrefs", [__logName]);

		scm.remoteCall(this, "receiveLogRange", "handleError",
				"requestLogRange", [__logName]);

		scm.callOnFinish(this, "go2");
		scm.start();
	}

	/**
	 * Entry point part two
	 */
	public function go2()
	{
		//debug( "go2" );
		// Initial volatile state is at the end of the log, with a view
		// range of 60 seconds

		// Create state if it hasn't been done from the outside
		if (__currentState == null)
		{
			this.initState( this.defaultGraphDisplayState() );
		}

		// Let's go!
		this.makeGraphController( __currentState, __initialVolatileState );

		//debug( "go2", "Setting interval" );
		//__interval = setInterval( this, "pump", 2500 );
	}

	/**
	 *
	 */
	private function defaultGraphDisplayState()
	{
		return new GraphDisplayState( "TopProc", null );
	}

	/**
	 *	Save the enabled and disabled statistics.
	 */
	public function saveEnabledStatOrder( category,
		enabledStatList, disabledStatList )
	{
		// debug( "saveEnabledStatOrder(" +
		//		__logName + ")",
		// 	"procType = " + procType +
		// 	", enabled stats = " + enabledStatList +
		// 	", disabled stats = " + disabledStatList );

		// Update our own display preference state first
		if (category =="machine")
		{
			__displayPrefs["enabledMachineStatOrder"] = enabledStatList;
		}
		else
		{
			__displayPrefs["enabledProcStatOrder"][category] = enabledStatList;
		}

		// Now tell the graph controllers

		// Process enabled stats
		for (var i:String in enabledStatList)
		{
			var enabledStat:String = enabledStatList[i];
			__graphController.setStatEnabled( category, enabledStat, true );
		}

		// Process disabled stats
		for (var i:String in disabledStatList)
		{
			var disabledStat:String = disabledStatList[i];
			__graphController.setStatEnabled( category, disabledStat, false );
		}

		// Save it in the backend

		// Don't bother using the RemotingCallbackManager, since we don't need
		// to manage a callback
		if (category =="machine")
		{
			__service.saveEnabledMachineStatOrder( __logName, enabledStatList );
		}
		else
		{
			__service.saveEnabledProcStatOrder( __logName, category,
				enabledStatList );
		}
	}

	/**
	 * Returns a vertical slice of the current statistics. Used for showing
	 * in the legend.
	 */
	public function getCurrentStats()
	{
		// Rate limit the use of this function, so that we
		// don't overload FlashJS

		if ((__lastGetStatsTime != null) &&
				((getTimer() - __lastGetStatsTime) < MIN_GETSTATS_TIME ) )
		{
			/*
			debug( "getCurrentStats", "Rate limited, not sending " +
				"(previous time is: " +
				(getTimer() - __lastGetStatsTime) + "ms)") ;
			*/
			return;
		}

		var stats:Object = __graphController.getCurrentStats();
		//debug( "getCurrentStats" );
		dispatchEvent( {
			type: "onGetCurrentStats",
			stats: stats
		} );

		__lastGetStatsTime = getTimer();
	}

	/**
	 * Gets the type of the current Graph display
	 */
	public function getGraphType():String
	{
		//debug( "getGraphType", "graphType is " + __currentState.graphType );
		
		return __currentState.graphType;
	}

	/**
	 * Gets the start and end times of the log
	 */
	public function getLogBounds():Object
	{
		return __graphController.getLogBounds();
	}

	/**
	 * Gets a display title string from the graphcontroller
	 */
	public function getTitle():String
	{
		return __graphController.getTitle();
	}


	/**
	 * Initiates update of graphs
	 */
	public function pump()
	{
		//debug( "pump" );
		__graphController.pump();
	}

	/**
	 * Simply updates graphs (stuff that happens out of the
	 * heartbeat interval, e.g. when the user pans)
	 */
	public function update()
	{
		__graphController.update();
	}

	// Public setters and getters
	// ========================================================================

	/**
	 *
	 */
	public function setService( service:Service )
	{
		__service = service;
	}

	/**
	 *
	 */
	public function setLogName( logName )
	{
		__logName = logName;
	}

	/**
	 *
	 */
	public function setUser( user:String )
	{
		__user = user;
	}

	// GraphController function forwarders
	// ========================================================================
	/**
	 *
	 */
	public function getCurrentTime()
	{
		return __graphController.getCurrentTime();
	}

	/**
	 *
	 */
	public function getCurrentRange()
	{
		return __graphController.getCurrentRange();
	}

	/**
	 *
	 */
	public function setCurrentTime( time:Number )
	{
		__graphController.setCurrentTime( time );
	}

	/**
	 *
	 */
	public function setCurrentRange( range:Number )
	{
		if (__graphController == null)
		{
			__initialVolatileState.currentRange = range;
		}
		else
		{
			__graphController.setCurrentRange( range );
		}
	}

	/**
	 *
	 */
	public function setSnapToEnd( snap:Boolean )
	{
		//debug( "setSnapToEnd( " + snap + " )" );
		__graphController.setSnapToEnd( snap );
	}

	/**
	 *
	 */
	public function setShowServiceApps( showSA:Boolean )
	{
		//debug( "setShowServiceApps( " + showSA + " )" );
		__graphController.setShowServiceApps( showSA );
	}

	/**
	 *
	 */
	public function setSelectedStat( category:String, statId:String )
	{
		//debug( "setSelectedStat( " + statId + " )" );
		__graphController.setSelectedStat( statId );
	}

	/**
	 *
	 */
	public function setStatColour( category:String, statId:Number,
		colour:String )
	{
		/*
		debug( "setStatColour( " + category + "." + statId + " = " +
			colour +_ " )" );
		*/

		if (category == "machine")
		{
			__displayPrefs.machineStatPrefs[statId].colour = colour;
			__graphController.setStatColour( category, statId, colour );
			__service.setMachineStatColour( __logName, statId, colour );
		}
		else
		{
			__displayPrefs.procPrefs[category][statId].colour = colour;
			__graphController.setStatColour( category, statId, colour );
			// Notify service of colour change
			__service.setProcessStatColour( __logName, category,
				statId, colour );
		}

	}

	/**
	 *
	 */
	public function getSelectedGraphCategory( )
	{
		return __graphController.getSelectedGraphCategory( );
	}

	/**
	 *
	 */
	public function getPreferences( )
	{
		return __graphController.getPreferences( );
	}

	/**
	 *
	 */
	public function getDisplayPreferences( )
	{
		return __graphController.getDisplayPreferences( );
	}

	// Private logic methods
	// ========================================================================
	/**
	 *
	 */
	private function receivePrefTree( prefTree:Object )
	{
		//debug( "receivePrefTree" );
		//BWUtils.printObject( prefTree, 5 );
		__prefTree = prefTree;
		dispatchEvent( {
			type: "onReceivePrefTree",
			prefTree: __prefTree
		} );
	}

	/**
	 *
	 */
	private function receiveLogRange( result:Object )
	{
		// This only happens once to initialise the graph controller
		//debug( "receiveLogRange",
		//	"Received log range: " + result.start + " - " + result.end );
		__initialVolatileState.logStartTime = result.start;
		__initialVolatileState.currentTime =
			__initialVolatileState.logEndTime = result.end;
	}

	/**
	 *
	 */
	private function receiveDisplayPrefs( result:Object )
	{
		__displayPrefs = result;
		//debug( "receiveDisplayPrefs", BWUtils.objectToString( result, 4 ) );

		dispatchEvent(
			{
				type: "onReceiveDisplayPrefs",
				prefs: __displayPrefs
			}
		);
	}


	/**
	 *
	 */
	private function makeGraphController( graphState:Object,
		volatileState:Object )
	{
		var newController:BaseGraphController = null;

		switch (graphState.graphType)
		{
			case "TopProc":
				newController = new TopProcGraphController();
			break;

			case "EveryProc":
				newController = new EveryProcGraphController();
			break;

			case "Proc":
				newController = new ProcGraphController();
			break;

			case "TopMachine":
				newController = new TopMachineGraphController();
			break;

			case "Machine":
				newController = new MachineGraphController();
			break;

			default:
				debug( "makeGraphController",
					"Invalid graph type: " + graphState.graphType );
				return;
		}

		__graphController = newController;

		// Hook event listeners in
		for (var i:Number = 0; i < __graphControllerEvents.length; ++i)
		{
			__graphController.addEventListener( __graphControllerEvents[i],
				this );
		}

		// Initialise graphController
		__graphController.setParams( graphState.params );
		__graphController.setVolatileState( volatileState );
		__graphController.setGraphRequestCallback( this, "requestGraph" );
		__graphController.setPreferences( __prefTree );
		__graphController.setDisplayPreferences( __displayPrefs );
		__graphController.setLogName( __logName );
		__graphController.setService( __service );
		__graphController.setUser( __user );
		__graphController.setMaxGraphs( this.getMaxGraphs() );

		__graphController.init();
		
		dispatchEvent( {
			type: 		"onGraphStateChanged",
			isRoot:		(__parentStateList.length == 0)
		} );
	}

	/**
	 *
	 */
	private function killGraphController()
	{
		this.killGraphs();

		// Hook event listeners in
		for (var i:Number = 0; i < __graphControllerEvents.length; ++i)
		{
			__graphController.removeEventListener( __graphControllerEvents[i],
				this );
		}

		__graphController.kill();
		delete __graphController;
	}

	/**
	 *
	 */
	public function killGraphs()
	{
		// Unselect the currently selected graph
		__graphController.deselectGraph();

		//debug( "killGraphs", "got " + __graphs.length + " graphs" );
		for (var graphID:Number = 0; graphID < __graphs.length; ++graphID)
		{
			__graphs[graphID].destroy();
		}

		BWUtils.clearArray( __graphs );

		__nextGraphID = 0;
	}

	/**
	 *
	 */
	private function goDownState( graphState:Object )
	{
		//debug( "goDownState", "__currentState = " +
		//	__currentState );
		//debug( "goDownState", "graphState = " + graphState );
		// Grab volatile state variables
		var volatileState:Object = __graphController.getVolatileState();

		// Destroy current controller
		this.killGraphController();


		// Push current state onto "state stack"
		__parentStateList.push( __currentState );
		//debug( "goDownState", "__parentStateList: " +
		//	__parentStateList );
		__currentState = graphState;

		// Create new graph controller
		this.makeGraphController( graphState, volatileState );

		// Start the new graph controller
		__graphController.pump();


	}

	/**
	 *
	 */
	private function goUpState()
	{
		//debug( "goUpState", " __parentStateList );

		// Grab volatile state variables
		var volatileState:Object = __graphController.getVolatileState();

		if (__parentStateList.length == 0)
		{
			debug("goUpState", "ERROR: No parent states to go to." );
			return;
		}

		// Pop the previous state off the list
		__currentState = __parentStateList.pop();

		//debug( "goUpState", "__currentState = " + __currentState );

		// Destroy current controller
		this.killGraphController();

		// Create new graph controller
		makeGraphController( __currentState, volatileState );

		// Start the new graph controller
		__graphController.pump();
	}

	// Private display related methods
	// ========================================================================

	/**
	 *
	 */
	public function setSize( width:Number, height:Number )
	{
		if (width != null)
		{
			__width = width;
		}
		if (height != null)
		{
			__height = height;
		}

		this.doResize();
	}

	/**
	 * Handle resizing
	 */
	private function doResize()
	{
		if (_global.isLivePreview)
		{
			// undocumented Flash feature; indicates whether we are being
			// viewed under the Flash authoring IDE
			_mcBoundingBox._visible = true;
			_mcBoundingBox._width = __width;
			_mcBoundingBox._height = __height;
		}
		else
		{
			var newMaxGraphs:Number = this.getMaxGraphs();
			//debug( "doResize", "__currentMaxGraphs = " +
			//	__currentMaxGraphs +
			//	", newMaxGraphs = " + newMaxGraphs );

			if (__currentMaxGraphs != newMaxGraphs &&
					__graphController.willRegroup( newMaxGraphs ))
			{
				__currentMaxGraphs = newMaxGraphs;
				this.killGraphs();
				__graphController.setMaxGraphs( newMaxGraphs );
				__graphController.recreateGraphs();

				// Notify controllers of new maxGraphs
				__graphController.setMaxGraphs( newMaxGraphs );
			}

			// Rejig the graphs
			this.rejigGraphLayout();
		}
	}

	public function getHeight():Number
	{
		return __height;
	}

	public function getWidth():Number
	{
		return __width;
	}

	/**
	 *
	 */
	private function getMaxGraphs():Number
	{
		var numCols:Number = Math.floor( __width / ___minGraphWidth );
		var numRows:Number = Math.floor( __height / ___minGraphHeight );

		if (numCols <= 0)
		{
			numCols = 1;
		}
		if (numRows <= 0)
		{
			numRows = 1;
		}
		var maxGraphs:Number = numCols * numRows;
		//debug( "getMaxGraphs",
		//	"dimensions: " + __width + "x"  + __height +
		//	", returning " + maxGraphs + "(" + numCols + "x" + numRows + ")" );
		return maxGraphs;
	}


	/**
	 *
	 */
	public function requestGraph( owner:BaseGraphController )
	{
		var graph:Graph = Graph( this.attachMovie(
			"Graph",
			"graph" + __nextGraphID,
			__nextGraphID
		) );
		//debug( "requestGraph", "created graph at depth " +
		//	graph.getDepth() );

		graph.setDesiredPointsPerView( __desiredPointsPerView );

		// Assign id
		graph.setId( __nextGraphID );
		++__nextGraphID;

		graph.addEventListener( "onChooseResolution", this );

		// Add to list of graphs
		__graphs.push( graph );

		/* Everytime a graph is added, rejig the graphs */
		/* TODO: Don't rejig until finished adding graphs */
		this.rejigGraphLayout();

		return graph;
	}


	/**
	 *
	 */
	public function rejigGraphLayout()
	{
		var areaWidth:Number = __width - 1;	// ensure that borders are drawn
											// within this area
		var areaHeight:Number = __height - 1;

		var areaRatio:Number = areaWidth / areaHeight;
		var graphRatio:Number = ___minGraphWidth / ___minGraphHeight;

		var numGraphs:Number = __graphs.length;
		if (!numGraphs)
		{
			return;
		}

		var rowRatio:Number = graphRatio / areaRatio;

		var numRowsFraction:Number = Math.sqrt( numGraphs * rowRatio );
		var numColsFraction:Number = numRowsFraction / rowRatio;

		// Try every combination now
		var numRows:Number;
		var numCols:Number;
		var numSpaces:Number;
		var ratioDiff:Number;

		var tempRows:Number;
		var tempCols:Number;
		var tempNumSpaces:Number;
		var tempRatioDiff:Number;

		// Combo 1: Round x up, y up
		numRows = Math.ceil( numRowsFraction );
		numCols = Math.ceil( numColsFraction );
		numSpaces = numRows * numCols;
		ratioDiff = Math.abs( (numRows / numCols) - rowRatio );

		// Combo 2: Round x up, y down
		tempCols = Math.round( numColsFraction );
		if (tempCols == 0)
		{
			tempCols = 1;
		}
		tempRows = Math.ceil( numGraphs / tempCols );
		tempNumSpaces = tempRows * tempCols;
		tempRatioDiff = Math.abs( (tempRows / tempCols) - rowRatio );
		if (tempNumSpaces >= numGraphs &&
			(tempNumSpaces < numSpaces ||
				(tempNumSpaces == numSpaces && tempRatioDiff < ratioDiff)
			)
		)
		{
			numRows = tempRows;
			numCols = tempCols;
			numSpaces = tempNumSpaces;
			ratioDiff = tempRatioDiff;
		}

		// Combo 3: Round x down, y up
		tempRows = Math.round( numRowsFraction );
		if (tempRows == 0)
		{
			tempRows = 1;
		}
		tempCols = Math.ceil( numGraphs / tempRows );
		tempNumSpaces = tempRows * tempCols;
		tempRatioDiff = Math.abs( (tempRows / tempCols) - rowRatio );
		if (tempNumSpaces >= numGraphs &&
			(tempNumSpaces < numSpaces ||
				(tempNumSpaces == numSpaces && tempRatioDiff < ratioDiff)
			)
		)
		{
			numRows = tempRows;
			numCols = tempCols;
			numSpaces = tempNumSpaces;
			ratioDiff = tempRatioDiff;
		}

		// Now do stuff!
		var newGraphHeight = (areaHeight -
			(__graphPadding * (numRows - 1)))/
				numRows;
		var newGraphWidth = (areaWidth -
			(__graphPadding * (numCols - 1)))/
				numCols;

		//debug( "rejigGraphLayout", "New size for " + __graphs.length
		//	+ " graphs is " + newGraphWidth + "x" + newGraphHeight );

		for (var i:Number = 0; i < __graphs.length; ++i)
		{
			var graph:Graph = __graphs[i];
			//debug( "rejigGraphLayout", "Graph is: " + graph );
			var row:Number = Math.floor( i / numCols );
			var col:Number = i % numCols;

			graph.setSize( newGraphWidth, newGraphHeight );

			graph._x = newGraphWidth * col + __graphPadding * col;
			graph._y = newGraphHeight * row + __graphPadding * row;
		}
	}

	// Event handlers
	// ========================================================================

	/**
	 * Event handler for when the graph controller wants to
	 * remove all graphs.
	 */
	private function onKillGraphs()
	{
		//debug( "onKillGraphs" );
		this.killGraphs();
	}

	/**
	 * Event handler for when the graph controller wants to
	 * drill down.
	 */
	private function onDrillDown( drillDown:Object )
	{
		this.goDownState( drillDown.state );
		this.dispatchEvent( drillDown );
	}

	/**
	 * Event handler for when the graph contrloller wants to
	 * drill up.
	 */
	private function onDrillUp( drillUp:Object )
	{
		//debug( "onDrillUp" );
		this.goUpState();
		this.dispatchEvent( drillUp );
	}

	/**
	 * Event handler for when the graph controller
	 * has changed the "onSnapToEnd" status.
	 */
	private function onSnapToEnd( snapEvent:Object )
	{
		this.dispatchEvent( snapEvent );
	}

	/**
	 * Event handler for when the graph controller
	 * changes the current time being viewed.
	 */
	private function onChangeTime( timeEvent:Object )
	{
		//debug( "onChangeTime" );
		this.dispatchEvent( timeEvent );
	}

	/**
	 * Event handler for when the graph controller
	 * changes the range being viewed.
	 */
	private function onChangeRange( rangeEvent:Object )
	{
		//debug( "onChangeRange" );
		this.dispatchEvent( rangeEvent );
	}

	/**
	 * Event handler for when the graph controller
	 * draws new lines.
	 */
	private function onDrawStats( drawStatEvent:Object )
	{
		this.getCurrentStats();
	}

	/**
	 * Event handler for when the user
	 * selects a particular graph.
	 */
	private function onGraphSelected( selectEvent:Object )
	{
		//debug( "onGraphSelected", selectEvent.category );
		this.dispatchEvent( selectEvent );
	}

	/**
	 *	Set the desired number of points per view for each graph created.
	 */
	public function setDesiredPointsPerView( numPoints:Number ):Void
	{
		__desiredPointsPerView = numPoints;
	}


	/**
	 *	Set the minimum dimensions of a graph in the GraphDisplay.
	 */
	public function setMinGraphDimensions( minWidth:Number,
			minHeight:Number ):Void
	{
		if (minWidth != null && minWidth != undefined && isFinite( minWidth ))
		{
			___minGraphWidth = minWidth;
		}

		if (minHeight != null && minHeight != undefined &&
				isFinite( minHeight ))
		{
			___minGraphHeight = minHeight;
		}
		this.doResize();
	}

	/**
	 * Frame handler called whenever a new frame is entered in Flash.
	 */
	private function onEnterFrame()
	{
		__graphController.onEnterFrame();
	}

	public function onReceiveLogRange( oEvent:Object ):Void
	{
		dispatchEvent( oEvent );
	}


	/**
	 * Handles resolution changes
	 */
	public function onChooseResolution( oEvent:Object ):Void
	{
		// Change update frequency depending on what resolution
		// we're looking at
		if (__intervalDuration != oEvent.windowSampleTime)
		{
			// Kill the interval update
			this.pause();
			__intervalDuration = oEvent.windowSampleTime;

			// This part is dodgy: move the log end time backwards
			// by windowSampleTime
			var logEndTime = this.getLogBounds()["end"];

			// Artifically add a buffer between end of log and what we can
			// see, as lower resolution. At the highest resolution, the
			// buffer should be 0. (Hence the subtraction bit)
			var newLogEndBuffer = oEvent.windowSampleTime - 
				__prefTree.tickInterval * 1000;

			//debug( "onChooseRes", "windowSampleTime: " + oEvent.windowSampleTime + " final buffer: " + newLogEndBuffer );

			__graphController.setLogEndBuffer( newLogEndBuffer );

			// Recreate the interval update
			this.resume();
		}
		dispatchEvent( oEvent );
	}

	public function pause()
	{
		if (__interval != null)
		{
			//trace("GraphDisplay.pause: Pausing GraphDisplay");
			clearInterval( __interval );
			__interval = null;
		}
	}

	public function resume()
	{
		if (__interval == null)
		{
			//trace("GraphDisplay.resume: Resuming GraphDisplay");
			__interval = setInterval( this, "pump", __intervalDuration );
		}
	}
}
