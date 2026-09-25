var BigWorld = {};

BigWorld.call = function( method, args ) {
	window.statusbar = false;
	var text = "@BW:" + MochiKit.Base.serializeJSON( [method, args] );
	window.status = text;
	window.status = "";
}

/**
* Use this function to call bigworld from flash
* @param   func the function to call
* @param   params the associative container containing the function parameters
* for example flash.external.ExternalInterface.call("callBigWorldFromFlash", "sendMsg", params);
*/
function callBigWorldFromFlash(func, params)
{
	BigWorld.call( func, params );
}

/**
* Use this function to call flash from BigWorld
* @param   func the function to call
* @param   params a param/associative container sent to the flash function
* for example self.js.callFlashFromBigWorld( "insertIntoTextArea", msg )
* Users should implement a getFlashObject function in their html file returning the flash object
* to call
*/
function callFlashFromBigWorld(func, params)
{
	getFlashObject()[func](params)
}
