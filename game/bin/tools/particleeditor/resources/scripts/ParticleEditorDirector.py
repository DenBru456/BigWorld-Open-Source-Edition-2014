import ParticleEditor
import PostProcessing

def init():
	print "ParticleEditor.init()"
	try:
		PostProcessing.init()
		PostProcessing.defaultChain(2)	#initialise to low graphics setting
	except Exception, e:
		print "ParticleEditor.init() - Error initialising PostProcessing: ", str( e )


def fini():
	print "ParticleEditor.fini()"
	PostProcessing.fini()
