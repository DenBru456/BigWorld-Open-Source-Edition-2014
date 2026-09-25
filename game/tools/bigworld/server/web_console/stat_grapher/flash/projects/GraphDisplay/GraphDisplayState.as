import com.bigworldtech.misc.JSON;

class GraphDisplayState
{
	public var graphType:String;
	public var params:Object;

	public function GraphDisplayState( graphType, params )
	{
		this.graphType = graphType;
		if (params == undefined)
		{
			this.params = new Object();
		}
		else
		{
			this.params = params;
		}
	}

	public function toString()
	{
		var o:Object =
		{
			graphType: 	this.graphType,
			params: 	this.params
		};
		return JSON.stringify( o );
	}

	public static function arrayToString( gsArray:Array )
	{
		var a:Array = new Array();
		for (var i:Number = 0; i < gsArray.length; i++)
		{
			var gs:GraphDisplayState = gsArray[i];
			a.push(
				{
					graphType: 	gs.graphType,
					params: 	gs.params
				}
			);
		}

		return JSON.stringify( a );
	}

	public static function fromString( s:String )
	{
		var o:Object = JSON.parse( s );
		var gs:GraphDisplayState = new GraphDisplayState( o.graphType,
			o.params );
		return gs;
	}

	public static function arrayFromString( s:String )
	{
		var a:Object = JSON.parse( s );

		var gsArray:Array = new Array();
		for (var i:Number = 0; i < a.length; i++)
		{
			gsArray.push( new GraphDisplayState(
				a[i].graphType, a[i].params ) );
		}
		return gsArray;
	}
}
