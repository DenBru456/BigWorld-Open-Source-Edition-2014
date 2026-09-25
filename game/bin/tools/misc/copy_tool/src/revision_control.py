import os
import sys
import subprocess
from log import *
	
class Perforce:
	
	def __init__(self):
		self._valid = self._valid()

	def _setDir(self):
		try:
			output = subprocess.check_output("p4 where ...", shell=True)
			# get game root directory, depends on the location of this file
			# to make sure we sync only this location and not the entire workspace
			location = output.split()[1].split("game")[-1] 
			# when we "type p4 where ..."
			# we should get somthing like -
			# //my_pc/bigworld/branches/release/2/current/game/tools/misc/copy_tool/...
			# we will remove game/tools/misc/copy_tool/... and add "..."
			self._perforceDir = output.split()[1].split("game" + location)[0] + "..."
			if self._perforceDir.strip() != "" :
				return True
		except:
			pass
		return False	
			
	def getDir(self):
		return self._perforceDir
		
	def validatePerforce(self ):
		return self._valid
		
	def getWorkspace(self):
		return self._workspace
		
	def _valid(self):
		self._workspace = ""
		try:
			output = subprocess.check_output("p4 info", shell=True)
			for line in output.split("\n"):
				if "Client name:" in line:
					self._workspace = line.split()[-1]
					break
			if self._workspace != "" :
				return self._setDir()
		except:
			pass
		return False
		
	def run(self, changelist, printer):
		if self._valid:
			cmd = "p4 sync " + self._perforceDir
			if str(changelist) != "0":
				cmd = cmd + "@" +str(changelist)
				
			printer.message( cmd )
			try:
				retcode = subprocess.call(cmd, shell=True)
				if retcode == 0:
					return True
				printer.error( cmd + " failed, return value = " + str(retcode) )
			except:
				printer.error( cmd + " failed" )
		return False
		