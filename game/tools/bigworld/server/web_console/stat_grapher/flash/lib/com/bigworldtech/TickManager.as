import com.bigworldtech.misc.SimpleDateFormatter;
import com.bigworldtech.BWUtils;
import com.bigworldtech.BWMemoize;
//import com.bigworldtech.BWProfiler;

/**
 * Abstract base class which represents a tick manager.
 * Provides functionality to handle time related ticks.
 *
 * Will need to override key functions in order to adapt
 * for use with other types of ticks (e.g. raw statistic
 * values).
 */

class com.bigworldtech.TickManager extends MovieClip
{
	// Array to hold the tick movieclips (e.g. "20 Dec 2006")
	private var __ticks:Array = null;
	private var __oldTicks:Array = null;
	private var __nextTickId:Number = 0;

	// There is a small difference between displayTime and
	// currentTime. currentTime is used in internal logic
	// while displayTime is the actual value used for displaying
	// the ticks. In short:
	// __currentTime = time that the user wants to view
	// __displayTime = time that we're currently viewing
	//
	// This allows us to have a sort of animation effect
	// happening (e.g. scroll from current time to another time)
	// although currently there isn't any animation
	// effects used anywhere. So in 99% of cases __displayTime
	// and __currentTime will be the same.
	private var __currentTime:Number = null;
	private var __displayTime:Number = null;

	// Current range over which we're viewing graphs
	private var __currentRange:Number = null;

	// Tick area length is the pixel length of the area
	// for which we can draw ticks
	private var __tickAreaLength:Number = null;

	// Array of resolution formats
	private var __resolutions:Array = null;
	private var __timeIntervals:Object = null;
	private var __isIntervalRegular:Object = null;

	// Minimum distance (in pixels) between ticks
	// In order to choose the resolution for the ticks,
	// we find the smallest resolution which does NOT
	// exceed the tick resolution.
	private var __minimumPixelDistance:Number = null;

	// A lock variable which prevents more than update()
	// method from being called at a time.
	private var __inUpdate:Boolean = false;

	// Array of tick movieclips which we're keeping around
	// so we don't have to create new ones all the time.
	private var __recycleBin:Array = null;
	private var __recycleBinMax:Number = null;

	private var memoizeCheck:Function;
	private var memoizeStore:Function;
	private var memoizeValue:Function;
	private var memoizeClear:Function;

