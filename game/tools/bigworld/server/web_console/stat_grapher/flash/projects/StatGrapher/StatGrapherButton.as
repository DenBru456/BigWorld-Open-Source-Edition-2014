import mx.events.EventDispatcher;

import com.bigworldtech.BWUtils;

/**
 *	Class of buttons in StatGrapher.
 *
 *	Buttons can be either entirely text buttons or icon buttons. In order to
 *	use this button, you must assign the release function to onReleaseFn
 *	instead of onRelease.
 *
 *	Buttons can also be toggled buttons, by calling setToggleButton( true ), in
 *	which case they will be highlighted when toggled, and normal when untoggled.
 *	The state of the toggle can be checked and set via the .toggle property,
 *	which is set prior to calling the release function.
 */
class StatGrapherButton extends MovieClip
{
	// ========================================================================
	// Section: Member variables
	// ========================================================================

	private var _mcBorderMask:MovieClip;
	private var _mcBorderBackground:MovieClip;
	private var _mcButtonMask:MovieClip;
	private var _mcButtonBackground:MovieClip;

	private var __borderColour:Number;
	private var __borderWidth:Number;

	private var __width:Number = 100;
	private var __height:Number = 100;

	private var __clip = null;

	private var __icon:MovieClip = null;

	private var __textField:TextField = null;

	private static var ___QUADWIDTH:Number = 4;

	private var __enabled:Boolean = true;

	/**	The disabled button state overlay clip. */
	private var _mcDisabledOverlay:MovieClip = null;
	/**	The disabled button state mask clip. */
	private var _mcDisabledMask:MovieClip = null;
	/**	The button state. See the STATE_* constants. */

	private var __state:Number = STATE_UP;

	/** Whether this is a toggle button or not. */
	private var __isToggle:Boolean = false;
	/** The toggle state. true = toggle on, false = toggle off. */
	private var __toggleState:Boolean = undefined;

	/**	Whether the button is in a rollover state and should be highlighted. */
	private var __rollOver:Boolean = false;

	/** The release action function. */
	private var __onReleaseFn:Function = null;

	// ========================================================================
	// Section: Static constants
	// ========================================================================
	/**	The margin around the text field for the border and the rollover
	 *	highlight. */
	private static var ___margin = 3;

	/**	The drop shadow distance. */
	private static var ___dropShadowDistance:Number = 0;

	/*	The button states. */
	/**	The up button state. */
	private static var STATE_UP:Number = 0;
	/** The rolled-over button state. */
	private static var STATE_OVER:Number = 1;
	/**	The down button state. */
	private static var STATE_DOWN:Number = 2;

	/* Depths */
	private static var DEPTH_BORDER_BACKGROUND:Number 		= 0;
	private static var DEPTH_BORDER_MASK:Number 			= 1;
	private static var DEPTH_BUTTON_BACKGROUND:Number 		= 2;
	private static var DEPTH_BUTTON_MASK:Number 			= 3;
	private static var DEPTH_CLIP:Number 					= 4;
	private static var DEPTH_DISABLED_OVERLAY:Number 		= 5;
	private static var DEPTH_DISABLED_MASK:Number 			= 6;

	// ========================================================================
	// Section: Functions from EventDispatcher
	// ========================================================================
	public var addEventListener:Function;
	public var removeEventListener:Function;
	private var dispatchEvent:Function;

	// ========================================================================
	// Section: Method implementations
	// ========================================================================

	/**
	 *	Constructor.
	 */
 	public function StatGrapherButton()
	{
		EventDispatcher.initialize( this );

		//this.debug( "(constructor)" );
	}

