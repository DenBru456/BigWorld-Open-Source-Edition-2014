/**
 * Crude inline profiler. Has a fairly large overhead if called a large amount
 * of times (e.g. in a while loop).
 *
 * Usage:
 * import com.bigworldtech.BWProfiler;
 * begin( "profileLabel" );
 * for (var i:Number = 0; i < 1000)
 * {
 * }
 * end();
 *
 * (or use endWithPrint() to print the time taken for that inline profile)
 *
 */
import com.bigworldtech.BWUtils;

class com.bigworldtech.BWProfiler
{
	private static var __times:Object = new Object();
	private static var __currentStarts:Object = new Object();
	private static var __profileLevels:Array = new Array();

	private static var __currentProfileId:Number = 0;
	private static var __nextProfileId:Number = 0;
	private static var __idToProfile:Object = new Object();
	private static var __profileToId:Object = new Object();

	private static var ___loggerObject:Object = null;
	private static var ___loggerFunction:String = null;

	public static function setLogger( loggerObject:Object,
			functionName:String )
	{
		___loggerObject = loggerObject;
		___loggerFunction = functionName;
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "BWProfiler." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}
	/**
	 *
	 */
	public static function begin( label:String )
	{
		__profileLevels.push( __currentProfileId );

		var currentProfile:String =
			__currentProfileId == 0 ? 
				label : __idToProfile[__currentProfileId].concat(".", label);
		//debug( "begin", "Got: " + currentProfile );

		__currentProfileId = __profileToId[currentProfile];
		if (__currentProfileId == undefined)
		{
			__currentProfileId = ++__nextProfileId;
			__profileToId[currentProfile] = __currentProfileId;
			__idToProfile[__currentProfileId] = currentProfile;
			//debug( "begin", "made entries" );
		}

		//debug( "begin", "CurrentProfileId is: " + __currentProfileId +
		//	" = " + __idToProfile[ __currentProfileId ] );
		__currentStarts[__currentProfileId] = getTimer();
	}

	/**
	 *
	 */
	public static function end()
	{

		var timeTaken:Number = getTimer() - __currentStarts[__currentProfileId];

		var timeObj:Object = __times[__currentProfileId];
		if (timeObj == undefined)
		{
			__times[__currentProfileId] = { time: timeTaken, count: 1, max: timeTaken, last:timeTaken };
		}
		else
		{
			timeObj.time += timeTaken;
			timeObj.last = timeTaken;
			timeObj.count += 1;

			if (timeObj.max < timeTaken)
			{
				timeObj.max = timeTaken;
			}
		}

		//trace( __idToProfile[__currentProfileId] + " (" + timeTaken + "ms)" );
		__currentProfileId = Number(__profileLevels.pop());
		//debug( "end", "Ended...back to "  + __currentProfileId + " = " +
		//	__idToProfile[ __currentProfileId ] );
	}

	/**
	 *
	 */
	/*
	public static function endWithPrint()
	{
		var timeTaken:Number = getTimer() - __currentStarts[__currentProfileId];

		if (__times[__currentProfileId] == undefined)
		{
			__times[__currentProfileId] =
			{
				time: timeTaken,
				count: 1
			};
		}
		else
		{
			__times[__currentProfileId].time += timeTaken;
			__times[__currentProfileId].count += 1;
		}

		debug( "end", __idToProfile[__currentProfileId] +
			" (" + timeTaken + "ms)" );

		__currentProfileId = Number(__profileLevels.pop());
	}
	*/

	/**
	 *
	 */
	public static function printTimes()
	{
		// Sort by name
		var pNames:Array = new Array();

		for (var i:String in __profileToId)
		{
			pNames.push( i );
		}

		pNames.sort();

		___loggerObject[___loggerFunction]( null );

		var output:Array = new Array();
		output.push( "===========================" );
		output.push( "Printing profile times " + new Date() );
		for (var j:Number = 0; j < pNames.length; ++j)
		{
			var id:Number = __profileToId[pNames[j]];
			var c:Object = __times[id];
					
			var lineOutput:String = "  " + pNames[j];
			var timeOutput:String = "     CUM:" + c.time +
				"ms, COUNT:" + c.count + ", AVG:" + 
				(int( 1000 * c.time / c.count) / 1000 ) + "ms, MAX:" +
				 c.max + "ms, LAST:" + c.last + "ms";
			output.push( lineOutput );
			output.push( timeOutput );
		}
		output.push( "===========================" );

		for (var i:Number = 0; i < output.length; ++i)
		{
			trace(output[i]);
		}

		___loggerObject[___loggerFunction]( output );
	}
}
