import com.bigworldtech.TickManager;
import com.bigworldtech.misc.SimpleDateFormatter;
import com.bigworldtech.BWUtils;

/**
 * TimeRuler class. 80% of the functionality occurs in the
 * TickManager, so look at that class for more source code.
 */

class TimeRuler extends TickManager
{
	// Child movieclip components
	private var _mcBoundingBox:MovieClip;
	private var _mcTimeRulerBox:MovieClip = null;
	private var _mcTimeRulerBackground:MovieClip = null;
	private var _mcMask:MovieClip = null;
	private var _mcCanvas:MovieClip = null;

	// Member names
	private var __width:Number;
	private var __height:Number;

	// Log boundary times
	private var __logStartTime:Number;
	private var __logEndTime:Number;

	// Animating variables
	var __isAnimating:Boolean;
	var __animateFromTime:Number;
	var __animateToTime:Number;
	var __animateTotalTime:Number;
	var __animateTimeElapsed:Number;
	var __lastAnimateFrame:Number;

	// Functions automatically defined by EventDispatcher
	private var dispatchEvent:Function;
	public var addEventListener:Function;
	public var removeEventListener:Function;

	/**
	 * Constructor for the class TimeRuler
	 */
	public function TimeRuler()
	{
		// Call parent constructor
		super();

		// Init some private variables
		__logStartTime = null;
		__logEndTime = null;
		__minimumPixelDistance = 25;

		// Setup visual elements
		this.init();
		this.createChildren();
		this.setEventHandlers();
		this.arrange();

		// Initialise event dispatcher
		mx.events.EventDispatcher.initialize( this );

		//debug( "(constructor)", "finished" );
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "TimeRuler." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	/**
	 * These two functions are the main functions which determine
	 * the TOTAL display range of the graph. Currently they mean
	 * that the entire graph's width is three times the current
	 * time range.
	 */
	private function getLeftMostDisplayTime():Number
	{
		var time:Number = __displayTime - __timeRange * 2;
		return time;
	}

	private function getRightMostDisplayTime():Number
	{
		var time:Number = __displayTime + __timeRange;
		return time;
	}

	/**
	 * Initialise MovieClip attributes
	 */
	public function init()
	{
		__width = this._width;
		__height = this._height;
		this._xscale = 100;
		this._yscale = 100;
		_mcBoundingBox._visible = false;
		_mcBoundingBox._width = 0;
		_mcBoundingBox._height = 0;
	}

	/**
	 * Construct the child movieclip components
	 */
	private function createChildren()
	{
		var nextDepth:Number = 0;
		this.attachMovie( "TimeRulerBackground", "_mcTimeRulerBackground",
				nextDepth++ );
		this.createEmptyMovieClip( "_mcMask", nextDepth++ );
		this.attachMovie( "TimeRulerBox", "_mcTimeRulerBox",
				nextDepth++ );
		this.createEmptyMovieClip( "_mcCanvas", nextDepth++ );

		// Draw the mask
		with ( _mcMask )
		{
			lineStyle();
			beginFill( 0x000000 );
			moveTo( 0, 0 );
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
	 * Set event handlers for movieclip components
	 */
	private function setEventHandlers()
	{
		_mcTimeRulerBox.onPress = function():Void
		{
			this.startDrag( false, 0, 0, _parent.__width - this._width, 0 );
			this.onRelease = this.onReleaseOutside = this.dragOnRelease;
		}
		_mcTimeRulerBox.dragOnRelease = function():Void
		{
			this._parent.endThumbDrag();
		}
	}

	/**
	 * Arrange the child movieclips into the right position
	 */
	private function arrange()
	{
		// Set the background to occupy the entire width
		_mcTimeRulerBackground._width = __width;
		_mcTimeRulerBackground._height = __height;
		_mcTimeRulerBackground._x = 0;
		_mcTimeRulerBackground._y = 0;

		// The box will occupy the central 1/3.
		_mcTimeRulerBox._width = __width / 3;
		_mcTimeRulerBox._height = __height;
		_mcTimeRulerBox._x = __width / 3;
		_mcTimeRulerBox._y = 0;

		// Resize mask
		_mcMask._width = __width;
		_mcMask._height = __height;

		// When the width changes, need to change tick area length too
		__tickAreaLength = __width;
	}

	/**
	 * Change the size of the movieclips
	 * The setSize() method is automatically called when the authoring time
	 * instance is resized.
	 */
	public function setSize( newWidth:Number, newHeight:Number )
	{
		__width = newWidth;
		__height = newHeight;
		arrange();
		this.update();
	}

	/**
	 * Handle the box dragging
	 */
	public function endThumbDrag( )
	{
		_mcTimeRulerBox.stopDrag();

		// Get the box's rightmost X coordinate...because that's the new
		// current time.
		var boxRightX:Number = _mcTimeRulerBox._x + _mcTimeRulerBox._width;
		var rightMostDisplayTime:Number = this.getRightMostDisplayTime();
		var leftMostDisplayTime:Number = this.getLeftMostDisplayTime();

		var newTime:Number = leftMostDisplayTime +
			(boxRightX / __width) *
			(rightMostDisplayTime - leftMostDisplayTime);

		//debug( "endThumbDrag",
		//	"Box released at " + newTime + " diff: " +
		//	(__currentTime - newTime) );

		animateToTime( __currentTime, newTime );
		__currentTime = newTime;

		delete _mcTimeRulerBox.onRelease;
		delete _mcTimeRulerBox.onReleaseOutside;

		//debug( "endThumbDrag", "Current time is: "  + __currentTime
		//	+ " Range: " + __timeRange );

		dispatchEvent( {
			type:	"onTimeRulerDrag",
			time:	__currentTime
		} );
	}

	public function animateToTime( fromTime:Number, toTime:Number )
	{
		__isAnimating = true;
		__animateFromTime = fromTime;
		__animateToTime = toTime;
		__animateTotalTime = 1 * 200;
		__animateTimeElapsed = 0;
		__lastAnimateFrame = getTimer();
	}

	public function doAnimate( )
	{
		var curAnimateFrame = getTimer();

		// Frame time
		var frameDiff:Number = curAnimateFrame - __lastAnimateFrame;
		__animateTimeElapsed += frameDiff;

		//debug( "doAnimate", "Animating " + __animateTimeElapsed +
		//	" total time: " + __animateTotalTime );

		// Calculate new display position
		var displayTime:Number = __animateFromTime +
			(__animateToTime - __animateFromTime) *
			(__animateTimeElapsed / __animateTotalTime);

		//debug( "doAnimate", "Display time: " + __displayTime );

		__displayTime = displayTime;

		// If we've finished, snap display time back
		// to the proper place!
		if (__animateTimeElapsed >= __animateTotalTime)
		{
			__isAnimating = false;
			__displayTime = __currentTime;
		}

		this.update( true );

		__lastAnimateFrame = curAnimateFrame;
	}

	public function onEnterFrame()
	{
		if (__isAnimating == true)
		{
			this.doAnimate();
		}
	}


	/**
	 * Set the start and end times of the logs.
	 * This is so that we can indicate on this ruler where the log
	 * ends.
	 */
	private function setLogBoundary( startTime:Number, endTime:Number )
	{
		__logStartTime = startTime;
		__logEndTime = endTime;
	}

	/**
	 * MAIN FUNCTION
	 * This is the function which creates and positions (or repositions)
	 * the ticks when any of the following states change:
	 *  - Current time
	 *  - Current view range
	 *  - Resized
	 */
	private function update( force:Boolean )
	{
		super.update( force );
		this.positionBox();
		//debug( "(" + this + ").update", clips: " +
		//	BWUtils.childMovieClipsToString( _mcCanvas ) );
	}

	/**
	 * Places the box according to the discrepancy between display time
	 * and the current time - so it may not appear in exactly the center
	 * of the time ruler. Used for animation.
	 */
	private function positionBox()
	{
		var leftMostDisplayTime:Number = this.getLeftMostDisplayTime();
		var rightMostDisplayTime:Number = this.getRightMostDisplayTime();

		// Position the box
		var boxRightXRatio:Number = (__currentTime - leftMostDisplayTime) /
			(rightMostDisplayTime - leftMostDisplayTime);
		var boxRightXPos:Number = boxRightXRatio * __width;

		var boxLeftXPos:Number = boxRightXPos - _mcTimeRulerBox._width;
		_mcTimeRulerBox._x = boxLeftXPos;
	}

	/**
	 * Create instance of tick movieclip
	 */
	private function createTickMC( tickID:Number )
	{
		//debug( "createTickMC( " + tickID + " )" );
		var tickMC:MovieClip =  _mcCanvas.attachMovie( "XRulerTick",
			"tick" + tickID, 10 + tickID );
		tickMC._y = 0;
		tickMC.setSize( null, __height );
		return tickMC;
	}

	/**
	 *
	 */
	public function setTickMCIsMajor( tickMc:MovieClip, isMajor:Boolean )
	{
		tickMc.setIsMajor( isMajor );
	}

	/**
	 *
	 */
	public function setTickMCFormat( tickMc:MovieClip, timestamp:Number,
		format:String )
	{
		var tickDate:Date = new Date( timestamp );
		var label:String =
			SimpleDateFormatter.formatDate( tickDate, format );
		tickMc.setText( label );
	}

	/**
	 * Position the tick movieclip
	 */
	public function positionTickMC( tickMC:MovieClip, targetTime:Number,
			format:String, isMajor:Boolean )
	{
		// Calculate X position
		var leftMostDisplayTime:Number = this.getLeftMostDisplayTime();
		var rightMostDisplayTime:Number = this.getRightMostDisplayTime();

		//debug( "positionTickMC", "displayTimes are " +
		//	leftMostDisplayTime + "-" + rightMostDisplayTime );

		var xRatio:Number = (targetTime - leftMostDisplayTime) /
			(rightMostDisplayTime - leftMostDisplayTime);
		var xPos:Number = xRatio * __width;

		//debug( "positionTickMC", "xPos is: " + xPos );

		tickMC._x = xPos;
		tickMC.draw();
	}
}
