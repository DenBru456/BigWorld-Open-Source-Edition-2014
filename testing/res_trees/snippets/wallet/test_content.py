import BigWorld
import srvtest

def _getAdjustFunc( account, contentName ):
	func_name = 'adjust' + contentName[:1].capitalize() + contentName[1:]
	return getattr( account.wallet, func_name )


@srvtest.testSnippet
def startWalletSession( accountID ):

	account = BigWorld.entities.get( accountID )

	def onSessionStarted( onStarted ):
		srvtest.finish( onStarted )

	account.wallet.startSession( onSessionStarted )


@srvtest.testSnippet
def setWalletContent( accountID, contentName, delta ):

	account = BigWorld.entities.get( accountID )

	val = getattr( account.wallet, contentName )

	_getAdjustFunc( account, contentName )( delta )

	account.wallet.commitAdjustments()

	srvtest.finish( val )


@srvtest.testSnippet
def checkWalletContent( accountID, contentName, originalValue, delta ):
	
	# freeXP has a different key in server.currentValues
	if contentName == 'freeXP':
		contentName = 'free_xp'

	contentKey = 'curr_%s' % contentName

	def onCheck( timerID, *rgs ):
		account = BigWorld.entities.get( accountID )

		val = originalValue + delta
		# premium is zero before the first adjustment.
		if contentName == 'premium':
			if originalValue == 0:
				BigWorld.delTimer( timerID )
				srvtest.finish()
			else:
				val = getattr( account.wallet, contentName )

		if account.wallet._server.currentValues[contentKey] == val and \
			account.wallet._server.currentValues[contentKey] != originalValue:

			BigWorld.delTimer( timerID )
			srvtest.finish()

	BigWorld.addTimer( onCheck, 0.5, 0.5 )
