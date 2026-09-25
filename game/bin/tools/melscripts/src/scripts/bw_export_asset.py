# Export BigWorld Asset 
import maya.cmds as cmds

def main():
    failing = False
    
    try: # Check if user has installed correctly
        import bw_common as bwcommon
    except:
        cmds.confirmDialog( title='Missing bw_common.py!', message="Please refer to the content creation manual for BigWorld melscript instatallation instructions", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
        failing = True
    
    # running bwGetVisualPluginPath will force plugin to be loaded
    if failing == False:
        pluginPath = bwcommon.bwGetVisualPluginPath()
    
    exportUrl = cmds.workspace( fre="BigWorldAsset" )
    
    if failing == False:
        multipleFilters = "Visual Files (*.visual);;Animation Files (*.animation)"
        saveUrl = cmds.fileDialog2( fileFilter=multipleFilters, dir=exportUrl, cap="Export BigWorld Asset To", dialogStyle=2 )
        allSelectedObjects = cmds.ls( selection=True )
        
        if len( allSelectedObjects ) == 0:
            if saveUrl != None:
                try: # Check if user has installed BigWorld exporters
                    cmds.file( saveUrl, force=True, options="", type="BigWorldAsset", pr=True, exportAll=True )
                except:        	
                    cmds.confirmDialog( title='Exporter failed!', message="Ensure exporters are installed and loaded, and that all resources are located in folders defined by paths.xml", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )        
        else:
            if saveUrl != None:
                validSelection = False
                for obj in allSelectedObjects:
                    if cmds.objectType(obj) in ['transform', 'mesh']:
                        validSelection = True
                if not validSelection:
                    cmds.confirmDialog(title='Exporter failed!', message="Invalid object types selected. Objects must be of type 'mesh' or 'transform'.", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
                    return
                try: # Check if user has installed BigWorld exporters
                    cmds.file( saveUrl, force=True, options="", type="BigWorldAsset", pr=True, exportSelected=True )
                except:        	
                    cmds.confirmDialog( title='Exporter failed!', message="Ensure exporters are installed and loaded, and that all resources are located in folders defined by paths.xml", button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )                    