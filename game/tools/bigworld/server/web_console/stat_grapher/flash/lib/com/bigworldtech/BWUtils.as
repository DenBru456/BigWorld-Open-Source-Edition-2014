import mx.rpc.FaultEvent;

import com.bigworldtech.misc.SimpleDateFormatter;

class com.bigworldtech.BWUtils
{
	/** The logger object, can be null. */
	private static var ___loggerObject:Object = null;

	/** The logging function name present on the logger object. The
		function must take a log message string as a parameter. */
	private static var ___loggerFunction:String = null;

	/**
	 *	Binary searches an array. The third parameter is used to
	 *	determine which element to retrieve if we don't have an exact match:
	 *	the element after the intended value or the element before the
	 *	intended value.
	 *
	 *	Returns the index of the element (or the nearest element).
	 *	Returns null if there is no match and no element in the direction
	 *	specified.
	 */
	public static function binarySearch( targetArray:Array, value:Number,
			getElementAfter:Boolean ):Number
	{
		var left:Number;
		var right:Number;
		var mid:Number;

		left = 0;
		right = targetArray.length - 1;

		// Standard binary search
		while (left <= right)
		{
			mid = left + Math.floor( (right - left) / 2 );
			if (value > targetArray[mid])
			{
				left = mid + 1;
			}
			else if (value < targetArray[mid])
			{
				right = mid - 1;
			}
			else {
				return mid;
			}
		}

		// Ok, we're here because there's been no match
		// in the array, and "left" index is now GREATER
		// than the "right" index (which is how the while
		// condition broke).

		if (getElementAfter)
		{
			if (left <= (targetArray.length - 1))
			{
				return left;
			}
		}
		else
		{
			if (right >= 0)
			{
				return right;
			}
		}

		return null;
	}

	/**
	 *	Inserts a value into a sorted array by use of binary search to find
	 *	the appropriate index.
	 */
	public static function binaryInsert( targetArray:Array,
			newValue:Number ):Number
	{
		// Special case where if we append to the end of the array
		// (at least it's easy to test)
		if (newValue >= targetArray[targetArray.length - 1])
		{
			targetArray.push( newValue );
			return targetArray.length - 1;
		}

		var index:Number = BWUtils.binarySearch( targetArray, newValue, true );
		targetArray.splice( index, 0, newValue );
		return index
	}


	/**
	 *	Same as binarySearch, except it operates on an array of objects which
	 *	have attributes. The value provided must also be an object with
	 *	attributes.
	 */
	public static function binarySearchOnAttribute( targetArray:Array,
			attribute:String, value:Object, getElementAfter:Boolean ):Number
	{
		var left:Number;
		var right:Number;
		var mid:Number;

		left = 0;
		right = targetArray.length - 1;

		// Standard binary search
		while (left <= right)
		{
			mid = left + Math.floor( (right - left) / 2 );
			if (value[attribute] > targetArray[mid][attribute])
			{
				left = mid + 1;
			}
			else if (value[attribute] < targetArray[mid][attribute])
			{
				right = mid - 1;
			}
			else
			{
				return mid;
			}
		}

		if (getElementAfter)
		{
			if (left <= (targetArray.length - 1))
			{
				return left;
			}
		}
		else
		{
			if (right >= 0)
			{
				return right;
			}
		}

		return null;
	}

	/**
	 *	Same as binaryInsert, except it works on an array of objects with
	 *	attributes.
	 */
	public static function binaryInsertOnAttribute( targetArray:Array,
			attribute:String, newValue:Object ):Number
	{
		if (newValue[attribute] >=
				targetArray[targetArray.length - 1][attribute])
		{
			targetArray.push( newValue );
			return (targetArray.length - 1);
		}

		var index:Number = BWUtils.binarySearchOnAttribute( targetArray,
				attribute, newValue, true );
		targetArray.splice( index, 0, newValue );
		return index;
	}


	/**
	 *	Same as binarySearch, except it operates on an array of indexes which
	 *	reference a data array. Both arrays must be provided.
	 */
	public static function binarySearchOnIndex( indexArray:Array,
			targetArray:Array, value:Object, getElementAfter:Boolean ):Number
	{
		var left:Number;
		var right:Number;
		var mid:Number;

		left = 0;
		right = indexArray.length - 1;

		// Standard binary search
		while (left <= right)
		{
			mid = left + Math.floor( (right - left) / 2 );
			if (value > targetArray[indexArray[mid]])
			{
				left = mid + 1;
			}
			else if (value < targetArray[indexArray[mid]])
			{
				right = mid - 1;
			}
			else
			{
				return mid;
			}
		}

		if (getElementAfter)
		{
			if (left <= (indexArray.length - 1))
			{
				return left;
			}
		}
		else
		{
			if (right >= 0)
			{
				return right;
			}
		}

		return null;
	}


	// Other container functions
	// ========================================================================

	/**
	 *	Basically a nicer way to say "empty my array please"
	 */
	public static function clearArray( targetArray:Array ):Void
	{
		targetArray.splice( 0 );
	}

	/**
	 *	Basically a nicer way to say "empty my object please"
	 */
	public static function clearObject( obj:Object ):Void
	{
		for (var i:String in obj)
		{
			delete obj[i];
		}
	}


