from test_case import TestCase
from test_case import fail_on_exception
import ResMgr
import Math
import math

from BWLogicNodeTree import *

class LogicalNodeTree( TestCase ):
	def __init__( self ):
		TestCase.__init__( self )

	def run( self ):
		rootDS = self.createNodeDataSection()
		self.testTemplateTree( rootDS )
		self.testLocalNodeTree( rootDS )
		self.testLocalAndWorldTree( rootDS )
		self.finishTest()

	def createNodeDataSection( self ):
		m = Math.Matrix()

		rootDS = ResMgr.DataSection( "nodeTest.xml" )
		
		# sceneRoot
		sceneRoot = rootDS.createSection( 'node' )
		sceneRoot.writeString( 'identifier', 'Scene Root' )
		sceneRoot.writeMatrix( 'transform', Math.Matrix() )
		
		# sceneRoot/translateX10
		m.setTranslate( (10,0,0) )
		translateX10 = sceneRoot.createSection( 'node' )
		translateX10.writeString( 'identifier', 'translateX10' )
		translateX10.writeMatrix( 'transform', m )
		
		# sceneRoot/translateX10/rotateY180
		m.setRotateX( math.radians( 180 ) )
		rotateY180 = translateX10.createSection( 'node' )
		rotateY180.writeString( 'identifier', 'rotateY180' )
		rotateY180.writeMatrix( 'transform', m )
		
		# sceneRoot/translateY10
		m.setTranslate( (0,10,0) )
		translateY10 = sceneRoot.createSection( 'node' )
		translateY10.writeString( 'identifier', 'translateY10' )
		translateY10.writeMatrix( 'transform', m )
		
		# sceneRoot/translateY10/rotateZ180
		m.setRotateY( math.radians( 180 ) )
		rotateZ180 = translateY10.createSection( 'node' )
		rotateZ180.writeString( 'identifier', 'rotateZ180' )
		rotateZ180.writeMatrix( 'transform', m )
		
		return rootDS

	def assertMatrixAngleIs180( self, matrix, idx ):
		elipson = 0.0003
		rad180 = math.radians(180)
		yawIs180 = math.fabs(math.fabs(matrix.yaw)-rad180) < elipson
		pitchIs180 = math.fabs(math.fabs(matrix.pitch)-rad180) < elipson
		rollIs180 = math.fabs(math.fabs(matrix.roll)-rad180) < elipson
		is180 = [yawIs180, pitchIs180, rollIs180]

		if is180[idx] and (not is180[(idx+1)%3]) and (not is180[(idx+2)%3]):
			return True
		if (not is180[idx]) and (is180[(idx+1)%3]) and (is180[(idx+2)%3]):
			return True
			
		return False
		
	def assertMatrixAnglesAre0 ( self, matrix ):
		self.assertAlmostEqual( matrix.yaw, 0 )
		self.assertAlmostEqual( matrix.pitch, 0 )
		self.assertAlmostEqual( matrix.roll, 0 )

	def assertMatrixEqual( self, matrix, translation, yaw_pitch_roll ):
		self.assertEqual( matrix.translation.x, translation[0] )
		self.assertEqual( matrix.translation.y, translation[1] )
		self.assertEqual( matrix.translation.z, translation[2] )
		
		# If -1 then none are 180 degrees, otherwise the index of which should
		# be 180
		if yaw_pitch_roll == -1:
			self.assertMatrixAnglesAre0( matrix )
		else:
			self.assertMatrixAngleIs180( matrix, yaw_pitch_roll )
		
	@fail_on_exception
	def testTemplateTree( self, rootDS ):
		m = Math.Matrix()
		
		nodeTree = BWNodeTreeTemplate( rootDS )
		worldNodes = nodeTree.processNodes( m, {} )
		
		self.assertMatrixEqual( worldNodes['translateX10'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateY180'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( worldNodes['translateY10'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateZ180'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = 0 )

		# Translate all y+150
		m.setTranslate( (0,150,0) )

		worldNodes = nodeTree.processNodes( m, {} )
		
		self.assertMatrixEqual( worldNodes['translateX10'],
					translation = ( 10, 150, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateY180'],
					translation = ( 10, 150, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( worldNodes['translateY10'],
					translation = ( 0, 160, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateZ180'],
					translation = ( 0, 160, 0 ), yaw_pitch_roll = 0 )
					
		# After translate all y+150, set scene root -150 (should be initial)
		minusY150 = Math.Matrix()
		minusY150.setTranslate( (0, -150, 0 ) )
		worldNodes = nodeTree.processNodes( m, \
			{'Scene Root' : minusY150} )
		
		self.assertMatrixEqual( worldNodes['translateX10'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateY180'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( worldNodes['translateY10'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateZ180'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = 0 )

	@fail_on_exception
	def testLocalNodeTree( self, rootDS ):
		m = Math.Matrix()
		
		nodeTreeTemplate = BWNodeTreeTemplate( rootDS )
		nodeTree = BWLogicalNodeTreeLocal( nodeTreeTemplate )
		
		# Check inputs
		self.assertMatrixEqual( nodeTree.input['translateX10'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( nodeTree.input['rotateY180'],
					translation = ( 0, 0, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( nodeTree.input['translateY10'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( nodeTree.input['rotateZ180'],
					translation = ( 0, 0, 0 ), yaw_pitch_roll = 0 )

		# Check initial
		worldNodes = nodeTree.processNodes( m )
		
		self.assertMatrixEqual( worldNodes['translateX10'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateY180'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( worldNodes['translateY10'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateZ180'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = 0 )

		# Translate all y+150
		m.setTranslate( (0,150,0) )
		worldNodes = nodeTree.processNodes( m )
		
		self.assertMatrixEqual( worldNodes['translateX10'],
					translation = ( 10, 150, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateY180'],
					translation = ( 10, 150, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( worldNodes['translateY10'],
					translation = ( 0, 160, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateZ180'],
					translation = ( 0, 160, 0 ), yaw_pitch_roll = 0 )
					
		# After translate all y+150, set scene root -150 (should be initial)
		nodeTree.input['Scene Root'].setTranslate( (0, -150, 0 ) )
		worldNodes = nodeTree.processNodes( m )
		
		self.assertMatrixEqual( worldNodes['translateX10'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateY180'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( worldNodes['translateY10'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( worldNodes['rotateZ180'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = 0 )


	@fail_on_exception
	def testLocalAndWorldTree( self, rootDS ):
		m = Math.Matrix()
		
		nodeTreeTemplate = BWNodeTreeTemplate( rootDS )
		nodeTree = BWLogicalNodeTreeLocalAndWorld( nodeTreeTemplate )

		# Check initial
		nodeTree.processNodes( m )
		
		self.assertMatrixEqual( nodeTree.output['translateX10'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( nodeTree.output['rotateY180'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( nodeTree.output['translateY10'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( nodeTree.output['rotateZ180'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = 0 )

		# Translate all y+150
		m.setTranslate( (0,150,0) )
		nodeTree.processNodes( m )
		
		self.assertMatrixEqual( nodeTree.output['translateX10'],
					translation = ( 10, 150, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( nodeTree.output['rotateY180'],
					translation = ( 10, 150, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( nodeTree.output['translateY10'],
					translation = ( 0, 160, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( nodeTree.output['rotateZ180'],
					translation = ( 0, 160, 0 ), yaw_pitch_roll = 0 )
					
		# After translate all y+150, set scene root -150 (should be initial)
		nodeTree.input['Scene Root'].setTranslate( (0, -150, 0 ) )
		nodeTree.processNodes( m )
		
		self.assertMatrixEqual( nodeTree.output['translateX10'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( nodeTree.output['rotateY180'],
					translation = ( 10, 0, 0 ), yaw_pitch_roll = 1 )

		self.assertMatrixEqual( nodeTree.output['translateY10'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = -1 )

		self.assertMatrixEqual( nodeTree.output['rotateZ180'],
					translation = ( 0, 10, 0 ), yaw_pitch_roll = 0 )


# logical_tree_nodes.py
