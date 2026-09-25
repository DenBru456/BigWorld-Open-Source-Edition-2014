# Attach Hard Point
import maya.cmds as cmds
import bw_common as bwcommon

def main():
	failing = False
	
	allSelectedObjects = cmds.ls( selection=True )
	if len( allSelectedObjects ) == 1:
		attachNodeTo = allSelectedObjects[0]
		attachingFlag = True
	else:
		cmds.confirmDialog( title='No parent node', message='Zero or multiple objects selected, HP will be positioned at world origin', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
		attachingFlag = False    
		
	result = cmds.promptDialog(
					title='Hard Point renamer',
					message='Enter Hard Point Name\n \"HP_\" prefix will be added automatically:',
					button=['OK', 'Cancel'],
					defaultButton='OK',
					cancelButton='Cancel',
					dismissString='Cancel' )
	
	if result == 'OK':
		hpName = cmds.promptDialog( query=True, text=True )        
		if hpName == "" or (hpName.find( "HP_" ) != -1):
			cmds.error( "Invalid Hard Point name" )
			cmds.confirmDialog( title='Invalid HardPoint Name', message='Invalid HardPoint name', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
		else:
			try: # Check if user has installed melscripts correctly
				cmds.file ( "%BIGWORLD_RES_DIR%/helpers/hardpoint/maya_hard_point.obj", i=True, type="OBJ", ra=True, options="mo=1;lo=0", pr=True, loadReferenceDepth="all" )
			except:
				cmds.confirmDialog( title='Missing HardPoint file!', message="Please refer to the content creation manual for BigWorld melscript instatallation instructions", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
				failing = True
			if failing == False:
				cmds.select ('maya_hard_point_HP_test', r=True )
				newName = "HP_" + hpName
				cmds.rename( 'maya_hard_point_HP_test', newName )
				if attachingFlag == True:
					cmds.delete( cmds.parentConstraint( attachNodeTo, newName ) )
					cmds.parent( newName, attachNodeTo ) 