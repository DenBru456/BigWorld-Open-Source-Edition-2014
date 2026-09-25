import mx.remoting.Service;
import mx.remoting.PendingCall;

import mx.rpc.RelayResponder;
import mx.rpc.FaultEvent;
import mx.rpc.ResultEvent;

import com.bigworldtech.BWUtils;

/**
 * 	The base class for all graph controllers.
 */

class BaseGraphController
{
	// Class members
	// ========================================================================
	// Name of controller (not really used except for debugging)
	public var __name:String = "Base";

	// List of graphs
	private var __graphs:Object;
	private var __graphData:Object;

	// Current time in seconds (unix timestamp)
	private var __currentTime:Number = null;
	private var __currentRange:Number = 60;
	private var __isSettingTime:Boolean = false;

	// Log boundaries
	private var __logStartTime:Number;
	private var __logEndTime:Number;

	// Currently selected graph and statistic id
	private var __selectedGraphId:Number;

	// Setting which shows whether we follow the latest time or not
	private var __snapToEnd:Boolean;

	// Setting which shows whether we display ServiceApps or not
	private var __showServiceApps:Boolean;

	// If we've zoomed out, we have to restrict
	private var __logEndBuffer:Number = 0;

	// Maximum number of graphs we can have
	private var __maxGraphs:Number;

	// Variables for making remote calls
	private var __service:Service;
	private var __logName:String;
	private var __user:String = null;

	// Animate vars
	private var __isAnimating:Boolean;
	private var __animateFromTime:Number;
	private var __animateToTime:Number;
	private var __animateTotalTime:Number;
	private var __animateTimeElapsed:Number;
	private var __lastAnimateFrame:Number;

	// Preference objects
	private var __prefTree:Object = null;
	private var __displayPrefs:Object = null;

	// Callback manager
	private var __rcm:RemotingCallbackManager;

	// Graph request callback
	private var __graphRequestObj:Object;
	private var __graphRequestFunc:String;

	// Functions automatically defined by Listener
	private var dispatchEvent:Function;
	public var addEventListener:Function;
	public var removeEventListener:Function;

	// Public class methods (initialiser functions)
	// ========================================================================

	/**
	 * Constructor
	 */
	public function BaseGraphController()
	{
		__graphs = new Object();
		__graphData = new Object();
		__snapToEnd = false;
		__showServiceApps = false;
		__isSettingTime = false;
		__isAnimating = false;

		__rcm = new RemotingCallbackManager();

		mx.events.EventDispatcher.initialize( this );
		//debug( "(constructor)" );
	}

