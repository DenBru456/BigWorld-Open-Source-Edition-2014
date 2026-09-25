import urllib
import urllib2
import socket
import base64
from simplejson import JSONDecoder

DEFAULT_TIMEOUT = 30

class Response:
	def __init__( self, status_code, text ) :
		self.status_code = status_code
		self.text = text

	def json( self ):
		return JSONDecoder().decode( self.text )

class BetterHTTPErrorProcessor( urllib2.HTTPErrorProcessor ):
	# a substitute/supplement to urllib2.HTTPErrorProcessor
	# that doesn't raise exceptions on status codes 201,204,206
	def http_error_201(self, request, response, code, msg, hdrs):
		return response
	
	def http_error_204(self, request, response, code, msg, hdrs):
		return response
	
	def http_error_206(self, request, response, code, msg, hdrs):
		return response

class NoRedirection( BetterHTTPErrorProcessor ):

	def http_response(self, request, response):
		code, msg, hdrs = response.code, response.msg, response.info()
		return response

def get( url, auth, headers, params, allow_redirects=True, method = None ):
	socket.setdefaulttimeout( DEFAULT_TIMEOUT )
	data = None
	if params:
		data = urllib.urlencode( params, doseq=1 )

	req  = urllib2.Request( url, data, headers )
	if method:
		req.get_method = lambda: method
	if auth:
		base64string = base64.encodestring( '%s:%s' % (auth))[:-1]
		authheader =  "Basic %s" % base64string
		req.add_header("Authorization", authheader)
	opener = None
	if allow_redirects:
		opener = urllib2.build_opener(BetterHTTPErrorProcessor)
	else:
		opener = urllib2.build_opener(NoRedirection)
	f = opener.open( req )

	res = Response( f.code, f.read() )
	socket.setdefaulttimeout( None )
	return res

