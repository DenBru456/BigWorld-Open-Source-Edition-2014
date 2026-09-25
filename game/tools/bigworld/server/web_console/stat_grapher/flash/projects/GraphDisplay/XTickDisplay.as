import com.bigworldtech.TickManager;
import com.bigworldtech.misc.SimpleDateFormatter;
import com.bigworldtech.BWProfiler;
import com.bigworldtech.BWUtils;

class XTickDisplay extends TickManager
{
	// Class members
	private var __width:Number;
	private var __height:Number;

	// Visual elements
	private var _mcMask:MovieClip;
	private var _mcCanvas:MovieClip;
	private var __nextDepth:Number = 0;

	/**
	 * Constructor for the class XTickDisplay
	 */
	public function XTickDisplay()
	{
		__minimumPixelDistance = 25;

		// Setup visual elements
		this.init();
		this.createChildren();
		this.arrange();
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "XTickDisplay." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	/**
	 * Return time corresponding to left edge of tick area
	 */
	private function getLeftMostDisplayTime()
	{
		return __displayTime - __currentRange;
	}

	/**
	 * Return time corresponding to right edge of tick area
	 */
	private function getRightMostDisplayTime()
	{
		return __displayTime;
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
	 * Construct the child movieclip components
	 */
	private function createChildren()
	{
		this.createEmptyMovieClip( "_mcCanvas", 0 );
		this.createEmptyMovieClip( "_mcMask", 1 );

		// Draw the mask
		with (_mcMask)
		{
			lineStyle();
			beginFill( 0x000000 );
			moveTo( 0,0 );
			lineTo( _parent.__width, 0 );
			lineTo( _parent.__width, _parent.__height );
			lineTo( 0, _parent.__height );
			lineTo( 0, 0 );
			endFill();
		}

		_mcCanvas.setMask( _mcMask );
		_mcCanvas._x = 0;
		_mcCanvas._y = 0;
	}

	/**
	 * Arrange the child movieclips into the right position
	 */
	private function arrange()
	{
		// Draw the mask
		with ( _mcMask )
		{
			clear();
			lineStyle();
			beginFill( 0x000000 );
			moveTo( 0, 0 );
			lineTo( _parent.__width, 0 );
			lineTo( _parent.__width, _parent.__height );
			lineTo( 0, _parent.__height );
			lineTo( 0, 0 );
			endFill();
		}

		// When the width changes, need to change tick area length too
		__tickAreaLength = __width;

		// Draw bounding box (for debugging)
		/*
		clear();
		lineStyle( 1, 0x000000 );
		moveTo( 0, 0 );
		lineTo( __width, 0 );
		lineTo( __width, __height );
		lineTo( 0, __height );
		lineTo( 0, 0 );
		*/
	}

	/**
	 * Return the pixel height needed to accomodate the tick labels.
	 * Tick labels are located at the bottom of the tick display.
	 *
	 * TODO: Actually calculate margin needed based on font and
	 * pattern.
	 */
	public function getTickMargin()
	{
		return 12;
	}

	/**
	 *
	 */
	public function setSize(width:Number, height:Number)
	{
		//trace("XTickDisplay.setSize: " + width + "x" + height);

		if (width != null) {__width = width; }
		if (height != null) {__height = height;}

		this.arrange();
		this.resizeTicks();
		this.update( );
	}

	/**
	 *
	 */
	private function resizeTicks()
	{
		//debug( "resizeTicks", __ticks.length + " ticks for " + this );

		// Change the height of ticks
		for (var i:Number = 0; i < __ticks.length; ++i)
		{
			var tickHolder:Object = __ticks[i];
			tickHolder.mc.setSize( null, __height );
		}

		// In the recycle bin too
		for (var i:Number = 0; i < __recycleBin.length; ++i)
		{
			var tickHolder:Object = __recycleBin[i];
			tickHolder.mc.setSize( null, __height );
		}
	}

	/**
	 * Create instance of tick movieclip
	 */
	private function createTickMC( tickID:Number )
	{
		//debug( "createTickMC( " + tickID + " )" );
		var tick:XGraphTick = XGraphTick( _mcCanvas.attachMovie( "XGraphTick",
			"tick" + tickID,
			__nextDepth++ ) );

		tick.setTickHeight( this.getTickMargin() );
		//debug( "createTickMC", "Setting size to " + __height );
		tick.setSize( null, __height );
		tick._y = 0;

		return tick;
	}

	/**
	 * Position the tick movieclip
	 */
	public function positionTickMC( tickMC:MovieClip, targetTime:Number,
			format:String, isMajor:Boolean )
	{
		//BWProfiler.begin("calculateStuff");
		// Calculate X position
		var leftMostDisplayTime:Number = this.getLeftMostDisplayTime();
		var rightMostDisplayTime:Number = this.getRightMostDisplayTime();

		var xRatio:Number = (targetTime - leftMostDisplayTime) /
			(rightMostDisplayTime - leftMostDisplayTime);
		var xPos:Number = xRatio * __width;

		tickMC._x = xPos;
		//BWProfiler.end();
	}

	/**
	 *
	 */
	public function setTickMCIsMajor( tickMC:MovieClip, isMajor:Boolean )
	{
		tickMC.setIsMajor( isMajor );
	}

	/**
	 *
	 */
	public function setTickMCFormat( tickMC:MovieClip, timestamp:Number,
		format:String )
	{
		var tickDate:Date = new Date( timestamp );
		var label:String =
			SimpleDateFormatter.formatDate( tickDate, format );
		tickMC.setText( label );
	}
}
