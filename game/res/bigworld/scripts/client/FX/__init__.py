'''
The FX module implements a data-driven special effects framework.

For more information, please refer to bigworld/docs/howto_SFX
'''


s_sectionProcessors = {}


#TODO : either implement or remove this.
def typeCheck( self, listOrType ):
	return 1


#Initialise the framework and build up the class factories
import Actors
import Events
import Joints


#Import the main entry points, for easy python syntax

from Effects._Effect import prerequisites
from Effects.OneShot import OneShot
from Effects.Persistent import Persistent
from Effects.Buffered import getBufferedOneShotEffect
from Effects.Buffered import bufferedOneShotEffect
from Effects.Buffered import cleanupBufferedEffects
from Effects.Buffered import outputOverruns
