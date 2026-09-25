import bwtest
import time

from bwtest import log
from bwtest import config
from bwtest import manual

from helpers.timer import runTimer


class LoadBalanceCommon( object ):

	def getSpaces( self ):
		""" This method returns a list of spaces in the cluster """
		cc = self._cc

		def getSpaces():
			spaces = []
			dirs = cc.getWatcherData( "spaces", "cellappmgr", None )
			for space in dirs:
				for elem in space:
					if elem.name == "id":
						spaces.append( elem.value )

			return spaces

		spaces = runTimer( getSpaces, lambda spaces: bool( spaces ) )

		return spaces
