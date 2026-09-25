import mx.transitions.Tween;
import com.bigworldtech.BWUtils;

class ScrollWheel extends MovieClip
{
	// Bounding box instance
	private var mcBoundingBox:MovieClip;

	// Movie clip assets
	private var _mcScrollThumb:MovieClip;
	private var _mcScrollTrack:MovieClip;

	// Important Note: While the scrolltrack's origin is the top left corner,
	//                 the scroll thumb's origin is the center of the bitmap.
	//                 Why? Because the only position we're really concerned
	//                 with in the thumb, is the center.

	// Interval
	private var __isThumbDragging:Boolean;

	// Dimensions
	private var __width:Number;
	private var __height:Number;

	// X position
	private var __thumbCenter:Number;

	// View range in seconds
	private var __viewRange:Number;
	private var __maxViewRangesPerSecond:Number;

	// Mouse dragging
	private var __startDragPos:Number;
	private var __lastFrameTime:Number;

	// Functions
	private var dispatchEvent:Function;
	public var addEventListener:Function;
	public var removeEventListener:Function;

	function ScrollWheel()
	{
		//BWUtils.log( "ScrollWheel.(constructor)" );
		init();
		initScrollThumb();
		//createChildren();
		arrange();
	}

	private function init()
	{
		__width = _width;
		__height = _height;
		_xscale = 100;
		_yscale = 100;
		mx.events.EventDispatcher.initialize( this );
		mcBoundingBox._visible = false;
		mcBoundingBox._width = 0;
		mcBoundingBox._height = 0;

		// Velocity is in the number of seconds to move per second.
		// E.g. when the bar is held at the max, we move this many number of
		// seconds in that direction. Max velocity will generally be set
		// to the current view range of the graph.
		__viewRange = 60;
		__maxViewRangesPerSecond = 4;
	}

	private function initScrollThumb():Void
	{
		_mcScrollThumb.onPress = function():Void
		{
			this._parent.beginThumbDrag();
			var halfWidth = this._width / 2;
			this.startDrag( false, halfWidth, _y + 0.5,
				_parent._mcScrollTrack._width - halfWidth, _y + 0.5 );
			this.onMouseUp = this.dragOnMouseUp;
			this.onMouseMove = this.dragOnMouseMove;
			this.onRelease = this.onReleaseOutside = this.dragOnRelease;
		}

		_mcScrollThumb.dragOnMouseUp = function():Void
		{
			this.stopDrag();
		}

		_mcScrollThumb.dragOnMouseMove = function():Void
		{
			this._parent.doThumbDrag();
		}

		_mcScrollThumb.dragOnRelease = function():Void
		{
			this._parent.endThumbDrag();
		}

	}

	private function getTrackCenter()
	{
		return _mcScrollTrack._x + (_mcScrollTrack._width / 2);
	}

	private function getThumbOffset()
	{
		return _mcScrollThumb._x - getTrackCenter();
	}

	public function beginThumbDrag()
	{
		__lastFrameTime = null;
		__isThumbDragging = true;
	}

	public function endThumbDrag()
	{
		__isThumbDragging = false;
		delete this._mcScrollThumb.onRelease;
		delete this._mcScrollThumb.onReleaseOutside;
		delete this._mcScrollThumb.onMouseMove;
		_mcScrollThumb._y = _mcScrollTrack._y + _mcScrollTrack._height / 2;
		var tw:Object = new mx.transitions.Tween(
			_mcScrollThumb, "_x", mx.transitions.easing.Regular.easeOut,
			_mcScrollThumb._x, getTrackCenter(), 0.2, true );
      	dispatchEvent({type: "onFinishDrag", target: this});
	}

	private function arrange()
	{
		// Standard text height
		// Using __width and __height, arrange elements
		if (_mcScrollTrack._height > __height)
		{
			_mcScrollTrack._height = __height;
		}
		_mcScrollTrack._width = __width;
		_mcScrollTrack._x = 0;
		_mcScrollTrack._y = (__height / 2) - (_mcScrollTrack._height / 2);

		_mcScrollThumb._height = Math.min( _mcScrollThumb._height, __height )
		_mcScrollThumb._x = getTrackCenter();
		_mcScrollThumb._y = _mcScrollTrack._y + _mcScrollTrack._height / 2;
	}

	// The setSize() method is automatically called when the authoring time
	// instance is resized.
	public function setSize( nW:Number, nH:Number ):Void
	{
		_xscale = 100;
		_yscale = 100;
		__width = nW;
		__height = nH;
		arrange();
	}

	public function onEnterFrame()
	{
		if (__isThumbDragging)
		{
			var now = getTimer();

			if (__lastFrameTime == null)
			{
				__lastFrameTime = now;
				return;
			}

			var elapsed = now - __lastFrameTime;

			var offset:Number = this.getThumbOffset();

			if (Math.abs(offset) < 1)
			{
				__lastFrameTime = null;
				return;
			}

			var movementRange = _mcScrollTrack._width / 2 -
				_mcScrollThumb._width / 2;
			var velocity = (offset / movementRange) * __viewRange *
				__maxViewRangesPerSecond;

			// Elapsed is in milliseconds...
			var change = velocity * elapsed / 1000;
			dispatchEvent({type: "onVelocityDrag", change: change});
			__lastFrameTime = getTimer();
		}
	}

	public function setViewRange( viewRange:Number )
	{
		__viewRange = viewRange;
	}

	public function getWidth():Number
	{
		return __width;
	}

	public function getHeight():Number
	{
		return __height;
	}
}
