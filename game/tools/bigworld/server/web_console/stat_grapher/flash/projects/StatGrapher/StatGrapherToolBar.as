import com.bigworldtech.BWUtils;

/**
 *	Toolbar clip for StatGrapherButton's. Lines them in a single horizontal
 *	line, vertically centred and supports left and right alignment. Adding
 *	elements from the right will impose a right-to-left order, e.g. the first
 *	right-aligned element is up against the width of the toolbar, the next
 *	right-aligned element is to the left of the first one, and so on.
 */
class StatGrapherToolBar extends MovieClip
{
	/**	The toolbar component clips. */
	private var __clips:Array;
	/**	The alignments of the buttons. See ALIGN_* static constants. */
	private var __clipAligns:Array;
	/**	The spacing between the buttons. */
	private var __spacing:Number;

	/**	The background clip. */
	private var __background:MovieClip;
	/**	The button clip. Buttons, when added, are added to this clip. */
	private var __childrenClip:MovieClip;
	/**	The next button ID. The button clip name is derived from this. */
	private var __nextClipID:Number;

	/**	The nominal width of the toolbar clip. */
	private var __width:Number;
	/**	The nominal height of the toolbar clip. */
	private var __height:Number;

	/** Depth of the next button in __childrenClip */
	private var __nextDepth:Number;

	/**	The background gradient colours of the toolbar clip. */
	private static var ___bgColours:Array =
			//[0xFAC54F, 0xFEECC4]; 	//orange -> white
			[0x1173BA, 0x5FC8EF]; 	//dark blue -> blue
	/**	The background gradient alphas of the toolbar clip. */
	private static var ___bgAlphas:Array = [100, 100];
	/** The background gradient ratios of the toolbar clip. */
	private static var ___bgRatios:Array = [0x0, 0xFF];

	/** Button border width. */
	private static var ___buttonWidth = 1;
	/** Button border colour. */
	private static var ___buttonColour = 0x000000;

	/** The top border colour. */
	private static var ___topBorderColour = 0xFF8000;

	/** The alignment constant for left-aligning. */
	public static var ALIGN_LEFT:Number = 0;
	/** The alignment constant for right-aligning. */
	public static var ALIGN_RIGHT:Number = 1;

	/** Separator width. */
	public static var SEPARATOR_WIDTH:Number = 20; // pixels

	/** The space around the perimeter of the border. */
	private static var ___gutter:Number = 1;

	/**
	 *	The constructor.
	 */
	public function StatGrapherToolBar()
	{
		//debug( "(constructor)" );
		__clips = new Array();
		__clipAligns = new Array();
		__spacing = 5;

		this.createEmptyMovieClip( "__background", 0 );
		this.createEmptyMovieClip( "__childrenClip", 1 );
		__nextDepth = 0;

		__nextClipID = 0;
		//this.trackAsMenu = true;
		//__childrenClip.trackAsMenu = true;
		__width = 0;
		__height = 0;
	}

	private static function debug( context:String, msg:String ):Void
	{
		var out:String = "StatGrapherToolbar." + context;
		if (msg != undefined)
		{
			out += ": " + msg;
		}
		BWUtils.log( out );
	}


	/**
	 *	Sets the nominal size of this tool bar.
	 *
	 *	@param width	the nominal width
	 *	@param height	the nominal height
	 */
	public function setSize( width:Number, height:Number ):Void
	{
		//debug( "setSize( " + width + ", " + height + " )" );
		if (width != null)
		{
			__width = width;
		}
		if (__height != null)
		{
			__height = height;
		}
		update();
		//debug( "setSize( _width = " + _width +
		//	", _height = " + _height + ")" );
	}


	/**
	 *	Set the spacing between the buttons.
	 *
	 *	@param spacing	the new spacing amount in pixels.
	 */
	public function set spacing( spacing:Number ):Void
	{
		__spacing = spacing;
	}


