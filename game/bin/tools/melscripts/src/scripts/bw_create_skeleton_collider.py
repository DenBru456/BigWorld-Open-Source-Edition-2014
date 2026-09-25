#Make Skeleton Collider

#Typical skeleton collider format
# <creature_skeleton.xml>
#         <SkeletonCollider>
#                 <BoxAttachment>
#                         <name>  biped Head      </name>
#                         <minBounds>     -0.100000 -0.100000 -0.100000  </minBounds>
#                         <maxBounds>     0.100000 0.100000 0.100000     </maxBounds>
#                 </BoxAttachment>
#                 <BoxAttachment>
#                         <name>  biped Pelvis    </name>
#                         <minBounds>     -0.200000 -0.200000 -0.200000  </minBounds>
#                         <maxBounds>     0.200000 0.200000 0.200000     </maxBounds>
#                 </BoxAttachment>
#         </SkeletonCollider>
# </creature_skeleton.xml>

import maya.cmds as cmds
from xml.dom.minidom import Document
import bw_common as bwcommon

BOX_SUFFIX = "_bwhitbox"

def main():	
	foundHitbox = False
	
	cmds.confirmDialog( title='Please Save', message='Please save your file first.', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
	
	allSceneObjects = cmds.ls()
	if len( allSceneObjects ) != 0:
		for node in allSceneObjects:
			if node.endswith( BOX_SUFFIX ) != -1:
				foundHitbox = True
	else:
		cmds.confirmDialog( title='No Objects in scene', message='There are no nodes in this scene.', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
	
	if foundHitbox == True:
		exportUrl = cmds.workspace( fre="BigWorldAsset" )
		saveUrl = cmds.fileDialog2( fileFilter="XML Files (*.xml)", dir=exportUrl, cap="Export Skeleton Collider To", dialogStyle=2 )
		
		if saveUrl != None:
			#Open a file
			myfile = open( saveUrl[0], 'w' )
			
			# Create the minidom document
			doc = Document()
		
			# Create the <creature_collider> root element
			root = doc.createElement( "creature_collider" )
			doc.appendChild( root )
			
			sTag = doc.createElement( "SkeletonCollider" )
			root.appendChild( sTag )            
		
			for hitbox in allSceneObjects:
				if hitbox.endswith( BOX_SUFFIX ):
					#BoxAttachement tag                
					bTag = doc.createElement( 'BoxAttachment' )
					sTag.appendChild( bTag )
					
					#Name Tag
					nTag = doc.createElement( 'name' )
					bTag.appendChild( nTag )                
					
					#Name Text
					strippedName = hitbox[:-9] 
					nText = doc.createTextNode( strippedName )
					nTag.appendChild( nText )
					
					#MinBounds tag
					minTag = doc.createElement( 'minBounds' )
					bTag.appendChild( minTag )
									
					#Move and align the hitbox to the origin to calculate its local bounding box
					hitboxParent = cmds.listRelatives( hitbox, p=True, type="transform" ) # Temporarily store the parent node so you can realign/attach the hitbox
					cmds.parent( hitbox, w=True ) # Detach from parent
					cmds.move( 0,0,0, hitbox, rotatePivotRelative=True )
					cmds.rotate( 0,0,0, hitbox, worldSpace=True )
					
					#Calculate the bounding box in world space. 
					hitboxBBox = cmds.polyEvaluate( hitbox, boundingBox=True )
					
					worldMinX = bwcommon.convertToMeters( hitboxBBox[0][0] )
					worldMinY = bwcommon.convertToMeters( hitboxBBox[1][0] )
					worldMinZ = bwcommon.convertToMeters( hitboxBBox[2][0] ) 
					
					#MinBounds text
					minText = doc.createTextNode( str( worldMinX ) + " " + str( worldMinY ) + " " + str( worldMinZ ) )
					minTag.appendChild( minText )
					
					worldMaxX = bwcommon.convertToMeters( hitboxBBox[0][1] )
					worldMaxY = bwcommon.convertToMeters( hitboxBBox[1][1] )
					worldMaxZ = bwcommon.convertToMeters( hitboxBBox[2][1] )
					
					#MaxBounds tag
					maxTag = doc.createElement( 'maxBounds' )
					bTag.appendChild( maxTag )
					
					#MaxBounds text
					maxText = doc.createTextNode( str( worldMaxX ) + " " + str( worldMaxY ) + " " + str( worldMaxZ ) )
					maxTag.appendChild( maxText )
					
					#Put the hitbox back where it belongs
					cmds.delete( cmds.parentConstraint(hitboxParent, hitbox) ) # Parent and align the new hitbox to the selected object
					cmds.parent( hitbox, hitboxParent )
			
			xmlString = doc.toprettyxml( indent="  " )
			
			#remove the xml version tag
			cleanXmlString = xmlString.lstrip( "<?xml version=\"1.0\" ?>" )
			cleanXmlString = cleanXmlString.lstrip( "\n" )
			myfile.write( cleanXmlString )
			
			#Close the file
			myfile.close()
			
			cmds.confirmDialog( title='Skeleton Collider Exported', message='Skeleton collider created.', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
			
			cmds.select( deselect=True )
			allSceneNodes = cmds.ls( long=True )
			for node in allSceneNodes: #Select all the Hitboxes
				if node.endswith( "_bwhitbox" ):
					cmds.select( node, add=True )        