	/**
	 *	Constructor for the class TickManager
	 */
	public function TickManager()
	{
		__ticks = new Array();
		__recycleBin = new Array();
		__recycleBinMax = 5;
		__minimumPixelDistance = 50;

		this.setupResolutions();
		this.setupIntervalInformation();
		this.optimiseResolutions();

		BWMemoize.initialise( this );
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "TickManager." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	/**
	 *	These two functions are the main functions which determine
	 *	the TOTAL display range of the graph.
	 */
	private function getLeftMostDisplayTime():Number
	{
		debug( "getLeftMostDisplayTime", "not implemented" );
		return null;
	}

	private function getRightMostDisplayTime():Number
	{
		debug( "getRightMostDisplayTime", "not implemented" );
		return null;
	}

	/**
	 *	Create the resolution scheme list, which represents
	 *	the possible tick display schemes we can use.
	 *
	 *	Each scheme is an object with the following attributes:
	 *	majorInt:		Major tick intervals
	 *	majorMul:		Major tick multiple to align to
	 *	(e.g. 3 for every 3rd)
	 *	majorFormat:		Text format of every major tick
	 *	minorInt:		Minor tick interval
	 *	minorMul:    	Minor tick multiple
	 *	minorrFormat:	Text format of every minor tick
	 *
	 *	For information on time formatting, see
	 *	SimpleDateFormatter.formatDate for information
	 *
	 *	Note that since months are not consistent lengths, distances
	 *	between ticks may not be equivalent.
	 *
	 *	Notes for the multiplier argument:
	 *	Use when you want ticks to happen at regular intervals rather than
	 *	every interval.
	 *	e.g. For a tick every 10 minutes
	 *	majorInt: "minute", majorMul: 10
	 *
	 *
	 *	Day multiples (will always snap to month - e.g. if you have a day
	 *	multiplier of 7, and a tick occurs at March 28, the next tick
	 *	will occur at Apr 1 instead of Apr 4)
	 */
	private function setupResolutions():Void
	{
		__resolutions =
		[
			{majorInt: "minute", majorMul: 1, majorFormat: "H:mm:ss",
				minorInt: "second", minorMul: 2, minorFormat: "ss"},
			{majorInt: "minute", majorMul: 1, majorFormat: "H:mm:ss",
				minorInt: "second", minorMul: 10, minorFormat: "ss"},
			{majorInt: "minute", majorMul: 1, majorFormat: "H:mm:ss",
				minorInt: "second", minorMul: 30, minorFormat: "ss"},
			{majorInt: "minute", majorMul: 5, majorFormat: "H:mm",
				minorInt: "minute", minorMul: 1, minorFormat: "mm"},
			{majorInt: "minute", majorMul: 15, majorFormat: "H:mm",
				minorInt: "minute", minorMul: 5, minorFormat: "mm"},
			{majorInt: "hour", majorMul: 1, majorFormat: "H",
				minorInt: "minute", minorMul: 30, minorFormat: "mm"},
			{majorInt: "day", majorMul: 1, majorFormat: "E NNN d",
				minorInt: "hour", minorMul: 1, minorFormat: "H"},
			{majorInt: "day", majorMul: 1, majorFormat: "E NNN d",
				minorInt: "hour", minorMul: 2, minorFormat: "H"},
			{majorInt: "day", majorMul: 1, majorFormat: "E NNN d",
				minorInt: "hour", minorMul: 12, minorFormat: "H"},
			{majorInt: "day", majorMul: 7, majorFormat: "NNN d",
				minorInt: "day", minorMul: 1, minorFormat: "d"},
			{majorInt: "month", majorMul: 1, majorFormat: "NNN",
				minorInt: "day", minorMul: 7, minorFormat: "d"},
			{majorInt: "year", majorMul: 1, majorFormat: "yyyy",
				minorInt: "month", minorMul: 1, minorFormat: "NNN"}
		]
	}

	/**
	 *	Setup general interval information which can be used by other functions
	 *	for various reasons.
	 */
	private function setupIntervalInformation():Void
	{
		// Setup values we can use to estimate the rough length of a
		// interval type. The reason is because that some time intervals
		// don't have a constant length and we need a value to roughly
		// estimate it.
		__timeIntervals =
		{
			second: 	1000,
			minute: 	1000 * 60,
			hour: 		1000 * 3600,
			day: 		1000 * 3600 * 24,
			month: 		1000 * 3600 * 24 * 30.5,
			year: 		1000 * 3600 * 24 * 365
		};

		// This dictionary lets us know if the interval type is a fixed length
		// or not.
		// e.g. Months are variable length(30, 31, 28 or 29 days long)
		__isIntervalRegular =
		{
			second: 	true,
			minute: 	true,
			hour: 		true,
			day: 		true,
			month: 		false,
			year: 		false
		}
	}

	/**
	 *	Optimise minor tick resolution table by converting interval types which
	 *	are regular into the equivalent number of seconds.

	 *	Don't convert major ticks because the tick position calculation
	 *	sometimes has special behaviour for interval types specified as
	 *	strings.
	 */
	private function optimiseResolutions():Void
	{
		for (var i:Number = 0; i < __resolutions.length; ++i)
		{
			var resolutionInfo = __resolutions[i];
			if (typeof(resolutionInfo.minorInt) == "string")
			{
				if (__isIntervalRegular[resolutionInfo.minorInt] == true)
				{
					//debug( "optimiseResolutions",
					//	"Converting " + resolutionInfo.minorInt +
					//	" into number");
					resolutionInfo.minorInt =
						__timeIntervals[resolutionInfo.minorInt];
				}
			}
		}
	}

	/**
	 *	Choose which tick resolution to use.
	 */
	public function chooseTickResolution():Object
	{
		if (this.memoizeCheck( "chooseTickResolution", 
				"__currentRange", "__tickAreaLength" ))
		{
			return this.memoizeValue( "chooseTickResolution" );
		}

		// Factors used in choosing the resolution:
		// - Pixel width of the ruler
		// - Viewrange
		// - And generally, the distance between ticks

		var leftMostDisplayTime:Number = this.getLeftMostDisplayTime();
		var rightMostDisplayTime:Number = this.getRightMostDisplayTime();

		// Yes, we could probably just use __currentRange * 3
		// but this way puts all the dependency on the
		// leftMostDisplayTime and rightMostDisplayTime functions,
		// making it easy to change total range at any point
		// in time.
		var totalRange = rightMostDisplayTime - leftMostDisplayTime;
		//debug( "chooseTickResolution", "Total range: " + totalRange +
		//	" Width: " + __tickAreaLength);

		var currentResolution:Object;

		// Check the pixel distance for each resolution
		for (var i:Number = 0; i < __resolutions.length; ++i)
		{
			currentResolution = __resolutions[i];
			var timeDistance:Number;

			if (typeof(currentResolution.minorInt) == "string")
			{
				timeDistance = __timeIntervals[currentResolution.minorInt] *
					currentResolution.minorMul;
			}
			else
			{
				timeDistance = currentResolution.minorInt *
					currentResolution.minorMul;
			}

			var pixelDistance = __tickAreaLength / (totalRange / timeDistance);

			//debug( "chooseTickResolution",
			//	"Pixel distance for " + timeDistance + "s is: " +
			//	pixelDistance );

			if (pixelDistance > __minimumPixelDistance)
			{
				break;
			}
		}

		this.memoizeStore( "chooseTickResolution", "__currentRange", 
			"__tickAreaLength", currentResolution );

		return currentResolution;
	}

	/**
	 *	Set the time range for which we're viewing the graph.
	 *	Note: This is NOT the time range of the ruler! This is
	 *	the range of the graphs we're viewing.
	 */
	public function setTimeRange( currentRange:Number ):Void
	{
		__currentRange = currentRange;
		this.update();
	}

	public function getTimeRange():Number
	{
		return __currentRange;
	}

	/**
	 *	Set the current time to display
	 *	Note that the current time corresponds to the right edge
	 *	of the ruler.
	 */
	public function setCurrentTime( currentTime:Number ):Void
	{
		__currentTime = currentTime;
		__displayTime = currentTime;
		this.update();
	}

	public function getCurrentTime():Number
	{
		return __currentTime;
	}

	/**
	 *	This function is not used, except for debugging. Basically removes
	 *	all ticks, both from movieclip and from our info list.
	 */
	public function clearTicks():Void
	{
		while (__ticks.length)
		{
			var tickHolder:Object = __ticks.shift();
			tickHolder.mc.kill();

			// Wipe all references from tick holder object
			for (var key:String in tickHolder)
			{
				delete tickHolder[key];
			}
		}
	}

	/**
	 *	Create the tick movieclip. Tickid is a unique number that
	 *	should be used to give the tick movieclip a unique name.
	 *
	 *	This function works with movieclips and is not implemented in
	 *	the base class.
	 */
	public function createTickMC( tickId:Number ):MovieClip
	{
		debug( "createTickMC", "Not implemented" );
		return null;
	}

	/**
	 *	Position the tick movieclip.
	 *	This function works with movieclips and is not implemented in
	 *	the base class.
	 */
	public function positionTickMC( tickMC:MovieClip, targetValue:Number):Void
	{
		debug( "positionTickMC", "Not implemented" );
	}

	/**
	 *
	 */
	public function setTickMCIsMajor( tickMC:MovieClip, isMajor:Boolean ):Void
	{
		debug( "setTickIsMajor", "Not implemented" );

	}

	/**
	 *
	 */
	public function setTickMCFormat( tickMC:MovieClip, timestamp:Number,
			format:String ):Void
	{
		debug( "setTickFormat", "Not implemented" );
	}

	/**
	 *	Tries to match up parameters to an existing tick, if unsuccessful then
	 *	we create a new one.
	 */
	public function setTick( timestamp:Number, format:Object,
			isMajor:Boolean ):Void
	{
		//debug("setTick", "    Setting tick " + timestamp );

		//BWProfiler.begin( "binarySearch" );
		var searchObject:Object = new Object();
		searchObject.time = timestamp;

		var searchIndex:Number = BWUtils.binarySearchOnAttribute( __oldTicks,
			"time", searchObject );
		delete searchObject;
		//BWProfiler.end( "binarySearch" );

		if (searchIndex != null)
		{
			//debug( "setTick", "    Found tick " + timestamp );

			var tickHolder:Object = __oldTicks[searchIndex];
			if (tickHolder.time == timestamp and tickHolder.format == format)
			{
				// Set the tick position. Don't need to set text
				// (3rd parameter of the positionTickMC
				// function), since we keep the tick's setting.
				// BWProfiler.begin( "positionTickMC" );
				this.positionTickMC( tickHolder.mc, timestamp, null, isMajor );
				// BWProfiler.end( "positionTickMC" );

				// Move tick object into the current tick list, since we're
				// recycling it
				//BWProfiler.begin( "insertIntoTickList" );
				this.insertIntoTickList( tickHolder, __ticks );
				//BWProfiler.end( "insertIntoTickList" );

				// Remove it from the old list
				//BWProfiler.begin( "removeFromTickList" );
				__oldTicks.splice( searchIndex, 1 );
				//BWProfiler.end( "removeFromTickList" );
				// We're done here
				return;
			}
		}
		else
		{
			//debug( "setTick", "    Didn't find tick " +
			//	timestamp );
		}

		// If we're here, then we haven't found an appropriate tick
		//BWProfiler.begin( "createTick" );
		createTick( timestamp, format, isMajor );
		//BWProfiler.end( "createTick" );
	}

	/**
	 *	Creates and positions a tick at the given time interval.
	 */
	public function createTick( targetTime:Number, format:Object,
			isMajor:Boolean ):Void
	{
		//BWProfiler.begin( "createTickInternal" );

		//debug( "createTick", "Creating tick at " + targetTime + " for " +
		//	this );

		var tickHolder:Object;

		if (__recycleBin.length > 0)
		{
			//debug( "createTick", "Recycling movie clip" );
			tickHolder = __recycleBin.shift();
			tickHolder.mc._visible = true;
		}
		else
		{
			//debug( "createTick", "Creating movie clip" );
			// Create tick movieclip
			var tickId:Number = __nextTickId++;
			//BWProfiler.begin( "createTickMC" );
			var tickMC:MovieClip = createTickMC( tickId );
			//BWProfiler.end( "createTickMC" );
			// Record information about this tick in our ordered list
			tickHolder = new Object();
			tickHolder.mc = tickMC;
		}

		tickHolder.time = targetTime;
		tickHolder.format = format;
		//BWProfiler.begin( "insertIntoTickList" );
		this.insertIntoTickList( tickHolder, __ticks );
		//BWProfiler.end( "insertIntoTickList" );

		//BWProfiler.begin( "stupidtest" );
		//BWProfiler.end( "stupidtest" );

		// Position the tick
		//BWProfiler.begin( "positionTickMC" );
		this.setTickMCFormat( tickHolder.mc, tickHolder.time,
			tickHolder.format );
		this.setTickMCIsMajor( tickHolder.mc, isMajor );
		this.positionTickMC( tickHolder.mc, targetTime );
		//BWProfiler.end( "positionTickMC" );

		//BWProfiler.end( "createTickInternal" );
	}

	/**
	 *	Ordered insert of tick information into our tick list
	 */
	public function insertIntoTickList( tickHolder:Object, tickList:Array ):Void
	{
		// New assumption, we always create tick list from lowest to highest
		// according to the update() function
		if (tickList[tickList.length - 1].time == tickHolder.time)
		{
			debug( "insertIntoTickList", "ERROR: " +
				"Two ticks at the same time: " + tickHolder.time );
		}
		else if (tickList[tickList.length - 1].time > tickHolder.time)
		{
			debug( "insertIntoTickList", "ERROR: " +
				"Out of order tick insertion: " + tickHolder.time );
		}
		else
		{
			tickList.push( tickHolder );
		}
	}

	private static function tickListToString( tickList:Array ):String
	{
		var out:String = '';
		for (var i:Number = 0; i < tickList.length; ++i)
		{
			var tickHolder:Object = tickList[i];
			var tickHolderDesc:String = i + ": " + tickHolder.mc +
				" : " + tickHolder.time;

			if (out == '')
			{
				out = tickHolderDesc;
			}
			else
			{
				out += ", " + tickHolderDesc;
			}
		}
		return "[" + out + "]";
	}

	/**
	 *	MAIN FUNCTION
	 *	This is the function which creates and positions (or repositions)
	 *	the ticks when any of the following states change:
	 *	- Current time
	 *	- Current view range
	 *	- Resized
	 */
	public function update( ):Void
	{
		//debug( "update" );

		if (__inUpdate)
		{
			return;
		}

		if (__currentTime == null)
		{
			return;
		}

		if (__currentRange == null)
		{
			return;
		}

		if (this.memoizeCheck( "update", "__currentTime", "__currentRange", "__tickAreaLength" ))
		{
			return;
		}

		//debug( "update" , "Going...Time: " +
		//	__currentTime + "@" + __currentRange + " for " + this );
		//this.printTicks();

		//BWProfiler.begin("update");

		// Create a new list
		//BWProfiler.begin("init");
		__oldTicks = __ticks;
		__ticks = new Array();
		__inUpdate = true;
		//BWProfiler.end("init");

		//BWProfiler.begin( "chooseTickResolution" );
		var resolutionInfo:Object = this.chooseTickResolution();
		//BWProfiler.end( "chooseTickResolution" );

		//BWProfiler.begin("extractResInfo");
		// Major interval (must be string e.g. "minute", "hour)
		var majorInt:String = resolutionInfo.majorInt;

		// Major multiplier (e.g. 3 for every 3rd hour, and so on)
		var majorMul:Number = resolutionInfo.majorMul;

		// Major tick format
		var majorFormat:String = resolutionInfo.majorFormat;

		// Minor interval (can be either number in seconds or string)
		var minorInt:Object = resolutionInfo.minorInt;

		// Minor multiplier (e.g. 3 for every 3rd hour)
		var minorMul:Number = resolutionInfo.minorMul;

		// Minor tick format
		var minorFormat:String = resolutionInfo.minorFormat;

		// Check what type the minor interval is
		var isMinorNumber:Boolean = (typeof(minorInt) == "number");
		//BWProfiler.end("extractResInfo");

		//debug( "update", "Is minorint " + minorInt + " a number: " +
		//	isMinorNumber );

		// Calculate aligned times to start drawing ticks from

		// Note that the display time corresponds to 2/3 along the ruler.
		// The ruler spans 3 * currentRange
		//BWProfiler.begin( "getDisplayTimes" );
		var leftMostDisplayTime:Number = this.getLeftMostDisplayTime();
		var rightMostDisplayTime:Number = this.getRightMostDisplayTime();
		//BWProfiler.end( "getDisplayTimes" );

		//BWProfiler.begin( "alignTimestamps" );
		var startMajorAlign:Number = this.alignTimestamp( leftMostDisplayTime,
				majorInt, majorMul );

		var nextMajorAlign:Number =
			this.alignTimestamp( leftMostDisplayTime, majorInt, majorMul, true );

		// Get the tick on or before the current time
		// TODO: Actually calculate up to the point before the current time
		var testTickTime:Number = startMajorAlign;
		var currentTickTime:Number = startMajorAlign;

		if (minorInt != null)
		{
			while (testTickTime < leftMostDisplayTime)
			{
				currentTickTime = testTickTime;
				//testTickTime = this.alignTimestamp( testTickTime,
				//	minorInt, minorMul, true );
				if (isMinorNumber)
				{
					testTickTime += Number(minorInt) * minorMul;
				}
				else
				{
					testTickTime = this.alignTimestamp(
						testTickTime, String(minorInt), minorMul, true );
				}
			}
		}
		//BWProfiler.end( "alignTimestamps" );

		//debug( "update", "Starting from " + currentTickTime +
		//	": Discrepancy of "+ (leftMostDisplayTime - currentTickTime) );

		//debug( "update", "minorInt is " + minorInt +
		//	", minorMul is " + minorMul );

		// Now start iterating from there
		//BWProfiler.begin( "tickLoop" );

		var seenTicks:Object = new Object();
		var iterations;

		while (currentTickTime < rightMostDisplayTime)
		{
			//debug( "update", "Current time is " + currentTickTime );

			//BWProfiler.begin( "setTick" );
			if (currentTickTime == startMajorAlign)
			{
				this.setTick( currentTickTime, majorFormat, true );
			}
			else
			{
				this.setTick( currentTickTime, minorFormat, false );
			}
			//BWProfiler.end( "setTick" );

			//BWProfiler.begin( "alignTimestamps" );
			if (minorInt != null)
			{
				//debug( "update", "Doing minor align" );
				if (isMinorNumber)
				{
					//debug( "update", "Adding " +
					//	(Number(minorInt) * minorMul) +
					//	" to currentTime (minorInt)" );
					currentTickTime += Number(minorInt) * minorMul;
				}
				else
				{
					currentTickTime = this.alignTimestamp(
						currentTickTime, String(minorInt), minorMul, true );
				}

				if (currentTickTime >= nextMajorAlign)
				{
					startMajorAlign = nextMajorAlign;
					nextMajorAlign = this.alignTimestamp(
							nextMajorAlign, majorInt, majorMul, true );
					currentTickTime = startMajorAlign;
				}

			}
			else
			{
				//debug( "update", "Doing major align" );
				startMajorAlign = nextMajorAlign;
				nextMajorAlign = this.alignTimestamp(
					nextMajorAlign, majorInt, majorMul, true );
				currentTickTime = startMajorAlign;
			}


			// Make sure we don't get stuck in an infinite loop
			if (seenTicks[currentTickTime] != null)
			{
				debug( "ERROR: Repeating a previously seen tick, aborting. " +
					"Vars:" + 
					"\n  MajorInt: " + majorInt + " MajorMul: " + majorMul + " MajorFormat: " + majorFormat + 
					"\n  MinorInt: " + minorInt + " MinorMul: " + minorMul + " MinorFormat: " + minorFormat +
					"\n  currentTickTime: " + currentTickTime );

				break;
			}

			seenTicks[currentTickTime] = true;

			// Update loop counter (used to check we don't loop over 500 times
			// which is an indication of an infinite loop)
			if (++iterations > 500)
			{
				debug( "ERROR: Loop went for 500 iterations for some reason, aborting. " +
					"Vars:" + 
					"\n  MajorInt: " + majorInt + " MajorMul: " + majorMul + " MajorFormat: " + majorFormat + 
					"\n  MinorInt: " + minorInt + " MinorMul: " + minorMul + " MinorFormat: " + minorFormat +
					"\n  currentTickTime: " + currentTickTime );
				break;
			}

			//BWProfiler.end( "alignTimestamps" );
		}
		//BWProfiler.end( "tickLoop" );

		// To finish up, clean the old unused ticks
		//BWProfiler.begin( "Cleanup" );
		while (__oldTicks.length)
		{
			var tickHolder:Object = __oldTicks.shift();
			this.moveToRecycleBin( tickHolder );
		}
		//BWProfiler.end( "Cleanup" );

		__oldTicks = null;
		__inUpdate = false;

		// Null value since this function doesn't have a return value
		this.memoizeStore( "update", "__currentTime", "__currentRange", "__tickAreaLength", null );

		//debug( "update", "End with " + __ticks.length + " ticks" );
		//printTicks();
		//BWProfiler.end("update");
	}

	/**
	 *
	 */
	private function moveToRecycleBin( tickHolder:Object )
	{
		if (__recycleBin.length < __recycleBinMax)
		{
			//debug( "moveToRecycleBin", "Moving to recycle bin" );
			__recycleBin.push( tickHolder );
			tickHolder.mc._visible = false;
		}
		else
		{
			tickHolder.mc.removeMovieClip();
			BWUtils.clearObject( tickHolder );
		}
	}


	/**
	 *	Align a number to the nearest multiple. Aligning up or down depends on
	 *	the third parameter, useCeil.
	 *
	 *	e.g.
	 *	snapToMultiple( 19, 3 ) returns 18
	 *	snapToMultiple( 19, 3, true ) returns 21
	 *
	 *	Note behaviour when number is already a multiple.
	 *	e.g.
	 *	snapToMultiple( 18, 3 ) returns 18
	 *	snapToMultiple( 18, 3, true ) returns 21
	 */
	public function snapToMultiple( value:Number, multiple:Number,
			useCeil:Boolean ):Number
	{
		if (multiple == null or multiple == 1)
		{
			if (useCeil == true)
			{
				return value + 1;
			}
			else
			{
				return value;
			}
		}

		if (useCeil == true)
		{
			if ( value % multiple == 0 )
			{
				return value + multiple;
			}
			else
			{
				return Math.ceil( value / multiple ) * multiple;
			}
		}
		else
		{
			return Math.floor( value / multiple ) * multiple;
		}
	}

	/**
	 *	Given a timestamp, return the timestamp aligned to the specified
	 *	resolution.
	 *	e.g. alignTimestamp( 1234567, "month" );
	 *	returns the timestamp of the beginning of the month corresponding
	 *	to that time.
	 *
	 *	If the third parameter is set to true, then the return value is
	 *	always AFTER the timestamp (even if the original timestamp was
	 *	already aligned
	 */
	public function alignTimestamp( timestamp:Number, resolution:String,
			multiple:Number, afterTimestamp:Boolean ):Number
	{
		var curDate:Date = new Date( timestamp );
		var newDate:Date;

		switch( resolution )
		{
			case "year":
				// Add the trailing 0 parameter otherwise Date constructor
				// treats the year as a unix timestamp in milliseconds,
				// which isn't good
				newDate = new Date( snapToMultiple( curDate.getFullYear(),
							multiple, afterTimestamp), 0 );
				break;
			case "month":
				newDate = new Date( curDate.getFullYear(),
						snapToMultiple( curDate.getMonth(),
							multiple, afterTimestamp ) );
				break;
			/*case "week":
				// Special case, 7 days aligned to the month
				var dayOfMonth =

				newDate = new Date( curDate.getFullYear(),
						snapToMultiple( curDate.getMonth(), multiple,
							afterTimestamp ) );*/
			case "day":
				// We perform implicit snapping to the month, sorry about that.
				// This is because when using multiples (e.g. for a tick every
				// 7 days) then undefined behaviour occurs, due to months
				// being irregular lengths.

				// Possible feature: Add an extra "snap" argument to resolution
				// schemes that automatically have an extra snapping step like
				// we do for "multiples of days" to months

				/*newDate = new Date( curDate.getFullYear(),
						curDate.getMonth(),
						snapToMultiple( curDate.getDate(),
							multiple, afterTimestamp ) );*/

				var monthAfter:Date = new Date(
						curDate.getFullYear(),
						curDate.getMonth() + 1 );

				newDate = new Date( curDate.getFullYear(),
						curDate.getMonth(),
						snapToMultiple( curDate.getDate(), multiple,
							afterTimestamp ) );

				// Snap to month
				if (newDate > monthAfter)
				{
					newDate = monthAfter;
				}

				break;
			case "hour":
				newDate = new Date( curDate.getFullYear(),
						curDate.getMonth(),
						curDate.getDate(),
						snapToMultiple( curDate.getHours(), multiple,
							afterTimestamp ) );
				break;
			case "minute":
				newDate = new Date( curDate.getFullYear(),
						curDate.getMonth(),
						curDate.getDate(),
						curDate.getHours(),
						snapToMultiple( curDate.getMinutes(), multiple,
							afterTimestamp ) );
				break;
			case "second":
				newDate = new Date( curDate.getFullYear(),
						curDate.getMonth(),
						curDate.getDate(),
						curDate.getHours(),
						curDate.getMinutes(),
						snapToMultiple( curDate.getSeconds(), multiple,
							afterTimestamp ) );
				break;
			default:
				debug( "alignTimestamp", "ERROR: unknown resolution " +
					resolution );
		}

		var newTimestamp:Number = newDate.valueOf();

		if (afterTimestamp and (newTimestamp == timestamp))
		{
			debug( "alignTimestamp", "ERROR: alignTimestamp returned " +
				" unchanged value " + newTimestamp + 
				" when 'afterTimestamp' was true. Date was: " + newDate +
				" Original timestamp was: " + timestamp +
				" Resolution was: " + resolution +
				" Multiple was: " + multiple );
		}

		return newTimestamp;
	}

	// DEBUG FUNCTIONS
	// ========================================================================
	public function printTicks ():Void
	{
		BWUtils.log( "=============================" );
		BWUtils.log( "Printing ticks" );
		for (var i:Number = 0; i < __ticks.length; ++i)
		{
			BWUtils.log( "  - " + __ticks[i].time );
		}
		BWUtils.log( "=============================" );
	}
}
