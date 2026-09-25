/**
 * BigWorld mixin class which implements memoization.
 *
 * Usage: In constructor of target class, call
 *   com.bigworldtech.BWMemoize.initialise();
 *
 * This adds the following class members:
 *   __memoize_dict
 *
 * And adds the following class methods:
 *   memoizeCheck( arg1, arg2, arg3... )
 *   memoizeStore( arg1, arg2, arg3... )
 *
 * I don't think there is an Australian spelling
 * of memoize (memoise doesn't look right) so I'm
 * leaving the case in.
 *
 * Lastly, using this mixin class will use a bit more memory
 * and possibly CPU per function call as it stores a separate copy
 * of each memoized variable per function.
 */

class com.bigworldtech.BWMemoize
{
	static private var _fBWMemoize:BWMemoize = undefined;
	static private var __memoizeDictName = "__memoizeDict";
	static private var __memoizeValueName = "__m_value";

	public function BWMemoize()
	{
		return;
	}

	/**
	 * Execute this initialising function in the constructor
	 * (or anywhere, really) of the target object in order
	 * to start using memoize functionality in that object.
	 *
	 * Warning! Australian spelling used for this function name
	 * (as opposed to EventDispatcher.initialize)
	 */
	public static function initialise( obj:Object, allowPrint:Boolean )
	{
		if (_fBWMemoize == undefined)
		{
			_fBWMemoize = new BWMemoize;
		}

		obj[__memoizeDictName] = new Object();
		obj.memoizeCheck = _fBWMemoize.memoizeCheck;
		obj.memoizeValue = _fBWMemoize.memoizeValue;
		obj.memoizeStore = _fBWMemoize.memoizeStore;
		obj.memoizeClear = _fBWMemoize.memoizeClear;
	
		if (allowPrint)
		{
			obj.memoizePrint = _fBWMemoize.memoizePrint;
		}
	}

	/**
	 * Stores any number of variables
	 * for later use with memoizeCheck().
	 *
	 * Takes a arbitrary number of class member names
	 * (strings, which must correspond to class
	 * member variables). 
	 *
	 * NOTE: The last argument is the return value to be memoized
	 */
	public function memoizeStore( funcName:String ) : Void
	{
		if (!this[BWMemoize.__memoizeDictName].hasOwnProperty( funcName ))
		{
			this[BWMemoize.__memoizeDictName][funcName] = new Object();
		}

		var dict:Object = this[BWMemoize.__memoizeDictName][funcName];

		for (var i:Number = 1; i < arguments.length - 1; i++)
		{
			var varName:String = arguments[i];

			/*
			trace( "BWMemoize: (" + funcName + ") Storing " + 
				this[varName] + " into " + varName );
			*/

			// Save the current value of the variable to our dictionary
			dict[varName] = this[varName];
		}

		// The last argument is the function's return value to be stored
		dict[BWMemoize.__memoizeValueName] = arguments[ arguments.length - 1 ];
	}

	/**
	 * Compares all user supplied class member
	 * names with the internal values stored
	 * from the last memoizeStore() call.

	 * Takes a arbitrary number of class member names
	 * (strings, which must correspond to class member
	 * variables).
	 */
	public function memoizeCheck( funcName:String ) : Boolean
	{
		if (!this[BWMemoize.__memoizeDictName].hasOwnProperty( funcName ))
		{
			//trace( "BWMemoize: (" + funcName + ") Nothing stored" );
			return false;
		}

		var dict:Object = this[BWMemoize.__memoizeDictName][funcName];

		for (var i:Number = 1; i < arguments.length; i++)
		{
			var varName:String = arguments[i];

			/*
			trace( " Comparing " + dict[varName] + " to " + 
				this[varName] + " for " + varName );
			trace( " Has own property? " + 
				this.hasOwnProperty( varName ) );
			 */

			// An object's property only seems to exist once it has been
			// directly accessed, so the possibility of this sanity check 
			// being triggered is too high, so we're ignoring.

			/*
			if (!this.hasOwnProperty( varName ))
			{
				trace( "ERROR: (BWMemoize) Target object " + this + " does not have " + 
					"attribute " + varName );
				return false;
			}
			*/

			if ((!dict.hasOwnProperty( varName )) ||
				(dict[varName] != this[varName]))
			{
				/*
				trace( "BWMemoize: (" + funcName + ") " + varName + 
					" has changed from " + dict[varName] + " to " + 
					this[varName] );
				*/
				return false;
			}
		}

		//trace( "BWMemoize: (" + funcName + ") No changes!" );
		return true;
	}

	/**
	 * Retrieves the currently stored return value for the function.
	 * Should be used in conjunction with memoizeCheck to make sure
	 * we can call this function.
	 */
	public function memoizeValue( funcName: String ) : Object
	{
		return this[BWMemoize.__memoizeDictName][funcName]
			[BWMemoize.__memoizeValueName];
	}

	/**
	 * Removes all currently stored values.
	 */
	public function memoizeClear( funcName:String ) : Void
	{
		if (funcName == null)
		{
			for (var i:String in this[BWMemoize.__memoizeDictName])
			{
				delete this[BWMemoize.__memoizeDictName][i];
			}
		}
		else
		{
			for (var i:String in this[BWMemoize.__memoizeDictName][funcName])
			{
				delete this[BWMemoize.__memoizeDictName][funcName][i];
			}
		}
	}

	/**
	 * Prints all memoized values
	 */
	public function memoizePrint( funcName:String ) : Void
	{

		if (funcName == null)
		{
			trace( "Printing all memoized values" );

			for (var func:String in this[BWMemoize.__memoizeDictName])
			{
				trace( "...Function " + func );

				var dict:Object = this[BWMemoize.__memoizeDictName][func];

				for (var varName:String in dict)
				{
					trace( "......" + varName + " = " + dict[varName] );
				}
			}
		}
		else
		{
			trace( "Printing memoized values for function " + func );

			var dict:Object = this[BWMemoize.__memoizeDictName][funcName];

			for (var varName:String in dict)
			{
				trace( "......" + varName + " = " + dict[varName] );
			}
		}
	}
}
