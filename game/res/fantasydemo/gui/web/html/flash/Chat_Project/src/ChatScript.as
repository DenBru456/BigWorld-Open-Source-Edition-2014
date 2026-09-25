// ActionScript file


package 
{

    	
 	import flash.display.*;
 	import flash.events.*;
 	import flash.external.*;
 	import flash.net.*;
	
	public class ChatScript
	{
		public function ChatScript(chat:Chat)
		{
			//declare the external called function
			//try to prevent popups when no permissions to use external interface from flash
			try
			{
				ExternalInterface.addCallback("insertIntoTextArea",insertIntoTextArea);
			}
			catch (e:Error)
			{
				
			}
			chat_ = chat;
			chat_.textInput1.addEventListener(flash.events.KeyboardEvent.KEY_DOWN, keyDown)
		}
		public function insertIntoTextArea(msg:Array): void
		{
			chat_.textarea1.text += Utils.fromUTF8Array(msg) + "\n";
			//adjust the scrolling
			chat_.textarea1.validateNow();
			chat_.textarea1.verticalScrollPosition = chat_.textarea1.maxVerticalScrollPosition; 
		}

		public function buttonClicked(msg:String) : void
		{
				//testing
				try
				{
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
				params['msg'] = Utils.toUTF8Array(chat_.textInput1.text);
				chat_.textInput1.text = "";
				//send the string
				try
				{
					flash.external.ExternalInterface.call("callBigWorldFromFlash", "sendMsg", params);
				}
				catch (e:Error)
				{
					
				}
			}
		}
		
		protected var chat_:Chat;
		
	}
}
