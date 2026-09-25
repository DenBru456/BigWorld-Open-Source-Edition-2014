import BigWorld
from PostProcessing.RenderTargets import *
from PostProcessing import Effect
from PostProcessing import VisualTransferMesh
from PostProcessing.Phases import *
from PostProcessing.Effects import implementEffectFactory
import Math

def getShimmerEffect():
	import PostProcessing
	c = PostProcessing.chain()
	for e in c:
		if e.name == "heatShimmer":
			return e
	return None
	

def setShimmerAlpha( v4p ):
	'''This method sets the fullscreen alpha shimmer'''
	sh = getShimmerEffect()
	if sh:
		if v4p == None:
			v4p = Math.Vector4(0,0,0,0)
		# When deserialising the shimmer effect chain, it may no longer
		# by a Vector4Combiner - so check it here.
		if type(sh.bypass) is not Math.Vector4Combiner:
			sh.bypass = Math.Vector4Combiner()
			sh.bypass.b = v4p
		sh.bypass.a = v4p
		sh.phases[1].material.fullscreenAlpha = v4p


@implementEffectFactory( "Shimmer", "Heat Shimmer effect, triggered by visuals using shimmer.fx, and particles using the shimmer material." )
def shimmer():
	'''This method creates and returns a post-process effect that emulates
	heat shimmer.  It uses the mask created by shimmer objects (those that
	use the shimmer channel, and output alpha).'''
	
	backBufferCopy = rt("backBufferCopy")

	e = Effect()
	c = pre = buildBackBufferCopyPhase( backBufferCopy )
	p = buildPhase( backBufferCopy.texture, None, "shaders/post_processing/heat_shimmer.fx" )
	p.name = "heat shimmer"
	p.filterQuad = VisualTransferMesh( "system/models/fx_shimmer_transfer.visual" )
	e.phases = [c,p]
	e.name = "Heat Shimmer"
	e.bypass = Math.Vector4Combiner()
	e.bypass.a = Math.Vector4(0,0,0,0)
	e.bypass.b = Math.Vector4(0,0,0,0)
	return e


def setShimmerStyle(h, style):
	'''This method replicates the 4 built-in shimmer styles from the BW1.9 C++
	implementation of heat shimmer.'''
	m = h.phases[1].material
	
	if style == 0:
		#this has an intentional 1-pixel inaccuracy when blending on the screen.
		#this style is used by default, for shimmer suits etc.  1 pixel offset means
		#it is easier to see		
		m.speed = 121.0
		m.spreadX = 0.1
		m.spreadY = 0.3
		m.freqS = 1.
		m.freqT = 0.7
		m.uFixup = 1.0
		m.vFixup = 1.0
	elif style == 1:
		#this is the full-on but screen-corrected style.  used for large shockwaves.		
		m.speed = 180.0
		m.spreadX = 0.4
		m.spreadY = 0.68
		m.freqS = 2.0
		m.freqT = 2.7
		m.uFixup = 0.0
		m.vFixup = 0.0
	elif style == 2:
		#Note - this is the default heat shimmer style, very subtle + no screen offset		
		m.speed = 121.0
		m.spreadX = 0.1
		m.spreadY = 0.3
		m.freqS = 1.0
		m.freqT = 0.7
		m.uFixup = 0.0
		m.vFixup = 0.0
	elif style == 3:
		#Note - this is a good setting for water shimmer		
		m.speed = 102.0
		m.spreadX = 1.0
		m.spreadY = 1.6
		m.freqS = -8.0
		m.freqT = -6.3
		m.uFixup = 0.0
		m.vFixup = 0.0
