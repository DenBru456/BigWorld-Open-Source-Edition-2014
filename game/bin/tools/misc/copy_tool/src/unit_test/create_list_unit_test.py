import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from create_list import *
import unittest
from xml.dom.minidom import parse
import shutil

CLIENT_SERVER = os.path.join( "\\\\ba01", "BuildArchive" )
WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
XML_FILE = os.path.join(WORKING_DIR, "test2.xml")
TEST_XML = "<root>\n\
	<test>\n\
		<type file=\"test1\\test.test\"/>\n\
	</test>\n\
	<keep>\n\
		<type file=\"test1\\test2.test\"/>\n\
		<type file=\"bin\\win32\\keep_file\"/>\n\
	</keep>\n\
</root>"

class TestBaseAction(unittest.TestCase):
	def setUp(self):
		root = os.path.join(WORKING_DIR,"test")
		if os.path.exists(root):
			shutil.rmtree(root)
			
		f = open(XML_FILE, 'w')
		f.write(TEST_XML)
		f.close()
	
			
		os.makedirs(root)
		f = open(os.path.join(root,"del_file"), 'w')
		f.close()
		f = open(os.path.join(root,"keep_file"), 'w')
		f.close()
		root = os.path.join(root,"bin")
		os.makedirs(root)
		os.makedirs(os.path.join(root,"win64"))
		root = os.path.join(root,"win32")
		os.makedirs(root)
		f = open(os.path.join(root,"del_file"), 'w')
		f.close()
		f = open(os.path.join(root,"keep_file"), 'w')
		f.close()

	def tearDown(self):	
		os.remove(XML_FILE)
		shutil.rmtree(os.path.join(WORKING_DIR,"test"))
		
	def test_returnListFilesFromPath(self):
		tree = parse( XML_FILE )
		root = tree.getElementsByTagName("root")[0]
		array = []
		for action in root.childNodes:
			if action.nodeName == "test":
				array = returnListFilesFromPath( action.getElementsByTagName( "type" ), 
												os.path.join(WORKING_DIR, "test") )
				
		array_test = [os.path.join( "test1", "test.test" )]

		self.assertTrue( array == array_test )
			
	def test_generateActionsList(self):
		xmlFile = os.path.join( XML_FILE )
		destDir = os.path.join(WORKING_DIR, "test")
		[copyArray, keepArray] = generateActionsList( "test", xmlFile, destDir, destDir)
		copy = [ os.path.join( "test1", "test.test" ) ]
		keep = [ os.path.join( "test1", "test2.test" ), os.path.join( "bin", "win32", "keep_file") ]

		self.assertTrue( copy == copyArray)
		self.assertTrue( keep == keepArray)
		
	def test_buildList(self):
		
		array1 = buildList()
		self.assertTrue( len(array1))
		
		array2 = buildList(SERVER)
		self.assertTrue( len(array2))
		for file in array2:
			self.assertTrue( file.startswith("linux64_"))
			
		array3 = buildList(CLIENT)
		self.assertTrue( len(array3))
		for file in array3:
			self.assertTrue( file.startswith("windows_"))
			
		for file in array1:
			self.assertTrue( file in array2 or file in array3)
		
if __name__ == '__main__':
	unittest.main()
		