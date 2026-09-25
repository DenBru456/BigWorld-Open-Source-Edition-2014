import com.bigworldtech.BWUtils;

class XRulerTick extends MovieClip
{
	// Members
	// ================================================
	private var __height:Number;
	private var __width:Number;
	private var __colour:Number;
	private var __text:String;
	private var __value:Number;
	private var __isMajor:Boolean;

	private static var ___textFormat:TextFormat = null;

	private var _mcTextField:TextField;

	// Methods
	// ================================================
	public function XRulerTick()
	{
		// Default height, will be overridden of course
		__height = 20;
		__width = 0;
		__colour = 0x0000FF;
		__text = "";
		__value = null;
		__isMajor = true;

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
		var out:String = "XRulerTick." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	private function refreshTextFormat()
	{
		if (___textFormat == null)
		{
			debug( "refreshTextFormat", "setting format" );
			var format:TextFormat = new TextFormat();
			format.font = "TickFont";
			format.align = "center";
			format.size = 9;
			format.color = __colour;
			___textFormat = format;
		}
		_mcTextField.setNewTextFormat( ___textFormat );
		_mcTextField.setTextFormat( ___textFormat );
	}

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
		this.draw();
	}

	public function setText( text:String )
	{
		__text = text;

		_mcTextField.text = "";
		this.refreshTextFormat();
		_mcTextField._x = 0;
		_mcTextField.text = text;
		//this.draw();
	}

	public function setColour( colour:Number )
	{
		__colour = colour;
		refreshTextFormat();
		this.draw();
	}

	public function setIsMajor( isMajor:Boolean )
	{
		if (__isMajor != isMajor)
		{
			__isMajor = isMajor;
			this.draw();
		}
	}

	public function draw()
	{
		this.clear();

		// Align text field
		var metrics:Object = ___textFormat.getTextExtent( __text );
		_mcTextField._height = metrics.textFieldHeight;

		// Draw line
		var lineHeight:Number = __height - metrics.textFieldHeight;
		lineStyle( 1, __colour );
		moveTo( 0, 0 );

		if (__isMajor)
		{
			lineTo( 0, lineHeight );
			_mcTextField._y = lineHeight;
		}
		else
		{
			lineTo( 0, lineHeight / 2 );
			_mcTextField._y = lineHeight / 2;
		}
	}

	public function kill()
	{
		_mcTextField.removeTextField();
		this.removeMovieClip();
	}
}