	/**
	 *	Add new button, and return it.
	 *	@param align	the alignment of the new button
	 *	@return			the new StatGrapherButton
	 */
	public function addButton( align:Number ):StatGrapherButton
	{
		if (align == undefined)
		{
			align = ALIGN_LEFT;
		}

		var buttonName:String = "button_" + __nextClipID++;
		__childrenClip.attachMovie( "StatGrapherButton", buttonName,
			__nextDepth++ );
		var button:StatGrapherButton = __childrenClip[buttonName];
		button.init( ___buttonColour, ___buttonWidth );
		button.addEventListener( "onButtonChangeShape", this );
		this.addClip( button, align );
		this.update();
		return button;
	}


	/**
	 *	Adds a ComboBox to the toolbar.
	 *
	 *	@kludge comboboxes are treated like buttons
	 */
	public function addComboBox( align:Number, initObject:Object,
			textFormat:TextFormat ):MovieClip
	{
		var clipID:Number = __nextClipID++;
		var buttonName:String = "combobox_" + clipID;
		var comboBoxName:String = "combo";
		var container:MovieClip = __childrenClip.createEmptyMovieClip(
			buttonName, __nextDepth++ );

		container.attachMovie(
			"ComboBox",
			comboBoxName, 0,
			initObject );

		container.getHeight = function():Number
		{
			var height:Number = this["combo"].textField._height;

			return height;
		}
		container.getWidth = function():Number
		{
			return this["combo"]._width;
		}

		var comboBox:MovieClip = __childrenClip[buttonName].combo;

		if (textFormat != undefined)
		{
			comboBox.setStyle( "fontFamily", textFormat.font );
			comboBox.setStyle( "embedFonts", true );
			comboBox.setStyle( "fontWeight",
				textFormat.bold ? "bold":"none" );
			comboBox.setStyle( "fontStyle",
				textFormat.italic ? "italic":"normal" );
			comboBox.setStyle( "fontSize", textFormat.size );
		}
		this.addClip( container, align );
		this.update();

		//debug( "addComboBox", "container: " + container + " with ID " +
		//	clipID + ", returning comboBox = " + comboBox );
		return comboBox;
	}

	/**
	 *	Add a new icon button with the specified icon.
	 *
	 *	@param iconGraphic	the name of the graphic to use as an icon in the
	 *						library.
	 *	@param align		the alignment of the new button.
	 */
	public function addIconButton( iconGraphic:String,
			align:Number ):StatGrapherButton
	{
		//debug( "addIconButton", "iconGraphic = " + iconGraphic );
		var button:StatGrapherButton = this.addButton( align );
		//debug( "addIconButton", "button = " + button );
		button.setIcon( iconGraphic );
		this.update();
		return button;
	}


	/**
	 *	Add a new text button with the specified text and text format.
	 *
	 *	@param text			the text of the new button
	 *	@param textFormat	the text format of the new button
	 *	@param align		the alignment of the new button.
	 */
	public function addTextButton( text:String,
			textFormat:TextFormat, align:Number ):Object
	{
		//debug( "addTextButton", "text = " + text );

		var button:StatGrapherButton = this.addButton( align );
		//debug( "addTextButton", "button = " + button );

		button.setText( text, textFormat );
		this.update();
		return button;

/*		Use Flash builtin Buttons. Make sure you have the Button UIComponent
		in the Library.

		var textButtonName = "textbutton_" + __nextClipID++;
		var container:MovieClip = __childrenClip.createEmptyMovieClip(
			textButtonName, __nextDepth++ );

		container.attachMovie( "Button", "button", 0, {label:text} );
		container.getWidth = function():Number
		{
			return this["button"]._width;
		}
		container.getHeight = function():Number
		{
			return this["button"]._height;
		}
		var button = container["button"];
		button.setStyle( "themeColor", "haloOrange" );
		this.addClip( container, align );
		this.update();
		return button;
*/
	}


	public function addSeparator( align:Number ):Void
	{
		this.addClip( null, align );
	}

