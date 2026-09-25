import StatisticData;
import mx.utils.Delegate;
import com.bigworldtech.BWUtils
import com.bigworldtech.misc.SimpleDateFormatter;
//import com.bigworldtech.BWProfiler;

/**
 *	Implements the graph logic behind the drawing, such as storing the
 *	raw values, and handling the making of remote requests.
 */
class Graph extends GraphDrawer
{
	// Class variables
	// ========================================================================
	// Identification
	private var __id:Number;

	// Data storage
	private var __data:StatisticData;

	// Local pref object references
	private var __prefTree:Object;
	private var __displayPrefs:Object;
	private var __category:String;
	private var __lastUpdateTime:Number;

	// Selected statistic id
	private var __selectedStatId:String = null;

	// Optimal number of points that we would like per "viewrange"
	private var __desiredPointsPerView:Number = 20;

	// Current number of processes summarised (corresponds to right hand side)
	private var __showNumSummarised:Boolean;
	private var __numSummarised:Number;

	// Disable updates (used when "smooth scrolling")
	private var __disableUpdates:Boolean = false;

	// Minimum time between updates in milliseconds
	private static var ___minUpdateMillis = 100;

	// Current optimal resolution
	private static var ___optimalResolutionIndex:Number = null;

	// Point marker size, specify null to not draw data points in addition to
	// the data lines
	private static var ___pointMarkerSize:Number = 1;



