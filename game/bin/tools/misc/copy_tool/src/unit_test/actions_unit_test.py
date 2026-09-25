import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from actions import *
import unittest

class TestBaseAction(unittest.TestCase):		
	def test_DeleteAction_eq(self):
		action1 = DeleteAction( "file", "destPath" )
		action2 = DeleteAction( "file", "destPath" )
		action3 = DeleteAction( "file", "destPath1" )
		action4 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type") )
		self.assertTrue( action1 == action1 )
		self.assertTrue( action2 == action1 )
		self.assertFalse( action1 == action3 ) 
		self.assertFalse( action1 == action4 )
		self.assertFalse( action3 == action4 )
		
	def test_CopyAction_eq(self):
		action1 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type") )
		action2 = CopyAction( "file", "destPath", SourcePath("sourcePath1", "type") )
		action3 = CopyAction( "file", "destPath1", SourcePath("sourcePath", "type") )
		action4 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type1") )
		action5 = DeleteAction( "file", "destPath" )
		self.assertTrue( action1 == action1 )
		self.assertTrue( action2 == action1 )
		self.assertFalse( action1 == action3 )
		self.assertTrue( action1 == action4 )
		self.assertFalse( action1 == action5 )
		
	def test_ne(self):
		action1 = DeleteAction( "file", "destPath" )
		action2 = DeleteAction( "file2", "destPath" )
		action3 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type") )
		action4 = CopyAction( "file1", "destPath", SourcePath("sourcePath", "type") )
		action5 = CopyAction( "file1", "destPath1", SourcePath("sourcePath", "type") )
		self.assertTrue( action1 != action2 )
		self.assertTrue( action3 != action1 )
		self.assertTrue( action1 != action3 )
		self.assertTrue( action4 != action3 )
		self.assertTrue( action4 != action5 )
		
	def test_returnActionType(self):
		action1 = DeleteAction( "file", "destPath" )
		action2 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type") )
		self.assertTrue( action1.returnActionType() == DELETE_ACTION )
		self.assertTrue( action2.returnActionType()	== COPY_ACTION )
		
class TestActionList(unittest.TestCase):		

	def test_getActionForFile(self):
		actionList = ActionList()
		action1 = DeleteAction( "file", "destPath" )
		action2 = CopyAction( "file2", "destPath", SourcePath("sourcePath", "type") )
		action3 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type") )
		
		actionList.append( action1 )
		actionList.append( action2 )
		actionList.append( action3 )
		
		self.assertTrue( actionList.getActionForFile("file") == action1 )
		self.assertTrue( actionList.getActionForFile("file2") == action2 )
		#need to fail, look for the first obj with file name "file"
		self.assertFalse( actionList.getActionForFile("file2") == action3 )
		
	def test_isFileInList(self):
		actionList = ActionList()
		action1 = DeleteAction( "file", "destPath" )
		action2 = CopyAction( "file2", "destPath", SourcePath("sourcePath", "type") )
		
		actionList.append( action1 )
		actionList.append( action2 )
		self.assertTrue( actionList.isFileInList("file") )
		self.assertTrue( actionList.isFileInList("file2")  )
		self.assertFalse( actionList.isFileInList("file3") )
		
	def test_isActionInList(self):
		actionList = ActionList()
		action1 = DeleteAction( "file", "destPath" )
		action2 = CopyAction( "file2", "destPath", SourcePath("sourcePath", "type") )
		action3 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type") )
		action4 = DeleteAction( "file2", "destPath" )
		action5 = DeleteAction( "file", "destPath" )
		
		actionList.append( action1 )
		actionList.append( action2 )
		
		self.assertTrue( actionList.isActionInList(action1 ))
		self.assertTrue( actionList.isActionInList(action2  ))
		self.assertFalse( actionList.isActionInList(action3 ))
		self.assertFalse( actionList.isActionInList(action4 ))
		self.assertTrue( actionList.isActionInList(action5 ))
		
	def test_deleteByIndex(self):
		actionList = ActionList()
		action1 = DeleteAction( "file", "destPath" )
		action2 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type") )
		
		actionList.append( action1 )
		actionList.append( action2 )
		
		actionList.deleteByIndex(0)
		self.assertFalse( actionList.isActionInList(action1 ))
		self.assertTrue( actionList.isActionInList(action2 ))
		
		actionList.append( action1 )
		actionList.deleteByIndex(1)
		
		self.assertFalse( actionList.isActionInList(action1 ))
		self.assertTrue( actionList.isActionInList(action2 ))
		
		self.assertRaises(IndexError, lambda: actionList.deleteByIndex(1))
		
	def test_removeDeleteActions(self):
		actionList = ActionList()
		action1 = DeleteAction( "file", "destPath" )
		action2 = CopyAction( "file", "destPath", SourcePath("sourcePath", "type") )
		
		actionList.append( action1 )
		actionList.append( action2 )
		actionList.removeDeleteActions( )

		self.assertFalse( actionList.isActionInList(action1 ))
		self.assertTrue( actionList.isActionInList(action2 ))
		
if __name__ == '__main__':
	unittest.main()
