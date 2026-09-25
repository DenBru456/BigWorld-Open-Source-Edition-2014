import com.bigworldtech.TickManager;
import com.bigworldtech.BWUtils;
/**
 * YTickDisplay class.
 * Note: Extends XTickDisplay, in which all internal variables refer to time.
 * However, YTicks (vertical axis) represent raw values, not time.
 * So in this class, references to times are really references to value.
 *
 * Also, the axis is switched. So left means down, and right means up.
 *
 * e.g. getLeftMostDisplayTime means the value (not time) corresponding
 *      to the bottom of the tick display.
 */
class YTickDisplay extends XTickDisplay
{
	private var __nextDepth:Number = 0;

	public function YTickDisplay()
	{
		//debug( "(constructor)" );
		__minimumPixelDistance = 20;
		__currentRange = null;

		// Setup visual elements
		this.init();
		this.arrange();
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "YTickDisplay." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	private function getLeftMostDisplayTime()
	{
		return 0;
	}

	private function getRightMostDisplayTime()
	{
		return __currentRange;
	}

	/**
	 * Initialise MovieClip attributes
	 */
	public function init()
	{
		// Dummy values
		__width = 10;
		__height = 10;
		this._xscale = 100;
		this._yscale = 100;
	}

	/**
	 * Set up possible resolutions. Note that although this function
	 * overrides a function in TickManager which would normally be unused in
	 * this class, it is independant from that function.
	 */
	 public function setupResolutions()
	 {
		 // TODO: Add SI prefixes and log10 values
		 //       e.g. log10(1000) = 3, prefix = "kilo"
		 __resolutions = [
		 	{log: -9, code: "n"}, // nano
		 	{log: -6, code: "µ"}, // micro
		 	{log: -3, code: "m"}, // milli
		 	{log: 0,  code: "" }, // Guess what this is
		 	{log: 3,  code: "k"}, // kilo
		 	{log: 6,  code: "M"}, // mega
		 	{log: 9,  code: "G"}, // giga
		 	{log: 12, code: "T"}  // tera
		];

		// Extend each object with a divideBy attribute
		// which is basically 10^log
		for (var i:Number = 0; i < __resolutions.length; ++i)
		{
			var resolution:Object = __resolutions[i];
			resolution.divideBy = Math.pow( 10, resolution.log );
		}
	 }

	 /**
	  * Dummy function to override unnecessary functionality inherited
	  * from TickManager
	  */
	 public function setupIntervalInformation()
	 {
	 }

	 /**
	  * Dummy function to override unnecessary functionality inherited
	  * from TickManager
	  */
	 public function optimizeResolutions()
	 {
	 }


	/**
	 * Main update function! Called whenever
	 * any key parameter of YTickDisplay has changed.
	 *
	 * Overrides TickManager's parameters.
	 */
	public function update()
	{
		// Implement basic behaviour: Divide range into equivalent
		// intervals. Each interval will be at least __minimumPixelDistance
		// apart.

		if (__currentRange == null)
		{
			this.clearTicks();
			return;
		}

		//debug( "update" );

		// Create a new list
		__oldTicks = __ticks;
		__ticks = new Array();

		// __currentRange actually corresponds to the "max" value of the graph
		//var valueRange:Number = __currentRange;
		var valueRange:Number = __currentRange;

		// Create boundary ticks first
		this.setTick( 0, null );

		// Check if we have room for non-boundary ticks
		if (__height > (__minimumPixelDistance * 2))
		{
			// Now, determine the steps
			var steps:Number = Math.pow( 10,
				Math.ceil( Math.log( valueRange ) / Math.log( 10 ) ) - 1 );

			// Hack...basically, if we have a value like 104, we don't want
			// the only step to be 100. So if we're too close above a value
			// which corresponds to 10^x, reduce the step size by 10.
			if ((valueRange / steps) < 1.1)
			{
				steps /= 10;
			}

			var resolution:Object = this.chooseResolution( steps );

			var lastValue:Number = 0;
			var currentValue:Number = steps;

			//debug( "update", "Height is " + __height +
			//	" value range is : " + valueRange + " Steps is: " + steps );

			// Loop until the tick just below max value
			while (currentValue < (valueRange - steps - 0.01))
			{
				//debug( "update", "Checking tick " + currentValue );
				//debug( "update", "valueRange - steps = " +
				//	(valueRange - steps) + "...so it's " +
				//	(currentValue < (valueRange - steps - 0.1)) );

				var pixelDistance:Number = __height * (currentValue - lastValue)
					/ valueRange;

				if (pixelDistance >= __minimumPixelDistance)
				{
					this.setTick( currentValue, resolution );
					lastValue = currentValue;
					//debug( "update", "Setting tick " +
					// currentValue + " PixelDistance " + pixelDistance );
				}

				currentValue += steps;
			}

			// Second last tick (before the topmost tick)...instead
			// of comparing the distance to the tick before, compare
			// with the distance from this tick to the topmost.
			var pixelDistance:Number = __height * (valueRange - currentValue )
				/ valueRange;

			if (pixelDistance >= __minimumPixelDistance)
			{
				//debug( "update", "Setting last tick " +
				//	currentValue + " PixelDistance " + pixelDistance );
				this.setTick( currentValue, resolution );
			}
		}

		// Add the final top boundary tick. It might be in a different resolution.
		this.setTick( valueRange, this.chooseResolution( valueRange ) );

		// To finish up, clean the old unused ticks
		while (__oldTicks.length)
		{
			//debug( "update", "Removing tick" );
			var tickHolder:Object = __oldTicks.shift();
			tickHolder.mc.removeMovieClip();
		}
	}

	/**
	 * Arrange the child movieclips into the right position
	 */
	private function arrange()
	{
		// When the width changes, need to change tick area length too
		__tickAreaLength = __width;

		/*
		// Draw bounding box (for debugging)
		clear();
		lineStyle(1, 0x000000);
		moveTo(0,0);
		lineTo(__width, 0);
		lineTo(__width, __height);
		lineTo(0, __height);
		lineTo(0,0);
		 */
	}

	public function setSize(width:Number, height:Number)
	{
		if (width != null) {__width = width; }
		if (height != null) {__height = height;}

		arrange();
		resizeTicks();
		update();
	}

	private function resizeTicks()
	{
		// Change the height of ticks
		for (var i:Number = 0; i < __ticks.length; ++i)
		{
			var tickHolder:Object = __ticks[i];
			tickHolder.mc.setSize( __width, null )
		}
	}

	/**
	 * Create instance of tick movieclip
	 */
	private function createTickMC( tickID:Number )
	{
		//debug( "createTickMC", tickID );
		var tick:YGraphTick = YGraphTick(
			this.attachMovie( "YGraphTick", "tick" + tickID,
			__nextDepth++ ) );

		tick.setTickWidth( this.getTickMargin() );

		return tick;
	}

	/**
	 * Position the tick movieclip.
	 *
	 * Parameters "format" and "isMajor" are ignored.
	 */
	public function positionTickMC( tickMC:MovieClip, targetValue:Number,
			format:String, isMajor:Boolean )
	{
		// Calculate X position
		var leftMostDisplayTime:Number = this.getLeftMostDisplayTime();
		var rightMostDisplayTime:Number = this.getRightMostDisplayTime();

		var yRatio:Number = (targetValue - leftMostDisplayTime)/
			(rightMostDisplayTime - leftMostDisplayTime);
		var yPos:Number = (1 - yRatio) * __height;

		//debug( "positionTickMC", "Ypos at: " + yPos );

		tickMC._y = yPos;
		tickMC._x = 0;
		tickMC.setSize( __width, null );

		tickMC.draw();
	}

	/**
	 *  Depending on the step
	 */
	private function chooseResolution( value:Number ):Object
	{
		var currentRes:Object;
		var logValue = Math.floor( Math.log( value ) / Math.LN10 );

		var searchObject:Object = { log: logValue }
		var pos:Number = BWUtils.binarySearchOnAttribute( __resolutions,
			"log", searchObject );

		if (pos == null)
		{
			currentRes = __resolutions[0];
		}
		else if (pos == __resolutions.length - 1)
		{
			currentRes = __resolutions[pos];
		}
		else
		{
			// Now we're between two resolutions, one before
			// and one after. Calculate which one is more
			// appropriate to use.
			var curDiff = Math.abs(logValue - __resolutions[pos].log);
			var nextDiff = Math.abs(logValue - __resolutions[pos + 1].log);

			if (curDiff < nextDiff)
			{
				currentRes = __resolutions[pos];
			}
			else
			{
				currentRes = __resolutions[pos + 1];
			}
		}

		/*
		debug( "chooseResolution",
			"Comparing: " + currentRes.code + " and " +
			resolution.code  + " (i am " + value +
			" which has a log of " + logValue );
		*/

		return currentRes;
	}

	/**
	 * Formats a number into something a bit more palatable.
	 */


	private function setTickMCFormat( tickMC:MovieClip, value:Number, resolution:Object )
	{
		var formatted:String;

		// Basic catcher
		if (value == 0 or resolution == null)
		{
			formatted = String( value );
		}
		else
		{
			// Divide the value according to the suffix we're going to add
			var newValue =  value / resolution.divideBy;

			// Now we can format the number to two decimal places
			var newValue:Number = Math.round( newValue * 100 ) / 100;

			formatted = String( newValue ) + resolution.code;

			//debug( "setTickMCFormat", value + " to " + formatted );
		}

		tickMC.setText( formatted );
	}

	/**
	 * Return the pixel width needed to accomodate the tick labels.
	 * Tick labels are located at the left of the tick display.
	 *
	 * TODO: Actually calculate margin needed based on font and
	 * pattern
	 */
	public function getTickMargin()
	{
		return 27;
	}
}
