import mx.remoting.Service;

import com.macromedia.javascript.JavaScriptProxy;

import com.bigworldtech.LayoutManager;
import com.bigworldtech.BWUtils;
import com.bigworldtech.misc.SimpleDateFormatter;
import mx.utils.Delegate;

// ----------------------------------------------------------------------------
// Section: Globals
// ----------------------------------------------------------------------------

// The JavaScript proxy instance
var jsProxy:JavaScriptProxy = null;
if (_root.flashId)
{
	jsProxy = new JavaScriptProxy( _root.flashId, _root.graphDisplay );
}

function debug( msg:String )
{
	BWUtils.log( "StatGrapher.as: " + msg );
}

// The layout manager
var layoutManager = new LayoutManager();

// Format descriptor for the buttons
var buttonTextFormat:TextFormat = new TextFormat();
buttonTextFormat.font = "ButtonFont";
buttonTextFormat.size = 12;
buttonTextFormat.bold = false;
buttonTextFormat.color = 0x333333;

var labelFormat:TextFormat = new TextFormat();
labelFormat.font = "ToolBarFontBold";
labelFormat.size = 12;
labelFormat.bold = true;
labelFormat.color = 0x333333;

var comboBoxTextFormat:TextFormat = new TextFormat();
comboBoxTextFormat.font = "ToolBarFont";
comboBoxTextFormat.size = 12;
comboBoxTextFormat.bold = false;
comboBoxTextFormat.color = 0x333333;

// Graph display state profiles
var graphDisplayProfiles:Object =
{
	process:	new GraphDisplayState( "TopProc", 		null ),
	machine:	new GraphDisplayState( "TopMachine", 	null )
}

// Zoom level limits
var absoluteZoomLow:Number = 15 * 1000.0;
var absoluteZoomHigh:Number = 365 * 24 * 60 * 60 * 1000;

// zoom levels
var ZOOM_LEVELS:Array =
[
	{	name: "1 minute",	amount: 60 * 1000 },
	{	name: "2 minutes",	amount: 2 * 60 * 1000 },
	{	name: "5 minutes",	amount: 5 * 60 * 1000 },
	{	name: "10 minutes",	amount: 10 * 60 * 1000 },
	{	name: "30 minutes",	amount: 30 * 60 * 1000 },
	{	name: "1 hour",		amount: 60 * 60 * 1000 },
	{	name: "2 hours",	amount:	2 * 60 * 60 * 1000 },
	{	name: "6 hours",	amount: 6 * 60 * 60 * 1000 },
	{	name: "12 hours",	amount:	12 * 60 * 60 * 1000 },
	{	name: "1 day",		amount:	24 * 60 * 60 * 1000 },
	{	name: "3 days",		amount: 3 * 24 * 60 * 60 * 1000 },
	{	name: "1 week",		amount:	7 * 24 * 60 * 60 * 1000 },
	{	name: "2 weeks",	amount:	2 * 7 * 24 * 60 * 60 * 1000 },
	{	name: "1 month",	amount: 30 * 24 * 60 * 60 * 1000 },
	{	name: "3 months",	amount: 3 * 30 * 24 * 60 * 60 * 1000 },
	{ 	name: "6 months",	amount: 6 * 30 * 24 * 60 * 60 * 1000 },
	{ 	name: "1 year",		amount: 365 * 24 * 60 * 60 * 1000 },
	{ 	name: "2 years",	amount: 2 * 365 * 24 * 60 * 60 * 1000 },
	{ 	name: "4 years",	amount: 4 * 365 * 24 * 60 * 60 * 1000 },
	{ 	name: "all",		amount: null }
];

var ZOOM_LEVEL_DEFAULT:Number = 1;

// ----------------------------------------------------------------------------
// Section: Helper functions
// ----------------------------------------------------------------------------

