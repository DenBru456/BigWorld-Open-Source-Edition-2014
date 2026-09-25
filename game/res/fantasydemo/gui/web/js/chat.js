var Chat = {};

Chat.MAX_LINES = 60;


Chat.addMsg = function ( msg, msgType ) {
	var out = $( "content" );

	// If it is scrolled to the bottom, stay there
	var isAtBottom = (out.scrollHeight <= out.clientHeight + out.scrollTop);

	if (msgType === undefined) {
		msgType = "say";
	}

	out.appendChild(
			DIV( {"class": msgType},
				SPAN( {"class":"msg"}, msg ) ) );

	while (out.childNodes.length > Chat.MAX_LINES)
	{
		out.removeChild( out.childNodes[0] );
	}


	if (isAtBottom) {
		out.scrollTop = out.scrollHeight - out.clientHeight;
	}
};

var addChatMsg = Chat.addMsg
