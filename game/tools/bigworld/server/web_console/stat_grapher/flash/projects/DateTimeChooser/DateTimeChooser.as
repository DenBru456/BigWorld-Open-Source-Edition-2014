import mx.controls.DateChooser;
import mx.managers.PopUpManager;
import mx.utils.Delegate;

/**
 * DateTimeChooser component which allows users to choose
 * date and time (minute resolution). Contains a DateChooser
 * and NumericSteppers for selecting time.
 *
 * This component is not resizeable with setSize.
 */
class DateTimeChooser extends MovieClip
{
	// Dimensions
	private var __width:Number;
	private var __height:Number;

	// DateChooser component
	private var _dateChooser:DateChooser;

	// TimeChooser "component" (which has no functionality by itself,
	// so we add it here)
	private var _timeChooser:MovieClip;

	// Accept button
	private var _acceptButton:Button;

	// Cancel button
	private var _cancelButton:Button;

	// Event dispatcher functions
 	public var dispatchEvent:Function;
 	public var addEventListener:Function;
 	public var removeEventListener:Function;

	/**
	 * Constructor.
	 */
	public function DateTimeChooser()
	{
		mx.events.EventDispatcher.initialize(this);

		// Save width, height
		__width = this._width;
		__height = this._height;

		// Enforce default zoom
		this._xscale = 100;
		this._yscale = 100;
	}

	/**
	 * We have to do initialisations involving child elements
	 * in the onLoad handler because they aren't accessible in
	 * the constructor (the constructor is called before the
	 * child elements are created). If we were manually creating
	 * the elements ourselves with attachMovie in the constructor, then we 
	 * wouldn't need to do this but in this case there's not much advantage 
	 * to that approach.
	 */
	public function onLoad()
	{
		_timeChooser.hours.addEventListener("change", 
			Delegate.create(this, onChangeHours));
		_timeChooser.minutes.addEventListener("change", 
			Delegate.create(this, onChangeMinutes));

		this.setupButtons();
		this.setCurrentTime( );
	}

	/**
	 * Set the current time displayed in the chooser.
	 */
	public function setCurrentTime(timestamp:Number)
	{
		// If timestamp is undefined, then it gets the current time
		var d:Date = new Date(timestamp);

		//trace("setting current time to: " + timestamp);

		_dateChooser.selectedDate = d;
		_timeChooser.hours.value = d.getHours();

		//trace("Hours: " + d.getHours() + " Minutes: " + d.getMinutes());;
		_timeChooser.minutes.value = d.getMinutes();
		
		this.makeDoubleDigits( _timeChooser.hours );
		this.makeDoubleDigits( _timeChooser.minutes );
	}

	/**
	 * Makes the NumericStepper object display double digits
	 * instead of a single digit for numbers < 10.
	 * Assumes NumericStepper only contains values > 0
	 *
	 * @ns: Object of type NumericStepper
	 */
	private function makeDoubleDigits( ns:Object )
	{
		if (ns.value < 10)
		{
			ns.inputField.text = "0" + ns.value;
		}
	}

	/**
	 * Event handler for when the user changes the hours NumericStepper.
	 */
	public function onChangeHours(event:Object)
	{
		var d:Date = _dateChooser.selectedDate;
		var hours:Object = _timeChooser.hours;

		// Check overflow (i.e. when value is "24" or "-1",
		// then we carry this overflow and subtract or add a day 
		// in the DateChooser.
		if (hours.value == 24)
		{
			hours.value = 0;
			d.setDate( d.getDate() + 1 );
			_dateChooser.selectedDate = d;
		}
		else if (hours.value == -1)
		{
			hours.value = 23;
			d.setDate( d.getDate() - 1 );
			_dateChooser.selectedDate = d;
		}

		this.makeDoubleDigits( hours );
	}

	/**
	 * Event handler for when the user changes the minutes NumericStepper.
	 */
	public function onChangeMinutes(event:Object)
	{
		var minutes:Object = _timeChooser.minutes;
		var hours:Object = _timeChooser.hours;

		// Check overflow (i.e. when value is "60" or "-1",
		// then we carry this overflow and subtract or add a day 
		// in the hours NumericStepper.
		if (minutes.value == 60)
		{
			minutes.value = 0;
			hours.value = hours.value + 1;
			this.onChangeHours();
		}
		else if (minutes.value == -1)
		{
			minutes.value = 59;
			hours.value = hours.value - 1;
			this.onChangeHours();
		}

		this.makeDoubleDigits( minutes );
	}

	/**
	 * Handle when the user clicks the accept button - then fires an event.
	 */
	private function onAccept()
	{
		var d:Date = _dateChooser.selectedDate;

		d.setHours( _timeChooser.hours.value );
		d.setMinutes( _timeChooser.minutes.value );

		this.dispatchEvent( {type:"accept", date:d} );
	}

	/**
	 * Handle when the user clicks the cancel button - then fires an event.
	 */
	private function onCancel()
	{
		this.dispatchEvent( {type:"cancel"} );
	}

	/**
	 * Setup button event handlers
	 */
	private function setupButtons()
	{
		_acceptButton.onRelease = Delegate.create(this, onAccept);
		_cancelButton.onRelease = Delegate.create(this, onCancel);
	}
}
