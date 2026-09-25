import BigWorld

from Helpers.BWCoroutine import *

from RestartClientPage import RestartClientPage

def applyGraphicsSettingsOrRestart( menu, callback=lambda:None ):
	BigWorld.savePreferences()
	if not BigWorld.graphicsSettingsNeedRestart():
		coApplyGraphicsSettings( menu, callback ).run()
	else:		
		msg = 'New settings require restarting the client'
		menu.push( RestartClientPage( menu, msg, callback ) )

@BWCoroutine
def coApplyGraphicsSettings( menu, callback ):
	menu.showProgressStatus( 'Applying new settings...' )
	yield BWWaitForPeriod( 1.0 )
	while BigWorld.hasPendingGraphicsSettings():
		BigWorld.commitPendingGraphicsSettings()
		yield BWWaitForPeriod( 0.5 )
	menu.clearStatus()
	callback()

	
def serverNetName( details ):
	'''Given a ServerDiscoveryDetails object,
	returns the network name for it.
	'''
	name = serverDottedHost( details.ip )
	if details.port:
		name += ':%d' % details.port
	return name


def serverNiceName( details ):
	'''Given a ServerDiscoveryDetails object,
	returns a human readable name for it.
	'''
	name = details.hostName
	if not name:
		name = serverDottedHost(details.ip)
	if details.port:
		name += ':%d' % details.port
	if details.ownerName:
		name += ' (' + details.ownerName + ')'
	return name


def serverDottedHost( ip ):
	'''Given a numeric IP address, returns a
	four digit, dot notation IP address.
	'''
	return '%d.%d.%d.%d' % (
		(ip>>24) & 0xFF,
		(ip>>16) & 0xFF,
		(ip>>8)  & 0xFF,
		(ip>>0)  & 0xFF)
