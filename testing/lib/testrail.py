import urllib2, base64
try:
	import simplejson as json
except ImportError:
	import json

class TestRail( object ):
	
	def __init__( self, server, username, password ):
		self.server = server+"/index.php?/api/v2/"
		base64string = base64.encodestring(
							'%s:%s' % (username, password)).replace('\n', '')
		self.headers = {'Content-Type': 'application/json',
						"Authorization": "Basic %s" % base64string }
		
	def get( self, url):
		req = urllib2.Request( self.server+"/"+url, None, self.headers)
		data = urllib2.urlopen(req).read()
		ret = ""
		if data:
			ret = json.loads( data )
		return ret
		
	
	def post( self, url, params):
		totalURL = self.server +"/" + url
		req = urllib2.Request( totalURL, json.dumps( params ), 
							self.headers)
		data = urllib2.urlopen(req).read()
		ret = ""
		if data:
			ret = json.loads( data )
		return ret

	
if __name__ == "__main__":
	tr = TestRail( "http://testrail.bigworldtech.com", "build", "build" )
	data = tr.get( "get_case/14" )
	print data