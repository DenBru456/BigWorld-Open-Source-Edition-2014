import mx.events.EventDispatcher;
import com.bigworldtech.BWUtils
import com.bigworldtech.BWProfiler;
import com.bigworldtech.misc.SimpleDateFormatter;

/**
 *	Class for managing and cacheing statistic data.
 *	Doesn't need to know about the type of statistics,
 *	such as the process type and ids.
 *
 */
class StatisticData
{
	// Class variables
	// ========================================================================

	// ============ Data storage members ============
	// Parallel element arrays
	private var __times:Array;
	private var __ticks:Array;
	private var __numSummarised:Array;
	private var __stats:Object;

	// Chunk marker arrays
	private var __startMarkers:Array;
	private var __endMarkers:Array;
	private var __resolutionMarkers:Array;
	private var __dirtyMarkers:Array;

	// Description:
	// ----------------------------------
	// __times, __ticks, __numSummarised, and all attributes of __stats
	// are parallel arrays, where each element corresponds to a single data
	// point.
	//
	// __startMarkers, __endMarkers, __dirtyMarkers and __resolutionMarkers
	// are another set of parallel arrays in which each element corresponds to
	// a range (chunk) of data rather than a single element.
	//
	// Details:
	// -----------------------------------
	// The elements in __startMarkers and __endMarkers contain the indexes
	// denoting the start and end points of each chunk.
	//
	// __resolutionMarkers contains the actual tick resolution of the chunk.
	//
	// __dirtyMarkers contains a flag which indicates whether the chunk should
	//    be discarded in the next updated. This happens only when a statistic
	//    is added or removed from the legend.

	// ========== End data storage members ==========

	// This array stores the ids of each statistic that we expect to get.
	// Everytime we receive data, we compare the stat ids to the ids in this
	// array to see if the set of statistics matches. If it doesn't match,
	// then basically we need to do something that handles the fact that
	// we'll be getting new statistics from now on.
	private var __currentStatSet:Array;

	// Pending requests which have been made to the requestStats method.
	private var __pendingRequests:Array;
	private var __nextPendingRequestId:Number;

	// Time in milliseconds for a pending request to time out
	private static var REQUEST_TIMEOUT:Number = 5000;

	// Distance between ticks in seconds (floating points allowed)
	private var __tickInterval:Number;

	// Functions automatically defined by EventDispatcher
	private var dispatchEvent:Function;
	public var addEventListener:Function;
	public var removeEventListener:Function;

