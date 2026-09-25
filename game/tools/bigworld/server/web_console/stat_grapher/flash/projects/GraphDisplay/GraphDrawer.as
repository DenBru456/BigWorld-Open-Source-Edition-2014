import mx.utils.Delegate;
import com.bigworldtech.BWUtils;

class GraphDrawer extends MovieClip
{
	// Visual related variables
	// ========================================================================
	private var __width:Number;
	private var __height:Number;

	// Internal components (movieclips, textfields)
	// ========================================================================

	// Id representation, needed for when the graph controller needs to dispatch
	// a server response to the right graph.
	private var __id:Object;

	// Text label...technically not a movieclip, but add the _mc prefix anyway
	// for consistency.
	private var _mcText:TextField;

	// Movieclips related to the line drawing area.
	private var _mcTerminator:MovieClip;
	private var _mcDrawArea:MovieClip;
	private var _mcDrawAreaBackground:MovieClip;
	private var _mcDrawAreaMask:MovieClip;
	private var _mcDrawAreaBorders:MovieClip;

	// Movieclips related to the tick on the graph.
	// (Implemented as their own classes)
	private var _mcXTickDisplay:XTickDisplay;
	private var _mcYTickDisplay:YTickDisplay;

	// Other necessary movieclips
	private var _mcBackground:MovieClip;

	// This movieclip is unhidden when selected
	// and hidden when not selected
	private var _mcSelected:MovieClip;

	// Overall margin for all elements in the graph
	private var __margin:Number = 3;

	// Internal visual variables
	// ========================================================================
	// Drag variables for panning
	private var __dragStartX;

	// Current text to show in the title bar
	private var __text;

	// Data related variables
	// ========================================================================
	// Current time
	private var __currentTime:Number;
	private var __currentRange:Number;

	// Other essential information
	private var __logStartTime:Number;
	private var __logEndTime:Number;

	// Canvas information - list of canvases we're using.
	// Array of objects with the following attributes:
	// - startTime:Number		Start of the canvas
	// - endTime:Number			End of the canvas
	// - resolution:Number		Resolution of the canvas (TODO: Remove this,
	// 							replace with drawnAt)
	// - mcName:String			Name of movieclip
	// - mc:MovieClip			Instance of movieclip
	// - drawnAt:Number			"Range" at which movieclip was drawn
	//
	// Current experiment: Create a pool of graphCanvases (try 3) for swapping
	private var __canvasPool:Array;
	private var __canvasInUse:Array;
	private var __canvasPoolSize:Number = 2;
	private var __canvasEdges:Array;

	// Draw area dimensions
	private var __drawAreaWidth:Number;
	private var __drawAreaHeight:Number;

	// Object to hold functions we'll assign to line movieclips
	private var __funcRepository:Object;

	// Functions automatically defined by EventDispatcher
	private var dispatchEvent:Function;
	public var addEventListener:Function;
	public var removeEventListener:Function;

