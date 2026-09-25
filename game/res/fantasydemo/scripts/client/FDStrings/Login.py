LOGIN_ERROR_STRINGS = dict(
	NOT_SET	=								'Not set',
	LOGGED_ON =								'Account Login succeeded',
	CONNECTION_FAILED =						'Login failed: Unable to contact login server',
	DNS_LOOKUP_FAILED =						'Login failed: DNS lookup failed',
	UNKNOWN_ERROR =							'Login failed: Unknown local client error',
	CANCELLED =								'Login failed: Login cancelled',
	ALREADY_ONLINE_LOCALLY =				'Login failed: Already online',
	PUBLIC_KEY_LOOKUP_FAILED =				'Login failed: Public key lookup failed',
	LOGIN_MALFORMED_REQUEST =				'Login failed: Malformed login request',
	LOGIN_BAD_PROTOCOL_VERSION =			'Login failed: Wrong protocol version',
	LOGIN_REJECTED_NO_SUCH_USER =			'Login failed: No such user: %(username)s',
	LOGIN_REJECTED_INVALID_PASSWORD =		'Login failed: Invalid password',
	LOGIN_REJECTED_ALREADY_LOGGED_IN =		'Login failed: Someone with account name %(username)s already logged in',
	LOGIN_REJECTED_BAD_DIGEST =				"Login failed: Client .def files do not match server's",
	LOGIN_REJECTED_DB_GENERAL_FAILURE =		'Login failed: Misc database rejection',
	LOGIN_REJECTED_DB_NOT_READY =			'Login failed: Unable to contact server database',
	LOGIN_REJECTED_ILLEGAL_CHARACTERS =		'Login failed: Illegal characters in user name/password',
	LOGIN_REJECTED_SERVER_NOT_READY =		'Login failed: Server not ready',
	LOGIN_REJECTED_UPDATER_NOT_READY =		'Login failed: Unable to contact Updater',
	LOGIN_REJECTED_NO_BASEAPPS =			'Login failed: Unable to contact BaseApps',
	LOGIN_REJECTED_BASEAPP_OVERLOAD =		'Login failed: BaseApp overloaded',
	LOGIN_REJECTED_CELLAPP_OVERLOAD =		'Login failed: CellApp overloaded',
	LOGIN_REJECTED_BASEAPP_TIMEOUT =		'Login failed: BaseApp timed-out',
	LOGIN_REJECTED_BASEAPPMGR_TIMEOUT =		'Login failed: BaseAppMgr overloaded',
	LOGIN_REJECTED_DBMGR_OVERLOAD =			'Login failed: Database overloaded',
	LOGIN_REJECTED_LOGINS_NOT_ALLOWED =		'Login failed: Logins not allowed',
	LOGIN_REJECTED_RATE_LIMITED =			'Login failed: Logins temporarily rate limited',

	LOGIN_REJECTED_AUTH_SERVICE_NO_SUCH_ACCOUNT =	'Login failed: No such account',
	LOGIN_REJECTED_AUTH_SERVICE_LOGIN_DISALLOWED =	'Login failed: Authenication failed. Sign in again.',
	LOGIN_REJECTED_AUTH_SERVICE_UNREACHABLE =		'Login failed: Authentication service is unreachable',
	LOGIN_REJECTED_AUTH_SERVICE_INVALID_RESPONSE =	'Login failed: Authentication service error',
	LOGIN_REJECTED_AUTH_SERVICE_GENERAL_FAILURE =	'Login failed: Authentication service error',

	LOGIN_REJECTED_NO_LOGINAPP =					'Login failed: Login server is not running',
	LOGIN_REJECTED_NO_LOGINAPP_RESPONSE =			'Login failed: No response from login server',
	LOGIN_REJECTED_NO_BASEAPP_RESPONSE =			'Login failed: %(serverMsg)s',
)

SERVER_COMPONENT_OVERLOADED = \
"""Login failed: %(serverMsg)s

The server component is temporarily overloaded. Try connecting again after waiting for the server load to reduce.
"""

DETAIL_ERROR_STRINGS = dict(
	LOGIN_REJECTED_NO_LOGINAPP_RESPONSE = \
"""Login failed: %(serverMsg)s

This login error occurs when the client does not receive a response from the LoginApp.
Some possible causes include:
- The server or LoginApp is not running
- UDP packets are being blocked due to a firewall on the LoginApp's external interface. There would be no extra activity in the LoginApp logs
- UDP packets from the LoginApp to the client are being blocked due to a client-side firewall. This activity should be seen in the LoginApp logs
- The address that the client is trying to connect to is wrong""",

	LOGIN_REJECTED_NO_BASEAPP_RESPONSE = \
"""Login failed: %(serverMsg)s

This login error occurs when the client does not receive a response from the BaseApp.
Some possible causes include:
- UDP packets from client to BaseApp are being blocked due to a firewall on the BaseApp's external interface. Check the firewall on the BaseApp's external port
- If the server is running behind a NAT:
  - UDP packets are not being directed from the NAT to the BaseApp port
  - UDP packets are being sent to the wrong address. Check the BaseApp IP address that the client is sending to. If this is an internal IP address and an external NAT is expected, networkAddressTranslation settings in bw.xml are incorrect.
- UDP packets are being blocked by a client-side firewall. This is less likely since the LoginApp reply has already been received.""",

	LOGIN_BAD_PROTOCOL_VERSION = \
"""Login failed: %(serverMsg)s

The client and server versions do not match. Make sure you are using the right client for this server.
""",

	LOGIN_REJECTED_BASEAPP_OVERLOAD = SERVER_COMPONENT_OVERLOADED,
	LOGIN_REJECTED_CELLAPP_OVERLOAD = SERVER_COMPONENT_OVERLOADED,
	LOGIN_REJECTED_DBMGR_OVERLOAD = SERVER_COMPONENT_OVERLOADED,

)
