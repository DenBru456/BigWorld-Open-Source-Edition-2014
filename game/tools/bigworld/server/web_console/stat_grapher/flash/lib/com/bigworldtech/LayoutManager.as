import com.bigworldtech.BWUtils;

class com.bigworldtech.LayoutManager
{
	private var items:Array;

	public static var ALIGN_TOP:Number 		= 1;
	public static var ALIGN_BOTTOM:Number 	= 2;
	public static var ALIGN_LEFT:Number 	= 4;
	public static var ALIGN_RIGHT:Number 	= 8;

	public static var EXPAND:Number = ALIGN_TOP | ALIGN_BOTTOM | ALIGN_LEFT |
		ALIGN_RIGHT;

	public static var ALIGN_HCENTER:Number	= 16;
	public static var ALIGN_VCENTER:Number 	= 32;

	private var __origWidth:Number;
	private var __origHeight:Number;

	function LayoutManager()
	{
		this.registerResizeEvent();
		this.initStageSize();
		this.items = new Array();
	}

	public function trigger():Void
	{
		this.doResize();
	}

	private function debug( context:String, msg:String ):Void
	{
		var out:String = "LayoutManager." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( msg );
	}

	private function initStageSize():Void
	{
		Stage.scaleMode = "showAll";
		__origWidth = Stage.width;
		__origHeight = Stage.height;
		Stage.scaleMode = "noScale";
	}

	private function registerResizeEvent():Void
	{
		//debug( "registerResizeEvent" );
		var owner:LayoutManager = this;
		var listener:Object = new Object();
		listener.onResize = function()
		{
			owner.doResize();
		}
		Stage.addListener( listener );
	}

	private function doResize():Void
	{
		//debug( "doResize: " +
		//	"Stage.width=" + Stage.width +
		//	", Stage.height=" +  Stage.height );

		for (var i:Number = 0; i < this.items.length; ++i)
		{
			var item:Object = this.items[i];
			var alignType:Number = item.alignType;
			var obj:Object = item.obj;
			var newLeftPos:Number = item.getX();
			var newRightPos:Number = item.getX() + item.getWidth();
			var newTopPos:Number = item.getY();
			var newBottomPos:Number = item.getY() + item.getHeight();

			if (alignType & ALIGN_VCENTER)
			{
				newTopPos = Stage.height / 2 - item.width / 2;
				newBottomPos = newTopPos + item.height;
			}

			if (alignType & ALIGN_HCENTER)
			{
				newLeftPos = (Stage.width / 2) - (item.width / 2);
				newRightPos = newLeftPos + item.width;
			}

			if (alignType & ALIGN_BOTTOM)
			{
				newBottomPos = Stage.height - item.bottomMargin;
				newTopPos = newBottomPos - item.height;
			}

			if (alignType & ALIGN_TOP)
			{
				newTopPos = item.topMargin;
			}

			if (alignType & ALIGN_RIGHT)
			{
				newRightPos = Stage.width - item.rightMargin;
				newLeftPos = newRightPos - item.width;
			}

			if (alignType & ALIGN_LEFT)
			{
				newLeftPos = item.leftMargin;
			}

			/*
			debug( "doResize", item.obj );
			debug( "doResize", "NewTopPos: " + newTopPos );
			debug( "doResize", "NewBottomPos: " + newBottomPos );
			debug( "doResize", "NewLeftPos: " + newLeftPos );
			debug( "doResize", "NewRightPos: " + newRightPos );
			debug( "doResize", "Stage width: " + Stage.width );
			debug( "doResize", "Stage height: " + Stage.height );
			*/

			if (newRightPos < newLeftPos)
			{
				newRightPos = newLeftPos + 1;
			}

			if (newBottomPos < newTopPos)
			{
				newBottomPos = newTopPos + 1;
			}

			var newWidth:Number = newRightPos - newLeftPos;
			var newHeight:Number = newBottomPos - newTopPos;

			item.width = newWidth;
			item.height = newHeight;

			item.setSize( item.width, item.height );
			item.setX( newLeftPos );
			item.setY( newTopPos );
		}

		updateAfterEvent();
	}

	private function _addItem( obj:Object, alignType:Number, stageWidth:Number,
			stageHeight:Number ):Void
	{

		var newItem:Object = new Object();
		newItem.obj = obj;

		//debug( "_addItem", "obj is a MovieClip" );
		newItem.setX = function( x:Number )
		{
			this.obj._x = x;
		}
		newItem.setY = function( y:Number )
		{
			this.obj._y = y;
		}
		newItem.getX = function()
		{
			return this.obj._x;
		}
		newItem.getY = function()
		{
			return this.obj._y;
		}

		newItem.setWidth = function( width:Number )
		{
			this.obj._width = width;
		}
		newItem.setHeight = function( height:Number )
		{
			this.obj._height = height;
		}
		newItem.getWidth = function()
		{
			if (this.obj.getWidth != undefined)
			{
				return this.obj.getWidth();
			}
			return this.obj._width;
		}
		newItem.getHeight = function()
		{
			if (this.obj.getHeight != undefined)
			{
				return this.obj.getHeight();
			}
			return this.obj._height;
		}

		if (obj.setSize != undefined)
		{
			newItem.setSize = function( w:Number, h:Number )
			{
				this.obj.setSize( w, h );
			}
		}
		else
		{
			newItem.setSize = function( w:Number, h:Number )
			{
				this.obj._width = w;
				this.obj._height = h;
			}
		}

		newItem.alignType = alignType;

		newItem.topMargin = newItem.getY();
		newItem.bottomMargin = stageHeight -
			newItem.getHeight() - newItem.getY();
		newItem.leftMargin = newItem.getX();
		newItem.rightMargin = stageWidth -
			newItem.getWidth() - newItem.getX();

		newItem.width = newItem.getWidth();
		newItem.height = newItem.getHeight();

		/*
		debug( "_addItem", "Right margin: " + newItem.rightMargin );
		debug( "_addItem", "Original height: " + this.__origHeight );
		*/
		this.items.push( newItem );
	}

	public function addItem( item:Object, alignType:Number, name:String ):Void
	{
		this._addItem( item, alignType, __origWidth, __origHeight, name );
	}

	public function addRuntimeItem( item:Object, alignType:Number,
			name:String ):Void
	{
		this._addItem( item, alignType, Stage.width, Stage.height, name );
	}
}
