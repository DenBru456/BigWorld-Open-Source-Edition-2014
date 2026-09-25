// ActionScript file


package 
{

	
 	import flash.display.*;
 	import flash.events.*;
 	import flash.external.*;
 	import flash.net.*;
	import Utils;
		
	public class WebScreenScript
	{
		  
		public function WebScreenScript(webScreen:WebScreenControls)
		{
			//declare the external called function
			try {
				ExternalInterface.addCallback("updateAddress",updateAddress);
			}
			catch (e:Error)
			{
				
			}

			gui_ = webScreen;
			gui_.address.addEventListener(flash.events.KeyboardEvent.KEY_DOWN, keyDown)
		}
		
		public function updateAddress(address:Array): void
		{
			gui_.address.text = Utils.fromUTF8Array(address);
		}

		public function buttonClicked(msg:String) : void
		{
				//testing
				try {
					flash.external.ExternalInterface.call("showMessage",msg)
				}
				catch (e:Error)
				{
					
				}
		}

		public function keyDown(event:KeyboardEvent): void
		{
			if (event.keyCode == 13)
			{
				var params:Object = new Object();
				params['address'] = Utils.toUTF8Array(gui_.address.text);
				try
				{
					//send the string
					flash.external.ExternalInterface.call("callBigWorldFromFlash", "navigate", params);
				}
				catch (e:Error)
				{
					
				}
			}
		}

		public function navigateBack() : void
		{
				//testing
				var params:Object = new Object();
				try {
					flash.external.ExternalInterface.call("callBigWorldFromFlash", "navigateBack",params)
				}
				catch (e:Error)
				{
					
				}
		}

		public function navigateForward() : void
		{
				//testing
				var params:Object = new Object();
				try {
					flash.external.ExternalInterface.call("callBigWorldFromFlash", "navigateForward",params)
				}
				catch (e:Error)
				{
					
				}
		}

		public function exit() : void
		{
				//testing
				var params:Object = new Object();
				try {
					flash.external.ExternalInterface.call("callBigWorldFromFlash", "exit",params)
				}
				catch (e:Error)
				{
					
				}
		}
				
		protected var gui_:WebScreenControls;
	}
}
