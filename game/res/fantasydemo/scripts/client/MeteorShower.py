import BigWorld
import Pixie
import Math
import math
import random
from functools import partial


'''Test script for particles-as-sky-boxes.
type MeteorShower.meteorShower() for a 60
second shower of meteors in the skybox.'''


def _createMotor( pos, target, duration ):
	'''Create and return a motor that moves a model from pos to target
	over duration seconds.'''
	ma = Math.MatrixAnimation()
	st = Math.Matrix()
	st.setTranslate( pos )
	en = Math.Matrix()
	en.setTranslate( target )
	ma.keyframes = [ (0.0, st), (duration, en) ]
	ma.loop = True
	ma.time = 0.0
	s = BigWorld.Servo( ma )
	return s


def _createMeteorEntry( pos ):
	'''Create and return a meteor entry particle system, attached to a dummy
	model.  Also returns a Vector4Provider so the model can be used as
	a skybox'''
	ps = Pixie.create( "particles/meteor_entry.xml" )
	dm = BigWorld.Model( "" )
	v = Math.Vector4Morph( (1,1,0,1) )
	dm.position = pos
	dm.root.attach(ps)
	return (dm,v)


def _createMeteor( pos ):
	'''Create and return a meteor particle system, attached to a dummy
	model.  Also returns a Vector4Provider so the model can be used as
	a skybox'''
	ps = Pixie.create( "particles/meteor.xml" )
	dm = BigWorld.Model( "" )
	v = Math.Vector4Morph( (1,1,0,1) )
	dm.position = pos
	dm.root.attach(ps)
	return (dm,v)
	
	
def _createMeteorImpact( pos ):
	'''Create and return a meteor impact particle system, attached to a dummy
	model.  Also returns a Vector4Provider so the model can be used as
	a skybox'''
	ps = Pixie.create( "particles/meteor_impact.xml" )
	dm = BigWorld.Model( "" )
	v = Math.Vector4Morph( (1,1,0,1) )
	dm.position = pos
	dm.root.attach(ps)
	return (dm,v)


def _circumferencePt( radius, angle, centerPt ):
	return ( centerPt[0] + radius * math.cos(angle), centerPt[2] + radius * math.sin(angle) )


def _startMeteor( meteor, st, en, duration ):
	motor = _createMotor( st, en, duration )
	meteor.motors = [motor]


def createMeteors( num = 10, radius = 500.0, centerPt = None ):
	'''Create num meteors, in a ring of size radius around the center point.
	By default they start at a height above sea level of the provided radius.
	The meteors are added to the skybox, and thus draw behind the normal
	scenery.  To get good looking fogging on the meteors, set the radius to about
	85 percent of the far plane, although this is just a guide.'''	
	entryTime = 4.0
	entryDuration = 8.0
	impactDuration = 5.8
	impactLeadIn = -0.67
	duration = 20.0

	if centerPt is None:
		centerPt = BigWorld.player().position
	
	height = radius + centerPt[1]

	for i in xrange( 0, num ):
		startTime = random.uniform( 0.0, 10.0 )
		angle = random.uniform( 0.0, math.pi * 2.0 )
		angle2 = angle + random.uniform( -0.5, 0.5 )
		(x,z) = _circumferencePt( radius, angle, centerPt )
		(x2,z2) = _circumferencePt( radius, angle2, centerPt )
		(meteorEntry,v1) = _createMeteorEntry( (x,height,z) )
		(meteor,v2) = _createMeteor( (x,height,z) )
		(meteorImpact,v3) = _createMeteorImpact( (x2,0,z2) )
		
		BigWorld.callback( startTime, partial( BigWorld.addSkyBox, meteorEntry, v1 ) )
		BigWorld.callback( startTime + entryDuration, partial( BigWorld.delSkyBox, meteorEntry, v1 ) )
		
		BigWorld.callback( startTime + entryTime, partial( BigWorld.addSkyBox, meteor, v2 ) )
		BigWorld.callback( startTime + entryTime, partial( _startMeteor, meteor, (x,height,z), (x2,0,z2), duration ) )
		BigWorld.callback( startTime + entryTime + duration, partial( BigWorld.delSkyBox, meteor, v2 ) )
		
		BigWorld.callback( impactLeadIn + startTime + entryTime + duration, partial( BigWorld.addSkyBox, meteorImpact, v3 ) )
		BigWorld.callback( impactLeadIn + startTime + entryTime + duration + impactDuration, partial( BigWorld.delSkyBox, meteorImpact, v3 ) )
		
		print "created meteor at %0.2f, %0.2f, %0.2f" % (x,height,z)


def meteorShower( duration = 60.0, radiusMin = 500.0, radiusMax = 900.0 ):
	'''Note the arbitrary far plane for environmental objects is 2000 metres'''
	if duration > 0.0:
		eta = random.uniform(2.5,10.0)
		radius = random.uniform(radiusMin,radiusMax)
		createMeteors( 1, radius )
		BigWorld.callback( eta, partial(meteorShower,duration-eta,radiusMin,radiusMax) )
