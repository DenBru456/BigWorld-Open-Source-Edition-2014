import com.bigworldtech.BWUtils;

class YGraphTick extends XGraphTick
{
	private var __tickWidth:Number;
	private var __textMargin:Number;

	// Methods
	// ================================================

	/**
	 * Constructor
	 */
	public function YGraphTick()
	{
		super();

		__height = 0;
		__width = 20;
		__textMargin = 0;

		_mcTextField.autoSize = "none";
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "YGraphTick." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}

	public function setTickWidth( width:Number )
	{
		__tickWidth = width;
	}

	private function makeTextFormat():TextFormat
	{
		var format:TextFormat = new TextFormat();
		format.font = "TickFont";
		format.align = "right";
		format.size = 9;
		format.color = __colour;
		return format;
	}

	public function draw()
	{
		this.clear();

		// Align text field
		/*var metrics:Object = __textFormat.getTextExtent( __text );
		_mcTextField._width = metrics.textFieldHeight;*/
		// Draw line
		//debug( "draw", "line height is: " + lineHeight );
		this.lineStyle( 1, __colour, 20 );
		this.moveTo( __tickWidth, 0 );
		this.lineTo( __width, 0 );
		_mcTextField._x = 0;
		//_mcTextField._y = 0;
		_mcTextField._width = __tickWidth - __textMargin;
	}

	public function setText( text:String )
	{
		super.setText( text );

		var textFieldHeight = _mcTextField._height;
		var newY = -(textFieldHeight / 2) + 5;
		_mcTextField._y = newY;
	}
}
