import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x

class LogFile:
	def __init__(self):
		self.filename = None
		self.log = None
		
	def open(self,filename,append=False,quiet=False):
		self.quiet = quiet
		self.log = ResMgr.openSection(filename,True)
		if (self.log!=None) and (append==False):
			tags = self.log.keys()
			for i in tags:
				self.log.deleteSection(i)
		self.log.createSection("errors")
		self.log.createSection("info")
		self.log.createSection("warnings")
			
	def root(self):
		return self.log
			
	def save(self):
		if self.log != None:
			self.log.save()
			
	def errorMsg(self,msg):
		if self.log != None:			
			self.root()["errors"].createSection("error").asString = msg
		if not self.quiet:
			print msg
			
	def infoMsg(self,msg):
		if self.log != None:			
			self.root()["info"].createSection("info").asString = msg
		if not self.quiet:
			print msg
			
	def warningMsg(self,msg):
		if self.log != None:			
			self.root()["warnings"].createSection("warning").asString = msg
		if not self.quiet:
			print msg
			
	def output(self):
		for (name,sect) in self.log.items():			
			print "--------------------------------------"
			print name + ":"
			for (key,value) in sect.items():
				print value.asString
		print "--------------------------------------"
			
errorLog = LogFile()