	public function addLabel( text:String, textFormat:TextFormat,
			align:Number ):TextField
	{
		var textFieldName = "text_" + __nextClipID++;
		var container:MovieClip = __childrenClip.createEmptyMovieClip(
			textFieldName, __nextDepth++ );

		container.createTextField(
			"_mcTextField",
			0,
			0, 0, 100, 100 );

		container.getWidth = function():Number
		{
			return this["_mcTextField"]._width;
		}
		container.getHeight = function():Number
		{
			return this["_mcTextField"]._height;
		}

		var textField:TextField = __childrenClip[textFieldName]["_mcTextField"];
		textField.embedFonts = true;
		//textField.antiAliasType = "normal";
		textField.autoSize = true;
		textField.selectable = false;
		textField.setTextFormat( textFormat );
		textField.setNewTextFormat( textFormat );
		textField.text = text;

		this.addClip( container, align );
		this.update();

		return textField;
	}

	public function addClip( clip:Object, align:Number ):Void
	{
		__clips.push( clip );
		if (align == undefined)
		{
			align = ALIGN_LEFT;
		}
		__clipAligns.push( align );
		//debug( "addClip", "clip: " + clip + ", align: " + align );
	}

	/**
	 *	Update the placings of the buttons.
	 */
	private function update():Void
	{
		// debug( "update", __width + "x" + __height );
		var leftX:Number = ___gutter;
		var rightX:Number = __width - ___gutter;
		for (var i:Number = 0; i < __clips.length; ++i)
		{
			var clip:Object = __clips[i];
			var align:Number = __clipAligns[i];
			var clipWidth:Number;
			if (clip)
			{
				clipWidth = clip.getWidth();
			}
			else
			{
				clipWidth = SEPARATOR_WIDTH;
			}

			if (align == ALIGN_LEFT)
			{
				if (clip)
				{
					clip._x = __spacing + leftX;
				}
				leftX += clipWidth + __spacing;
			}
			else
			{	// align == ALIGN_RIGHT
				if (clip)
				{
					clip._x = rightX - (clipWidth + __spacing);
				}
				//debug( "update", "clip " + i + ": rightX = " + rightX );
				rightX -= (clipWidth + __spacing);
			}
			if (clip)
			{
				clip._y = 2 * ___gutter +
					(__height - clip.getHeight()) / 2;
			}
			/*
			debug( "update", "put clip " + i + ": " + clip +
				" at (" + clip._x + ", " + clip._y + "), " +
				"aligned " + (align == ALIGN_LEFT ? 'left':'right') +
					"(" + align +"), " +
				"clipWidth = " + clipWidth + ", " +
				"leftX = " + leftX + ", rightX = " + rightX );
			*/
		}
		updateBackground();
		updateAfterEvent();
	}

	/**
	 *	Update the background clip of the toolbar.
	 */
	private function updateBackground():Void
	{
		// make sure this is divisible by 2
		var topBorderWidth:Number = 1 * 2;
		__background.clear();

		__background.moveTo( 0, topBorderWidth / 2 );
		__background.beginGradientFill( "linear",
			___bgColours, ___bgAlphas, ___bgRatios,
			{
				matrixType: 	'box',
				x: 				0,
				y:				0,
				w:				__width,
				h:				__height,
				r:				0
			} );
		__background.lineStyle( topBorderWidth, ___topBorderColour );
		__background.lineTo( __width,  topBorderWidth / 2 );
		__background.lineStyle( undefined );
		__background.lineTo( __width, __height);
		__background.lineTo( 0, __height );
		__background.lineTo( 0, 0 );
		__background.endFill();

	}


	/**
	 *	Callback from a StatGrapherButton when it changes shape.
	 */
	public function onButtonChangeShape( e:Object ):Void
	{
		this.update();
	}

	/**
	 *	Return the nominal width of this tool bar.
	 */
	public function getWidth():Number
	{
		return __width;
	}

	/**
	 *	Return the nominal height of this tool bar.
	 */
	public function getHeight():Number
	{
		return __height;
	}

}
