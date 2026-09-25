import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from create_build_number_list import *
import unittest
import shutil

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
CLIENT_SERVER =  os.path.join(WORKING_DIR,"test")
BUILD_NAME = "test"
P4_CHANGELIST_NUMBER_FILE = "p4_changelist_number.txt"

class TestBaseAction(unittest.TestCase):		
		
	def setUp(self):
		if os.path.exists(CLIENT_SERVER):
			shutil.rmtree(CLIENT_SERVER)
		
		os.makedirs(CLIENT_SERVER)
		
		clientPath = os.path.join(CLIENT_SERVER,BUILD_NAME) + "_client"
		os.makedirs(clientPath)
		toolsPath = os.path.join(CLIENT_SERVER,BUILD_NAME) + "_tools"
		os.makedirs(toolsPath)
		
		os.makedirs(os.path.join(clientPath,"1"))
		os.makedirs(os.path.join(toolsPath,"1"))
		time.sleep(1)
		
		os.makedirs(os.path.join(toolsPath,"3"))
		f = open(os.path.join( toolsPath,"3", P4_CHANGELIST_NUMBER_FILE ), 'w')
		f.write("1")
		f.close()
		
		os.makedirs(os.path.join(clientPath,"2"))
		f = open(os.path.join( clientPath,"2", P4_CHANGELIST_NUMBER_FILE ), 'w')
		f.write("1")
		f.close()
		time.sleep(1)
		
		os.makedirs(os.path.join(clientPath,"3"))
		f = open(os.path.join( toolsPath,"3", P4_CHANGELIST_NUMBER_FILE ), 'w')
		f.write("1")
		f.close()
		time.sleep(1)
		
		os.makedirs(os.path.join(toolsPath,"4"))
			
	def tearDown(self):	
		shutil.rmtree(CLIENT_SERVER)
		
	def test_createBuildDir(self):
		clientPath = os.path.join(CLIENT_SERVER,BUILD_NAME) + "_client"
		dirPath = os.path.join(clientPath,"1")
		buildDir1 = BuildDir( "0", "1", time.ctime(os.path.getctime(dirPath)))
		self.assertTrue( buildDir1 == createBuildDir(clientPath, "1"))
		
		dirPath = os.path.join(clientPath,"2")
		buildDir2 = BuildDir( "1", "2", time.ctime(os.path.getctime(dirPath)))
		self.assertTrue( buildDir2 == createBuildDir(clientPath, "2"))
		self.assertFalse( buildDir1 == createBuildDir(clientPath, "2"))
		
		toolsPath = os.path.join(CLIENT_SERVER,BUILD_NAME) + "_tools"
		buildDir1 = BuildDir( "0", "1", time.ctime(os.path.getctime(toolsPath)))

		self.assertTrue( buildDir1 == createBuildDir(toolsPath, "1"))
		
		dirPath = os.path.join(toolsPath,"3")
		buildDir1 = BuildDir( "1",  "3", time.ctime(os.path.getctime(dirPath)))
		self.assertTrue( buildDir1 == createBuildDir(toolsPath, "3"))


	def test_createBuildsArray(self):
		actionList = createBuildsArray(os.path.join(CLIENT_SERVER,BUILD_NAME+ "_client"))
		list = []
		clientPath = os.path.join(CLIENT_SERVER,BUILD_NAME) + "_client"
		
		dirPath = os.path.join(clientPath,"1")	
		list.append(BuildDir( "0", "1", time.ctime(os.path.getctime(dirPath))))
		dirPath = os.path.join(clientPath,"2")
		list.append(BuildDir( "1", "2", time.ctime(os.path.getctime(dirPath))))
		dirPath = os.path.join(clientPath,"3")
		list.append(BuildDir( "0", "3", time.ctime(os.path.getctime(dirPath))))
		
		self.assertTrue( len(list) == len(actionList))
		for i in range(0,len(actionList)):
			self.assertTrue(actionList[i] == list[i])
			
	def test_createBuildsArray_2(self):
		actionList = createBuildsArray(os.path.join(CLIENT_SERVER,BUILD_NAME+ "_client"))
		list = []
		clientPath = os.path.join(CLIENT_SERVER,BUILD_NAME) + "_client"
		
		dirPath = os.path.join(clientPath,"2")	
		list.append(BuildDir( "0", "1", time.ctime(os.path.getctime(dirPath))))
		dirPath = os.path.join(clientPath,"1")
		list.append(BuildDir( "1", "2", time.ctime(os.path.getctime(dirPath))))
		dirPath = os.path.join(clientPath,"3")
		list.append(BuildDir( "0", "0", time.ctime(os.path.getctime(dirPath))))
		
		self.assertTrue( len(list) == len(actionList))
		for i in range(0,len(actionList)):
			self.assertFalse(actionList[i] == list[i])
		

	
		
if __name__ == '__main__':
	unittest.main()