	private static function debug( context:String, msg:String )
	{
		var out:String = "BaseGraphController." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	/**
	 * Set parameters for the graph controller
	 */
	public function setParams( params:Object )
	{
		debug( "setParams", "override me" );
	}

	/**
	 * Set volatile state variables. So far, these are:
	 * - Current time
	 * - Current range
	 * - Snap to end
	 * - Showing ServiceApps
	 * - Log ranges
	 */
	public function setVolatileState( stateVars:Object )
	{
		//debug( "setVolatileState" );

		// Set log ranges
		if (stateVars.logStartTime != null && stateVars.logEndTime != null)
		{
			this.setLogRange( stateVars.logStartTime, stateVars.logEndTime );
		}

		// Set current time
		if (stateVars.currentTime != null)
		{
			//__currentTime = stateVars.currentTime;
			this.setCurrentTime( stateVars.currentTime );

			debug( "applyVolatileStateVars",
				"Applying current time: " + stateVars.currentTime );

		}

		// Set current range
		if (stateVars.currentRange != null)
		{
			//__currentRange = stateVars.currentRange ;
			this.setCurrentRange( stateVars.currentRange );

			//debug( "applyVolatileStateVars",
			//	"Applying new range: " + __currentRange );

		}

		// Set lock to latest
		if (stateVars.snapToEnd != null)
		{
			this.setSnapToEnd( stateVars.snapToEnd );

			//debug( "applyVolatileStateVars",
			//	"Applying lock to latest: " + stateVars.snapToEnd );
		}
		
		if (stateVars.showServiceApps != null)
		{
			this.setShowServiceApps( stateVars.showServiceApps );
		}
	}

	/**
	 * Sets the callback for the graph creation function.
	 */
	public function setGraphRequestCallback( obj:Object, func:String )
	{
		__graphRequestObj = obj;
		__graphRequestFunc = func;
	}

	/**
	 * Set the preference options of the graph. This must be called after
	 * creating the BaseGraphController class.
	 */
	public function setPreferences( prefTree:Object )
	{
		__prefTree = prefTree;
	}

	/**
	 * Set the display preference options of the graph. This must be called
	 * after creating the BaseGraphController class.
	 */
	public function setDisplayPreferences( displayPrefs:Object )
	{
		__displayPrefs = displayPrefs;
	}

	/**
	 * Here's the REAL constructor, called after parameters and
	 * volatile state vars are set.
	 */
	public function init()
	{
		debug( "init", "override me" );
	}

	// Public setters and getters
	// ========================================================================

	/**
	 * Sets the name of the stat_logger database log.
	 */
	public function setLogName( logName:String )
	{
		__logName = logName;
	}

	/**
	 * Sets the user id (a number) of the log.
	 */
	public function setUser( user:String )
	{
		__user = user;
	}


	/**
	 * Sets the flash remoting Service object.
	 */
	public function setService( service:Service )
	{
		__service = service;
		__rcm.setService( __service );
	}

	/**
	 * Set current time
	 */
	public function setCurrentTime( time:Number, skipUpdate:Boolean )
	{
		if (__isSettingTime == true)
		{
			//debug( "setCurrentTime", "Aborting " + "setCurrentTime" );
			return;
		}

		__isSettingTime = true;

		//debug( "setCurrentTime", time + " old time was: " + __currentTime );

		var oldTime:Number = __currentTime;

		__currentTime = time;

		if (!__isAnimating)
		{
			// XTerm style snapToEnd activation if we're at the
			// end of the log.
			if (__currentTime >= (__logEndTime - __logEndBuffer))
			{
				this.setSnapToEnd( true );
			}
			else if (__currentTime < (__logEndTime - __logEndBuffer))
			{
				//trace("Unsetting snap to end! currentTime: " + __currentTime + 
				//	" logEndTime: " + __logEndTime + " logEndbuffer: " + __logEndBuffer );
				this.setSnapToEnd( false );
			}

			// This function can change our __currentTime value
			// but whatever the value is at the end of this
			// if statement, it gets propagated to all
			// graphs anyway.
			this.restrictToLogRange();
		}
		else
		{
			//debug("setCurrentTime", "isAnimating is true");
		}

		if (__currentTime != oldTime)
		{
			for (var i:String in __graphs)
			{
				var graph:Graph = __graphs[i];
				graph.setCurrentTime( __currentTime );
			}

			dispatchEvent({
				type: "onChangeTime",
				time: __currentTime
			});
		}

		//debug( "setCurrentTime", "finished" );
		__isSettingTime = false;
		
		if (!skipUpdate)
		{
			this.update();
		}
	}

	/**
	 * Returns the current time.
	 */
	public function getCurrentTime( time:Number )
	{
		return __currentTime;
	}

	/**
	 * Returns the start and end timestamps of the current log
	 */
	public function getLogBounds():Object
	{
		return {start:__logStartTime, end:__logEndTime };
	}

	/**
	 * Set current time initiated from outside (i.e. propagate downwards)
	 */
	public function setCurrentRange( range:Number )
	{
		var oldTime = __currentTime;
		__currentRange = range;

		// Restricts us to between the log ranges
		this.restrictToLogRange();

		for (var i:String in __graphs)
		{
			var graph:Graph = __graphs[i];

			//debug("Setting graph range: " + range );
			graph.setCurrentRange( __currentRange );

			// If restrictToLogRange changed __currentTime,
			// then we need to apply it
			if (__currentTime != oldTime)
			{
				graph.setCurrentTime( __currentTime );
			}
		}

		this.update();

		dispatchEvent({
			type: "onChangeRange",
			range: __currentRange
		});
	}

	/**
	 * Returns the current time range (i.e. the viewing time range).
	 */
	public function getCurrentRange( time:Number )
	{
		return __currentRange;
	}

	/**
	 * Sets whether we have graphs follow the end of the log.
	 */
	public function setSnapToEnd( snap:Boolean )
	{
		//debug( "setSnapToEnd( " + snap + " )" );

		__snapToEnd = snap;

		// Snap to end if true
		if (__snapToEnd && __logEndTime)
		{
			this.setCurrentTime( __logEndTime - __logEndBuffer );
		}

		dispatchEvent( {
			type: "onSnapToEnd",
			snap: snap
		} );
	}

	/**
	 * Returns whether we're following the end of the log.
	 */
	public function getSnapToEnd()
	{
		return __snapToEnd;
	}

	/**
	 * Sets whether we show ServiceApps in the top level process display.
	 */
	public function setShowServiceApps( showSA:Boolean )
	{
		//debug( "setShowServiceApps( " + showSA + " )" );

		__showServiceApps = showSA;
	}

	/**
	 * Returns whether we're showing a graph for ServiceApps.
	 */
	public function getShowServiceApps()
	{
		return __showServiceApps;
	}

	/**
	 * Sets a new colour for a certain statistic under a certain category.
	 * Does not update the server, that should be done in the GraphDisplay
	 * object.
	 */
	public function setStatColour( category:String, statId:Number,
		newColour:String )
	{
		//debug( "setStatColour( category=" + category +
		//	", statId=" + statId + ", newColour=" + newColour + " )" );
		for (var graphId:String in __graphs)
		{
			var graph:Graph = __graphs[ graphId ];
			var graphCategory:String = this.getGraphCategory( graphId );

			if (category == graphCategory)
			{
				//debug( "setStatColour", "graph " + graphId );
				graph.setStatColour( statId, newColour );
			}
		}
	}

	/**
	 * Enables or disables a statistic. In the case of disable, remove
	 * the data for that statistic from our cache and redraw. For enable,
	 * we have no choice but to wipe all current data and re-request.
	 */
	public function setStatEnabled( category:String, statId:Number,
		enabled:Boolean )
	{
		//debug( "setStatEnabled( " +
		//	category + "." + statId + " = " + enabled + ")" );

		for (var i:String in __graphs)
		{
			if (category == this.getGraphCategory( i ))
			{
				__graphs[i].setStatEnabled( statId, enabled );
			}
		}
	}

	/**
	 * Selects a certain statistic. It's assumed that the stat
	 * being selected belongs to the currently selected graph.
	 * The effect of selecting a stat will be to bring that statistic's
	 * line to the front and draw it thicker.
	 */
	public function setSelectedStat( statId:String )
	{
		//debug( "setSelectedStat" );

		var graph:Graph = __graphs[__selectedGraphId];
		graph.setSelectedStat( statId );
	}

	/**
	 * Returns the category of the current graph which is selected
	 * e.g. "CellApp", "Machine", etc.
	 */
	public function getSelectedGraphCategory() : String
	{
		if (__selectedGraphId != null)
		{
			return getGraphCategory( __selectedGraphId );
		}
		else
		{
			return null;
		}
	}


	/**
	 * Returns a vertical slice of the current statistics. Used for showing
	 * in the legend.
	 */
	public function getCurrentStats()
	{
		if (__selectedGraphId != null)
		{
			return __graphs[__selectedGraphId].getCurrentStats();
		}
		else
		{
			return null;
		}
	}

	/**
	 * Returns the current preference object.
	 */
	public function getPreferences()
	{
		return __prefTree;
	}

	/**
	 * Returns the current display preference object.
	 */
	public function getDisplayPreferences()
	{
		return __displayPrefs;
	}

	/**
	 * Used by the GraphDisplay object, to set the maximum
	 * recommended amount of graphs on the screen.
	 *
	 * Called whenever GraphDisplay is resized.
	 */
	public function setMaxGraphs( maxGraphs:Number )
	{
		__maxGraphs = maxGraphs;
	}


	// Public class methods
	// ========================================================================
	/**
	 * Main function for graph controllers. Called at regular
	 * intervals, and is expected to initiate the remote
	 * requests and handle drawing lines on the screen.
	 */
	public function pump()
	{
		this.requestLogRange();
		this.update();
	}

	/**
	 * Returns a display title for the graph controller. For now, it doesn't 
	 * get updated at a regular interval. Maybe in the future...
	 */
	public function getTitle() : String
	{
		return "BaseGraphController (override me)";
	}

	/**
	 * This function is called when the flash window is resized and
	 * we need to determine whether we're going to "regroup" graphs
	 * (e.g. group multiple processes into a graph)
	 *
	 * @param	maxGraphs is the new maximum number of graphs that we can
	 *			fit on the screen. This is not a hard limit, but exceeding
	 *			this limit should only be done where necessary.
	 *
	 * @return	A boolean which indicates whether the GraphDisplay should
	 *			initiate regrouping of graphs.
	 */
	public function willRegroup( maxGraphs:Number ) : Boolean
	{
		return false;
	}

	/**
	 * Called when the user double clicks on one of the GraphController's
	 * classes.
	 *
	 * @param	id is the unique number assigned to each graph when it is created.
	 */
	public function drillDown( id:Object )
	{
		debug( "drillDown", "override me" );
	}

	/**
	 * Called just before we discard any GraphController object.
	 * This function should perform cleanup of any internal
	 * class members.
	 *
	 * Do not implement here; should be overridden by inheriting classes.
	 */
	public function kill()
	{
		debug( "kill", "override me" );
	}

	/**
	 * Returns data corresponding to the current state that we want to
	 * keep when transferring graphs.
	 *
	 * e.g. When drilling down or up, we want to maintain:
	 * - The current time
	 * - The current zoom level
	 * - Whether we're snapping to end or not
	 * - Whether we're showing ServiceApps or not
	 */
	public function getVolatileState()
	{
		var stateVars:Object = new Object();
		stateVars.currentTime = Math.round( __currentTime );
		stateVars.currentRange = Math.round( __currentRange );
		stateVars.snapToEnd = __snapToEnd;
		stateVars.showServiceApps = __showServiceApps;
		stateVars.logStartTime = __logStartTime;
		stateVars.logEndTime = __logEndTime;

		return stateVars;
	}

	/**
	 * Public interface to setting log range (used in initialisation)
	 */
	public function setLogRange( logStartTime:Number, logEndTime:Number )
	{
		this.receiveLogRange( null, {start: logStartTime, end: logEndTime } );
	}

	/**
	 * Set the log end buffer (when using lower resolution tables, they don't
	 * quite reach to the end so we have to compensate)
	 */
	public function setLogEndBuffer( logEndBuffer:Number )
	{
		if (__logEndBuffer != logEndBuffer)
		{
			__logEndBuffer = logEndBuffer;
			//debug( "setLogEndBuffer", "New log end buffer is: " + logEndBuffer );

			if (__snapToEnd == true)
			{
				// Set skipUpdate parameter to true, because this function
				// is only called in the middle of larger operations
				// and we don't want to trigger a premature update
				this.setCurrentTime( __logEndTime - __logEndBuffer, true );
			}

			// Re-restrict
			this.restrictToLogRange();
		}
	}

	/**
	 * Returns the category of the graph. In most cases it will be the process
	 * type (e.g. "CellApp", "BaseApp").
	 * There is also a special "Machine" category.
	 */
	public function getGraphCategory( graphId:Number )
	{
		return __graphs[graphId].getCategory();
	}

	// Private class methods (Graph management)
	// ========================================================================

	/**
	 * Given an id of a graph, destroys a graph and associated data.
	 */
	private function killGraph( id:Number )
	{
		__graphs[ id ].kill();
		delete __graphs[ id ];
		delete __graphData[ id ];
	}

	/**
	 * Destroys all graphs owned by this graph controller.
	 */
	private function killAllGraphs()
	{
		for (var i:String in __graphs)
		{
			killGraph( __graphs[i].id )
		}
	}

	/**
	 * Requests a graph from the GraphDisplay via a callback which was
	 * assigned to us upon construction. We then attach event listeners
	 * to this graph, and perform other initialisation routines.
	 */
	public function requestGraph( associatedData:Object, category:String )
	{
		//debug( "requestGraph" );

		var graph:Graph = __graphRequestObj[__graphRequestFunc]( this );

		__graphs[ graph.id ] = graph;
		__graphData[ graph.id ] = associatedData;

		// Hook up event listeners to the graphs
		graph.addEventListener("onDrag", this);
		graph.addEventListener("onDrillDown", this);
		graph.addEventListener("onGraphSelected", this);
		graph.addEventListener("onRemoteRequestByTicks", this);
		graph.addEventListener("onRemoteRequestByTime", this);
		graph.addEventListener("onDrawStats", this);

		// Set preference objects
		graph.setPreferences( __prefTree );
		graph.setDisplayPreferences( __displayPrefs );

		// Set current state
		graph.setCurrentTime( __currentTime );
		graph.setCurrentRange( __currentRange );
		graph.setLogRange( __logStartTime, __logEndTime );

		// Set category type
		graph.setCategory( category );

		// Update!!
		graph.update();

		return graph;
	}

	/**
	 * Called when the graphs need to be recreated. This happens when:
	 * - the browser is resized
	 * - new processes/machines are found which need to be graphed
	 */
	public function recreateGraphs()
	{
		// Kill graphs
		this.dispatchEvent({type: "onKillGraphs"});

		// Clear graph data
		BWUtils.clearObject( __graphs );
		BWUtils.clearObject( __graphData );

		// Make the actual graphs
		this.constructGraphs();

		// If only one graph exists, select the graph
		this.checkSingleGraph();
	}

	/**
	 *
	 */
	public function constructGraphs()
	{
		debug( "constructGraphs", "override me" );
	}

	/**
	 * Deselects the currently selected graph
	 */
	public function deselectGraph()
	{
		//debug( "deselectGraph" );

		if (__selectedGraphId != null)
		{
			__graphs[__selectedGraphId].setSelected( false );
			__selectedGraphId = null;

			this.dispatchEvent({type: "onGraphSelected",
				category: null});
		}
	}



	// Private class methods
	// ========================================================================
	/**
	 *	This is the default error handler for when a Flash Remoting call goes
	 *	wrong. Used when it isn't important to handle errors.
	 */
	private function handleError( context:Object, fe:FaultEvent )
	{
		BWUtils.printPythonError( fe );
	}

	/**
	 * If we only have one graph, select that one.
	 */
	private function checkSingleGraph()
	{
		if (numGraphs() == 1)
		{
			// This is tricky, we need a loop
			// just to access the single element
			// in __graphs
			for (var i:String in __graphs)
			{

				//debug( "checkSingleGraph", "Single graph " + i +
				//	" selected" );
				this.onGraphSelected({graphId: i})
				break;
			}
		}
	}

	/**
	 * Calls update() for all of our graphs.
	 */
	private function update()
	{
		//debug( "update" );
		for (var graphID:String in __graphs)
		{
			var graph:Graph = __graphs[ graphID ];
			graph.update( true );
		}
	}

	/**
	 * Requests the current log range from the server.
	 */
	private function requestLogRange()
	{
		//debug( "requestLogRange" );

		__rcm.remoteCall( this, "receiveLogRange", "handleError", null,
			"requestLogRange", [__logName] );
	}

	/**
	 * Receives the log range from the server, and propagates it downwards.
	 */
	private function receiveLogRange( context:Object, logRanges:Object )
	{
		//debug( "receiveLogRange" );

		if (logRanges.end < __logEndTime)
		{
			debug("receiveLogRange", "Our log is getting smaller?" );
		}

		if (logRanges.start == __logStartTime && logRanges.end == __logEndTime)
		{
			return;
		}

		__logStartTime = logRanges.start;
		__logEndTime = logRanges.end;

		var logRange:Number = __logEndTime - __logStartTime;

		/*
		debug( "receiveLogRange",
			__logStartTime + "-" + __logEndTime +
			"(Log went for " + (__logEndTime - __logStartTime) + "s )" );
		*/

		BWUtils.assert(__logEndTime > __logStartTime,
			"Log end time (" + __logEndTime +
			")should be greater than log start time (" +
			__logStartTime + ")!");

		//debug("receiveLogRange", "Log range: " + logRange + " View range: " + __currentRange);

		// Follow the end if we have snapToEnd activated
		// and the log is larger than our viewing area
		if (__snapToEnd == true && logRange > __currentRange)
		{
			// Propagate up, since it'll propagate downwards again.
			//this.setCurrentTime( __logEndTime );
			//debug( "receiveLogRange", "End is " + __logEndTime );
			this.animateToTime( __currentTime, (__logEndTime - __logEndBuffer) );
		}

		// Propagate log range to graphs
		for (var i:String in __graphs)
		{
			__graphs[i].setLogRange( __logStartTime, __logEndTime );
		}
		dispatchEvent( { type: "onReceiveLogRange",
			value: logRanges } );
	}

	/**
	 * When the current time or zoom level changes, we need to run the
	 * "restriction" routines again so that we can't scroll past the start
	 * or the end.
	 */
	private function restrictToLogRange()
	{

		var logRange:Number = __logEndTime - __logStartTime;

		if (logRange < __currentRange)
		{
			__currentTime = (__logEndTime - __logEndBuffer);
		}
		else if (__currentTime > (__logEndTime - __logEndBuffer))
		{
			//debug( "setCurrentTime", "Restricting to end" );
			__currentTime = (__logEndTime - __logEndBuffer);
		}
		else if ((__currentTime - __currentRange) < __logStartTime)
		{
			//debug( "setCurrentTime: ", "Restricting to start" );
			__currentTime = __logStartTime + __currentRange;
		}
	}

	/**
	 * Count the number of graphs
	 */
	private function numGraphs()
	{
		var i:Number = 0;
		for (var j:String in __graphs)
		{
			i += 1;
		}

		return i;
	}


	// Scroll animation
	// ========================================================================
	/**
	 * onEnterFrame handler (not that this isn't automatically called since
	 * this isn't a MovieClip. Instead it's called by GraphDisplay every frame)
	 */
	public function onEnterFrame()
	{
		if (__isAnimating == true)
		{
			//debug( "onEnterFrame", "animate" );
			this.doAnimate();
		}
	}

	/**
	 * Begins animating the graph scrolling from fromTime to endTime.
	 * Sets a flag which will be checked during every onEnterFrame
	 */
	public function animateToTime( fromTime:Number, toTime:Number )
	{
		/*
		trace( "animateToTime", "Animating from " +
			fromTime + " to " + toTime +
			"(Distance: " + (toTime - fromTime) + ")" );
		*/

		__isAnimating = true;
		__animateFromTime = fromTime;
		__animateToTime = toTime;
		__animateTotalTime = 1 * 200;
		__animateTimeElapsed = 0;
		__lastAnimateFrame = getTimer();

		for (var i:Number = 0; i < __graphs.length; i++)
		{
			__graphs[i].setDisableUpdate( true );
		}
	}

	/**
	 * Executes a single frame of the animateToTime operation.
	 * Called during onEnterFrame.
	 **/
	public function doAnimate( )
	{
		var curAnimateFrame = getTimer();

		// Frame time
		var frameDiff:Number = curAnimateFrame - __lastAnimateFrame;
		__animateTimeElapsed += frameDiff;

		//debug( "doAnimate", "Animating: "
		// + __animateTimeElapsed + " total time: " + __animateTotalTime );

		if (__animateTimeElapsed > __animateTotalTime)
		{
			__animateTimeElapsed = __animateTotalTime;
		}

		// Calculate new display position
		var displayTime:Number = __animateFromTime +
			(__animateToTime - __animateFromTime) *
			(__animateTimeElapsed / __animateTotalTime);

		//debug( "doAnimate", "Display time: " + __displayTime );

		this.setCurrentTime( displayTime );

		// If we've finished, snap display time back
		// to the proper place!
		if (__animateTimeElapsed >= __animateTotalTime)
		{
			__isAnimating = false;

			for (var i:String in __graphs)
			{
				__graphs[i].setDisableUpdate( false );
			}

			// Triggers update
			this.setCurrentTime( __animateToTime );
		}

		__lastAnimateFrame = curAnimateFrame;
	}

	// Graph event listeners (i.e. handles events triggered by graphs)
	// ========================================================================

	/**
	 * Called when the user performs a pan on the graph.
	 */
	private function onDrag( drag:Object )
	{
		this.setCurrentTime( __currentTime + drag.timediff );
	}

	/**
	 * Called when the user tries to drill down into a graph.
	 */
	private function onDrillDown( drillDown:Object )
	{
		debug( "onDrillDown", "override me" );
	}

	/**
	 * Called when new statistics are drawn on the graph.
	 */
	private function onDrawStats( drawStatEvent:Object )
	{
		if (drawStatEvent.graphId == __selectedGraphId)
		{
			this.dispatchEvent( drawStatEvent );
		}
	}

	/**
	 * Called when the user selects a graph
	 */
	private function onGraphSelected( graphSelect:Object )
	{
		// Do nothing if the same graph has been "selected"
		if (graphSelect.graphId == __selectedGraphId)
		{
			return;
		}

		__graphs[__selectedGraphId].setSelected( false );
		__selectedGraphId = graphSelect.graphId;

		//debug( "setSelectedGraph",
		//	"Selected graph is " + __graphs[__selectedGraphId].getText() );
		__graphs[__selectedGraphId].setSelected( true );

		dispatchEvent({
			type: "onGraphSelected",
			category: this.getGraphCategory( __selectedGraphId )
		});
	}


	/**
	 * Requests remote data from the server. Do not override this function;
	 * instead, override "makeRemoteRequestByTick".
	 */
	private function onRemoteRequestByTicks( request:Object )
	{
		//debug( "onRemoteRequestByTicks" );

		var startTicks:Array = request.startTicks;
		var endTicks:Array = request.endTicks;
		var category:String = this.getGraphCategory( request.graphId );

		for (var i:Number = 0; i < startTicks.length; ++i)
		{
			var startTick:Number = startTicks[i];
			var endTick:Number = endTicks[i];
			var context:Object = {
				requestId:request.requestId,
				resolution: request.resolution,
				graphId: request.graphId
			};

			this.makeRemoteRequestByTick( context, request.graphId, startTick,
				endTick, request.resolution );
		}
	}

	/**
	 * Requests remote data from the server. Do not override this function;
	 * instead, override "makeRemoteRequestByTime".
	 */
	private function onRemoteRequestByTime( request:Object )
	{
		//debug( "onRemoteRequestByTime" );

		var category:String = this.getGraphCategory( request.graphId );

		var startTime:Number = request.startTime;
		var endTime:Number = request.endTime;
		var context:Object = {
			requestId:	request.requestId,
			resolution:	request.resolution,
			graphId: 	request.graphId
		};

		this.makeRemoteRequestByTime( context, request.graphId, startTime,
			endTime, request.resolution );
	}

	// Generic receive data method
	// ========================================================================

	/**
	 * Event handler for when we receive data from the server
	 */
	private function receiveData( context:Object, stats:Object )
	{


		//debug( "receiveData", "for controller: "
		//	+ __name + ")" );
		//debug( "receiveData",
		//	BWUtils.objectToString( stats.data, 3 ) +
		//	" (" + typeof( stats.data ) + ")" );

		stats.resolution = context.resolution;
		var graph:Graph = __graphs[ context.graphId ];
		graph.receiveRemoteData( context.requestId, stats );

		BWUtils.clearObject( stats );
	}

	// Abstract functions
	// ========================================================================

	/**
	 * Main remote server request function. Requests data from the server
	 * between startTime and endTime. Callback for the remote call should be
	 * set to "receiveData".
	 */
	private function makeRemoteRequestByTime( context:Object, graphId:Number,
		startTime:Number, endTime:Number, resolution:Number )
	{
		debug( "makeRemoteRequestByTime", "Implement me" );
	}

	/**
	 * Main remote server request function. Requests data from the server
	 * between startTick and endTick. Callback for the remote call should be
	 * set to "receiveData".
	 */
	private function makeRemoteRequestByTick( context:Object, graphId:Number,
		startTick:Number, endTick:Number, resolution:Number )
	{
		debug( "makeRemoteRequestByTicks", "Implement me");
	}
}
