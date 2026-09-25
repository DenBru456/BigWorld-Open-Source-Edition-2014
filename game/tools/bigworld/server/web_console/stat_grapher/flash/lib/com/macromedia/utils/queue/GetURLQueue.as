/*
	GetURLQueue.as

	Part of the Flash / JavaScript Integration Kit
	http://www.macromedia.com/go/flashjavascript

	Created by:

	Mike Chambers
	http://weblogs.macromedia.com/mesh/
	mesh@macromedia.com

	Christian Cantrell
	http://weblogs.macromedia.com/cantrell/
	cantrell@macromedia.com

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

class com.macromedia.utils.queue.GetURLQueue extends com.macromedia.utils.queue.FunctionQueue
{
    private static var _instance:GetURLQueue = undefined;

    private function GetURLQueue()
    {
    }

    public static function getInstance():GetURLQueue
    {
        if(GetURLQueue._instance == undefined)
        {
            GetURLQueue._instance = new GetURLQueue();
        }

        return GetURLQueue._instance;
    }

    //supports allarguments supported by getURL
    function addCall(s:String):Void
    {
        var f:Function = super["addCall"];

        arguments.splice(0,0,_root);
        arguments.splice(1,0,"getURL");

        f.apply(super, arguments);
    }

}
