from FX.Event import Event
from FX.Event import TRANSFORM_DEPENDENT_EVENT
from FX import s_sectionProcessors
from bwdebug import *
import traceback


#------------------------------------------------------------------------------
#	PlaySound - plays an fxSound with the given name.
#------------------------------------------------------------------------------
class PlaySound( Event ):
	'''
	This class implements an event that plays a sound.  The sound may be
	associated with a particular actor to provide its 3D position; if not the
	sound will be played on the source model.
	'''
	def __init__( self ):		
		self.tag = None
		self.attachToActor = False


	def load( self, pSection, prereqs = None ):
		'''
		This method loads the PlaySound event via an XML data section. It
		reads the sound tag name from the section name.  It also looks for an
		"attachToActor" tag to specify whether the sound should be played at
		the given actor's position, or the effect source's position.
		'''
		self.tag = pSection.asString
		if self.tag == "":
			WARNING_MSG( "PlaySound had no associated tag" )
		self.attachToActor = pSection.has_key( "attachToActor" )
		return self


	def go( self, effect, actor, source, target, **kargs ):

		# All the calls to playSound() are commented out here because
		# FantasyDemo is missing the majority of referenced sound events.

		# NOTE: We don't really need all this duration stuff.  PyModels have the
		# stopSoundsOnDestroy attribute which can be used to allow sounds to
		# continue playing after the model has been destroyed, which is a much
		# simpler and more efficient way to handle this problem.

		sound = None

		if self.tag != "":
			if kargs.has_key("suffix"):
				tag = self.tag + kargs[ 'suffix' ]
			else:
				tag = self.tag

			if self.attachToActor:
				try:
					pass # sound = actor.playSound( tag )
				except:
					ERROR_MSG( "error playing sound on actor", self, actor, source, tag )
					traceback.print_exc()
					#traceback.print_stack()
			else:
				try:
					pass # sound = source.model.playSound(tag)
				except:
					try:
						pass # sound = source.playSound(tag)
					except:
						ERROR_MSG( "error playing sound", self, actor, source, tag )
						traceback.print_exc()
						#traceback.print_stack()

		# return duration to allow sounds to play to their natural conclusion.
		# (otherwise if the rest of the effect finished before the sound it would be truncated)
		#DEBUG_MSG("duration=", duration)
		return sound.duration if sound else 0.0


	def eventTiming( self ):
		return TRANSFORM_DEPENDENT_EVENT


s_sectionProcessors[ "PlaySound" ] = PlaySound
