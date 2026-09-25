import time
from datetime import datetime

class SilentOutput:
	def message(self, text):
		pass
		
class LogToFileOutput:
	def __init__(self, file):
		self._file = open(file, 'a')
		self._file.write( "Starting log " + str(datetime.now()) + '\n')
		
	def message(self, text):
		self._file.write( text )
		
	def __del__(self):
		self._file.close()

class ConsoleOutput:
	def message(self, text):
		print text

class CombinedOutput:
	def __init__(self, file = 'copy_tool.log'):
		self._console = ConsoleOutput()
		self._logfile = LogToFileOutput(file)
		
	def message(self, text):
		self._console.message(text)
		self._logfile.message(text)
		
class FormattingPrinter:
	def __init__(self, output, verbose = True):
		self._output = output
		self._verbose = verbose
		
	def message(self, text):
		if self._verbose:
			self._output.message(text + "\n")
		
	def warning(self, text):
		self._output.message("\nWARNING: " + text + "\n\n")
		
	def error(self, text):
		self._output.message("\nERROR: " + text + "\n\n")
		