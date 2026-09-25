#!/usr/bin/env python

import os
import sys
import optparse
import smtplib
import socket
import time

import bwsetup; bwsetup.addPath( ".." )

from pycommon import cluster
from pycommon import uid as uidmodule

import logging
log = logging.getLogger( __name__ )


CC = "%s/../control_cluster.py" % bwsetup.appdir
DOMAIN = "bigworldtech.com"

uid = uidmodule.getuid()
username = uidmodule.getname( uid )


# Send an email to all interested parties
#----------------------------------------
def sendMail( isOkay, statusMsg="", checkOutput=None ):

	# Send email
	if not options.no_mail:

		message = ("""
From: %s
To: %s
Subject: [server-status] %s: %s on %s

%s""" % (options.fromaddr, options.to, ("DOWN", "OK")[ isOkay ],
			username, socket.gethostname(), options.message)).lstrip()

		if checkOutput and os.path.isfile( checkOutput ):
			message += "\n" + open( checkOutput, 'r' ).read()

		message += statusMsg

		server = smtplib.SMTP( "localhost" )
		server.sendmail( options.fromaddr, options.to, message )
		server.quit()

		log.info( "Sent email to %s", options.to )


# Simple helper function to convert number of seconds into an uptime string
#--------------------------------------------------------------------------
def secondsToUptime( inputtime ):
	secsInDay  = 86400
	secsInHour = 3600

	days  = (inputtime / secsInDay)
	if days:
		inputtime -= (days * secsInDay)
	hours = (inputtime / secsInHour) % 24
	if hours:
		inputtime -= (hours * secsInHour)
	mins  = inputtime / 60

	return "%d days, %d:%02d" % ( days, hours, mins )


def checkStatus():
	statusMsg = ""

	if not options.no_status:
		userCluster = cluster.cache.get( uid=uid )
		procs = set( userCluster.getProcs() )

		for i in procs:
			if i.name == "cellapp":

				gameTime = i.getWatcherData( "gameTimeInSeconds" )
				if (gameTime.value == None):
					# If we were unable to query the gameTimeInSeconds watcher
					# we may be talking to an old (1.8 or below) server
					gameHertz = 10
					gameTime = i.getWatcherData( "gameTime" )

					if (gameTime.value == None):
						statusMsg += "Server Uptime: Unknown (Watcher Query Failed)\n"
					else:
						try:
							gameTimeSecs = int(gameTime.value) / gameHertz
						except:
							print "Game Time:", gameTime
							print "GameTime.value:", gameTime.value
							raise
						statusMsg += "Server Uptime: %s\n" % secondsToUptime( gameTimeSecs )
				else:
					statusMsg += "Server Uptime: %s\n" % secondsToUptime( int(gameTime.value) )

				break

		statusMsg += "--\n%s" % os.popen( "%s -u %s" % (CC, uid) ).read()

		# Display the status information if we're not sending an email
		if options.no_mail:
			log.info( statusMsg )

	return statusMsg



opt = optparse.OptionParser( "Usage: %prog <username>" )
opt.add_option( "-u", dest = "uid", default = uid,
				help = "UID or username of the BigWorld server to check on" )
opt.add_option( "-t", "--to", dest = "to",
				default = "root@%s" % DOMAIN,
				help = "Address to send mail to in event of failure" )
opt.add_option( "-f", "--from", dest = "fromaddr",
				default = "%s@%s" % (username, DOMAIN),
				help = "Address to send mail to in event of failure" )
opt.add_option( "-m", "--message", dest = "message",
				default = "",
				help = "Message text in email" )
opt.add_option( "-n" ,"--notify-success", action = "store_true",
				dest = "notify_success", default = False,
				help = "Make noise / send an email even if the server is fine" )
opt.add_option( "-q" ,"--quiet", action = "store_true",
				dest = "quiet", default = False,
				help = "Quiet mode: surpress any output to stdout" )
opt.add_option( "-l", "--layout", dest = "saved_layout",
				default = "",
				help = "Saved layout to use when health checking" )
opt.add_option( "--no-mail", action = "store_true",
				help = "Don't send email on failure" )
opt.add_option( "--no-status", action = "store_true", default = False,
				help = "Don't display / email server information." )
(options, args) = opt.parse_args()

# In case -u was specified, update the username
try:
	uid = uidmodule.getuid( options.uid )
	username = uidmodule.getname( uid )
except Exception, e:
	log.error( e )
	sys.exit( 1 )

FAIL_FILE = "%s/.health_check_failed.%s" % (bwsetup.appdir, username)
TOUCH_FILE = "%s/.health_check_stamp.%s" % (bwsetup.appdir, username)

if options.quiet:
	log.console.setLevel( log.logging.ERROR )

failedLastCheck = False

# If the failure file is too old, blow it away
if os.path.exists( FAIL_FILE ):
	failedLastCheck = True
	if os.path.isfile( TOUCH_FILE ):
		if time.time() - os.stat( TOUCH_FILE ).st_ctime > 24 * 60 * 60:
			os.unlink( FAIL_FILE )

statusMsg = ""
if not os.system( "%s -u %s check %s > %s 2>&1" % \
	(CC, uid, options.saved_layout, FAIL_FILE) ):

	log.info( "Server is up" )

	statusMsg = checkStatus()

	# Remove failure file
	if os.path.exists( FAIL_FILE ):
		os.unlink( FAIL_FILE )
	if failedLastCheck or options.notify_success:
		# Send success
		sendMail( True, statusMsg )

	sys.exit( 0 )

log.info( "Server is down" )

# If failure file exists, abort now
if failedLastCheck:
	log.warning( "Bailing with 0 exit status due to recent "
				 "%s file" % os.path.basename(FAIL_FILE) )
	sys.exit( 0 )

# Send failure
if not options.no_status:
	statusMsg = os.popen( "%s -u %s" % (CC, uid) ).read()
sendMail( False, statusMsg, checkOutput=FAIL_FILE )
open( TOUCH_FILE, "w" ).close()
