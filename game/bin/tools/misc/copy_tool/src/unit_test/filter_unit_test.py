import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from filter import *
import unittest

class TestFilter(unittest.TestCase):	

	def test_check(self):
		filter = ExcludeFilter(r'a')
		self.assertTrue( filter.check( "fadfd" ) )
		self.assertFalse( filter.check( "a" ) )
		
		filter = ExcludeFilter(r'\S*\.pdb$')
		self.assertTrue( filter.check("hi.pdb.txt" ))	
		self.assertFalse( filter.check( os.path.join("c:", "dfdf", "fdfd.pdb" ) ))	
		
		filter = ExcludeFilter(r'^tools\\exporter\\(maya|3dsmax)')
		#filter = ExcludeFilter(r'\S*maya\S+|S*3dsmax\S+')
		self.assertFalse( filter.check( os.path.join("tools", "exporter", "3dsmax3243wer", "trtr.pdb" ) ))	
		#self.assertFalse( filter.check( os.path.join("3dsmax", "fdfd.pdb" ) ))
		#self.assertFalse( filter.check( os.path.join("maya32", "fdfd.pdb" ) ))
		
		
class TestFilterList(unittest.TestCase):	
		
	def test_check(self):
		list = FilterList()
		filter = ExcludeFilter(r'a')
		list.add(filter)
		self.assertTrue( list.check( "fadfd" ) )
		self.assertFalse( list.check( "a" ) )
		
		filter = ExcludeFilter(r'\S*\.pdb$')
		list.add(filter)
		self.assertFalse( list.check( os.path.join("c:", "dfdf", "fdfd.pdb" ) ))	
		
		filter = ExcludeFilter(r'\S*maya\S+|S*3dsmax\S+')
		list.add(filter)
		self.assertFalse( list.check( os.path.join("3dsmax", "fdfd.pdb" ) ))
		self.assertFalse( list.check( os.path.join("maya32", "fdfd.pdb" ) ))

if __name__ == '__main__':
	unittest.main()
		