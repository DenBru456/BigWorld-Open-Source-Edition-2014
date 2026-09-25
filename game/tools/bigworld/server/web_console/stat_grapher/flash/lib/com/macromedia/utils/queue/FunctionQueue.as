/*
	FunctionQueue.as

	Part of the Flash / JavaScript Integration Kit
	http://www.macromedia.com/go/flashjavascript

	Created by:

	Mike Chambers
	http://weblogs.macromedia.com/mesh/
	mesh@macromedia.com

	Christian Cantrell
	http://weblogs.macromedia.com/cantrell/
	cantrell@macromedia.com

	Modified by:

	Dominic Wong - removed trace messages
	dominicw@bigworldtech.com

	----
	Macromedia(r) Flash(r) JavaScript Integration Kit License


	Copyright (c) 2005 Macromedia, inc. All rights reserved.

	Redistribution and use in source and binary forms, with or without modification,
	are permitted provided that the following conditions are met:

	1. Redistributions of source code must retain the above copyright notice, this
	list of conditions and the following disclaimer.

	2. Redistributions in binary form must reproduce the above copyright notice,
	this list of conditions and the following disclaimer in the documentation and/or
	other materials provided with the distribution.

	3. The end-user documentation included with the redistribution, if any, must
	include the following acknowledgment:

    "This product includes software developed by Macromedia, Inc.
    (http://www.macromedia.com)."

	Alternately, this acknowledgment may appear in the software itself, if and
	wherever such third-party acknowledgments normally appear.

	4. The name Macromedia must not be used to endorse or promote products derived
	from this software without prior written permission. For written permission,
	please contact devrelations@macromedia.com.

	5. Products derived from this software may not be called "Macromedia" or
	"Macromedia Flash", nor may "Macromedia" or "Macromedia Flash" appear in their
	 name.

	THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
	INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
	FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MACROMEDIA OR
	ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
	EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
	OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
	INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
	STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
	OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
	DAMAGE.

*/

//if there is nothing in the queue, should we make it call immediately

class com.macromedia.utils.queue.FunctionQueue
{
    var timer:MovieClip;
    var callQueue:Array = new Array();

    private static var _instance:FunctionQueue = undefined;

    private function FunctionQueue()
    {
        //if fp 7, use this.getNextHighestDepth()

        timer = _root.createEmptyMovieClip("_FunctionQueue805_", 7382);
        timer.scope = this;
    }

    public static function getInstance():FunctionQueue
    {
        if(FunctionQueue._instance == undefined)
        {
            FunctionQueue._instance = new FunctionQueue();
        }

        return FunctionQueue._instance;
    }

    function addCall(scope:Object, functionName:String):Void
    {
        var callObj:Object = new Object();
            callObj.scope = scope;
            callObj.functionName = functionName;

            arguments.shift();
            arguments.shift();

            callObj.args = arguments;

        callQueue.push(callObj);

		//trace( "FunctionQueue.addCall" );

        if(timer.onEnterFrame == undefined)
        {
            timer.onEnterFrame = checkQueue;
        }
    }

    function checkQueue()
    {

        var scope:Object = this["scope"];

        // trace("FunctionQueue.checkQueue:" + scope.callQueue.length);

        if(scope.callQueue.length < 1)
        {
            scope.timer.onEnterFrame = undefined;
            return;
        }

        var o:Object = scope.callQueue.shift();

        var f:Function = o.scope[o.functionName];

		//trace("FunctionQueue.checkQueue: Calling: " +
		//	o.scope + " With args: " + o.args);

		//call the function in the correct scope, passing the arguments
		f.apply(o.scope, o.args);


    }

    function getQueueCount(Void):Number
    {
        return callQueue.length;
    }
}