/**
 *	Helper function to retrieve values from FlashVars and put them in the
 *	_root namespace.
 *
 *	@param varName the variable name
 *	@param defaultValue the value returned if the variable does not exist
 */
function getFlashParam( varName, defaultValue )
{
	_root[varName] = (_level0[varName] != undefined) ?
		_level0[varName] : defaultValue;
}

/**
 *	Set the zoom level / view range.
 *
 *	@param index 	index into ZOOM_LEVELS.
 */
function setZoomLevel( index:Number ):Void
{
	var comboBox:MovieClip = _root.zoomLevelComboBox;
	if (0 <= index && index < ZOOM_LEVELS.length)
	{
		//BWUtils.log( "setZoomLevel: " + index );
		if (comboBox.selectedIndex != index)
		{
			comboBox.selectedIndex = index;
		}
		if (ZOOM_LEVELS[index].amount != null)
		{
			_root.graphDisplay.setCurrentRange( ZOOM_LEVELS[index].amount );
		}
		else
		{
			var logBounds:Array = _root.graphDisplay.getLogBounds();
			var logRange:Number = logBounds.end - logBounds.start;
			//BWUtils.log( "oListener.change: logRange = " + logRange );
			_root.graphDisplay.setCurrentRange(  1.1 * logRange );
		}

		if (_root.useDemoButtons)
		{
			// Update the state of the zoom in / out buttons
			_root.zoomState = index;
			updateButtonState();
		}
	}

}


/**
 *	Updates the zoom in / out buttons to enable or disable them based on
 *	the current zoom level.
 */
function updateButtonState()
{
	//BWUtils.log( "updateButtonState: " + _root.zoomState );
	//BWUtils.log( "  upper is: " + ZOOM_LEVELS.length );

	if (_root.zoomState <= 0)
	{
		_root.zoomInButton.enabled = false;
	}
	else
	{
		_root.zoomInButton.enabled = true;
	}

	if (_root.zoomState >= (ZOOM_LEVELS.length - 1))
	{
		_root.zoomOutButton.enabled = false;
	}
	else
	{
		_root.zoomOutButton.enabled = true;
	}
	toolBar.update();
}



// ----------------------------------------------------------------------------
// Section: main function
// ----------------------------------------------------------------------------

