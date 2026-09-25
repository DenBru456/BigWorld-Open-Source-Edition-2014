import BigWorld
import Math
import math
import random

#------------------------------------------------------------------------------	
# Method: stab
# Description:
#	Test a single vertical line
#------------------------------------------------------------------------------	
def stab( start ):
	samplePointStart = start - ( 0, 10000, 0 )
	samplePointEnd = start + ( 0, 10000, 0 )

	# Do test
	return BigWorld.collide( BigWorld.player().spaceID, samplePointStart, samplePointEnd )

#------------------------------------------------------------------------------	
# Method: spam
# Description:
#	Spam vertical lines across a axis-aligned rectangular area. 
#	Area is from start to start+extent
#	Returns number of misses (zero if completely successful)
#------------------------------------------------------------------------------
def spam( numSamples, start, extent ):
	
	# Total misses for this test
	misses = 0
	
	for i in range(numSamples):
		
		# Build a random sample point within area
		samplePoint = Math.Vector3()
		samplePoint[0] = start[0] + extent[0] * random.random()
		samplePoint[1] = 0
		samplePoint[2] = start[2] + extent[2] * random.random()
		
		samplePointStart = samplePoint - ( 0, 10000, 0 )
		samplePointEnd = samplePoint + ( 0, 10000, 0 )
		
		# Do test
		if None == stab( samplePoint ):
			print 'Miss @ X,Z (', samplePointStart[0], ',', samplePointEnd[2], ')'
			misses += 1
	
	# Return total misses
	return misses
	
#------------------------------------------------------------------------------	
# Method: scan
# Description:
#	Scan vertical lines from start to start+extent. Returns number of misses 
#	(zero if completely successful)
#------------------------------------------------------------------------------
def scan( numSamples, start, extent ):
	
	# Total misses for this test
	misses = 0
	
	# one over number of samples
	ooNumSamples = 1 / float(numSamples)
	
	for i in range(numSamples):
		
		# Build a sample point on line
		t = i * ooNumSamples
		
		sample = Math.Vector3()
		sample[0] = start[0] + extent[0] * t
		sample[1] = 0
		sample[2] = start[2] + extent[2] * t 
		
		# Do test
		if None == stab( sample ):
			print 'Miss @ X,Z (', sample[0], ',', sample[2], ')'
			misses += 1
		
	# Return total misses
	return misses
	