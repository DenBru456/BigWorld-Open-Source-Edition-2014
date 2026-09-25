function imageData( imageName ) {
	return IMG( {"src":"../images/"+imageName} );
};

/*
 *	transport: "bigworld", "xmpp", "msn", "aim", "yahoo"
 *	friendType: "online", "offline", "aoi"
 */
function addFriend( name, transport, friendType ) {
	log( "addFriend " + name );
	var body = $( "friend_body" );

	var chatImage = "";

	if (friendType != "offline")
	{
		chatImage = imageData( "chat.png" );
	}

	if (friendType == "aoi")
	{
		var friendImage = imageData( "add_friend.png" );
	}
	else
	{
		var friendImage = imageData( "del_friend.png" );
	}

	body.appendChild(
			TR( {"class": friendType},
				TD( {class: "name"}, name ),
				TD( {class: "transport"}, imageData( transport+".png" ) ),
				TD( {class: "friend"}, friendImage ),
				TD( {class: "chat"}, chatImage ) ) );
};


function addEntity( name, isFriend ) {
	if (isFriend)
	{
		// TODO: Change the state of existing friend entry
		addFriend( name, "bigworld", "online" );
	}
	else
	{
		addFriend( name, "bigworld", "aoi" );
	}
};

// friends.js