function main()
{
	getFlashParam( "serviceURL", "http://toolbox:8080/statg/graph/amfgateway" );
	getFlashParam( "user", "" );
	getFlashParam( "logName", "bw_stat_log_data1" );
	getFlashParam( "profile", "machine" );
	getFlashParam( "desiredPointsPerView", "80" );
	getFlashParam( "minGraphWidth", "250" );
	getFlashParam( "minGraphHeight", "200" );
	getFlashParam( "bwdebug", "false" );

	// Activate debug statements over FlashJS
	if (_root.bwdebug == "true")
	{
		BWUtils.setLogger( jsProxy, "flashDebug" );
	}

	debug( "=== StatGrapher is running ===" );
	debug( "flashId:                " + _root.flashId );
	debug( "serviceURL:             " + _root.serviceURL );
	debug( "user:                   " + _root.user );
	debug( "logName:                " + _root.logName );
	debug( "profile:                " + _root.profile );
	debug( "desiredPointsPerView:   " + _root.desiredPointsPerView );
	debug( "bwdebug:                " + _root.bwdebug );
	debug( "minGraphDimensions:     " + _root.minGraphWidth + "x" +
		_root.minGraphHeight );

	var contextMenu:ContextMenu = new ContextMenu();
	contextMenu.hideBuiltInItems();
	this.menu = contextMenu;

	/*
	// periodic reporting
	var varReporter:Object = new Object();
	varReporter.onTimer = function():Void
	{
		debug( "varReporter: " + BWUtils.childMovieClipsToString( _root, 6 ) );
	}
	varReporter.intervalID = setInterval( varReporter, "onTimer", 15000 );
	*/

	// Clear labels
	_root.samplePeriodLabel.text = _root.timeLabel.text = '';

	// Setup event handlers
	// ========================================================================

	// set up various event handlers from our child components
	var oListener:Object = new Object();

	oListener.onVelocityDrag = function( oEvent:Object ) : Void
	{
		var time = _root.graphDisplay.getCurrentTime();

		_root.graphDisplay.setCurrentTime( time + oEvent.change );
		updateAfterEvent();

	};

	oListener.onTimeRulerDrag = function( oEvent:Object ) : Void
	{
		var currentTime = oEvent.time;

		_root.graphDisplay.setCurrentTime( currentTime );
	}

	oListener.onChooseDate = function( oEvent:Object ) : Void
	{
		_root.graphDisplay.setCurrentTime( oEvent.date.getTime() );
	}

	oListener.onShowDateTimePopup = function( oEvent:Object ) : Void
	{
		var currentTime:Number = _root.graphDisplay.getCurrentTime();
		//trace("Date is : " + currentTime);
		_root.dateTimePopup.setCurrentTime( currentTime );
	}

	oListener.onChangeTime = function( oEvent:Object ) : Void
	{
		//debug("StatGrapher.onChangeTime");

		// Print the current date
		var currentViewTime:Date = new Date( oEvent.time );

		timeLabel.text = SimpleDateFormatter.formatDate(
				currentViewTime, "E yyyy-MM-dd HH:mm:ss" );
		//dateField.selectedDate = currentViewTime;

		// Update the lines and make new remote requests
		//_root.graphDisplay.update();

		updateAfterEvent();

		// Inform legend of new updated statistics
		_root.graphDisplay.getCurrentStats();
		//jsProxy.call( "setCurrentStats", currentStats );
	}

	oListener.onSnapToEnd = function( oEvent:Object ) : Void
	{
		snapToEndButton.toggle = oEvent.snap;
		//debug( "Setting lock to " + oEvent.lock );
	}

	oListener.onChangeRange = function( oEvent:Object ) : Void
	{
		//debug( "StatGrapher.main.oListener.onChangeRange: New range: " +
		//	range );
		//BWUtils.printObject( oEvent );
		var range = oEvent.range;
		_root.velocityBar.setViewRange( range );
	}

	oListener.onGraphSelected = function( oEvent:Object ) : Void
	{
		jsProxy.call( "setLegendType", oEvent.category );
		_root.graphDisplay.getCurrentStats();
	}

	oListener.onReceivePrefTree = function( oEvent:Object ) : Void
	{
		jsProxy.call( "setPrefTree", oEvent.prefTree );
	}

	oListener.onReceiveDisplayPrefs = function( oEvent:Object ) : Void
	{
		// debug( "Calling jsProxy.setDisplayPrefs: " + oEvent.prefs );
		jsProxy.call( "setDisplayPrefs", oEvent.prefs );
	}

	oListener.onGetCurrentStats = function( oEvent:Object ) : Void
	{
		jsProxy.call( "setCurrentStats", oEvent.stats );
	}

/*
	oListener.onDrillUp = function( oEvent:Object ) : Void
	{
	}

	oListener.onDrillDown = function( oEvent:Object ) : Void
	{
	}
*/

	_root.velocityBar.addEventListener( "onVelocityDrag", oListener );

	_root.dateTimePopup.addEventListener( "accept", 
			Delegate.create(oListener, oListener.onChooseDate) );
	_root.dateTimePopup.addEventListener( "onShow", 
			Delegate.create(oListener, oListener.onShowDateTimePopup) );

	_root.graphDisplay.setDesiredPointsPerView(
		_root.desiredPointsPerView );
	_root.graphDisplay.addEventListener( "onChangeTime", oListener );
	_root.graphDisplay.addEventListener( "onSnapToEnd", oListener );
	_root.graphDisplay.addEventListener( "onChangeRange", oListener );
	_root.graphDisplay.addEventListener( "onGraphSelected", oListener );
	_root.graphDisplay.addEventListener( "onReceivePrefTree",
		oListener );
	_root.graphDisplay.addEventListener( "onReceiveDisplayPrefs",
		oListener );
	_root.graphDisplay.addEventListener( "onGetCurrentStats",
		oListener );
	_root.graphDisplay.addEventListener( "onReceiveLogRange",
		oListener );
	_root.graphDisplay.addEventListener( "onGraphStateChanged",
		oListener );
	//_root.graphDisplay.addEventListener( "onDrillUp", oListener );
	//_root.graphDisplay.addEventListener( "onDrillDown", oListener );

	// setup the toolbar

	// drill up button
	var drillUpButton:StatGrapherButton = toolBar.addIconButton(
		"BackButtonGraphic" );
	drillUpButton.enabled = false;
	drillUpButton.onReleaseFn = function()
	{
		_root.graphDisplay.goUpState();
	}

	// legend button
	var legendButton:Object = toolBar.addTextButton( "Legend",
		buttonTextFormat, StatGrapherToolBar.ALIGN_RIGHT );
	legendButton.setToggleButton( true );
	legendButton.toggle = false;

	legendButton.onReleaseFn = function()
	{
		//var prefTree = _root.graphDisplay.getPrefTree();
		//var colours = _root.graphDisplay.getColourTree();
		// debug( "legendButton: PrefTree before sending: " + prefTree );
		if (this.toggle)
		{
			jsProxy.call( "showLegend" );
		}
		else
		{
			jsProxy.call( "hideLegend" );
		}
	}
	//legendButton.addEventListener( "click", buttonListener );

	// snap to end button
	var snapToEndButton:Object = toolBar.addTextButton(
		"Snap To End", buttonTextFormat, StatGrapherToolBar.ALIGN_RIGHT );
	//snapToEndButton.setToggleButton( true );
	snapToEndButton.setToggleButton( true );
	snapToEndButton.toggle = true;
	snapToEndButton.onReleaseFn = function( eventObject:Object )
	{
		_root.graphDisplay.setSnapToEnd( this.toggle );
	}
	//snapToEndButton.addEventListener( "click", buttonListener );

	// show ServiceApps button
	if (_root.profile == "process")
	{
		var showServiceAppsButton:Object = toolBar.addTextButton(
			"ServiceApps", buttonTextFormat, StatGrapherToolBar.ALIGN_RIGHT );
		showServiceAppsButton.setToggleButton( true );
		showServiceAppsButton.toggle = false;
		showServiceAppsButton.onReleaseFn = function( eventObject:Object )
		{
			_root.graphDisplay.setShowServiceApps( this.toggle );
			_root.graphDisplay.__graphController.recreateGraphs();
		}
	}

	oListener.onGraphStateChanged = function( oEvent:Object ):Void
	{
		//debug( "oListener.onGraphStateChanged" );
		drillUpButton.enabled = !oEvent.isRoot;
		graphTitle.text = _root.graphDisplay.getTitle();
		showServiceAppsButton.enabled =
			(_root.graphDisplay.getGraphType() == "TopProc");
	}

	// listener for "change" from zoom level combobox
	oListener.change = function( eventObject:Object ):Void
	{
		//BWUtils.log( "oListener.change: " + eventObject.target );
		if (eventObject.target == zoomLevelComboBox)
		{
			setZoomLevel( zoomLevelComboBox.selectedIndex );
		}
		/*
		else if (eventObject.target == dateField)
		{
			var currentTime:Date = new Date(
				_root.graphDisplay.getCurrentTime() );

			var selectedDate:Date = dateField.selectedDate;

			if (selectedDate == undefined or currentTime == selectedDate)
			{
				return;
			}
			var logRange:Object = _root.graphDisplay.getLogRange();

			//selectedDate.setUTCHours( currentTime.getUTCHours() );
			//selectedDate.setUTCMinutes( currentTime.getUTCMinutes() );
			//selectedDate.setUTCSeconds( currentTime.getUTCSeconds() );

			BWUtils.log( "oListener.change: selectedDate: " + selectedDate );
			if (selectedDate > logRange)
			{
				_root.graphDisplay.setCurrentTime( logRange["end"] );
				_root.graphDisplay.setSnapToEnd( true );
			}
			else
			{
				_root.graphDisplay.setCurrentTime(
					selectedDate.getTime() );
				_root.graphDisplay.setSnapToEnd( false );
			}
		}
		*/

	}
	// set up the zoom level combobox
	_root.zoomLevelComboBox = toolBar.addComboBox(
		StatGrapherToolBar.ALIGN_RIGHT,
		{ _width: 90 },
		comboBoxTextFormat );

	var zoomLevelComboBox:MovieClip = _root.zoomLevelComboBox;
	zoomLevelComboBox.focusEnabled = false;
	zoomLevelComboBox.setStyle( "themeColor", "haloOrange" );
	zoomLevelComboBox.setStyle( "rollOverColor", 0xFEC792 );
	zoomLevelComboBox.setStyle( "selectionColor", 0xFF8000 );
	zoomLevelComboBox.setStyle( "textSelectedColor", 0xFFFFFF );
	zoomLevelComboBox.dataProvider = ZOOM_LEVELS;
	zoomLevelComboBox.rowCount = ZOOM_LEVELS.length;
	zoomLevelComboBox.selectedItem = ZOOM_LEVELS[ZOOM_LEVEL_DEFAULT];
	zoomLevelComboBox.labelFunction = function( itemObj ):String
	{
		return itemObj.name;
	}
	zoomLevelComboBox.addEventListener( "change", oListener );
	zoomLevelComboBox.focusEnabled = false;

	// zoom level arrow up/down handler
	var zoomLevelKeyListener:Object = new Object();
	zoomLevelKeyListener.onKeyUp = function()
	{
		var key:Number = Key.getCode();
		if (key == Key.UP)
		{
			setZoomLevel( zoomLevelComboBox.selectedIndex - 1,
				zoomLevelComboBox );
		}
		else if (key == Key.DOWN )
		{
			setZoomLevel( zoomLevelComboBox.selectedIndex + 1,
				zoomLevelComboBox );
		}
	}

	Key.addListener( zoomLevelKeyListener );

	/* NOTE: This code is left in place but disabled in case
		it is needed again at some point for a trade show. It doesn't
		really make sense to use in any other context as it confuses
		the interface.
	*/
	_root.useDemoButtons = false;

	if (_root.useDemoButtons)
	{
		_root.zoomState = ZOOM_LEVEL_DEFAULT;

		var zoomOutButton:StatGrapherButton = toolBar.addIconButton(
			"ZoomOutButtonGraphic", StatGrapherToolBar.ALIGN_RIGHT );
		_root.zoomOutButton = zoomOutButton;
		_root.zoomOutButton.setToggleButton( false );
		_root.zoomOutButton.onReleaseFn = function()
		{
			//BWUtils.log( "zoomOutButton.onRelease: " + _root.zoomState );

			_root.zoomState++;
			setZoomLevel( _root.zoomState );
		}

		var zoomInButton:StatGrapherButton = toolBar.addIconButton(
			"ZoomInButtonGraphic", StatGrapherToolBar.ALIGN_RIGHT );
		_root.zoomInButton = zoomInButton;
		_root.zoomInButton.setToggleButton( false );
		_root.zoomInButton.onReleaseFn = function()
		{
			//BWUtils.log( "zoomInButton.onRelease: " + _root.zoomState );

			_root.zoomState--;
			setZoomLevel( _root.zoomState );
		}
	}

	// zoom level label
	var labelTextField:TextField = toolBar.addLabel(
		"View range:", labelFormat, StatGrapherToolBar.ALIGN_RIGHT );


	// date field
	/* TODO: put this back in later on
	var dateField:MovieClip = toolBar.addDateField(
		StatGrapherToolBar.ALIGN_RIGHT,
		{ _width: 120 },
		comboBoxTextFormat );

	dateField.dateFormatter = function( d:Date )
	{
		return SimpleDateFormatter.formatDate( d, "E yyyy-MM-dd" );
	}

	dateField.addEventListener( "change", oListener );
	oListener.onReceiveLogRange = function( eventObject:Object ):Void
	{
		var logRanges:Object = eventObject.value;
		//BWUtils.log( "oListener.onReceiveLogRange: " +
		//	BWUtils.objectToString( logRanges ) );

		dateField.disabledRanges = [
			{rangeEnd:		new Date( logRanges.start - 24 * 60 * 60 * 1000)},
			{rangeStart:	new Date( logRanges.end + 24 * 60 * 60 * 1000)}
		];
	}
	*/

	oListener.onChooseResolution = function( oEvent:Object ):Void
	{
		/*
		BWUtils.log( "oListener.onChooseResolution: window ID = " +
			oEvent.windowIndex );
		BWUtils.log( "oListener.onChooseResolution: " +
			"window sample period ticks = " +
			oEvent.windowPref.samplePeriodTicks );
		*/
		_root.samplePeriodLabel.text = "Data point period: " +
			SimpleDateFormatter.formatDuration(
				oEvent.windowSampleTime, true );
		if (oEvent.windowSampleTicks > 1)
		{
			_root.samplePeriodLabel.text += " (" +
				oEvent.windowSampleTicks +
				" samples aggregated per data point)";
		}


	}
	_root.graphDisplay.addEventListener( "onChooseResolution", oListener );


	// Setup layout
	// ========================================================================
	// set up the components with the layout manager
	toolBar.setSize( _root.velocityBar._width, 35 );
	layoutManager.addItem( _root.toolBar,
		LayoutManager.ALIGN_LEFT |
		LayoutManager.ALIGN_RIGHT |
		LayoutManager.ALIGN_TOP );
	layoutManager.addItem( _root.graphTitle,
		LayoutManager.ALIGN_LEFT |
		LayoutManager.ALIGN_RIGHT |
		LayoutManager.ALIGN_TOP );
	layoutManager.addItem( _root.graphDisplay, LayoutManager.EXPAND );
	layoutManager.addItem( _root.velocityBar,
		LayoutManager.ALIGN_LEFT |
		LayoutManager.ALIGN_RIGHT |
		LayoutManager.ALIGN_BOTTOM );
	layoutManager.addItem( _root.timeLabel, LayoutManager.ALIGN_BOTTOM |
		LayoutManager.ALIGN_RIGHT );
	layoutManager.addItem( _root.samplePeriodLabel,
		LayoutManager.ALIGN_BOTTOM | LayoutManager.ALIGN_LEFT );
	layoutManager.addItem( _root.dateTimePopup, LayoutManager.ALIGN_BOTTOM | 
		LayoutManager.ALIGN_RIGHT );
	layoutManager.trigger();

	// initialise our child GraphDisplay component
	var service:Service = new Service(
		_root.serviceURL, 		// gatewayURI
		null, 					// logger
		"StatGrapherBackend",	// serviceName
		null,					// conn
		null 					// resp
	);

	// Start!
	// ========================================================================
	_root.graphDisplay.setService( service );
	_root.graphDisplay.setLogName( _root.logName );
	_root.graphDisplay.setUser( _root.user );
	_root.graphDisplay.setMinGraphDimensions( _root.minGraphWidth,
		_root.minGraphHeight );
	_root.graphDisplay.initState( graphDisplayProfiles[profile] );
	setZoomLevel( ZOOM_LEVEL_DEFAULT );
	_root.graphDisplay.go();


}

main();

// StatGrapher.as
