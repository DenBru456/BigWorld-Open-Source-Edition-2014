import mx.remoting.Service;
import mx.remoting.PendingCall;
import mx.rpc.RelayResponder;
import mx.rpc.ResultEvent;
import mx.rpc.FaultEvent;

import com.bigworldtech.BWUtils

import SyncCallbackManager;
import RemotingCallbackManager;

_root.serviceURL = "http://fooby:8080/statg/graph/amfgateway";
_root.logName = "bwlogData1";
_root.user = "1008";

// ============================================================================


var g:Graph = this.attachMovie( "Graph", "blah", getNextHighestDepth() );
g.setCategory( "CellApp" );
g._x = 100;
g._y = 100;


function onDrag( drag:Object )
{
	var amount:Number = drag.timediff;
	//trace("Drag happened! " + amount + "s");

	g.setCurrentTime( g.getCurrentTime() + amount );

	g.update();
}

function receiveData( context:Object, stats:Object )
{
	//trace("blah resolution: " + context.resolution);

	// Enhance stuff
	stats.resolution = context.resolution;
	g.receiveRemoteData( context.requestId, stats );
}

function onRemoteRequestByTicks( request:Object )
{
	trace("Remote request by ticks!");

	var startTicks:Array = request.startTicks;
	var endTicks:Array = request.endTicks;

	for (var i:Number = 0; i < startTicks.length; i++)
	{
		var startTick:Number = startTicks[i];
		var endTick:Number = endTicks[i];
		var context:Object = {
			requestId:request.requestId,
			resolution: request.resolution,
			graphId: request.graphId
		};

		rcm.remoteCall( this, "receiveData", "errorHandler", context, 
			"requestData", [logName, user, "CellApp", null, startTick, 
			endTick, request.resolution] );

		/*var pc:PendingCall = service.requestData(0, logName, user, "CellApp", 
			null, startTick, endTick, request.resolution);

		pc.responder = new RelayResponder(this, "receiveData", "errorHandler");*/
	}
}

function onRemoteRequestByTime( request:Object )
{
	trace("Remote request by time!");
	trace("Resolution: " + request.resolution);

	var startTime:Number = request.startTime;
	var endTime:Array = request.endTime;
	var context:Object = {
		requestId:request.requestId,
		resolution: request.resolution,
		graphId: request.graphId
	};

	trace( "Request id: " + request.requestId );

	rcm.remoteCall( this, "receiveData", "errorHandler", context, "requestDataByTime",
		[logName, user, "CellApp", null, startTime, endTime, request.resolution] );

	//var pc:PendingCall = service.requestDataByTime(0, logName, user, "CellApp", 
	//	null, startTime, endTime, request.resolution);

	//pc.responder = new RelayResponder(this, "receiveData", "errorHandler");

	/*pc = service.requestLogRange(logName);
	pc.responder = new RelayResponder(this, "receiveLogRange", "errorHandler");*/
	
}



g.addEventListener("onDrag", this);
g.addEventListener("onRemoteRequestByTicks", this);
g.addEventListener("onRemoteRequestByTime", this);


zoomIn.onPress = function() {
	g.setCurrentRange( g.getCurrentRange() / 2);
	g.update();
}

zoomOut.onPress = function() {
	g.setCurrentRange( g.getCurrentRange() * 2);
	g.update();
}

update.onPress = function()
{
	trace("\nMANUAL UPDATE CALLED");
	g.update();
}

var service:Service = new Service(
		_root.serviceURL, 	// gatewayURI
		null, 				// logger
		"StatGrapherBackend",	// serviceName
		null,				// conn
		null 				// resp
);

var rcm:RemotingCallbackManager = new RemotingCallbackManager();
rcm.setService(service);

var prefTree:Object;
var displayPrefs:Object;
var logStart:Number;
var logEnd:Number;

var interval:Number;

function receivedData()
{
}

function receiveDisplayPrefs(result:Object)
{
	trace("Received preftree");
	/*for (var i:String in result)
	{
		trace(i + ": " + result[i]);
	}*/
	displayPrefs = result;
}

function receivePrefTree(result:Object)
{
	trace("Received preftree");
	/*for (var i:String in result)
	{
		trace(i + ": " + result[i]);
	}*/
	prefTree = result;
}

function receiveLogRange(result:Object)
{
	trace( "Received log range: " + result.start + " - " + result.end );
	logStart = result.start;
	logEnd = result.end;
}

function pump()
{
	g.update();
}

function helloWorld()
{
	trace("Let's go on!");

	interval = setInterval( this, "pump", 2000 );

	g.setPreferences( prefTree );
	g.setDisplayPreferences( displayPrefs );
	g.setCurrentTime( logEnd );
	g.setCurrentRange( 20 );
	g.update();
}

function errorHandler(fe:FaultEvent)
{
	BWUtils.printPythonError( fe );
}

function initFromServer()
{
	var scm:SyncCallbackManager = new SyncCallbackManager();
	scm.setService(service);

	scm.remoteCall(this, "receivePrefTree", "errorHandler", 
			"requestPrefTree", [logName]);

	scm.remoteCall(this, "receiveDisplayPrefs", "errorHandler", 
			"requestDisplayPrefs", [logName]);

	scm.remoteCall(this, "receiveLogRange", "errorHandler", 
			"requestLogRange", [logName]);

	scm.callOnFinish(this, "helloWorld");
	scm.start();
}

var prefs:Object = {
	tickInterval:2,
	windowPrefs: [
		{samples: 1000, samplePeriodTicks: 1},
		{samples: 1000, samplePeriodTicks: 2},
		{samples: 1000, samplePeriodTicks: 4},
		{samples: 1000, samplePeriodTicks: 8}
		]
};

initFromServer();


/*g.setCurrentTime( g.getCurrentTime() + 60 );
g.update();

g.setCurrentTime( g.getCurrentTime() + 70 );
g.update(2);*/
