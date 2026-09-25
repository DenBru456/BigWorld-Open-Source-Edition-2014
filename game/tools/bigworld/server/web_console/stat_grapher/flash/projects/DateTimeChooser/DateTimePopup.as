import DateTimeChooser;
import mx.managers.PopUpManager;
import mx.utils.Delegate;

/**
 * DateTimePopup class which, when clicked on, shows a DateTimeChooser
 * with which the user can select the current time.
 *
 * The date is only accessible via the "accept" event, in the attribute
 * "date". You'll have to add an event listener to the "accept" event.
 *
 * The other event is the "onShow" event, in which we suggest calling
 * setCurrentTime to set the time you want shown when the chooser pops up.
 */
class DateTimePopup extends MovieClip
{
	// Functions automatically defined by Listener
	private var dispatchEvent:Function;
	public var addEventListener:Function;
	public var removeEventListener:Function;

	// DateTimeChooser movieclip
	private var _mcPopup:DateTimeChooser;

	// Icon which shows/hides the popup
	private var _mcIcon:MovieClip;

	// Showing popup
	private var __showingPopup:Boolean;

	// Mouse listener object which contains mouse event handlers
	private var __mouseListener:Object;

	// Dimensions
	private var __width:Number;
	private var __height:Number;

	/*----------------------------------------------------
	 * Methods
	 *----------------------------------------------------*/

	/**
	 * Constructors
	 */
	public function DateTimePopup()
	{
		this.init();
		this.createChildren();
	}

	/**
	 * Initialisation
	 */
	public function init()
	{
		mx.events.EventDispatcher.initialize( this );
		__width = this._width;
		__height = this._height;
		__showingPopup = false;
	}

	/**
	 * Create and configure children objects.
	 */
	public function createChildren()
	{
		// The popup is owned by the _root object and not by us (the icon) for 
		// the following reasons:
		// - We override the onPress event which causes strange things to
		//   happen to the DateTimeChooser mouse interaction.
		// - We want to handle mouse events separately for the popup and for 
		//   us, which we can't do if we own the popup
		_mcPopup = DateTimeChooser(_root.attachMovie("DateTimeChooser", "_mcPopup", 
			this.getNextHighestDepth()));
		_mcPopup.addEventListener( "accept", Delegate.create(this, onAccept) );
		_mcPopup.addEventListener( "cancel", Delegate.create(this, onCancel) );
		_mcPopup._visible = false;
	}

	/**
	 * Change the current time (call before showing the popup - you can call 
	 * this in the "onShow" handler.
	 */
	public function setCurrentTime( time:Number )
	{
		_mcPopup.setCurrentTime( time );
	}

	/**
	 * Shows or hides the popup. If showing, fires an "onShow" event in
	 * which you should probably set the current time.
	 */
	public function showPopup( show:Boolean )
	{
		if (show == __showingPopup) { return; }

		_mcPopup._visible = show;
		__showingPopup = show;

		if (show)
		{
			this.positionPopup();
			this.setupMouseListener();
			this.dispatchEvent( {type:"onShow"} );
		}
		else
		{
			Mouse.removeListener( __mouseListener );
		}
	}

	/**
	 * Positions the popup in the correct place.
	 * TODO: More special case handling at the edges of the stage
	 */
	private function positionPopup()
	{
		var width:Number = _mcPopup._width;
		var height:Number = _mcPopup._height;

		var pt:Object = new Object();

		pt.x = this._x;
		pt.y = this._y;
		this._parent.localToGlobal( pt );

		// Constrain x position to Stage dimensions
		if ((pt.x + width) > _root.width)
		{
			pt.x = _root.width - width;
		}

		_root.globalToLocal( pt );
		_mcPopup._x = pt.x;
		_mcPopup._y = pt.y -_mcPopup._height;
	}

	/**
	 * Creates the mouse listener object to handle mouse events.
	 */
	private function setupMouseListener()
	{
		if (!__mouseListener)
		{
			__mouseListener = new Object();
			__mouseListener.parent = _mcPopup;
			__mouseListener.controller = this;
			__mouseListener.onMouseDown = function()
			{
				var pt:Object = {x:_root._xmouse, y:_root._ymouse}
				//this.controller.tracePt( "rootlocal", pt );
				_root.localToGlobal( pt );
				//this.controller.tracePt( "global", pt );

				if ((!this.parent.hitTest( pt.x, pt.y, false )) and
					(!this.controller.hitTest( pt.x, pt.y, false )))
				{
					this.controller.showPopup( false );
				}
			}
		}
		Mouse.addListener( __mouseListener );
	}

	/*----------------------------------------------------
	 * Event handlers
	 *----------------------------------------------------*/
	/**
	 * onPress event to handle when the user clicks on the icon.
	 */
	public function onPress( )
	{
		// Executes callback on success, with argument datetime
		this.showPopup( !__showingPopup );
	}

	/**
	 * onAccept event to handle when the user clicks the green tick
	 */
	public function onAccept(e:Object)
	{
		var d:Date = e.date;

		//trace("Got date: " + d);
		dispatchEvent( {type:'accept', date:d} );
		this.showPopup( false );
	}

	/**
	 * onCancel event to handle when the user clicks cancel 
	 */
	public function onCancel(e:Object)
	{
		this.showPopup( false );
	}

	/*----------------------------------------------------
	 * Helper functions
	 *----------------------------------------------------*/

	/**
	 * Debug function to print a "point" object
	 */
	private function tracePt( prefix:Object, point:Object )
	{
		if (point == undefined)
		{
			point = prefix;
			prefix = "";
		}
		trace( prefix + " X: " + point.x + " Y: " + point.y );
	}
}