	// Public methods
	// ========================================================================
	/**
	 * Constructor
	 */
	public function GraphDrawer()
	{
		__canvasPool = new Array();
		__canvasInUse = new Array();
		__canvasEdges = new Array();

		// Initialise event handler
		mx.events.EventDispatcher.initialize( this );

		// Various other initialisers
		this.initDisplay();
		this.createChildren();
		this.initDrawAreaMask();
		this.arrange();
		this.createCanvasPool( __canvasPoolSize );
		this.initFunctionRepository();
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "GraphDrawer." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	// Initialisers and various visual event handlers
	// ========================================================================
	/**
	 * Initialise class variables related to display
	 */
	private function initDisplay()
	{
		__width = this._width;
		__height = this._height;
		this._xscale = 100;
		this._yscale = 100;
	}

	/**
	 * Create visual elements
	 */
	private function createChildren()
	{
		// for assigning depths
		var nextDepth:Number = 0;

		// Create tick displays
		this.createEmptyMovieClip( "_mcBackground", nextDepth++ );

		// Create background
		this.createEmptyMovieClip("_mcDrawAreaBackground",
				nextDepth++ );

		// Create tick displays
		this.attachMovie( "XTickDisplay", "_mcXTickDisplay",
				nextDepth++ );
		this.attachMovie( "YTickDisplay", "_mcYTickDisplay",
				nextDepth++ );


		// Create line drawing canvas and mask
		this.createEmptyMovieClip("_mcDrawArea",
			nextDepth++ );

		_mcTerminator = _mcDrawArea.createEmptyMovieClip("_mcTerminator",
			0 );

		this.createEmptyMovieClip("_mcDrawAreaMask",
			nextDepth++ );
		this.createEmptyMovieClip("_mcDrawAreaBorders",
			nextDepth++ );
		_mcDrawArea.setMask( _mcDrawAreaMask );

		// create selected bar
		this.createEmptyMovieClip( "_mcSelected", nextDepth++ );
		_mcSelected._visible = false;

		// create the title text label
		var textFormat:TextFormat = new TextFormat();
		textFormat.font = "GraphTitleFont";
		textFormat.size = 11;
		textFormat.align = "center";

		var titleHeight:Number =
			1.5 * textFormat.getTextExtent( "Ay" ).textFieldHeight;

		this.createTextField( "_mcText", nextDepth++,
			0, 0,
			_mcSelected._width, titleHeight );
		_mcText.autoSize = "height";
		_mcText.selectable = false;
		_mcText.setTextFormat( textFormat );
		_mcText.setNewTextFormat( textFormat );
		_mcText.text = "GraphTitle";
		_mcText.embedFonts = true;

		var titleHeight:Number = _mcText._height;

		_mcSelected.lineStyle( 0, 0x000000, 0 );
		_mcSelected.beginGradientFill( "linear", [0xECF8FD, 0x47BFED, 0xECF8FD],
			[100, 100, 100], [0, 128, 255],
			{matrixType:"box",
				x:0, y:0,
				w:_width, h:titleHeight,
				r:0 } );
		BWUtils.drawRect( _mcSelected, 0, 0, _width, titleHeight );
		_mcSelected.endFill();
	}

	/**
	 * Assign event handlers
	 */
	private function initDrawAreaMask()
	{
		//debug( "initDrawAreaMask", "setting event handlers" );
		// Check for double clicks
		// Note: This event handler assigns members to the _mcDrawArea
		//       MovieClip. These variables are NOT part of the GraphMC
		//       class.
		_mcDrawAreaMask.onPress = function()
		{
			var clickTime:Number = getTimer();
			var clickX:Number = this._xmouse;
			var clickY:Number = this._ymouse;

			//BWUtils.log( "GraphDrawer._mcDrawAreaMask.onPress: " +
			//	"line canvas clicked" );

			if (this.__lastClickTime != null)
			{
				var clickTimeDiff:Number = clickTime - this.__lastClickTime;
				var clickXDistance:Number = clickX - this.__lastClickX;
				var clickYDistance:Number = clickY - this.__lastClickY;

				// Click distance squared
				var clickDistance2:Number = (clickXDistance * clickXDistance) +
					(clickYDistance * clickYDistance);

				if (clickTimeDiff < 400 && clickDistance2 < 100)
				{
					//BWUtils.log( "GraphDrawer._mcDrawAreaMask.onPress: " +
					//	"doubleclick detected: " +
					//	_parent.onLineMaskDoubleClick );
					_parent.onLineMaskDoubleClick();
				}
				else
				{
					/*
					BWUtils.log( "GraphDrawer._mcDrawAreaMask.onPress: " +
						"clickXDistance = " + clickXDistance + ", " +
						"clickYDistance = " + clickYDistance + ", " +
						"clickDistance2 = " + clickDistance2 + ", " +
						"__lastClickTime = " + this.__lastClickTime + ", " +
						"clickTime = " + clickTime + ", " +
						"clickDiff = " + clickTimeDiff );
					*/
					_parent.onLineMaskMousePress();
				}
			}
			else
			{
				_parent.onLineMaskMousePress();
			}

			this.__lastClickTime = clickTime;
			this.__lastClickX = clickX;
			this.__lastClickY = clickY;
		}

		_mcDrawAreaMask.dragOnMouseUp = function()
		{
			this._parent.endDrag();
		}

		/*_mcDrawAreaMask.onRollOver = function()
		{
			this._parent.doRollOver();
		}*/

	}

	/**
	 * Position elements in the right place
	 */
	private function arrange()
	{
		// Everything but the background is restricted to the internal width,
		// which is basically width minus the margins on either side.
		var internalWidth = __width - 2 * __margin;
		var internalHeight = __height - 2 * __margin;

		// Resize graph background
		_mcBackground.clear();
		_mcBackground.lineStyle( 1, 0x5FC8EF );
		_mcBackground.beginFill( 0xECF8FD );
		BWUtils.drawRect( _mcBackground, 0, 0, __width, __height );
		_mcBackground.endFill();

		// Get margins for the draw area so that we have space for the ticks.
		var leftMargin:Number = _mcYTickDisplay.getTickMargin();
		var bottomMargin:Number = _mcXTickDisplay.getTickMargin();
		var topMargin:Number = _mcText._height;

		// Calculate remaining space for the other elements
		__drawAreaWidth = internalWidth - leftMargin;
		__drawAreaHeight = internalHeight - bottomMargin - topMargin;

		// Now position and size everything
		_mcText._y = __margin;
		_mcText._x = __margin;
		_mcText._width = internalWidth;

		// Selected indicator
		_mcSelected._y = 1; // Don't want to draw over 1 pixel border
		_mcSelected._x = __margin;
		_mcSelected._width = internalWidth;

		// Set line canvas properties
		_mcDrawArea._y = __margin + topMargin + __drawAreaHeight;
		_mcDrawArea._x = __margin + leftMargin;
		_mcDrawArea._yscale = -100;
		_mcDrawArea._xscale = 100;

		// Note: Don't set _mcDrawArea._height or _width.
		//       Why? So that we don't screw up the scale
		//       of the line drawing.

		// Set mask properties
		_mcDrawAreaMask._y = __margin + topMargin;
		_mcDrawAreaMask._x = __margin + leftMargin;

		// Draw mask again, to right dimensions
		_mcDrawAreaMask.clear();
		_mcDrawAreaMask.beginFill( 0x000000 );
		_mcDrawAreaMask.moveTo( 0, 0 );
		_mcDrawAreaMask.lineTo( __drawAreaWidth, 0 );
		_mcDrawAreaMask.lineTo( __drawAreaWidth, __drawAreaHeight );
		_mcDrawAreaMask.lineTo( 0, __drawAreaHeight );
		_mcDrawAreaMask.lineTo( 0, 0 );
		_mcDrawAreaMask.endFill();

		// Set line borders
		_mcDrawAreaBorders._y = __margin + topMargin;
		_mcDrawAreaBorders._x = __margin + leftMargin;

		// Draw line axes
		_mcDrawAreaBorders.clear();
		_mcDrawAreaBorders.lineStyle( 1, 0x000000 );
		_mcDrawAreaBorders.moveTo( 0, 0 );
		_mcDrawAreaBorders.lineTo( 0, __drawAreaHeight );
		_mcDrawAreaBorders.lineTo( __drawAreaWidth, __drawAreaHeight );

		// Draw line background
		_mcDrawAreaBackground._y = __margin + topMargin;
		_mcDrawAreaBackground._x = __margin + leftMargin;
		_mcDrawAreaBackground.clear();
		_mcDrawAreaBackground.beginFill( 0xFBFBFF );
		_mcDrawAreaBackground.lineTo( __drawAreaWidth, 0 );
		_mcDrawAreaBackground.lineTo( __drawAreaWidth, __drawAreaHeight );
		_mcDrawAreaBackground.lineTo( 0, __drawAreaHeight );
		_mcDrawAreaBackground.lineTo( 0, 0 );
		_mcDrawAreaBackground.endFill( );


		// Set the tick display properties
		_mcXTickDisplay._x = __margin + leftMargin;
		_mcXTickDisplay._y = __margin + topMargin;
		_mcXTickDisplay.setSize( internalWidth - leftMargin,
				internalHeight - topMargin );

		_mcYTickDisplay._x = __margin;
		_mcYTickDisplay._y = __margin + topMargin;
		_mcYTickDisplay.setSize( internalWidth,
				internalHeight - topMargin - bottomMargin);
	}

	/**
	 *
	 */
	public function initFunctionRepository()
	{
		__funcRepository = new Object();

		__funcRepository.onLineClick = function()
		{
			debug( "(initFunctionRepository).onLineClick",
				"Line " + this.statId + " was clicked" );
		}

		__funcRepository.onMouseOver = function()
		{
			debug( "(initFunctionRepository).onMouseOver",
				"Line " + this.statId + " was mouse-overed" );
		}
	}

	// Public setters and getters
	// ========================================================================
	/**
	 *
	 */
	public function setId( id:Number )
	{
		__id = id;
	}

	/**
	 *
	 */
	public function get id()
	{
		return __id;
	}

	// Exposed interface functions
	// ========================================================================

	/**
	 * Set title of graph
	 */
	public function setText( text:String )
	{
		//debug( "setText", text );

		if (text != __text)
		{
			__text = text;
			this.updateText();
		}
	}

	/**
	 * Get title of graph
	 */
	public function getText( text:String )
	{
		return __text;
	}

	/**
	 * Set the current time. Time corresponds to the
	 * RIGHT hand side of the graph.
	 */
	public function setCurrentTime( time:Number )
	{
		__currentTime = time;
		 _mcXTickDisplay.setCurrentTime( time );

		this.repositionCanvases();
	}

	/**
	 * Set the current time range in seconds.
	 */
	public function setCurrentRange( timeRange:Number )
	{
		__currentRange = timeRange;
		_mcXTickDisplay.setTimeRange( timeRange );

		this.repositionCanvases();
	}

	/**
	 * Sets the log range received from the server.
	 */
	public function setLogRange( logStartTime:Number, logEndTime:Number )
	{
		//debug( "setLogRange", logStartTime + "-" + logEndTime );
		__logStartTime = logStartTime;
		__logEndTime = logEndTime;
	}

	/**
	 * Get the current time. Time corresponds to the
	 * RIGHT hand side of the graph.
	 */
	public function getCurrentTime()
	{
		return __currentTime;
	}

	/**
	 * Get the current time range in seconds.
	 */
	public function getCurrentRange( )
	{
		return __currentRange;
	}

	/**
	 * Sets whether the current graph is selected or not.
	 */
	public function setSelected( selected:Boolean )
	{
		_mcSelected._visible = selected;
	}

	/**
	 * Sets the size of the graph.
	 */
	public function setSize( width:Number, height:Number )
	{
		if (width != null)
		{
			__width = width;
		}
		if (height != null)
		{
			__height = height;
		}

		this.arrange();
	}


	// Interaction functions below
	// ================================================================

	/**
	 *
	 */
	private function onLineMaskMousePress()
	{
		dispatchEvent({
			type: "onGraphSelected",
			graphId: __id
		});

		beginDrag();
	}

	/**
	 *
	 */
	private function onLineMaskDoubleClick()
	{
	}

	/**
	 * Start mouse panning
	 */
	private function beginDrag()
	{
		__dragStartX = _mcDrawAreaMask._xmouse;
		//debug( "beginDrag" );

		// onMouseMove is global, so we'll just assign to us
		this.onMouseMove = this.doDrag;

		_mcDrawAreaMask.onMouseUp = _mcDrawAreaMask.dragOnMouseUp;
	}

	/**
	 * Starts handling mouse dragging (for panning)
	 */
	private function doDrag()
	{
		//debug( "doDrag" );
		if (_level0._xmouse < 0 || _level0._xmouse > Stage.width)
		{
			//debug( "doDrag", "Cancelling drag" );
			return;
		}

		//__controller.setLockToLatest( false );
		var mouseX:Number = _mcDrawAreaMask._xmouse;
		var xdiff:Number = mouseX - __dragStartX;

		// Drag to the left, means the current time moves forward
		var timeDiff = -xdiff * (__currentRange / __drawAreaWidth);


		dispatchEvent({
			type: "onDrag",
			graphId: __id,
			timediff: timeDiff
		});


		//this.setCurrentTime( __currentTime + timeDiff );

		__dragStartX = _mcDrawAreaMask._xmouse;
	}

	/**
	 * End mouse dragging
	 */
	private function endDrag()
	{
		//debug( "endDrag" );
		delete this.onMouseMove;
		delete _mcDrawAreaMask.onMouseUp;
		__dragStartX = null;
	}

	/**
	 *
	 */
	private function doRollOver()
	{
		//debug( "doRollover" );
	}

	/**
	 * Function to handle when the graph is selected
	 */
	private function onGraphSelect()
	{
		//debug( "onGraphSelect", "unimplemented" );
	}

	// Private methods
	// ========================================================================

	/**
	 * Updates the title of the graph.
	 */
	private function updateText()
	{
		//debug( "updateText", __text );
		_mcText.text = __text;
	}

	/**
	 * Place the canvases in their right positions
	 */
	private function repositionCanvases()
	{
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();
		var viewRange:Number = viewEnd - viewStart;

		_mcDrawArea.clear();

		for (var canvasIndex:Number = 0; canvasIndex < __canvasInUse.length;
				++canvasIndex)
		{
			var canvasInfo:Object = __canvasInUse[canvasIndex];

			var xPos:Number = __drawAreaWidth *
				((canvasInfo.startTime - viewStart) / viewRange);

			//debug( "repositionCanvases",
			//	"Moving canvas which starts at " + canvasInfo.startTime +
			//	" to " + xPos + " (Current view start is: " + viewStart + ")");

			/*
			// - canvas markers
			// TODO: We can get rid of this variable later
			var xPosEnd:Number = __drawAreaWidth *
				((canvasInfo.endTime - viewStart) / viewRange );

			_mcDrawArea.lineStyle(2, 0xFFFF00);
			_mcDrawArea.moveTo(xPos+1,0);
			_mcDrawArea.lineTo(xPos+1,__drawAreaHeight);

			_mcDrawArea.lineStyle(2, 0xFFFF00);
			_mcDrawArea.moveTo(xPosEnd-1,0);
			_mcDrawArea.lineTo(xPosEnd-1,__drawAreaHeight);
			*/

			canvasInfo.mc._x = xPos;
			canvasInfo.mc._y = 0;
		}
		this.drawStartTerminator( 6 /*lineThickness*/,
			0xFF0000 /* lineColour */,
			100 /* lineAlpha*/,
			0x333333 /* fillColour */,
			30 /* fillAlpha */ );
	}

	/**
	 * Creates preset canvases (essentially empty movieclips)
	 * for the canvas pool
	 */
	private function createCanvasPool( poolSize:Number )
	{
		for (var canvasIndex:Number = 0; canvasIndex < poolSize; ++canvasIndex)
		{
			var mcName:String = "canvas" + canvasIndex;
			var mc:MovieClip = _mcDrawArea.createEmptyMovieClip( mcName,
				canvasIndex + 1 // extra higher for the terminator
			);
			mc.cacheAsBitmap = true;

			//debug( "createCanvasPool", "mc: " + mc );

			var canvasInfo:Object = new Object();
			canvasInfo.startTime = null;
			canvasInfo.endTime = null;
			canvasInfo.resolution = null;
			canvasInfo.name = mcName;
			canvasInfo.mc = mc;
			canvasInfo.drawnAt = null;

			__canvasPool.push( canvasInfo );
		}
	}


	/**
	 * Creates a movieclip spanning start time and end time. Returns the index
	 * of the canvas as used in the member array __canvasMcs.
	 */
	private function assignCanvas( startTime:Number, endTime:Number,
			resolution:Number, isPlaceholder:Boolean ):Number
	{
		//debug( "assignCanvas",
		//	"startTime: " + startTime +
		//	", endTime: " + endTime +
		//	", resolution: " + resolution +
		//	", isPlaceholder: " + isPlaceholder );
		//this.printCanvasInfo();

		var canvasInfo:Object;
		var dataRange:Number = endTime - startTime;
		var maxCanvasRange:Number = this.getMaxCanvasRange();

		var chosenCanvasIndex:Number = null;
		var chosenCanvasInfo:Object = null;

		// Check existing canvases to see if we can extend instead of
		// assigning an unused canvas
		for (var canvasIndex:Number = 0; canvasIndex < __canvasInUse.length;
				++canvasIndex)
		{
			canvasInfo = __canvasInUse[canvasIndex];

			var canvasRange:Number = canvasInfo.endTime - canvasInfo.startTime;

			//debug( "assignCanvas",
			//	"Comparing this canvas to existing canvas: " +
			//	canvasInfo.startTime + " - " + canvasInfo.endTime );

			// Shares the same start time
			if ((canvasInfo.startTime == startTime))
			{
				//debug( "assignCanvas", "Repurposing canvas which starts at " +
				// canvasInfo.startTime );
				canvasInfo.mc.clear();
				chosenCanvasInfo = canvasInfo;
				chosenCanvasInfo.startTime = startTime;
				chosenCanvasInfo.endTime = endTime;
				chosenCanvasIndex = canvasIndex;
				break;
			}
			// Can "connect" to an existing canvas
			else if (canvasInfo.endTime == startTime)
			{
				if (canvasRange + dataRange <= maxCanvasRange)
				{
					//debug( "assignCanvas", "Can append to canvas.." );
					chosenCanvasInfo = canvasInfo;
					chosenCanvasInfo.endTime = endTime;
					chosenCanvasIndex = canvasIndex;
					break;
				}
				else
				{
					//debug( "assignCanvas",
					//	"We could append, but then it'd be too long...(" +
					//	(canvasRange + dataRange) + " which is longer than " +
					//	maxCanvasRange + ")" );
				}
			}
			else if (canvasInfo.startTime == endTime)
			{
				if (canvasRange + dataRange <= maxCanvasRange)
				{
					//debug( "assignCanvas", "Can prepend to canvas.." );
					chosenCanvasInfo = canvasInfo;
					canvasInfo.startTime = startTime;
					chosenCanvasIndex = canvasIndex;
					break;
				}
				else
				{
					//debug( "assignCanvas",
					//	"We could append, but then it'd be too long...(" +
					//	(canvasRange + dataRange) + " which is longer than " +
					//	maxCanvasRange + ")" );
				}
			}

			// Engulfs an existing canvas (then use existing canvas instead)
			else if (startTime <= canvasInfo.startTime &&
					endTime >= canvasInfo.endTime)
			{
				//debug( "assignCanvas",
				//	"Repurposing canvas which is overlapped " +
				//	"which starts at " + canvasInfo.startTime );
				canvasInfo.mc.clear();
				chosenCanvasInfo = canvasInfo;
				chosenCanvasInfo.startTime = startTime;
				chosenCanvasInfo.endTime = endTime;
				chosenCanvasIndex = canvasIndex;
				break;
			}

			// Partially overlaps an existing canvas
			else if (startTime >= canvasInfo.endTime &&
					canvasInfo.endTime >= endTime)
			{
				if (canvasInfo.isPlaceholder)
				{
					//debug( "assignCanvas",
					//	"Got placeholder, we're dumping..." );
					canvasInfo.mc.clear();
					chosenCanvasInfo = canvasInfo;
					chosenCanvasInfo.startTime = startTime;
					chosenCanvasInfo.endTime = endTime;
					chosenCanvasIndex = canvasIndex;
					break;
				}
				else
				{
					debug( "assignCanvas", "ERROR: Overlapping canvases?" );
				}
			}

			// Dwarfed by existing canvas
			else if (startTime >= canvasInfo.startTime &&
					endTime <= canvasInfo.endTime)
			{
				if (canvasInfo.isPlaceholder)
				{
					//debug( "assignCanvas",
					//	"Got placeholder, we're dumping..." );
					canvasInfo.mc.clear();
					chosenCanvasInfo = canvasInfo;
					chosenCanvasInfo.startTime = startTime;
					chosenCanvasInfo.endTime = endTime;
					chosenCanvasIndex = canvasIndex;
					break;
				}
				else
				{
					debug( "assignCanvas", "ERROR: Overlapping canvases? " +
						"(dwarf case)" );
					this.printCanvasInfo();
				}
			}
		}

		// Grab an unused canvas from the pool if we can't use an existing one
		if (chosenCanvasIndex == null)
		{
			if (__canvasPool.length > 0)
			{

				// All canvases in canvasPool are fair game for "repurposing"
				chosenCanvasInfo = __canvasPool.shift();
				chosenCanvasInfo.startTime = startTime;
					chosenCanvasInfo.endTime = endTime;

				// Insert into "used" array in order
				chosenCanvasIndex = BWUtils.binaryInsertOnAttribute(
						__canvasInUse, "startTime", chosenCanvasInfo );
			}
			else
			{
				debug( "assignCanvas", "No canvases available for " +
					startTime + " - " + endTime +
					" (Placeholder: " + isPlaceholder + ")" );
				this.printCanvasInfo();
				return null;
			}
		}

		chosenCanvasInfo.resolution = resolution;
		chosenCanvasInfo.drawnAt = this.__currentRange;
		chosenCanvasInfo.isPlaceholder = isPlaceholder;

		this.repositionCanvases();

		return chosenCanvasIndex;
	}


	/**
	 * Draws a line on the canvas, with the specified parameters. The statId
	 * is purely an identifier by which we can later modify the movieclip,
	 * which currently is only by redrawing.
	 */
	private function drawCanvasLine( canvasId:Number, times:Array,
			values:Array, upperBound:Number, statId:String, colour:Number,
			thickness:Number, markerSize:Number, maxDistance:Number )
	{
		var canvasInfo:Object = __canvasInUse[canvasId];

		var mc:MovieClip = canvasInfo.mc;

		var canvasStart:Number = canvasInfo.startTime;
		var canvasEnd:Number = canvasInfo.endTime;
		var canvasRange:Number = canvasEnd - canvasStart;
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();
		var viewRange:Number = viewEnd - viewStart;
		var canvasWidth:Number = (canvasRange / viewRange) * __drawAreaWidth;
		var lastXPos:Number = null;
		var lastYPos:Number = null;

		var yBuffer:Number = thickness / 2;

		// Note: Because the mask obscures the lines on the very edges...
		//       we need to make a 1 pixel buffer on top and bottom.
		var lineDrawHeight:Number = __drawAreaHeight - (2 * yBuffer);

		//debug( "Max distance: " + maxDistance + "s" );
		//debug( "drawCanvasLine", "Drawing line on canvas " +
		//	canvasId + "...mc is " + mc );

		var xPos:Number = (times[0] - canvasStart) * canvasWidth / canvasRange;
		var yPos:Number = yBuffer +
			BWUtils.constrain( values[0], 0, upperBound ) *
				lineDrawHeight / upperBound;

		mc.lineStyle( thickness, colour );

		// Move to first position
		mc.moveTo(xPos, yPos);

		var noData:Boolean = false;
		for (var i:Number = 1; i < times.length; ++i)
		{
			if (values[i] == null)
			{
				noData = true;
				continue;
			}
			lastXPos = xPos;
			lastYPos = yPos;
			yPos = yBuffer + BWUtils.constrain( values[i], 0, upperBound) *
				lineDrawHeight / upperBound;
			xPos = (times[i] - canvasStart) * canvasWidth / canvasRange;
			if (!noData)
			{
				var timeDistance:Number = times[i] - times[i-1];

				if (timeDistance < maxDistance)
				{
					mc.lineTo( xPos, yPos );
				}
				else
				{
					mc.lineStyle( thickness-2, colour, 50 );
					debug("drawCanvasLine", "thickness is: " + (thickness - 2) + " startX is: " + lastXPos + " X is: " + xPos);
					//debug( "drawCanvasLine", "Distance between points is: " + timeDistance + " which exceeds maxDistance of " + maxDistance + "!");
					mc.lineTo( xPos, yPos );
					mc.lineStyle( thickness, colour, 100 );
				}

				if (typeof( markerSize ) == "number" && isFinite( markerSize ))
				{
					// Draw square marker
					mc.lineStyle( 0, colour );
					mc.moveTo( xPos - markerSize, yPos - markerSize);
					mc.lineTo( xPos + markerSize, yPos - markerSize);
					mc.lineTo( xPos + markerSize, yPos + markerSize);
					mc.lineTo( xPos - markerSize, yPos + markerSize);
					mc.lineTo( xPos - markerSize, yPos - markerSize);
					mc.moveTo( xPos, yPos );
					mc.lineStyle( thickness, colour );
				}
			}
			else
			{
				mc.moveTo( xPos, yPos );
			}
			noData = false;
		}
	}

	/**
	 * Draw visual start of log indicator on the graph.
	 */
	private function drawStartTerminator( lineThickness:Number,
			lineColour:Number, lineAlpha:Number,
			fillColour, fillAlpha ):Void
	{
		//debug( "drawStartTerminator",
		//	"thickness = " + thickness +
		//	", colour = " + colour +
		//	", _mcTerminator = " + _mcTerminator +
		//	", __drawAreaHeight = " + __drawAreaHeight );
		var leftTime:Number = __currentTime - __currentRange;

		var terminatorMC:MovieClip = _mcTerminator;
		terminatorMC.clear();

		if (__currentTime - __currentRange < __logStartTime &&
					__logStartTime < __currentTime)
		{

			var xPos:Number = ((__logStartTime - leftTime) / __currentRange) *
				__drawAreaWidth -
				Math.ceil( lineThickness/ 2 );

			terminatorMC.beginFill( fillColour, fillAlpha );
			terminatorMC.moveTo( 0, 0 );
			terminatorMC.lineStyle( 0, fillColour, fillAlpha );
			terminatorMC.lineTo( xPos, 0 );
			terminatorMC.lineStyle( lineThickness, lineColour, lineAlpha );
			terminatorMC.lineTo( xPos, __drawAreaHeight );
			terminatorMC.lineStyle( 0, fillColour, fillAlpha );
			terminatorMC.lineTo( 0, __drawAreaHeight );
			terminatorMC.lineTo( 0, 0 );
			terminatorMC.endFill();

			//debug( "drawStartTerminator", "xPos = " + xPos );
			if (terminatorMC.textField == undefined)
			{
				terminatorMC.createTextField( "textField", 1 );
			}
			var textFormat:TextFormat = new TextFormat();
			var textField = terminatorMC.textField;
			textField.setTextFormat( textFormat );
			textField.setNewTextFormat( textFormat );
			textField.setText( "Start" );
			textField._x = xPos;
			textField._y = 0;

		}

	}


	/**
	 * Empties a canvas and places it back in the canvas pool.
	 */
	private function retireCanvas( inUseIndex:Number )
	{
		// Clear it?
		// Move from "InUse" to the pool
		var canvasInfo:Object = __canvasInUse[inUseIndex];
		__canvasInUse.splice(inUseIndex, 1);
		__canvasPool.push(canvasInfo);
		canvasInfo.mc.clear();
		/*
		for (var i:String in canvasInfo.mc)
		{
			if (canvasInfo.mc[i] instanceof MovieClip)
			{
				canvasInfo.mc[i].removeMovieClip();
			}
		}
		*/

		//debug( "retireCanvas", "Movieclip is " + canvasInfo.mc );
	}

	/**
	 * Gets rid of all canvases
	 */
	private function clearCanvases()
	{
		while (__canvasInUse.length > 0)
		{
			this.retireCanvas( 0 );
		}
	}

	/**
	 *
	 */
	private function getMinCanvasRange()
	{
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();
		var viewRange:Number = viewEnd - viewStart;
		var minCanvasRange:Number = viewRange / (__canvasPoolSize - 1);

		return minCanvasRange;
	}

	/**
	 *
	 */
	private function getMaxCanvasRange()
	{
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();
		var viewRange:Number = viewEnd - viewStart;
		var maxCanvasRange:Number = viewRange;

		return maxCanvasRange;
	}

	/**
	 * Get the left hand side of the view.
	 */
	private function getViewStart()
	{
		return __currentTime - __currentRange;
	}

	/**
	 * Get the right hand side of the view.
	 */
	private function getViewEnd()
	{
		return __currentTime;
	}

	private function printCanvasInfo()
	{
		var viewStart:Number = this.getViewStart();
		var viewEnd:Number = this.getViewEnd();
		var viewRange:Number = viewEnd - viewStart;

		BWUtils.log( "Printing canvas information" );
		BWUtils.log( "========================================" );
		// Print further information
		BWUtils.log( " ViewRange: " + viewRange );
		for (var canvasIndex:Number = 0; canvasIndex < __canvasInUse.length;
				++canvasIndex)
		{
			var canvasInfo:Object = __canvasInUse[canvasIndex];
			var canvasLength:Number = canvasInfo.endTime - canvasInfo.startTime;

			BWUtils.log( " " + canvasIndex + ": " +
				"Goes from " + canvasInfo.startTime +
				" to " + canvasInfo.endTime + "( Length: " + canvasLength
				+ ") Placeholder: " + canvasInfo.isPlaceholder );
		}
		BWUtils.log( "========================================" );
	}

}