	// Public methods
	// ========================================================================
	/**
	 *	Constructor. Note that because this
	 *	class is instantiated using attachMovieClip,
	 *	we can't have any constructor parameters.
	 */
	public function Graph()
	{
		super();

		__id = null;
		__lastUpdateTime = null;
		__showNumSummarised = true;

		// Create data statistic classes
		__data = new StatisticData();
		__data.addEventListener("onRemoteRequestByTicks", this);
		__data.addEventListener("onRemoteRequestByTime", this);
		__data.addEventListener("onRemoteRequestByTime", this);
		__data.addEventListener("onRemoteDataArrived", this);
		__data.addEventListener("onDataReady", this);
		__data.addEventListener("onStatSetChanged", this);
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "Graph." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	/**
	 *	Destroy and clean up this movie clip.
	 */
	public function destroy():Void
	{
		this.removeMovieClip();
	}

	/**
	 *	Set the id of the graph. This must be called after
	 *	creating the Graph class.
	 */
	public function setId( id:Number ):Void
	{
		__id = id;
	}

	/**
	 *	Get the id of the graph
	 */
	public function get id():Number
	{
		return __id;
	}

	/**
	 *	Set the preference options of the graph. This must be called after
	 *	creating the Graph class.
	 */
	public function setPreferences( prefTree:Object ):Void
	{
		__prefTree = prefTree;
		__data.setTickInterval( prefTree.tickInterval * 1000 );
	}

	/**
	 *	Set the display preference options of the graph. This must be called
	 *	after creating the Graph class.
	 */
	public function setDisplayPreferences( displayPrefs:Object ):Void
	{
		__displayPrefs = displayPrefs;
	}

	/**
	 *	Set the category of the graph. This must be called after
	 *	creating the Graph class.
	 */
	public function setCategory( category:String ):Void
	{
		__category = category;
	}

	/**
	 *	Set the category of the graph. This must be called after
	 *	creating the Graph class.
	 */
	public function getCategory():String
	{
		return __category;
	}

	/**
	 *
	 */
	public function setDisableUpdates( disableUpdates:Boolean )
	{
		__disableUpdates = disableUpdates;
	}


	/**
	 *	Main updating function.
	 */
	public function update( force:Boolean )
	{
		var now:Number = getTimer();
		if ( force == true || 
			__lastUpdateTime == null || 
			(now - __lastUpdateTime) > ___minUpdateMillis )
		{
			/*if (force)
			{
				debug( "update", "Performing forced update!" );
			}*/

			__lastUpdateTime = now;
			this.rejigCanvases();
			//debug( "update", "Graph " + __id + ": Ending update" );
		}
	}

	/**
	 *	Overridden function from GraphDrawer class.
	 */
	public function setCurrentTime( time:Number )
	{
		super.setCurrentTime( time );

		if (!__disableUpdates)
		{
			// Everytime we exceed 20 times of our current range in data,
			// cull back down to 5 times of our current data.
			__data.cullData( __currentTime - __currentRange / 2,
				5 * __currentRange, 20 * __currentRange );

			this.updateNumSummarised();
		}
	}

	/**
	 *	Overridden function from GraphDrawer class.
	 */
	public function setCurrentRange( range:Number )
	{
		// Void pending requests because it's coming in at a different
		// resolution now.
		if (__currentRange != range)
		{
			__data.voidPendingRequests();
		}

		if (!__disableUpdates)
		{
			var oldRange:Number = __currentRange;

			super.setCurrentRange( range );
			// Clear resolution, because the range has changed and the
			// resolution now needs to be recalculated
			___optimalResolutionIndex = null;

			var cullReferencePoint:Number = __currentTime - __currentRange / 2;
			var minCullThreshold:Number = 5 * __currentRange;
			var maxCullThreshold:Number = 20 * __currentRange;

			var cullLogEndThreshold:Number = null;

			// If we're zooming out, first calculate the new
			// resolution we're going to use. Then chop off the last part
			// of the statistics so that we don't get a weird visual artifact
			// at the end of the log which corresponds to the part of the log
			// that can't be replaced.
			if (__currentRange > oldRange )
			{
				var resolution:Number = this.chooseResolution();

				// Resolutions is in seconds, every other time variable is in
				// milliseconds

				// We cut quite a bit off the end, it's to ensure we don't have
				// high res stats "hanging" off the end of the low resolution
				// stats we're about to retrieve
				var cullLogEnd:Number = __logEndTime - 1000 * (resolution * 2);

				if ((cullReferencePoint + maxCullThreshold) > cullLogEnd )
				{
					cullLogEndThreshold = cullLogEnd - cullReferencePoint;

					/*
					debug( "setCurrentRange: Special culling to " + cullLogEnd + 
						" Threshold: " + cullLogEndThreshold + " Log end is " 
						+ __logEndTime + " Resolution is " + resolution );
					*/
				}
			}

			if (cullLogEndThreshold == null)
			{
				// Standard and most common call
				__data.cullData( cullReferencePoint, minCullThreshold, 
					maxCullThreshold );
			}
			else
			{
				// The four parameter version of cullData is
				// (beforeMinThreshold, beforeMaxThreshold, afterMinThreshold,
				// afterMaxThreshold)
				// Basically we're specifying a hard cut off point corresponding
				// to just before the log end. Only happens when zooming out
				// (see above comment)
				__data.cullData( cullReferencePoint, minCullThreshold, 
					maxCullThreshold, cullLogEndThreshold, cullLogEndThreshold );
			}
		}
	}

	/**
	 *	Forwards received data onto the statistics object.
	 *
	 *	Note: We don't draw lines directly from this data, so leave the line
	 *	drawing to the drawStats method.
	 */
	public function receiveRemoteData( requestId:Number, stats:Object )
	{
		//debug( "receiveRemoteData" );
		// Convert resolution index back into actual resolution before
		// passing it on
		stats.resolution =
			__prefTree.windowPrefs[ stats.resolution ].samplePeriodTicks;
		// Now forward it on!
		__data.receiveRemoteData( requestId, stats );
	}

	/**
	 *	Enables or disables stats.
	 *
	 *	Disabling a stats removes the statistic completely from the stored data.
	 *
	 *	Enabling a stat wipes the entire data and causes a re-request from
	 *	scratch.
	 */
	public function setStatEnabled( statId:String, enabled:Boolean )
	{
		//debug( ".setStatEnabled: " + statId + ": " + enabled );

		//__data.setStatEnabled( statId, enabled );
		__data.clear();
		__data.voidPendingRequests();
		this.clearCanvases();

		//this.redrawAll();
		this.rejigCanvases();
	}

	/**
	 *	Redraws the current graph if a statistic colour has changed.
	 *
	 *	Note that the colour has already been set by the time this
	 *	function has been called, so by this point all we do is
	 *	redraw the lines.
	 *
	 *	(Colour information is stored in the __displayPrefs class member,
	 *	which other objects tend to reference as well.)
	 */
	public function setStatColour( statId:Number, colour:String )
	{
		//debug( "setStatColour", "statId = " + statId +
		//	", colour = " + colour );
		this.redrawAll();
	}

	/**
	 *	Registers the statistic which has been selected from the legend.
	 *
	 *	This causes the selected statistic to be drawn on top and drawn
	 *	twice as thick.
	 */
	public function setSelectedStat( statId:String )
	{
		//debug( "setSelectedStat", statId );

		if (__selectedStatId != statId)
		{
			__selectedStatId = statId;
			this.redrawAll();
		}

		if (statId == null)
		{
			_mcYTickDisplay.setTimeRange( null );
			_mcYTickDisplay.update();
		}
		else
		{
			var statPref:Object = this.getStatPrefs( statId );
			var max:Number = statPref.maxAt;

			_mcYTickDisplay.setTimeRange( max );
			_mcYTickDisplay.update();
		}
	}

	/**
	 *	Returns a vertical slice of the most recent values in the
	 *	current viewing area.
	 *
	 *	Used for getting the data for showing in the legend.
	 *	RForwards request onto StatisticData object.
	 */
	public function getCurrentStats( )
	{
		return __data.getStats( this.getViewStart(),
			this.getViewEnd() );
	}

	/**
	 *	Overriding default setSize function to redraw our graph
	 *	when the size changes.
	 */
	public function setSize( width:Number, height:Number )
	{
		super.setSize( width, height );

		if (__currentTime != undefined && __currentRange != undefined)
		{
			this.redrawAll();
		}
	}

	/**
	 *	Update the graph title with the number of processes/machines summarised
	 */
	public function updateNumSummarised( time:Number )
	{
		if (__showNumSummarised)
		{
			if (time == null) { time = __currentTime; }

			var newNumSummarised = this.getNumSummarised;

			if (newNumSummarised != __numSummarised)
			{
				__numSummarised = this.getNumSummarised();
				this.updateText();
			}
			//debug( "updateNumSummarised", __numSummarised );
		}
	}

	/**
	 * Sets a flag whether a graph should show the number of items summarised
	 * after the title.
	 */
	public function setShowNumSummarised( show:Boolean )
	{
		__showNumSummarised = show;

		this.updateText();
	}

	/**
	 * Gets the current number of summarised items in the view range
	 */
	public function getNumSummarised()
	{
		var numSummarised:Number = __data.getNumSummarised(
				this.getViewStart(), this.getViewEnd() );

		//debug( "getNumSummarised", "Returning " + numSummarised );
		return numSummarised;
	}


	// Private methods
	// ========================================================================

	/**
	 *	Main requesting function.
	 *
	 *	First calls retireUnusedCanvases to free up useless canvases.
	 *	It then makes a request to our data cache (__data) for
	 *	new data to draw to fill up the blank space.
	 */
	private function rejigCanvases()
	{
		//debug( "rejigCanvases", "Starting rejig" );

		if (__currentRange == null || __currentTime == null)
		{
			return;
		}

		var resolution:Number = this.chooseResolution();
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();
		var viewRange:Number = viewEnd - viewStart;

		// extraRange is the "extra" amount which we want to request.
		// i.e. instead of requesting one view width at a time, we're now
		//      requesting three view widths in whatever direction we
		//      need to draw lines.
		var extraRange:Number = viewRange * 2;
		var maxCanvasRange:Number = this.getMaxCanvasRange();

		if (viewStart == null || viewEnd == null)
		{
			return;
		}

		this.retireUnusedCanvases();

		// One constraint we will always keep is that
		// canvases will always be contiguous. Thanks to the retiring step,
		// above, the remaining canvases left are visible on the screen,
		// and at the right resolution.
		//
		// Note that we have only 2 canvases on the screen at a time.
		// This code probably doesn't work with more than 2, nor would we want
		// to have more than 2 anyway.

		if (__canvasInUse.length == 0)
		{
			__data.requestStats( viewStart - extraRange, viewEnd + extraRange,
				resolution, true );
			//debug( "rejigCanvases", "Requesting from scratch. " +
			//	viewStart + "-" + viewEnd );
			return;
		}

		var drawStart:Number = __canvasInUse[0].startTime;
		var drawEnd:Number = __canvasInUse[__canvasInUse.length - 1].endTime;

		if (drawStart <= viewStart && drawEnd >= viewEnd)
		{
			// Current view area is already covered, then don't worry
			//debug( "rejigCanvases", "Not doing anything" );
		}
		else if (drawStart >= viewEnd || drawEnd <= viewStart)
		{
			// We've scrolled all visible areas off the screen?
			this.clearCanvases();
			__data.requestStats( viewStart - extraRange, viewEnd + extraRange,
				resolution );
		}
		else if (drawStart >= viewStart && drawEnd <= viewEnd)
		{
			// zoomed out

			// Re-request everything
			// Mark all as placeholders
			for (var i:Number = 0; i < __canvasInUse[i]; ++i)
			{
				__canvasInUse[i].isPlaceholder = true;
			}
			__data.requestStats( viewStart - extraRange, viewEnd + extraRange,
				resolution );
			//debug( "rejigCanvases", "Super re-request!" );

		}
		else if (drawStart <= viewStart && drawEnd <= viewEnd)
		{
			// pan right
			// Request from drawEnd to viewEnd
			__data.requestStats( drawEnd, viewEnd + extraRange,
				resolution );
			//debug( "rejigCanvases", "Append request!" );
			//debug( "rejigCanvases",
			//	"   Requested " + ((drawEnd + extraRange) - __logEndTime) +
			//	"s past currently known end of log" );
		}
		else if (drawStart >= viewStart && drawEnd >= viewEnd )
		{
			// pan left
			__data.requestStats( viewStart - extraRange, drawStart,
				resolution );
			/*
			debug( "rejigCanvases", "Prepend request!" );
			if (__canvasInUse[0].isPlaceholder)
			{
				debug( "rejigCanvases",
					"   but last canvas is a placeholder!" );
			}
			*/
		}
	}

	/**
	 *	Removes canvases which are:
	 *	- Drawn at a different zoom level
	 *	- Out of view
	 *
	 *	...and moves them back into the canvas pool for later reuse.
	 *
	 *	Called by rejigCanvases.
	 */
	private function retireUnusedCanvases()
	{
		// Do a linear search, we shouldn't have many
		// canvases to check
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();
		var viewRange:Number = viewEnd - viewStart;
		var resolution:Number = this.chooseResolution();

		//debug( "retireUnusedCanvases", "Resolution is: " + resolution );

		var canvasInfo:Object;

		//debug( "retireUnusedCanvases",
		//	"Trying to retire canvases (current view: " +
		//		viewStart + " - " + viewEnd + ")" );

		for (var i:Number = 0; i < __canvasInUse.length; ++i)
		{
			canvasInfo = __canvasInUse[i];

			var canvasRange:Number = canvasInfo.endTime - canvasInfo.startTime;

			// When do we "retire" a canvas?
			// 1) If a canvas is no longer being displayed, or
			// 2) If a canvas was drawn at a different "range" (aka zoom)
			if ((canvasInfo.endTime < viewStart) ||
					(canvasInfo.startTime > viewEnd) ||
					(canvasInfo.drawnAt != __currentRange))
			{
				this.retireCanvas( i );

				/*
				debug( "retireUnusedCanvases",
					"Retiring canvas which starts at " +
					canvasInfo.startTime + " and ends at " +
					canvasInfo.endTime );
				*/

				// retireCanvas actually removes it from the array, so we need
				// to decrement the counter to compensate
				--i;
			}
		}
	}

	/**
	 *	Calculate which resolution we would like to request.
	 *	Of course, there is a likelihood that the resolution
	 *	we request is NOT the same as that we receive.
	 *
	 *	Return value is the actual resolution (i.e. samplePeriodticks),
	 *	and not the resolution window index.
	 *
	 *	TODO: This should be refactored to the GraphDisplay/BaseGraphController
	 *	class.
	 */
	private function chooseResolution():Number
	{
		//debug( "chooseResolution", "__currentRange: " + __currentRange + " logEndTime: " + __logEndTime );

		if (___optimalResolutionIndex == null)
		{
			// Get approximate ticks per viewrange
			var ticksPerRange:Number = __currentRange /
				(__prefTree.tickInterval * 1000);
			var closestWindow:Number = null;
			var closestTickDiff:Number = null;

			for (var i:Number = 0; i < __prefTree.windowPrefs.length; ++i)
			{
				var windowPref:Object = __prefTree.windowPrefs[i];
				//var samples:Number = windowPref.samples;
				var ticksPerSample:Number = windowPref.samplePeriodTicks;

				var pointsPerRange:Number = ticksPerRange / ticksPerSample;

				var tickDiff:Number =
					Math.abs( pointsPerRange - __desiredPointsPerView );


				/*
				debug( "chooseResolution", "Checking resolution: " +
					ticksPerSample + " ticks per sample" );
				debug( "chooseResolution", " - points per viewrange: " +
					pointsPerRange );
				debug( "chooseResolution", " - tickDiff: " + tickDiff );
				*/


				if (closestWindow == null || tickDiff < closestTickDiff)
				{
					closestWindow = i;
					closestTickDiff = tickDiff;
				}
			}

			var res:Number =
				__prefTree.windowPrefs[closestWindow].samplePeriodTicks;

			___optimalResolutionIndex = closestWindow;

			/*
			var optimalPref:Object =
				__prefTree.windowPrefs[___optimalResolutionIndex];
			var samplePeriodTicks:Number = optimalPref.samplePeriodTicks;
			debug( "chooseResolution", this + ": window " +
				___optimalResolutionIndex +
				", " + samplePeriodTicks + " SPT" );
			*/
		}

		var tickInterval:Number = __prefTree.tickInterval;
		var viewStart:Number = this.getViewStart();
		var windowId:Number = null;

		// Check distance from log end (long term data is stored
		// at lower resolutions)
		if (__logEndTime != undefined)
		{
			for (	var i:Number = ___optimalResolutionIndex;
					i < __prefTree.windowPrefs.length;
					++i)
			{
				var windowPref:Object = __prefTree.windowPrefs[i];

				// Make a very close guess to how far back the resolution covers
				var windowStart:Number = __logEndTime -
					(windowPref.samples * windowPref.samplePeriodTicks *
						tickInterval * 1000);

				/*
				debug( "chooseResolution", "i: " + i +
					", logEndTime: " + __logEndTime
					+ " windowPref.samples: " + windowPref.samples
					+ " windowPref.samplePeriodTicks: " +
						windowPref.samplePeriodTicks
					+ " tickInterval: " + tickInterval);

				debug( "chooseResolution: Window start for " +
					windowPref.samplePeriodTicks + " is: " + windowStart );
				*/

				if (windowStart < viewStart)
				{
					//debug( "chooseResolution",
					//	"  This window is good, we can use this" );
					windowId = i;
					break;
				}
				else
				{
					//debug( "chooseResolution", "  Can't use this, it starts " +
					//	(windowStart - viewStart) + "s too early");
				}
			}

			if (windowId == null)
			{
				windowId = __prefTree.windowPrefs.length - 1;
			}
		}
		else
		{
			windowId = ___optimalResolutionIndex;
		}



		var windowPref = __prefTree.windowPrefs[windowId];
		var res = windowPref.samplePeriodTicks;

		dispatchEvent( {
			type:				"onChooseResolution",
			windowIndex:		windowId,
			windowSampleTime:	windowPref.samplePeriodTicks *
									__prefTree.tickInterval * 1000,
			windowSampleTicks:	windowPref.samplePeriodTicks
		} );

		//debug( "chooseResolution", "windowId = " + windowId );
		//debug( "chooseResolution",  res );
		return res;
	}

	/**
	 *	Given a samplePeriodTicks value, look up the index in
	 *	prefTree.windowPrefs which pertains to that value.
	 */
	private function reverseResolutionLookup(resolution:Number):Number
	{
		for (var i:Number = 0; i < __prefTree.windowPrefs.length; ++i)
		{
			if (__prefTree.windowPrefs[i].samplePeriodTicks == resolution)
			{
				return i;
			}
		}

		//debug( "reverseResolutionLookup", "Resolution " + resolution +
		//	" not found." );
	}

	/**
	 *	Given a time range, return whether any portion of the time range is
	 *	currently being viewed.
	 */
	private function timeRangeInView( startTime:Number, endTime:Number ):Boolean
	{
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();

		if (startTime >= viewEnd || endTime <= viewStart)
		{
			return false;
		}

		return true;
	}

	/**
	 *	Refresh the graph title (including number of machines/processes
	 *	summarised.
	 */
	private function updateText()
	{
		if (__showNumSummarised)
		{
			if (__numSummarised == undefined)
			{
				_mcText.text = __text + " [None]";
			}
			else
			{
				_mcText.text = __text + " [" + __numSummarised + "]";
			}
		}
		else
		{
			_mcText.text = __text;
		}
	}

	/**
	 *	Returns an ordered array of statistic preference ids relevant to
	 *	this graph.
	 */
	public function getStatOrder():Array
	{
		if (__category == "machine")
		{
			return __displayPrefs["enabledMachineStatOrder"];
		}
		else
		{
			return __displayPrefs["enabledProcStatOrder"][__category];
		}
	}

	/**
	 *	Given a statistic id, returns the statistic preference relevant
	 *	to this graph.
	 */
	public function getStatPrefs( statId:String ):Object
	{
		if (__category == "machine")
		{
			var machinePrefs:Object = __prefTree.machineStatPrefs[statId];
			return machinePrefs;
		}
		return __prefTree.procPrefs[__category].statPrefs[statId];
	}

	/**
	 *	Given a statistic id, returns statistic display preferences relevant
	 *	to this graph.
	 */
	public function getStatDisplayPrefs( statId:String ):Object
	{
		if (__category == "machine")
		{
			return __displayPrefs.machineStatPrefs[statId];
		}
		return __displayPrefs.procPrefs[__category][statId];
	}

	// Drawing methods
	// ========================================================================
	/**
	 *	Redraws the current view.
	 *
	 *	Used for certain scenarios, such as changing colours.
	 */
	private function redrawAll()
	{
		this.clearCanvases();
		this.rejigCanvases();
	}

	/**
	 *	We've now got the statistics that we want to draw on a canvas.
	 *	So draw it!
	 */
	private function drawStats( stats:Object )
	{
		//debug( "drawStats", "Number of elements: " + stats.times.length );
		//BWUtils.printObject( stats.data, 3 );

		var desiredResolution:Number = this.chooseResolution();

		// Maximum distance between points
		var maxPointSeparation:Number = 10
		var maxDistance:Number = desiredResolution * 
			__prefTree.tickInterval * maxPointSeparation * 1000;

		var startTime:Number = stats.times[0];
		var endTime:Number = stats.times[stats.times.length - 1];
		var resolution:Number = stats.resolution;
		var isPlaceholder:Boolean = stats.isPlaceholder;

		// Create movieclip to draw oassign
		var canvasId:Number = this.assignCanvas( startTime, endTime,
			resolution, isPlaceholder );

		// TEST CODE
		/*
		var canvas:MovieClip = __canvasInUse[canvasId].mc;
		var rightSide:Number = ((endTime - startTime) / __currentRange) *
			__drawAreaWidth;
		//debug( "drawStats", "Canvas is: " + canvas );
		canvas.beginFill(0xFF00FF, 10);
		canvas.lineStyle(2, 0x0000FF);
		canvas.moveTo(0,0);
		canvas.lineTo(0,__drawAreaHeight);

		canvas.lineStyle(null);
		canvas.lineTo(rightSide, __drawAreaHeight);
		canvas.lineStyle(2, 0xFF0000);
		canvas.lineTo(rightSide, 0);
		canvas.endFill();
		return;
		*/

		// Now, start the loop
		var times:Array = stats.times;
		var statDict:Object = stats.data;

		// Some vars to declare first
		var colour:Number = null;
		var thickness:Number;
		var max:Number;
		var markerSize:Number = ___pointMarkerSize;

		//debug( "drawStats", "Category: " + __category );
		//debug( "drawStats", "Selected stat: " + __selectedStatId );

		if (!BWUtils.assert(__displayPrefs != null, "Display prefs is null"))
		{
			return;
		}

		// Get stat order to draw bottom(last stat) to top (first stat), plus
		// the selected stat on very top
		var statOrder:Array = this.getStatOrder();
		var statDrawOrder:Array = new Array();

		// Reconstruct the draw order of stats for us to draw
		for (var i:Number = statOrder.length - 1; i >= 0; --i)
		{
			var statId:String = statOrder[i];
			if (statId != __selectedStatId)
			{
				statDrawOrder.push( statId );
			}
		}

		// Add our selected stat to the end (if we have one)
		if (__selectedStatId != null)
		{
			statDrawOrder.push( __selectedStatId );
		}

		// Draw stats
		for (var i:Number = 0; i < statDrawOrder.length; ++i)
		{
			var statId:String = statDrawOrder[i];

			//debug( "drawStats", "statId = " + statId );
			var statPrefs:Object = this.getStatPrefs( statId );
			var statDisplayPrefs:Object = this.getStatDisplayPrefs( statId );

			colour = parseInt( "0x" + statDisplayPrefs.colour );
			max = statPrefs.maxAt;
			thickness = 2;

			if (statId == __selectedStatId)
			{
				thickness = 4;
			}

			this.drawCanvasLine( canvasId, times, statDict[statId],
				max, statId, colour, thickness, markerSize, maxDistance );
		}

	}



	// Interaction handlers
	// ========================================================================

	/**
	 *	Handle double click event.
	 */
	private function onLineMaskDoubleClick()
	{
		this.dispatchEvent({
			type: "onDrillDown",
			graphId: __id
		})
	}

	// Event handlers
	// ========================================================================

	/**
	 *	Propagate remote server requests upwards from our StatisticData object.
	 *
	 *	We massage some of the variables passed upwards since the StatisticData
	 *	object isn't fully aware of some data such as id of the graph it's
	 *	attached to.
	 */
	private function onRemoteRequestByTime( eventObj:Object )
	{
		// Transform resolution back by looking up actual resolution with
		// the index containing that value
		eventObj.resolution =
			this.reverseResolutionLookup( eventObj.resolution );

		// Attach our id to the event object
		eventObj.graphId = __id;

		//this.makeRemoteRequestByTime( eventObj.startTime,
		//	eventObj.endTime, eventObj.resolution );

		// Propagate request upwards
		this.dispatchEvent( eventObj );
	}

	/**
	 *	Propagate remote server requests upwards from our StatisticData object.
	 *
	 *	We massage some of the variables passed upwards since the StatisticData
	 *	object isn't fully aware of some data such as id of the graph it's
	 *	attached to.
	 */
	private function onRemoteRequestByTicks( eventObj:Object )
	{
		eventObj.resolution =
			this.reverseResolutionLookup( eventObj.resolution );

		// Attach our id to the event object
		eventObj.graphId = __id;

		//this.makeRemoteRequestByTicks( eventObj.startTicks,
		//	eventObj.endTicks, eventObj.resolution );

		// Propagate request upwards
		this.dispatchEvent( eventObj );
	}

	/**
	 *	Event handler for when our data cache delivers data to us to draw.
	 */
	private function onDataReady( eventObj:Object )
	{
		//BWProfiler.begin("onDataReady");
		var stats:Object = eventObj.stats;
		var startTime:Number = stats.times[0];
		var endTime:Number = stats.times[stats.times.length - 1];

		if (this.timeRangeInView( startTime, endTime ))
		{
			this.drawStats( stats );

			// Perform actions upon drawing new lines on the graph
			// This usually entails updating the legend as well as
			// updating the graph title with the number of processes
			// summarised.
			this.updateNumSummarised();
			this.dispatchEvent({
				type: "onDrawStats",
				graphId: __id
			});
			// TODO: Dispatch event
			//this.dispatchEvent();
		}
		else
		{
			debug( "onDataReady", "Not drawing stats as it's off the screen.");
		}

		//BWProfiler.end( "onDataReady" );
	}

	/**
	 *	Event handler for when our data cache receives remote data.
	 */
	private function onRemoteDataArrived( eventObj:Object )
	{
		//debug( "onRemoteDataArrived" );
		//BWProfiler.begin("onRemoteDataArrived");
		var startTime:Number = eventObj.startTime;
		var endTime:Number = eventObj.endTime;
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();
		var requestId:Number = eventObj.requestId;

		//if (this.timeRangeInView( startTime, endTime ))
		if (true)
		{
			var resolution:Number = this.chooseResolution();

			this.clearCanvases();

			// Add small buffer on either side to make sure we fill the window
			__data.grabAndSendData(
				viewStart - resolution,
				viewEnd + resolution * 2,
				resolution, false );
		}
		else
		{
			/*
			debug( "onRemoteDataArrived", "Data is not in time range" );
			debug( "onRemoteDataArrived", "  Our view: " +
				viewStart + "-" + viewEnd +
				", Data time range: " + startTime + "-" + endTime +
				" Number of elements: " + eventObj.numElements );
			*/
		}
		//BWProfiler.end( "onRemoteDataArrived" );
	}

	/**
	 *	Event handler for when the statistic set being received
	 *	from remote requests change.
	 */
	private function onStatSetChanged( eventObj:Object )
	{
		var newStats:Array = eventObj.newStats;
		var removedStats:Array = eventObj.removedStats;

		//debug( "onStatSetChanged", + newStats.length + " new stats, " +
		//	removedStats.length + " deleted stats." );
	}


	/**
	 *	Set the desired points per view.
	 */
	public function setDesiredPointsPerView( numPoints:Number ):Void
	{
		__desiredPointsPerView = numPoints;
	}
}
