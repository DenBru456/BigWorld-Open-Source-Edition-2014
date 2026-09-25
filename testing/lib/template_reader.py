
class TemplateReader:
	
	
	def __init__( self, templatePath, **kwargs ):
		self.path = templatePath
		self.kwargs = kwargs
		
	
	def read( self ):
		return open( self.path ).read() % self.kwargs