	private static function debug( context:String, msg:String )
	{
		var out:String = "StatGrapherButton." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	public function init( borderColour:Number, borderWidth:Number )
	{
		__borderColour = borderColour;
		__borderWidth = borderWidth;

		this.createEmptyMovieClip(
			"_mcBorderBackground",
			DEPTH_BORDER_BACKGROUND );

		this.attachMovie(
			"ButtonMask", "_mcBorderMask",
			DEPTH_BORDER_MASK );

		_mcBorderBackground.setMask( _mcBorderMask );
		//_mcBorderBackground._alpha = 20;

		this.attachMovie(
			"ButtonBackground", "_mcButtonBackground",
			DEPTH_BUTTON_BACKGROUND );

		//_mcButtonBackground._alpha = 20;

		this.attachMovie(
			"ButtonMask", "_mcButtonMask",
			DEPTH_BUTTON_MASK );
		_mcButtonBackground.setMask( _mcButtonMask );
		//_mcButtonBackground._alpha = 20;

		//this.debug( "init", "border bg = " + _mcBorderBackground + ", " +
		//	"border mask = " + _mcBorderMask + ", " +
		//	"button background = " + _mcButtonBackground + ", " +
		//	"button mask = " + _mcButtonMask );

		this.createEmptyMovieClip( "_mcDisabledOverlay",
			DEPTH_DISABLED_OVERLAY );
		this.attachMovie( "ButtonMask", "_mcDisabledMask",
			DEPTH_DISABLED_MASK );
		_mcDisabledOverlay.setMask( _mcDisabledMask );

	}

	/**
	 *	Make this button a toggle button.
	 *
	 *	@param isToggle		whether to make this button a toggle button or not
	 *						a toggle button.
	 *	@param initialState	the initial state of the toggle, if this is set
	 *						to be a toggle button, otherwise this parameter
	 *						is ignored.
	 */
	public function setToggleButton( isToggle:Boolean,
			initialState:Boolean ):Void
	{
		__isToggle = isToggle;
		if (__isToggle)
		{
			__toggleState = initialState;
		}
		else
		{
			__toggleState = undefined;
		}
	}



	/**
	 *	Set this button to be an icon button with the specified library clip.
	 *	@param clipName 	the name of the exported movie clip/graphic in the
	 *						library
	 */
	public function setIcon( clipName:String ):Void
	{
		if (__icon != null)
		{
			__icon.removeMovieClip();
		}
		if (__textField != null)
		{
			__textField.removeTextField();
			__textField = null;
		}

		this.attachMovie( clipName, "__icon", DEPTH_CLIP );
		__icon._x = __icon._y = ___margin;
		__clip = __icon;

		setSize( __icon._width + 2 * ___QUADWIDTH,
			__icon._height + 2 * ___QUADWIDTH );

		setState( STATE_UP );
		dispatchEvent( {
			type: "onButtonChangeShape",
			button: this
		});
	}

	/**
	 *	Set this button to be a text button with the given text and text format.
	 *	@param text			the text string
	 *	@param textFormat	the text format
	 *	@param maxWidth		the maximum width of the text field
	 */
	public function setText( text:String, textFormat:TextFormat ):Void
	{
		if (__textField == null)
		{
			this.createTextField( "__textField",
				DEPTH_CLIP,
				0, 0,
				0, 0 );
		}

		if (__icon != null)
		{
			__icon.removeMovieClip();
			__icon = null;
		}
		__clip = __textField;

		var textExtent:Object = textFormat.getTextExtent( text );
		__textField._width = textExtent.textFieldWidth;
		__textField._height = textExtent.textFieldHeight;
		__textField.text = text;
		__textField.embedFonts = true;
		__textField.selectable = false;

		__textField.setTextFormat( textFormat );
		__textField.setNewTextFormat( textFormat );
		__textField.text = text;
		setSize( __textField._width + 2 * ___QUADWIDTH,
			__textField._height + 2 * ___QUADWIDTH );
		setState( STATE_UP, __rollOver );
		dispatchEvent( {
			type: "onButtonChangeShape",
			button: this
		});
	}

	/**
	 *	Set the hit area for this clip based on the size of the current clip and
	 *	the margin.
	 */

	private function setHitArea():Void
	{
/*
		__hitArea.clear();

		__hitArea.beginFill( 0x000000 );
		drawRect( __hitArea, 0, 0,
			__clip._x + __clip._width +
				2 * ___margin,
			__clip._y + __clip._height +
				2 * ___margin,
			undefined, undefined,
			0x000000, 0 );
*/
	}


	/**
	 *	Sets the state of this button, and makes changes to the visuals to
	 *	reflect the new state.
	 *	@param state 		the new state
	 *	@param rollOver		whether we are in rolled-over state
	 */
	private function setState( state:Number, rollOver:Boolean,
			toggleState:Boolean, enabled:Boolean ):Void
	{
		var changed:Boolean = false;

		if (state != undefined and __state != state)
		{
			__state = state;
			changed = true;
		}

		if (rollOver != undefined and __rollOver != rollOver)
		{
			__rollOver = rollOver;
			changed = true;
		}

		if (__isToggle and toggleState != undefined and
				__toggleState != toggleState)
		{
			__toggleState = toggleState;
			changed = true;
		}

		if (enabled != undefined and __enabled != enabled)
		{
			__enabled = enabled;
			__rollOver = false;
			__state = STATE_UP;
			changed = true;
		}

		if (!changed)
		{
			return;
		}

		if (!__enabled)
		{
			__icon.gotoAndStop( 4 );
			_mcButtonBackground.gotoAndStop( 4 );
		}
		else if (state == STATE_DOWN)
		{
			__icon.gotoAndStop( 2 );
			_mcButtonBackground.gotoAndStop( 2 );
		}
		else if (__rollOver)
		{
			__icon.gotoAndStop( 3 );
			_mcButtonBackground.gotoAndStop( 3 );
		}
		else if (__isToggle and __toggleState)
		{
			__icon.gotoAndStop( 2 );
			_mcButtonBackground.gotoAndStop( 2 );
		}
		else
		{
			__icon.gotoAndStop( 1 );
			_mcButtonBackground.gotoAndStop( 1 );
		}

		/*
		if (state != STATE_DOWN)
		{
			// draw the shadow
			__border.lineStyle( ___dropShadowDistance, ___borderColour, 50 );
			var halfShadowDist:Number = ___dropShadowDistance / 2;
			__border.moveTo( 2 * ___margin + __clip._width +
					halfShadowDist,
				halfShadowDist );
			__border.lineTo( 2 * ___margin + __clip._width +
					halfShadowDist,
				2 * ___margin + __clip._height + halfShadowDist );
			__border.lineTo( halfShadowDist,
				2 * ___margin + __clip._height + halfShadowDist );
		}
		*/

	}

	private function recreateMask( maskMC:MovieClip,
			x:Number, y:Number,
			width:Number, height:Number ):Void
	{
		//this.debug( "recreateMask", "mask = " + maskMC +
		//	", (x, y) = (" + x + ", " + y + ")" +
		//	", width x height = " + width + " x " + height );

		var quads:Array = [maskMC._mcTopLeftQuad,
			maskMC._mcTopRightQuad,
			maskMC._mcBottomLeftQuad,
			maskMC._mcBottomRightQuad];

		var quadWidth:Number = Math.min( height / 2, ___QUADWIDTH );
		//this.debug( "recreateMask", "quadWidth = " + quadWidth );
		// reset everything
		maskMC.clear();

		for (var i:Number = 0; i < quads.length; ++i)
		{
			quads[i]._x = x;
			quads[i]._y = y;
			quads[i]._width = quads[i]._height = quadWidth;
		}

		maskMC._mcBottomLeftQuad._y =
			maskMC._mcBottomRightQuad._y =
				y + height - quadWidth;
		maskMC._mcBottomRightQuad._x =
			maskMC._mcTopRightQuad._x =
				x + width - quadWidth;

		drawRect( maskMC,
			x + quadWidth, y,
			width - 2 * quadWidth, height,
			undefined, undefined, undefined,
			0x000000 );

		if (height > 2 * quadWidth)
		{
			drawRect( maskMC, x, y + quadWidth,
				quadWidth, height - 2 * quadWidth,
				undefined, undefined, undefined,
				0x000000 );
			drawRect( maskMC, x + width - quadWidth, y + quadWidth,
				quadWidth, height - 2 * quadWidth,
				undefined, undefined, undefined,
				0x000000 );
		}

		for (var i:Number = 0; i < quads.length; ++i)
		{
			//this.debug( "recreateMask", quads[i] +
			//	", x, y = " + quads[i]._x + ", " + quads[i]._y +
			//	", width x height = " + quads[i]._width +
			//		" x " + quads[i]._height );
		}

	}

	private static function drawRect( mc:MovieClip, x:Number, y:Number,
			width:Number, height:Number,
			lineWidth:Number, lineColour:Number, lineAlpha:Number,
			fillColour:Number, fillAlpha:Number ):Void
	{
		if (fillAlpha == undefined)
		{
			fillAlpha = 100;
		}
		if (fillColour != null and fillColour != undefined)
		{
			mc.beginFill( fillColour, fillAlpha );
		}
		if (lineAlpha == undefined)
		{
			lineAlpha = 100;
		}
		mc.lineStyle( lineWidth, lineColour, lineAlpha );
		BWUtils.drawRect( mc, x, y, width, height );
		mc.endFill();
	}

	private function rearrange():Void
	{
		//this.debug( "rearrange",
		//	"width x height = " + __width + " x " + __height +
		//	", borderWidth = " + __borderWidth );

		_mcBorderBackground.clear();
		drawRect( _mcBorderBackground, 0, 0, __width, __height,
			undefined, undefined, undefined,
			__borderColour, 100 );

		//this.debug( "rearrange",
		//	"_mcBorderMask = " + _mcBorderMask );
		this.recreateMask( _mcBorderMask, 0, 0, __width, __height );

		var buttonWidth:Number = __width - 2 * __borderWidth;
		var buttonHeight:Number = __height - 2 * __borderWidth;

		_mcButtonBackground._y = _mcButtonBackground._x = __borderWidth;
		_mcButtonBackground._width = buttonWidth;
		_mcButtonBackground._height = buttonHeight;

		this.recreateMask( _mcButtonMask, __borderWidth, __borderWidth,
			buttonWidth, buttonHeight );

		this.recreateMask( _mcDisabledMask, 0, 0, __width, __height );

		if (this.__clip)
		{
			this.__clip._x = (__width - __clip._width) / 2;
			this.__clip._y = (__height - __clip._height) / 2;
		}

		setDisabledMask();
		setHitArea();
	}

	/**
	 *	Sets the disabled mask. If the button is disabled, then the
	 *	disabled mask is filled based on the clip and the margin.
	 *	If the button is enabled, then the disabled mask is cleared.
	 */
	private function setDisabledMask():Void
	{
		_mcDisabledOverlay.clear();
		if (!__enabled)
		{
			//this.debug( "setDisabledMask" );
			drawRect(
				_mcDisabledOverlay, 0, 0,
				__width,
				__height,
				undefined, undefined, undefined,
				0xFFFFFF, 60 );
		}
	}


	/**
	 *	Set whether this button is enabled or disabled.
	 *
	 *	@param enabled		if true, set this button to be enabled, otherwise
	 *						set it to be disabled.
	 */
	public function set enabled( enabled:Boolean ):Void
	{
		setState( undefined, undefined, undefined, enabled );
		setDisabledMask();
	}


	/**
	 *	Return whether the button is enabled.
	 */
	public function get enabled():Boolean
	{
		return this.__enabled;
	}

	// ========================================================================
	// Section: Event handlers
	// ========================================================================

	/**
	 *	Rollover event handler.
	 */
	private function onRollOver():Void
	{
		if (!__enabled)
		{
			return;
		}
		setState( STATE_OVER, true );
	}

	/**
	 *	Roll-out event handler.
	 */
	private function onRollOut():Void
	{
		if (!__enabled)
		{
			return;
		}
		setState( STATE_UP, false );
	}


	/**
	 *	Release event handler. After doing checks such as whether it is enabled,
	 *	settings its own visual state, then the user defined release function
	 *	is called.
	 */
	private function onRelease():Void
	{
		//this.debug( "onRelease" );
		if (!__enabled)
		{
			return;
		}

		var toggleState = __toggleState;
		if (__isToggle)
		{
			toggleState = !toggleState;
		}

		setState( STATE_UP, __rollOver, toggleState );
		doOnRelease();
	}

	/**
	 *	Release outside event handler.
	 */
	private function onReleaseOutside():Void
	{
		//this.debug( "onReleaseOutside" );
		if (!__enabled)
		{
			return;
		}
		setState( STATE_UP, false );
	}


	/**
	 *	Check we are enabled and call the release action function if we have
	 *	one.
	 */
	private function doOnRelease():Void
	{
		if (__onReleaseFn != null and __enabled)
		{
			__onReleaseFn();
		}
	}


	/**
	 *	Press event handler. Do not override or replace.
	 */
	private function onPress():Void
	{
		//this.debug( "onPress" );
		setState( STATE_DOWN, true );
	}


	/**
	 *	Mouse-up event handler. Do not override or replace.
	 */
	private function onMouseUp():Void
	{
		//this.debug( "onMouseUp" );
		if (!__enabled)
		{
			return;
		}
		setState( STATE_UP, __rollOver );
	}


	/**
	 *	Set method for the text of the button, if it is a text button.
	 */
	public function set text( text:String ):Void
	{
		if (__textField != null)
		{
			setText( text, __textField.getTextFormat() );
		}
	}


	/**
	 *	Set method for the release action function.
	 *
	 *	@param onReleaseFn 	the release action function
	 */
	public function set onReleaseFn( onReleaseFn:Function ):Void
	{
		__onReleaseFn = onReleaseFn;
	}


	/**
	 *	Get method for the toggle state. Returns null if not a toggle button.
	 */
	public function get toggle():Boolean
	{
		if (!__isToggle)
		{
			return null;
		}
		return __toggleState;
	}


	/**
	 *	Set method for the toggle state. Traces an error if this is not a
	 *	toggle button.
	 */
	public function set toggle( newToggleState:Boolean ):Void
	{
		if (!__isToggle)
		{
			//this.debug( "toggle", "not a toggle button" );
			return;
		}
		setState( undefined, undefined, newToggleState );
	}

	private function setSize( width:Number, height:Number ):Void
	{
		//this.debug( "setSize", "width x height = " + width + " x " + height );
		__width = width;
		__height = height;
		this.rearrange();
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
