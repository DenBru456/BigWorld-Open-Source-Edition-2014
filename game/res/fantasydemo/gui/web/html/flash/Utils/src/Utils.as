package {
	import flash.display.Sprite;
 
	public class Utils extends Sprite
	{
	// public method for encoding a string into utf
	public static function toUTF8Array (string:String) :Array {
 
 		var utftext:Array = new Array();
 
		for (var n:int = 0; n < string.length; n++) {
 
			var c:int = string.charCodeAt(n);
 
	  		if (c < 128) {
				utftext.push((int)((c)));
			}
			else if((c > 127) && (c < 2048)) {
				utftext.push((int)(((c >> 6) | 192)));
				utftext.push((int)(((c & 63) | 128)));
			}
			else {
				utftext.push((int)(((c >> 12) | 224)));
				utftext.push((int)((((c >> 6) & 63) | 128)));
				utftext.push((int)(((c & 63) | 128)));
			}
 
		}
 
		return utftext;
	}
 
	// public method for decoding utf into a string
	public static function fromUTF8Array (utftext:Array) : String {
		var string:String = "";
		var i:int = 0;
		var c:int;
		var c1:int; 
		var c2:int;
		var c3:int;
		c3 = c1 = c2 = c = 0;
 
		while ( i < utftext.length ) {
 
			c = utftext[i];
 
			if (c < 128) {
				string += String.fromCharCode(c);
				i++;
			}
			else if((c > 191) && (c < 224)) {
				c2 = utftext[i+1];
				string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
				i += 2;
			}
			else {
				c2 = utftext[i+1];
				c3 = utftext[i+2];
				string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
				i += 3;
			}
 
		}
 
		return string;
		}
	}
}
