import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

from revision_control import *
import unittest

class TestPerforce(unittest.TestCase):		
	def test_init(self):
		perforceObj = Perforce()
		self.assertTrue( perforceObj.validatePerforce() )
				
	# def test_dir(self):
		# perforceObj = Perforce()
		# self.assertTrue( perforceObj.getDir() == "//ellaz_workspace/bw/2_current/current/..." )
	
	# def test_run(self):
		# perforceObj = Perforce()
		# self.assertTrue( perforceObj.run(0,FormattingPrinter(output = CombinedOutput()))		)
		# self.assertTrue( perforceObj.run("0",FormattingPrinter(output = CombinedOutput()))		)
		
		

if __name__ == '__main__':
	unittest.main()
