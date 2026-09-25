# -------------------------------------------------------------------------
# Section: Stanza Templates
# -------------------------------------------------------------------------

# % ( host )
STREAM_START = """
<stream:stream
  xmlns='jabber:client'
  xmlns:stream='http://etherx.jabber.org/streams'
  to='%s'
  version='1.0'>
"""

STREAM_END = """
</stream:stream>
"""

REGISTRATION_IQ = """
<iq type='get' id='reg1'>
  <query xmlns='jabber:iq:register'/>
</iq>
"""

# % ( user, passwd )
REGISTRATION = """
<iq type='set' id='reg2'>
  <query xmlns='jabber:iq:register'>
    <username>%s</username>
    <password>%s</password>
  </query>
</iq>
"""

AUTHENTICATION_START = """
<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl'
         mechanism='DIGEST-MD5'/>
"""

AUTHENTICATION_RESPONSE = """
<response xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>
%s
</response>
"""

# % ( user, realm, nonce, cnonce, host, response )
AUTHENTICATION_BODY = """username="%s",realm="%s",nonce="%s",cnonce="%s",nc=00000001,qop=auth,digest-uri="xmpp/%s",response=%s,charset=utf-8"""

AUTHENTICATION_END = """
<response xmlns='urn:ietf:params:xml:ns:xmpp-sasl'/>
"""

# % ( resourceName )
BIND_RESOURCE = """
<iq type='set' id='bind_2'>
	<bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'>
		<resource>%s</resource>
	</bind>
</iq>
"""

SESSION = """
<iq type='set' id='sess_1'>
	<session xmlns='urn:ietf:params:xml:ns:xmpp-session'/>
</iq>
"""

# % ( from, to )
MESSAGE = """
<message from='%s' to='%s' xml:lang='en'>
	<body>%s</body>
</message>
"""


PRESENCE = """
<presence/>
"""
def presence():
	return PRESENCE


# % ( from, stanza_id )
QUERY_ROSTER = """
<iq from='%s' type='get' id='%s'>
	<query xmlns='jabber:iq:roster'/>
</iq>
"""
def queryRoster( stanzaID, fromJID ):
	return QUERY_ROSTER % (fromJID, stanzaID)


# % ( from, stanza_id, jid, jid, from, jid )
ROSTER_ADD = """
<iq from='%s' type='set' id='%s'>
  <query xmlns='jabber:iq:roster'>
    <item jid='%s' name='%s'/>
  </query>
</iq>
<presence from='%s' to='%s' type='subscribe'/>
"""

def rosterAdd( stanzaID, senderJID, recipientJID ):
	return ROSTER_ADD % \
			( senderJID, stanzaID, recipientJID,
				recipientJID, senderJID, recipientJID )


ROSTER_SET_REPLY = """
<iq from='%s' to='%s' type='result' id='%s'/>
"""

def rosterSetReply( stanzaID, senderJID, recipientJID ):
	return ROSTER_SET_REPLY % (senderJID, recipientJID, stanzaID)


# % ( id, jid )
ROSTER_DEL = """
<iq type='set' id='%s'>
  <query xmlns='jabber:iq:roster'>
    <item jid='%s' subscription='remove'/>
  </query>
</iq>
"""

def rosterDel( stanzaID, jidToRemove ):
	return ROSTER_DEL % ( stanzaID, jidToRemove )


# % ( from, to )
SUBSCRIBE_ALLOW = """
<presence from='%s' to='%s' xml:lang='en' type='subscribed'/>
"""


# % ( from, gateway )
QUERY_GATEWAY = """
<iq from='%s' to='%s' type='get' id='reg1'>
	<query xmlns='jabber:iq:register'/>
</iq>
"""
def gatewayQuery( senderJID, transportDomain ):
	return QUERY_GATEWAY % ( senderJID, transportDomain )


# % ( from, gateway, username, password )
REGISTER_GATEWAY = """
<iq from='%s' to='%s' type='set' id='%s'>
	<query xmlns='jabber:iq:register'>
		<username>%s</username>
		<password>%s</password>
	</query>
</iq>
"""
def gatewayRegister( stanzaID, senderJID, gateway, username, password ):
	return REGISTER_GATEWAY % \
			( senderJID, gateway, stanzaID, username, password )


# % ( fromJID, toTransportJID, stanzaID )
DEREGISTER_GATEWAY = """
<iq type='set' from='%s' to='%s' id='%s'>
  <query xmlns='jabber:iq:register'>
    <remove/>
  </query>
</iq>
"""
def gatewayDeregister( stanzaID, fromJID, toTransportJID ):
	return DEREGISTER_GATEWAY % (fromJID, toTransportJID, stanzaID)


PRESENCE_SUBSCRIBE = """<presence from='%s' to='%s' type='subscribe'/>"""
def presenceSubscribe( fromJID, toJID ):
	return PRESENCE_SUBSCRIBE % (fromJID, toJID)