	// Class methods
	// ========================================================================
	/**
	 *	Constructor
	 */
	public function StatisticData()
	{
		__times = new Array();
		__ticks = new Array();
		__numSummarised = Array();
		__stats = new Object();
		/*__skTimes = new Array();
		__skTicks = new Array();
		__skStats = new Array();*/
		__startMarkers = new Array();
		__endMarkers = new Array();
		__resolutionMarkers = new Array();
		__dirtyMarkers = new Array();
		__tickInterval = null;
		__currentStatSet = new Array();

		// Initialise pending requests
		__pendingRequests = new Array();
		__nextPendingRequestId = 0;

		// Initialise event handler
		mx.events.EventDispatcher.initialize( this );
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "StatisticData." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	/**
	 *	Set the tick interval
	 */
	public function setTickInterval( tickInterval:Number )
	{
		//debug( "setTickInterval", tickInterval );
		__tickInterval = tickInterval;
	}

	// Public methods
	// ========================================================================

	/**
	 *	Complete erases all data in memory.
	 *
	 *	Usually performed when a new statistic is added, since for
	 *	now it's a little tricky to easily accomodate a new statistic
	 *	while keeping the parallel array and chunk structure.
	 */
	public function clear()
	{
		BWUtils.clearArray( __times );
		BWUtils.clearArray( __ticks );
		BWUtils.clearArray( __startMarkers );
		BWUtils.clearArray( __endMarkers );
		BWUtils.clearArray( __resolutionMarkers );
		BWUtils.clearObject( __stats );
	}

	/**
	 *	Calling this function informs us that any data replies that we're
	 *	currently expecting from the server are to be ignored.
	 *
	 *	Used when we've zoomed out, so the data we want is now different from
	 *	the data we're about to receive.
	 */
	public function voidPendingRequests()
	{
		for (var i:Number = 0; i < __pendingRequests.length; ++i)
		{
			__pendingRequests[i].valid = false;
		}
	}


	/**
	 *	Returns a vertical slice of the most recent values between the
	 *	timerange.
	 *
	 *	Used for getting the data for showing in the legend.
	 */
	public function getStats( startTime:Number, endTime:Number )
	{
		//debug( "getStats" );

		var statIndex:Number = BWUtils.binarySearch( __times, endTime );

		if (__times[statIndex] < startTime)
		{
			return null;
		}

		var stats:Object = new Object();

		for (var i:String in __stats)
		{
			stats[i] = __stats[i][ statIndex ];
		}

		return stats;
	}

	/**
	 *	Returns the most recent value for "number of processes/machines"
	 *	summarised between the timerange.
	 *
	 *	Used for showing the number of processes in the graph title.
	 */
	public function getNumSummarised( startTime:Number, endTime:Number )
	{
		//debug( "getNumSummarised" );

		var statIndex:Number = BWUtils.binarySearch( __times, endTime );

		if (__times[statIndex] < startTime)
		{
			return null;
		}

		//debug( "getNumSummarised", "statIndex: " + statIndex );
		//debug( "getNumSummarised", "__numSummarised: " + __numSummarised );

		return __numSummarised[statIndex];
	}

	/**
	 *	Performs actions when a statistic is enabled or disabled.
	 *
	 *	Note that the actual enabling or disabling of a statistic is
	 *	not handled by this function, as it involves notifying the
	 *	server of the changes.
	 *
	 *	i.e. If you try to disable a statistic only by this function, then
	 *	you'll continue to receive it from the server. So don't do that!
	 */
	public function setStatEnabled( statId:String, enabled:Boolean)
	{
		//debug( "setStatEnabled(" + statId + " = " + enabled
		//	+ ")" );

		if (enabled == false)
		{
			if (__stats[statId] != undefined)
			{
				delete __stats[statId];
			}
		}
		else
		{
			if (__stats[statId] == undefined)
			{
				__stats[statId] = new Array();

				// Insert a dummy array for the newly enabled stat
				for (var i:Number = 0; i < __times.length; ++i)
				{
					__stats[statId].push( null );
				}

				// Insert
				for (var i:Number = 0; i < this.chunkCount(); ++i)
				{
					__dirtyMarkers[i] = true;
				}
			}
		}

		//this.printChunks();
	}

	// Requesting functions
	// ========================================================================
	/**
	 *	Drawing code ALWAYS requests in terms of times.
	 *	It's this class's responsibility to decide
	 *	whether to make the query in terms of timestamps
	 *	or ticks.
	 */
	public function requestStats( from:Number, to:Number, resolution:Number,
		sendPlaceholder:Boolean )
	{
		//debug( "requestStats",
		//	"from: " + SimpleDateFormatter.formatDate(
		//		new Date( from ), "HH:mm:ss" ) +
		//	", to: " + SimpleDateFormatter.formatDate(
		//		new Date( to ), "HH:mm:ss" ) +
		//	", resolution: " + resolution );

		if (sendPlaceholder == null) { sendPlaceholder = false; }

		// First, check to see if we already have the data in storage
		if (checkForAndSendStats( from, to, resolution ))
		{
			//debug( "requestStats", "Sending immediate stats" );
			return;
		}

		// We don't have all the data in storage...this means we're going
		// to have to make remote requests. So first,
		// check if we're already waiting for requests first
		if (this.canMakeRequest() == false)
		{
			// Send placeholder stats for the time being

			//grabAndSendData( from, to, resolution,
			// 		true /* isPlaceholder */ );
			return;
		}

		//debug( "requestStats",
		//	"Tickinterval: " + __tickInterval + " Res: " + resolution );

		// If we request data further than 5 ticks off either the start or
		// end of our data, then we use timestamps instead to request.
		var disjointThreshold:Number = __tickInterval *	resolution * 5;

		// Ok, let's check if we have any data at all between our timestamps.

		// Cases:
		// 1) Completely disjoint from current data (after, before)
		//    - Use timestamps to request, to avoid timestamp drift issues
		//
		// 2) Overwrites other chunks of same resolution
		//    - Split/truncate request depending on whether it "dwarfs" other
		//      chunk or not.
		//
		// 3) Overwrites other chunks of different resolution
		//    - Ignore

		// Our requests are going to be a parallel array of start and end ticks.
		// This is because requests can likely consist of disjoint regions.

		// Check if requested timerange is disjoint from current data
		var lastDataTime:Number = __times[__times.length - 1];
		var firstDataTime:Number = __times[0];
		var lastDataTick:Number = __ticks[__ticks.length - 1];
		var firstDataTick:Number = __ticks[0];

		// Ok, we're disjoint or there's no elements in the array, make a simple
		// time call and return.
		if ((__times.length == 0) ||
				(from >= (lastDataTime + disjointThreshold)) ||
				(to <= (firstDataTime - disjointThreshold)))
		{
			/*
			debug( "requestStats", "Request stats: Disjoint request! " +
				"Printing extra information: \n" +
				"    Request: " + from + " - " + to + "\n" +
				"    Times in memory: " + firstDataTime +
					" - " + lastDataTime + "\n" +
				"    Thresholds: " + (firstDataTime - disjointThreshold) +
						" - " + (lastDataTime - disjointThreshold) );
			*/

			var requestId:Number =
				this.addPendingRequest( from, to, resolution );

			dispatchEvent( {
				type: "onRemoteRequestByTime",
				startTime: from,
				endTime: to,
				resolution: resolution,
				requestId: requestId
			} );
			return;
		}

		// Note: We use ticks mainly to make our requests. In the one case
		// where we use timestamps to denote the start and end points of the
		// requests, we don't use these arrays.
		var requestTickStarts:Array = new Array();
		var requestTickEnds:Array = new Array();

		// Get some tick references
		var fromReferenceIndex:Number = BWUtils.binarySearch( __times, from );
		var toReferenceIndex:Number = BWUtils.binarySearch( __times, to, true );


		//  Do a bit of correction if "from" time starts before any of our data
		if (fromReferenceIndex == null)
		{
			fromReferenceIndex = 0;
		}

		// Test on the right hand side of the current tick to see if it's a
		// better use as a reference
		else if (fromReferenceIndex < (__times.length - 1))
		{
			var fromReferenceTimeDiff:Number = from -
				__times[fromReferenceIndex];
			var nextFromReferenceTimeDiff:Number =
				__times[fromReferenceIndex + 1] - from;

			if (nextFromReferenceTimeDiff < fromReferenceTimeDiff)
			{
				++fromReferenceIndex;
			}
		}

		// Now, do the same with the toReferenceIndex
		if (toReferenceIndex == null)
		{
			toReferenceIndex = __ticks.length - 1;
		}

		// Test on the left hand side of the current tick to see if it's a
		// better use as a reference
		else if (toReferenceIndex > 0)
		{
			var toReferenceTimeDiff:Number = __times[toReferenceIndex] - to;
			var prevToReferenceTimeDiff:Number =
				to - __times[toReferenceIndex - 1];

			if (prevToReferenceTimeDiff < toReferenceTimeDiff)
			{
				--toReferenceIndex;
			}
		}

		// Get the request tick start
		var requestTickStart:Number = __ticks[fromReferenceIndex] +
			(from - __times[fromReferenceIndex]) / __tickInterval
			- resolution;

		var requestTickEnd:Number = __ticks[toReferenceIndex] +
			(to - __times[toReferenceIndex]) / __tickInterval
			+ resolution;

		// Now cut out the bits we already have
		var chunkIndex = BWUtils.binarySearchOnIndex(__startMarkers,
			__ticks, requestTickStart );

		if (chunkIndex == null)
		{
			chunkIndex = 0;
		}

		for ( ; chunkIndex < this.chunkCount(); ++chunkIndex )
		{
			var chunkTickStart:Number = __ticks[__startMarkers[chunkIndex]];
			var chunkTickEnd:Number = __ticks[__endMarkers[chunkIndex]];
			var chunkResolution:Number = __resolutionMarkers[chunkIndex];
			var chunkIsDirty:Number = __dirtyMarkers[chunkIndex];

			// Chunk needs replacing no matter what
			if (chunkIsDirty)
			{
				continue;
			}

			if (chunkResolution == resolution)
			{
				// Case 1:  Chunk intrudes into request from left
				// Data:     DDDDDDDDDDDDDD
				// Request:     >---------------------------<
				// Action:  Truncate request from the left
				if ((chunkTickStart <= requestTickStart)
					and (chunkTickEnd < requestTickEnd))
				{
					requestTickStart = chunkTickEnd;
				}

				// Case 2:  Chunk intrudes into request from right
				// Data:                               DDDDDDDDDDDDDD
				// Request:     >---------------------------<
				// Action:  Truncate request from the right
				else if ((chunkTickStart > requestTickStart)
					and (chunkTickEnd >= requestTickEnd))
				{
					requestTickEnd = chunkTickStart;
				}

				// Case 3:  Chunk dwarfed by data
				// Data:               DDDDDDDDDDDDDD
				// Request:     >---------------------------<
				// Action:  Split request into two parts minus the overlapped
				//          area.
				else if ((chunkTickStart <= requestTickStart)
					and (chunkTickEnd >= requestTickEnd))
				{
					// Add left part to the array, which ends
					// at the start of the chunk
					requestTickStarts.push( requestTickStart );
					requestTickEnds.push( chunkTickStart );

					// Second part starts at the end of the chunk
					// (retain the previous tick end)
					requestTickStart = chunkTickEnd;
				}

				// Case 4:  Data dwarfed by chunk
				// Data:               DDDDDDDDDDDDDD
				// Request:     >---------------------------<
				// Action:  Abandon request
				else if ((chunkTickStart <= requestTickStart)
					and (chunkTickEnd >= requestTickEnd))
				{
					requestTickStart = null;
					requestTickEnd = null;
				}
			}

			if (chunkTickEnd > requestTickEnd)
			{
				break;
			}
		}

		// Add the last request to the array
		if (requestTickStart != null && requestTickEnd != null)
		{
			requestTickStarts.push( requestTickStart );
			requestTickEnds.push( requestTickEnd );
		}

		var requestId:Number = this.addPendingRequest( from, to, resolution );

		//debug( "requestStats", "Making remote request since " +
		//	"we don't have the data" );

		// Dispatch the events
		dispatchEvent( {
			type: "onRemoteRequestByTicks",
				startTicks: requestTickStarts,
				endTicks: requestTickEnds,
				resolution: resolution,
				requestId: requestId
			} );

		// Send placeholder stats for the time being
		if (sendPlaceholder)
		{
			grabAndSendData( from, to, resolution, true );
			//debug( "requestStats", "Sending placeholder data" );
		}
	}


	/**
	 *	This function checks to see if we already can satisfy a request for
	 *	stats, and sends that data if it does.
	 */
	private function checkForAndSendStats( from:Number, to:Number,
			resolution:Number )
	{
		//debug( "checkForAndSendStats" );
		//this.printChunks();

		var chunkIndex:Number = BWUtils.binarySearchOnIndex(
			__startMarkers, __times, from );

		for ( ; chunkIndex < this.chunkCount(); ++chunkIndex)
		{
			var chunkResolution:Number 	= __resolutionMarkers[chunkIndex];
			var chunkIsDirty:Number 	= __dirtyMarkers[chunkIndex];
			var chunkStartIndex:Number 	= __startMarkers[chunkIndex];
			var chunkEndIndex:Number 	= __endMarkers[chunkIndex];

			if ((from >= __times[chunkStartIndex]) &&
					(to <= __times[chunkEndIndex]) &&
					(resolution == chunkResolution) &&
					(!chunkIsDirty))
			{
				this.grabAndSendData( from, to, resolution );
				return true;
			}

			if (__times[chunkEndIndex] > to)
			{
				break;
			}
		}
		return false;
	}


	/**
	 *	This is the single callback function that is expected to be called after
	 *	we make a call to either requestDataByTime or requestDataByTick.
	 */
	public function receiveRemoteData( requestId:Number, stats:Object )
	{
		//debug( "receiveRemoteData" );

		var idx:Number = BWUtils.binarySearchOnAttribute(
			__pendingRequests, "requestId", requestId );
		//debug( "receiveRemoteData", "Index is: " + idx );

		// Don't do anything unless we were expecting it
		var requestObject:Object = __pendingRequests[idx];
		if (requestObject.requestId != requestId)
		{
			return;
		}

		//debug( "receiveRemoteData",
		//	"Spliced index " + idx + "...Number of requests left: " +
		//	__pendingRequests.length );

		// If not valid, dump it and return.
		if (requestObject.valid == false)
		{
			__pendingRequests.splice( idx, 1 );
			return;
		}

		//debug( "receiveRemoteData", "Received remote data" );
		//debug( "receiveRemoteData", "Data is " + stats.times.length +
		//	" elements long." );
		//debug( "receiveRemoteData", stats );
		//BWUtils.printObject( stats );

		this.integrateData( stats );
		//this.printChunks();

		dispatchEvent( {
			type: 		"onRemoteDataArrived",
			startTime:	stats.times[0],
			endTime:	stats.times[ stats.times.length - 1 ],
			numElements: stats.times.length,
			requestId:	requestId
		} );

		__pendingRequests.splice( idx, 1 );
	}

	// Private methods
	// ========================================================================

	/**
	 *	Lets listeners know when the statistic set has changed. This essentially
	 *	happens when the enable/disable dialog is used by another computer
	 *	logged onto the same user.
	 */
	private function notifyStatSetChange( newStats:Array, removedStats:Array )
	{
		this.dispatchEvent( {
			type: "onStatSetChange",
			newStats: newStats,
			removedStats: removedStats
		} );
	}

	/**
	 *	Main function to integrate the data into the current arrays, after
	 *	receiving from the remote server.
	 *
	 *	There is a possibility that we have to "overwrite" some stats we
	 *	already have, especially if they're of a different resolution.
	 */
	private function integrateData( stats:Object )
	{
		//debug( "integrateData" );
		//BWProfiler.begin("integrateData");

		// Get the start and end times
		var statStartTime:Number = stats.times[0];
		var statEndTime:Number = stats.times[ stats.times.length - 1 ];
		var statStartTick:Number = stats.ticks[0];
		var statEndTick:Number = stats.ticks[ stats.ticks.length - 1 ];
		var statResolution:Number = stats.resolution;

		//debug( "integrateData", "Resolution is " +
		//	statResolution );

		//debug( "integrateData",
		//	"Integrating new data from " + statStartTime + " to " +
		//	statEndTime );
		//debug( "integrateData", "stats: " +
		//	BWUtils.objectToString( stats, 3 ) );

		//BWProfiler.begin("calculateIndices");

		// Get tick start index
		var insertStartIndex:Number =
			BWUtils.binarySearch( __ticks, statStartTick, true );

		// Get tick end index
		var insertEndIndex:Number = BWUtils.binarySearch(
			__ticks, statEndTick );

		// Special cases:
		// 1) insertStartIndex == null
		//    - Append to array, don't delete any current stats
		// 2) insertEndIndex == null
		//    - Prepend to array, don't delete any current stats
		// 3) insertEndIndex == (insertStartIndex - 1)
		//    - Insert between existing ticks, don't delete any current stats

		var deleteAmount:Number;

		// 1) Append case
		if (insertStartIndex == null)
		{
			insertStartIndex = __ticks.length;
			deleteAmount = 0;
		}

		// 2) Prepend case
		else if (insertEndIndex == null)
		{
			insertStartIndex = 0;
			deleteAmount = 0;
		}

		// 3) Insert in between existing ticks case
		else if (insertEndIndex < insertStartIndex)
		{
			insertStartIndex = insertEndIndex;
			deleteAmount  = 0;
		}

		// and...the normal case
		else
		{
			deleteAmount = insertEndIndex - insertStartIndex + 1;
		}

		// How many values are we going to insert?
		var insertAmount:Number = stats.ticks.length;

		//BWProfiler.end();

		// Now, with the following variables:
		// - insertStartIndex
		// - insertAmount
		// - deleteAmount
		// - statStartTick
		// - statEndTick
		// - statResolution
		//
		// ...we can update the chunks as needed.
		// There are quite a few cases which we will
		// have to handle.
		//BWProfiler.begin("updateChunkMarkers");
		this.updateChunkMarkers( insertStartIndex, insertAmount, deleteAmount,
			statResolution );
		//BWProfiler.end();

		// Actually update the actual statistics now
		//BWProfiler.begin("applyNewStatistics");
		this.applyNewStatistics( insertStartIndex, deleteAmount, stats );
		//BWProfiler.end();

		// Stitch chunks together (i.e. join adjacent chunks of the same
		// resolution)
		//BWProfiler.begin("stitchChunks");
		this.stitchChunks();
		//BWProfiler.end();

		// DEBUG: Print list of chunks that we have
		//this.printChunks();
		//BWProfiler.end();
	}

	/**
	 *	Second part of integrateData. Updates the chunk indexes
	 */
	private function updateChunkMarkers( insertStartIndex:Number,
			insertAmount:Number, deleteAmount:Number,
			statResolution:Number )
	{
		//debug( "updateChunkMarkers", "statResolution = " +
		//	statResolution );
		var i:Number;

		// We're basically reconstructing the indices again...so first convert
		// into a more manageable form
		var chunkSizes:Array = new Array();
		var chunkResolutions:Array = __resolutionMarkers.slice();
		var chunkIsDirty:Array = __dirtyMarkers.slice();

		for (i = 0; i < this.chunkCount(); ++i)
		{
			chunkSizes.push( __endMarkers[i] - __startMarkers[i] + 1 );
		}

		var deleteRemaining:Number = deleteAmount;

		// IMPORTANT NOTE:
		// From this point on during this function, the __startMarkers,
		// __endMarkers and __resolutionMarkers arrays are going to be
		// "out of sync" and therefore unusable until resynced later near
		// the end of the function..
		//
		// The chunkSizes and chunkResolutions array will instead represent
		// this information.

		// Begin chunk modifications
		// =======================================
		// The hard part is deleting the first chunk, as we will quite
		// possibly start deleting from the middle of the first chunk

		// Find chunk to start from quickly
		var chunkIndex:Number =
			BWUtils.binarySearch( __startMarkers, insertStartIndex );
		if (chunkIndex == null)
		{
			chunkIndex = 0;
		}

		// Start with some chunk info
		var chunkStartIndex:Number = __startMarkers[chunkIndex];
		var chunkEndIndex:Number = __endMarkers[chunkIndex];
		var elementsInChunk:Number = chunkEndIndex - chunkStartIndex + 1;

		// Special case: Append to end of data (without deleting, of course)
		if (insertStartIndex >= __ticks.length)
		{
			BWUtils.assert( deleteRemaining == 0,
				"updateChunkMarkers: " +
				"appending to end of data, so deleteRemaining == 0");
			chunkIndex = chunkSizes.length;
		}
		else if (chunkStartIndex < insertStartIndex)
		{
			// we delete from middle for the first chunk
			var canDeleteAmount:Number = chunkEndIndex - insertStartIndex + 1;

			// Delete all the way to end
			if (canDeleteAmount <= deleteRemaining)
			{
				deleteRemaining -= canDeleteAmount;
				chunkSizes[chunkIndex] -= canDeleteAmount;

				++chunkIndex;
			}

			// Don't delete all the way to end...special case, because
			// we need to split a chunk into two and insert into the
			// centre
			else
			{
				// Split into two
				var firstChunkSize:Number = insertStartIndex - chunkStartIndex;
				var secondChunkSize:Number = chunkEndIndex -
					insertStartIndex - deleteRemaining + 1;

				deleteRemaining = 0;

				// Modify first chunk size
				chunkSizes[chunkIndex] = firstChunkSize;

				++chunkIndex;

				// Insert new entry for second chunk
				chunkSizes.splice( chunkIndex, 0, secondChunkSize );

				// Copy resolution and dirty information from first chunk part
				chunkResolutions.splice( chunkIndex, 0,
					chunkResolutions[chunkIndex - 1] );
				chunkIsDirty.splice(chunkIndex, 0,
					chunkIsDirty[chunkIndex - 1] );
			}
		}

		// Insert just before the current chunk index!
		if (insertAmount > 0)
		{	/**
	 *	Remove data which is outside our threshold time.
	 */

			chunkSizes.splice( chunkIndex, 0, insertAmount );
			chunkResolutions.splice( chunkIndex, 0, statResolution );
			chunkIsDirty.splice( chunkIndex, 0, false );
			++chunkIndex;
		}

		// Now start looping
		while (deleteRemaining > 0)
		{
			if (chunkSizes[chunkIndex] <= deleteRemaining)
			{
				deleteRemaining -= chunkSizes[chunkIndex];
				chunkSizes[chunkIndex] = 0;
			}
			else
			{
				chunkSizes[chunkIndex] -= deleteRemaining;
				deleteRemaining = 0;
			}

			++chunkIndex;
		}

		// Delete empty chunks
		for (i = 0; i < chunkSizes.length; ++i)
		{
			if (chunkSizes[i] == 0)
			{
				chunkSizes.splice( i, 1 );
				chunkResolutions.splice( i, 1 );
				chunkIsDirty.splice( i, 1 );
				__startMarkers.splice( -1, 1 );
				__endMarkers.splice( -1, 1 );
				__resolutionMarkers.splice( -1, 1 );
				__dirtyMarkers.splice( -1, 1 );
				--i;
			}
		}

		// Expand the __startMarkers and __endMarkers array
		var resizeAmount:Number = chunkSizes.length - __startMarkers.length;
		for (i = 0; i < resizeAmount; ++i)
		{
			__startMarkers.push( null );
			__endMarkers.push( null );
		}


		var currentIndex:Number = 0;

		// Reconstruct chunk indexes for __startMarkers and __endMarkers
		for (i = 0; i < chunkSizes.length; ++i)
		{
			__startMarkers[i] = currentIndex;
			__endMarkers[i] = currentIndex + chunkSizes[i] - 1;
			__resolutionMarkers[i] = chunkResolutions[i];
			__dirtyMarkers[i] = chunkIsDirty[i];
			currentIndex += chunkSizes[i];
		}
	}

	/**
	 * Delete a contiguous section of the statistics.
	 */
	private function applyRemoveStatistics( removeStartIndex:Number,
			deleteAmount:Number )
	{

		/*
		debug( "applyRemoveStatistics( removeStartIndex=" +
			removeStartIndex +
			", deleteAmount=" + deleteAmount + " )" );

		debug( "applyRemoveStatistics",
			"__ticks.length = " + __ticks.length +
			", __times.length = " + __times.length );
		*/
		__ticks.splice( removeStartIndex, deleteAmount );
		__times.splice( removeStartIndex, deleteAmount );
		__numSummarised.splice( removeStartIndex, deleteAmount );

		for (var statId:String in __stats)
		{
			var statValueList:Array = __stats[statId];
			//debug( "applyRemoveStatistics",
			//	__stats[" + statId +"].length=" + statValueList.length );
			statValueList.splice( removeStartIndex, deleteAmount );
		}
	}

	/**
	 *	Modify our actual stored values now. Also check the set of statistics
	 *	that we're working with too.
	 */
	private function applyNewStatistics( insertStartIndex:Number,
			deleteAmount:Number, stats:Object )
	{
		//debug( "applyNewStatistics" );

		// Dictionaries of which statistics are found
		var newStats:Object = new Object();
		var foundStats:Object = new Object();
		var unfoundStats:Object = new Object();
		var oldStatLength:Number = __times.length;

		//debug( "applyNewStatistics", "stats.num is " + stats.num );

		// Delete ticks which overlap, then insert the new stats
		BWUtils.spliceArray( __ticks, insertStartIndex, deleteAmount,
				stats.ticks );
		BWUtils.spliceArray( __times, insertStartIndex, deleteAmount,
				stats.times );
		BWUtils.spliceArray( __numSummarised, insertStartIndex, deleteAmount,
				stats.num );

		var statPrefId:String;
		var newStatisticSet:Boolean = false;

		// Found stats
		for (statPrefId in stats.data)
		{
			// Check that the length of stats is the same as the number
			// of timestamps
			BWUtils.assert(
				stats.data[statPrefId].length == stats.times.length,
				"Received statistic " + statPrefId + "(" +
				stats.data[statPrefId].length + ") has a different " +
				"number of elements to our timestamps (" +
				stats.times.length + ")" );

			// Create array object for stat if it doesn't exist already
			if (__stats[statPrefId] == null)
			{
				newStats[statPrefId] = true;
				__stats[statPrefId] = new Array();

				// Fill it with dummy values so it's the same length
				// as the other arrays were before we added these new stats
				for (var i:Number = 0; i < oldStatLength; ++i)
				{
					__stats[statPrefId].push( null );
				}
				newStatisticSet = true;
			}

			foundStats[statPrefId] = true;

			BWUtils.spliceArray( __stats[statPrefId], insertStartIndex,
				deleteAmount, stats.data[statPrefId] );
		}

		// Check which stats weren't updated
		/*for (statPrefId in __stats)
		{
			if (foundStats[statPrefId] == null)
			{
				unfoundStats[statPrefId] = true;
				newStatisticSet = true;
			}
		}

		// Dispatch event if we have a new statistic set
		if (newStatisticSet == true)
		{
			this.dispatchEvent( {
				type: "onUpdateStatisticSet",
				newStats: newStats,
				missingStats: unfoundStats
			} );
		}*/
	}

	/**
	 *	Combine chunks together if they're adjacent and also of the
	 *	same resolution.
	 */
	private function stitchChunks()
	{
		var chunkTickEnd:Number;
		var nextChunkTickStart:Number;
		var chunkResolution:Number = 0;
		var nextChunkResolution:Number = 0;
		var chunkDifference:Number = 0;

		// Start the loop
		//
		// NOTE: We loop only until the second last element as we check two
		//       chunks at a time.
		for (var chunkIndex:Number = 0;
				chunkIndex < (this.chunkCount() - 1);
				++chunkIndex)
		{
			chunkTickEnd = __ticks[__endMarkers[chunkIndex]];
			chunkResolution = __resolutionMarkers[chunkIndex];
			nextChunkTickStart = __ticks[__startMarkers[chunkIndex + 1]];
			nextChunkResolution = __resolutionMarkers[chunkIndex + 1];

			if (chunkResolution == nextChunkResolution)
			{
				chunkDifference == nextChunkTickStart - chunkTickEnd;
				BWUtils.assert( (chunkDifference % chunkResolution) == 0,
					"Ticks must be a multiple of its resolution ("
					+ chunkResolution + ")");

				// Stitch chunks together!
				if (chunkDifference <= chunkResolution)
				{
					// Expand current chunk
					__endMarkers[chunkIndex] = __endMarkers[chunkIndex + 1];

					// Remove next chunk
					__startMarkers.splice(chunkIndex + 1, 1);
					__endMarkers.splice(chunkIndex + 1, 1);
					__resolutionMarkers.splice(chunkIndex + 1, 1);
					__dirtyMarkers.splice(chunkIndex + 1, 1);
				}
			}
		}
	}

	/**
	 *	This function checks waiting requests and replies to them if we can
	 *	fulfill them.
	 */
	private function checkPendingRequests()
	{
		for (var i:Number = 0; i < __pendingRequests.length; ++i)
		{
			var prStart:Number = __pendingRequests[i].startTime;
			var prEnd:Number = __pendingRequests[i].endTime;
			var prResolution:Number = __pendingRequests[i].resolution;
			var prId:Number = __pendingRequests[i].requestId;

			var chunkIndex:Number = BWUtils.binarySearchOnIndex( __startMarkers,
				__times, prStart );

			// Continue if binary search indicates that there's no chunk which
			// starts on or before our "from" time
			if (chunkIndex != null)
			{
				// Check if we have data which matches the request
				if ((__resolutionMarkers[chunkIndex] == prResolution) &&
					(__times[__startMarkers[chunkIndex]] <= prStart) &&
					(__times[__endMarkers[chunkIndex]] >= prEnd))
				{
					// Remove from pending requests
					__pendingRequests.splice( i, 1 );

					// Now, actually grab the data
					this.grabAndSendData( prStart, prEnd, prResolution );

					return;
				}
			}

			//debug( "checkPendingRequests",
			//	"Not enough data to display for " + prStart +
			//	" to " + prEnd );
		}
	}

	/**
	 *	Retrieve data from our data storage. Assumes we've already checked
	 *	that the storage does in fact have the exact data we need and doesn't
	 *	need to be requested.
	 */
	public function grabAndSendData( from:Number, to:Number,
			resolution:Number, isPlaceholder:Boolean )
	{
		if (isPlaceholder == null)
		{
			isPlaceholder = false;
		}

		// No stats to send...abort!
		if (__times.length == 0)
		{
			return;
		}

		/*
		if (isPlaceholder)
		{
			debug( "grabAndSendData", "Sending placeholder data" );
		}
		*/

		var dataIndexStart:Number =
			BWUtils.binarySearch( __times, from );
		if (dataIndexStart == null)
		{
			dataIndexStart = 0;
		}

		var dataIndexEnd:Number =
			BWUtils.binarySearch( __times, to, true );
		if (dataIndexEnd == null)
		{
			dataIndexEnd = __times.length - 1;
		}

		// No data to send, abort
		if (dataIndexStart == dataIndexEnd)
		{
			//debug( "grabAndSendStats", "No data to send" );
			return;
		}

		// Ok, let's slice all the arrays and send it to our requester to draw
		var stats:Object = new Object();

		stats.times = __times.slice( dataIndexStart, dataIndexEnd + 1 );
		stats.resolution = resolution;
		stats.data = new Object();
		stats.isPlaceholder = isPlaceholder;

		for (var statPrefId:String in __stats)
		{
			stats.data[statPrefId] = __stats[statPrefId].slice( dataIndexStart,
				dataIndexEnd + 1 );
		}

		//debug( "grabAndSendData", "from " + from + " to " + to +
		//	"(Data indexes: " + dataIndexStart + " - " + dataIndexEnd );


		dispatchEvent( {
			type: "onDataReady",
			stats: stats
		});
	}

	/**
	 *	Register a pending request in our array, so we can match incoming replies
	 *	to requests.
	 */
	private function addPendingRequest( from:Number, to:Number,
			resolution:Number )
	{
		var requestId:Number = __nextPendingRequestId++;

		var obj:Object = new Object();

		// Add to pending requests
		obj.startTime = from;
		obj.endTime = to;
		obj.resolution = resolution;
		obj.requestId = requestId;
		obj.requestTime = getTimer();
		obj.valid = true;
		__pendingRequests.push( obj );

		return requestId;
	}

	/**
	 * Remove data which is outside our threshold time. It will
	 * not cull data unless we have data which exceeds the
	 * maxThreshold; then it culls to the minThreshold.
	 * It's a type of hysteresis.
	 */
	public function cullData( referenceTime:Number,
		beforeMinThreshold:Number, beforeMaxThreshold:Number,
		afterMinThreshold:Number, afterMaxThreshold:Number)
	{
		if (__times.length == 0)
		{
			return;
		}

		if (afterMinThreshold == undefined)
		{
			afterMinThreshold = beforeMinThreshold;
		}
		if (afterMaxThreshold == undefined)
		{
			afterMaxThreshold = beforeMaxThreshold;
		}

		// Check first element
		var firstTime:Number = __times[0];
		if (firstTime < (referenceTime - beforeMaxThreshold))
		{
			// Cull before
			var cullBefore:Number = BWUtils.binarySearch( __times,
				referenceTime - beforeMinThreshold );

			// Binary search returns null if there's no values before our
			// threshold
			if (cullBefore != null)
			{
				//BWProfiler.begin( "updateChunkMarkers" );
				updateChunkMarkers( 0, 0, cullBefore, null );
				//BWProfiler.end();
				//BWProfiler.begin( "applyRemoveStatistics" );
				applyRemoveStatistics(0, cullBefore);
				//BWProfiler.end();
				//debug( "cullData", "Culling " + cullBefore +
				//	" elements from the start." );
			}
		}

		// Check last element
		var lastTime:Number = __times[__times.length - 1];
		if (lastTime > (referenceTime + afterMaxThreshold))
		{
			var cullAfter:Number = BWUtils.binarySearch( __times,
				referenceTime + afterMinThreshold, true );

			if (cullAfter != null)
			{
				var numRemoved:Number = __times.length - cullAfter;
				updateChunkMarkers( cullAfter, 0, numRemoved, null );
				applyRemoveStatistics( cullAfter, numRemoved );
				//debug( "cullData", "Culling " + numRemoved +
				//	" elements from the end." );
				//debug( "cullData", "Culling up to " + (referenceTime + afterMinThreshold) );
			}
		}

		//this.printChunks();
		this.checkChunkIntegrity();
	}

	/**
	 *	Checks whether we already have a request which we're waiting on.
	 *	Currently, can have no more than one request at a time.
	 */
	private function canMakeRequest()
	{
		// Clear old requests
		for (var i:Number = 0; i < __pendingRequests.length; ++i)
		{
			var waitingTime:Number = 
				getTimer() - __pendingRequests[i].requestTime;

			if (waitingTime > REQUEST_TIMEOUT)
			{
				//debug( "canMakeRequest: Deleting old request" );

				// Delete the pending request
				__pendingRequests.splice( i );
				--i;
			}
		}

		return __pendingRequests.length == 0;
	}

	/**
	 *	Returns the numbers of chunks that we have in our array.
	 */
	private function chunkCount()
	{
		return __startMarkers.length;
	}

	// Debugging functions
	// ========================================================================
	/**
	 *	Prints to trace output the current list of chunks
	 */
	public function printChunks()
	{

		BWUtils.log("Printing chunks:");
		BWUtils.log("=========================");
		for (var i:Number = 0; i < this.chunkCount(); ++i)
		{
			BWUtils.log( "Index: " +
				__startMarkers[i] + " - " + __endMarkers[i] + ": "
				+ " Resolution " + __resolutionMarkers[i] +
				" [Tick: " + __ticks[__startMarkers[i]] + " - "
					+ __ticks[__endMarkers[i]] + "]" +
				" [Time: " + __times[__startMarkers[i]] + " - "
				+ __times[__endMarkers[i]] + "]" +
				" [Dirty: " + __dirtyMarkers[i] + "]" );

		}
		BWUtils.log( "  List of stats: " + this.getStatList() );
		BWUtils.log( "__ticks.length = " + __ticks.length + "\n" +
			"__times.length = " + __times.length + "\n" +
			"__startMarkers.length = " + __startMarkers.length + "\n" +
			"__endMarkers.length = " + __endMarkers.length + "\n" +
			"__dirtyMarkers.length = " + __dirtyMarkers.length + "\n" +
			"__resolutionMarkers.length = " + __resolutionMarkers.length );
		BWUtils.log( "=========================" );
	}

	/**
	 * Prints the list of timestamps
	 */
	public function printTimes()
	{
		BWUtils.log( "Timestamps: " );
		for (var i:Number = 1; i < __times.length; ++i)
		{
			BWUtils.log( i + ": " + __ticks[i] + ": " + (__times[i] - __times[i - 1]) );
		}
	}

	/**
	 *	Get the current set of statistics that we've got stored.
	 */
	public function getStatList()
	{
		var statList:Array = new Array();

		for (var statPrefId:String in __stats)
		{
			statList.push( statPrefId + " (" + __stats[statPrefId].length +
				")" );
		}

		return statList;
	}

	/**
	 *	Check chunk integrity
	 */
	public function checkChunkIntegrity()
	{
		var numStartMarkers:Number = __startMarkers.length;

		if (__endMarkers.length != numStartMarkers)
		{
			debug( "checkChunkIntegrity", "ERROR: " +
				"End marker length (" + __endMarkers.length +
				") differs from start marker length (" +
				numStartMarkers + ")." );
		}

		if (__resolutionMarkers.length != numStartMarkers)
		{
			debug( "checkChunkIntegrity", "ERROR: " +
				"Resolution marker length (" +__resolutionMarkers.length +
				") differs from start marker length (" +
				numStartMarkers + ")." );
		}

		if (__dirtyMarkers.length != numStartMarkers)
		{
			debug( "checkChunkIntegrity", "ERROR: " +
				"Dirty marker length (" +__dirtyMarkers.length +
				") differs from start marker length (" +
				numStartMarkers + ")." );
		}

		if (__times.length == 0)
		{
			if (__startMarkers.length != 0)
			{
				debug( "checkChunkIntegrity", "ERROR: " +
					"Chunks exist when we have no statistics" );
			}

			return;
		}

		// Check first chunk starts with 0
		if (__startMarkers[0] != 0)
		{
			debug( "checkChunkIntegrity", "ERROR: First chunk does "
				+ "not start at index 0 (current: " + __startMarkers[0] + ")" );
		}

		// Check last chunk ends at the last time index
		if (__endMarkers[__endMarkers.length - 1] != (__times.length - 1))
		{
			debug( "StatisticsData.checkChunkIntegrity",
				"ERROR: Last chunk does not end at last time index " +
				(__times.length - 1) +
				" (instead: " + __endMarkers[__endMarkers.length - 1] + ")" );
			this.printChunks();
		}

		var lastEnd:Number = -1;
		// Check contiguity of chunks
		for (var i:Number = 0; i < this.chunkCount(); ++i)
		{
			var chunkStartIndex:Number = __startMarkers[i];
			var chunkEndIndex:Number = __endMarkers[i];

			if (chunkStartIndex != lastEnd + 1)
			{
				debug( "checkChunkIntegrity", "ERROR: Chunk " + i +
					" does not continue on from previous chunk which ended at "
					+ lastEnd);

				this.printChunks();
			}

			/*
			if (chunkEndIndex == chunkStartIndex)
			{
				debug( "checkChunkIntegrity", "ERROR: Chunk " + i +
					" has a start marker equal to end marker (" +
					chunkEndIndex + ")" );
			}
			*/

			if (chunkEndIndex < chunkStartIndex)
			{
				debug( "checkChunkIntegrity", "ERROR: Chunk " + i +
					" has a end marker smaller than start marker (" +
					chunkStartIndex + "-" + chunkEndIndex + ")" );
			}

			lastEnd = chunkEndIndex;
		}

		// Check statistic lengths
		if (__times.length != __ticks.length)
		{
			debug( "checkChunkIntegrity", "ERROR: " +
				"__times (" + __times.length + ") has a different number of" +
				" elements to __ticks (" + __ticks.length + ")" );
		}

		// Check statistic lengths
		for (var j:String in __stats)
		{
			var stat:Array = __stats[j];

			if (stat.length != __times.length)
			{
				debug( "checkChunkIntegrity", "ERROR: " +
					"Statistic " + j + "(" + stat.length + ") " +
					"has a different number of elements to __times (" +
					__times.length + ")."+
					" Aborting integrity check." );
				break;
			}
		}
	}
}
