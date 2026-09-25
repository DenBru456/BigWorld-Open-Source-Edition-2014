#this script will test batch_compiler 

import sys
import os
import pipes
import subprocess
import re
import optparse

os.chdir(os.path.dirname(os.path.realpath(__file__)))
WARNING = "WARNING:"
FAILED = "FAILED:"
NONE = "NONE"
SUMMARY = "========== Conversion:"
START = "========== Found:"

BATCH_COMPILER_BIN_EXE = "..\\..\\..\\game\\bin\\tools\\asset_pipeline\\win64\\batch_compiler.exe"
BATCH_COMPILER_EXE = "..\\..\\..\\game\\bin\\tools\\asset_pipeline_release\\batch_compiler.exe"

class Log( ):
	def __init__( self, number ):
		self.number = int(number)
		self._output = []
		self.type = NONE
	
	def add( self, line ):
		self._output.append(line)
		if FAILED in line:
			self.type = FAILED
		elif WARNING in line and self.type != FAILED:
			self.type = WARNING

	def __eq__( self, other ):
		return self.number == other.number
		
	def __lt__ (self, other): 
		return self.number < other.number
	
	def __str__(self):
		output=""
		for l in self._output:
			output += l
		return output	
		
class Message( ):
	def __init__( self, number, line ):
		self.number = int(number)
		self.line = line

	def __eq__( self, other ):
		return self.number == other.number
		
	def __lt__ (self, other): 
		return self.number < other.number
	
	def __str__(self):
		return self.line			


def runScript():

	usage = "\npython %prog -d [batch_compiler destination directory]\n"
	
	parser = optparse.OptionParser( usage )
	
	parser.add_option( "-d", "--destination",
			dest = "destination", default="",
			help = "batch_compiler destination directory\n" )
			
	parser.add_option( "-f", "--forceRebuild",
					dest = "forceRebuild", default = False,
					action = "store_true",
					help = "Force Rebuild" )
					
	parser.add_option( "--useLocalExe",
					dest = "useLocalExe", default = False,
					action = "store_true",
					help = "Use game\\bin\\tools\\asset_pipeline\\win64\\batch_compiler.exe" )

						
	(options, args) = parser.parse_args() 
	
	if options.useLocalExe:
		cmd = BATCH_COMPILER_BIN_EXE
	else:
		cmd = BATCH_COMPILER_EXE
	cmd = cmd + " " + options.destination + " -cachePath \\\\ASSETCACHE\\assetcache -j 8"
	if options.forceRebuild:
		cmd = cmd + " -forceRebuild"
	
	print "Running " + cmd

	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	
	output = []	
	summary =""
	for line in iter(p.stdout.readline, ''):
		m = re.search(r'^(\d+)>', line)
		if m:
			number =  m.group(1)
			obj = Message(number, line)
			output.append(obj)
		else:
			if START in line:
				print line
			if SUMMARY in line:
				summary = line

	p.stdout.close()
	output = sorted(output)
	
	logsList = []
	number = -1
	failed = 0
	warning = 0
	
	log = None
	for line in output:
		if line.number > number:
			number = line.number
			if log != None:
				logsList.append(log)
			log = Log(number)
		else:	
			log.add(line.line)
	
	for log in logsList:
		if WARNING == log.type:
			print log
			warning += 1
		if FAILED == log.type:
			print log
			failed += 1

	print summary
	
	return failed
	
if __name__ == "__main__":
	sys.exit( runScript() )