'''RenderTargets python module
This module manages the render targets used by the post-processing chain.
'''
import BigWorld
import traceback

__all__ = [ 
	'calcMemoryUsage', 
	'reportMemoryUsage', 
	'clearRenderTargets', 
	'getRenderTargets',
	'createStubs',
	'rt' 
	]

rts = {}

rtData = {
	"backBufferCopy" :	(0, 0),
	"backBufferCopyB":	(0, 0),
	"downSample1":		(-1, -1),
	"downSample1B":		(-1, -1),
	"downSampleBlur1":	(-1, -1),
	"bkDownSample1":	(-1, -1),
	"bkDownSampleN1":	(-1, -1),
	"bkBlur1":			(-1, -1, False, 'A16B16G16R16F'),
	"bkBlurN1":			(-1, -1, False, 'A16B16G16R16F'),
	"downSample2":		(-2, -2),
	"downSample2B":		(-2, -2),
	"downSampleBlur2":	(-2, -2),
	"bkDownSample2":	(-2, -2),
	"bkDownSampleN2":	(-2, -2),
	"bkBlur2":			(-2, -2, False, 'A16B16G16R16F'),
	"bkBlurN2":			(-2, -2, False, 'A16B16G16R16F'),
	"downSample3":		(-3, -3),
	"downSample3B":		(-3, -3),
	"downSampleBlur3":	(-3, -3),
	"bkDownSample3":	(-3, -3),
	"bkDownSampleN3":	(-3, -3),
	"bkBlur3":			(-3, -3, False, 'A16B16G16R16F'),
	"bkBlurN3":			(-3, -3, False, 'A16B16G16R16F'),
	"computeBuffer1":	(-3, -3),
	"computeBuffer2":	(-3, -3),
	"fpComputeBuffer1": (0, 0, False, 'G16R16F'),
	"fpComputeBuffer2": (0, 0, False, 'G16R16F'),
	"bkComputeBuffer":  (0, 0, False, 'A32B32G32R32F')
	}


def _create( name, width, height, reuseZ = False, format = 'A8R8G8B8' ):	
	global rts
	rt = BigWorld.RenderTarget( name, int(width), int(height), reuseZ, format )
	rts[name] = rt
	return rt


def calcMemoryUsage( silent ):
	total = 0.0
	for (name,rt) in rts.items():
		total += float(rt.textureMemoryUsed)
		if rt.textureMemoryUsed > 0 and not silent:
			print "PostProcessing: %s (%d x %d)" % (rt.name,rt.width,rt.height)
	total /= (1024.0*1024.0)
	if not silent:
		print "PostProcessing: total memory used by default RenderTargets : %0.2f MB" % (total,)
	return total


def reportMemoryUsage():
	calcMemoryUsage( False )


def rt( rtName ):
	'''Return a render target by name, or raise a KeyError exception'''
	if not rts.has_key(rtName):
		rts[rtName] = _create( rtName, *rtData[rtName] )
	return rts[rtName]


def getRenderTargets():
	return rts.values()


def clearRenderTargets():
	for (name,rt) in rts.items():
		rt.release()


def createStubs():
	for (name,data) in rtData.items():
		_create(name, *data)


def fini():
	print "RenderTargets.fini()"
	clearRenderTargets()
	rts = {}
