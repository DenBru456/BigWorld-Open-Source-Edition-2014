import ModelEditor
import PostProcessing

def init():
	print "ModelEditor.init"
	try:
		PostProcessing.init()
		PostProcessing.defaultChain(2)	#initialise to low graphics setting
	except Exception, e:
		ModelEditor.addCommentaryMsg( "Error initialising PostProcessing: " + str( e ), 1 )


def fini():
	print "ModelEditor.fini"
	PostProcessing.fini()