	/**
	 *	Insert an array into an element
	 */
	public static function spliceArray( targetArray:Array, pos:Number,
			deleteCount:Number, newElements:Array ):Void
	{
		targetArray.splice.apply( targetArray,
				[pos, deleteCount].concat( newElements ) );
	}


	// Misc math functions
	// ========================================================================

	/**
	 *	Constrain a value between a min and max number
	 */

	public static function constrain( value:Number, minBound:Number,
			maxBound:Number ):Number
	{
		return Math.max( minBound, Math.min( value, maxBound ) );
	}



	// Debug output functions
	// ========================================================================
	/**
	 *	Print contents of an object
	 */
	public static function printObject( obj:Object, depth:Number ):Void
	{
		BWUtils.log( objectToString( obj, depth ) );
	}

	/**
	 *	Returns a string listing the properties of the given objects and their
	 *	corresponding values.
	 */
	public static function objectToString( obj:Object, depth:Number,
			depthIndent:String ):String
	{
		if (depth == 0)
		{
			return String( obj );
		}

		if (depth == undefined)
		{
			depth = 1;
		}
		if (depthIndent == undefined)
		{
			depthIndent = "";
		}
		var newDepthIndent = depthIndent + "    ";

		var out:String = new String();
		for (var i:String in obj)
		{
			out += depthIndent + i + ": " + obj[i] + "\n";
			if (obj[i] instanceof Array)
			{
				var arrayString:String = "";
				for (var j:Number = 0; j < obj[i].length; ++j)
				{
					if (j > 0)
					{
						arrayString += ", ";
					}
					arrayString += obj[i][j] + ": " +
						objectToString( obj[i][j], depth - 1,
							newDepthIndent );
				}
				out += depthIndent + "[" + arrayString + "]" + "\n";
			}
			else if (typeof( obj[i] ) == "object" and depth - 1 > 0)
			{
				out += objectToString( obj[i], depth - 1, newDepthIndent );
			}
		}
		return out;
	}


	// Flash Remoting helper function
	// ========================================================================
	public static function printPythonError( fe:FaultEvent )
	{
		BWUtils.log( 'Flash remoting error:' );
		BWUtils.log( fe.fault.faultstring );
		BWUtils.log( fe.fault.detail );
	}

	// Assert functions
	// ========================================================================

	/**
	 *	Assert true function
	 */
	public static function assert( value:Object, msg:String ):Boolean
	{
		if (value != true)
		{
			BWUtils.log( "Assert error: " + msg );
			return false;
		}
		return true;
	}

	/**
	 *	Assert equals function
	 */
	public static function assertEquals( target:Object, value:Object,
			msg:String ):Boolean
	{
		if (value != target)
		{
			BWUtils.log( "Assert error: " + msg );
			return false;
		}
		return true;
	}

	/**
	 *	Assert less than or equals function
	 */
	public static function assertLTE( value:Object, target:Object,
			msg:String ):Boolean
	{
		if (not (value <= target))
		{
			BWUtils.log( "Assert error: " + msg );
			return false;
		}
		return true;
	}

	/**
	 *	Assert greater than or equals function
	 */
	public static function assertGTE( value:Object, target:Object,
			msg:String ):Boolean
	{
		if (not (value >= target))
		{
			BWUtils.log( "Assert error: " + msg );
			return false;
		}
		return true;
	}


	/**
	 *	Returns a human-readable string containing the names of the contained
	 *	references of the given movie clip of type MovieClip.
	 */
	public static function childMovieClipsToString( mc:MovieClip,
			depth:Number ):String
	{
		// print out any child movie clips
		var clips:String = null;
		var count:Number = 0;
		for (var prop in mc)
		{
			var propValue = eval( "mc." + prop );
			if (typeof( propValue ) == 'movieclip')
			{
				var movieClipString:String = prop;
				if (depth > 0)
				{
					movieClipString = prop + ": " +
						childMovieClipsToString( propValue, depth - 1);
				}
				else
				{
					movieClipString = prop;
				}

				if (clips == null)
				{
					clips = movieClipString;
				}
				else
				{
					clips += ", " + movieClipString;
				}
				++count;
			}
		}
		return "(" + count + "):[" + clips + "]";
	}

	/**
	 *	Log a message. Use this instead of trace().
	 *
	 *	@param msg	the message to log
	 */
	public static function log( msg:String ):Void
	{
		trace( msg );
		if (___loggerObject)
		{
			___loggerObject[___loggerFunction]( msg );
		}
	}

	/**
	 *	Sets the logger object and function.
	 *
	 *	@param 	loggerObject	the logger object
	 *	@param	functionName	the function name to call on the logger object
	 */
	public static function setLogger( loggerObject:Object,
			functionName:String,
			format:String ):Void
	{
		___loggerObject = loggerObject;
		___loggerFunction = functionName;
	}

	/**
 	 *	Draw a rectangle on a movieclip.
	 *
	 *	@param	mc		the movie clip
	 *	@param	x		the x coordinate of the top left corner
	 *	@param	y		the y coordinate of the top left corner
	 *	@param	w		the width of the rectangle
	 *	@param	h		the height of the rectangle
	 */
	public static function drawRect( mc, x:Number, y:Number, w:Number,
			h:Number ):Void
	{
		mc.moveTo( x, y );
		mc.lineTo( x + w, y );
		mc.lineTo( x + w, y + h );
		mc.lineTo( x, y + h );
		mc.lineTo( x, y );
	}

}
