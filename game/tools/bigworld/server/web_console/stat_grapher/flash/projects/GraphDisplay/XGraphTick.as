import com.bigworldtech.BWUtils;

class XGraphTick extends MovieClip
{
	private var __height:Number;
	private var __tickHeight:Number;
	private var __width:Number;
	private var __colour:Number;
	private var __text:String;
	private var __textFormat:TextFormat;
	private var __isMajor:Boolean;

	private var _mcTextField:TextField;

	// Methods
	// ================================================
	public function XGraphTick()
	{
		// Default height, will be overridden of course
		__height = 20;
		__width = 0;
		__colour = 0x117eBA;
		__text = "";
		__isMajor = false;

		this.createTextField( "_mcTextField", 0,
				0, __height, 0, 20 );
		_mcTextField._x = 0;
		_mcTextField._y = __height;
		_mcTextField.autoSize = "center";
		_mcTextField.selectable = false;
		_mcTextField.embedFonts = true;

		refreshTextFormat();
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "XGraphTick." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	private function makeTextFormat():TextFormat
	{
		var format:TextFormat = new TextFormat();
		if (__isMajor)
		{
			format.font = "TickFontBold";
			//format.font = "Arial";
		}
		else
		{
			format.font = "TickFont";
			//format.font = "Arial";
		}
		format.align = "center";
		format.size = 9;
		format.color = __colour;
		return format;
	}

	private function refreshTextFormat()
	{
		__textFormat = this.makeTextFormat();
		_mcTextField.setNewTextFormat( __textFormat );
		_mcTextField.setTextFormat( __textFormat );
	}

	public function setSize(width:Number, height:Number)
	{
		//trace("XGraphTick.setSize: Height is " + height );

		if (width != null) {__width = width;}
		if (height != null) {__height = height;}
		this.draw();
	}

	public function setText( text:String )
	{
		__text = text;
		_mcTextField.text = "";
		this.refreshTextFormat();
		_mcTextField._x = 0;
		_mcTextField.text = text;
	}

	public function setColour( colour:Number )
	{
		__colour = colour;
		refreshTextFormat();
		this.draw();
	}

	public function setIsMajor( isMajor:Boolean )
	{
		if ( __isMajor == isMajor )
		{
			return;
		}

		__isMajor = isMajor;
		this.refreshTextFormat();
		this.draw();
	}

	public function setTickHeight( tickHeight:Number )
	{
		__tickHeight = tickHeight;
	}

	public function draw()
	{
		this.clear();

		// Draw line
		var lineHeight:Number = __height - __tickHeight;
		//debug( "draw", "line height is: " + lineHeight );
		this.lineStyle( 1, __colour, 20 );
		//this.lineStyle( 1, __colour );
		this.moveTo( 0,0 );
		this.lineTo( 0, lineHeight );
		_mcTextField._y = lineHeight;
	}


	public function kill()
	{
		_mcTextField.removeTextField();
		this.removeMovieClip();
	}
}
