#!/usr/bin/env python
"""
Script to summarise logs for the last user-defined time interval.
"""

DATE_FORMAT="%a %d %b %Y %H:%M:%S"

import datetime
import optparse
import smtplib
import cStringIO
import os

import util
import mlcat

import bwsetup
bwsetup.addPath( ".." )

from pycommon import util as pyutil
import pycommon.log_storage_interface

import logging
# Removed pyutil.setUpBasicCleanLogging from here. mlcat is imported above,
# which calls the logging setup function. Doing so again here causes log lines
# to be output twice.
log = logging.getLogger( __name__ )


def main():
	optionParser = optparse.OptionParser(
		usage="%prog [options] tools_dir [logdir]",
		description="Show summaries of log output of the last user-defined "\
			"time interval. " )

	optionParser.add_option( "--days",
		dest="days",
		action="store",
		type="int",
		help="the interval, in days, (default %default)",
		default="1"
	)

	optionParser.add_option( "--hours",
		dest="hours",
		action="store",
		type="int",
		help="the interval, in hours (overrides the --days option)",
		default=None
	)

	optionParser.add_option( "--minutes",
		dest="minutes",
		action="store",
		type="int",
		help="the interval, in minutes (overrides the --days option)",
		default=None
	)

	optionParser.add_option( "--seconds",
		dest="seconds",
		action="store",
		type="int",
		help="the interval, in seconds (overrides the --days option)",
		default=None
	)

	optionParser.add_option( "-u", "--uid",
		dest="uid",
		action="store",
		type="string",
		help="the user to summarise for (default current user)",
		default=None
	)

	optionParser.add_option( "--all-users",
		dest="allUsers",
		action="store_true",
		default=False,
		help="run summary for all users" )

	optionParser.add_option( "--mail-to",
		dest="mailToAddrs",
		metavar="MAIL_TO_ADDRS",
		action="store",
		help="if set, mails the log to the given mail addresses",
		default=None
	)

	optionParser.add_option( "--mail-from",
		dest="mailFromAddr",
		metavar="ADDR",
		action="store",
		help="if set, then mail sent has the given from address "\
			"(default '%default')",
		default="bwlog"
	)

	optionParser.add_option( "--summary-flags",
		dest="summaryFlags",
		metavar="FLAGS",
		action="store",
		help="the summary flags, same as mlcat.py --summary "\
			"(default='%default')",
		default="Sm"
	)

	optionParser.add_option( "--summary-min",
		dest="summaryMin",
		type="int",
		default=1,
		help="The minimum count to include in a summary" )

	optionParser.add_option( "--mail-subject-prefix",
		dest="mailSubjectPrefix",
		metavar="PREFIX",
		action="store",
		help="if set, defines the mail subject prefix "
			"(default '%default')",
		default="[bwlog-summary]"
	)

	optionParser.add_option( "--mail-host",
		dest="mailSmtpHost",
		metavar="SMTPHOST",
		action="store",
		default="localhost",
		help="the SMTP host to use when sending mail summaries "
			"(default '%default')"
	)

	optionParser.add_option( "--severities",
		dest="severities",
		metavar="SEVERITIES",
		action="store",
		help="the severities mask, same as in mlcat.py --severities",
		default=None
	)

	optionParser.add_option( "--storage-type",
		default = pycommon.log_storage_interface.log_db_constants.BACKEND_MLDB,
		help = "Specify which storage backend to use for the query. "
			"Valid backend options are: %s" %
				str( pycommon.log_storage_interface.getValidBackendsByName() ) )

	options, args = optionParser.parse_args()
	if options.storage_type:
		storageType = options.storage_type
	else:
		storageType = None
	reader = util.initReader( storageType, args )
	output = cStringIO.StringIO()

	timeUnit = ""
	timeValue = 0
	if not options.seconds is None:
		interval = datetime.timedelta( seconds = options.seconds )
		(timeUnit, timeValue) = ("second", options.seconds)
	elif not options.minutes is None:
		interval = datetime.timedelta( minutes = options.minutes )
		(timeUnit, timeValue) = ("minute", options.minutes)
	elif not options.hours is None:
		interval = datetime.timedelta( hours = options.hours )
		(timeUnit, timeValue) = ("hour", options.hours)
	else:
		interval = datetime.timedelta( days = options.days )
		(timeUnit, timeValue) = ("day", options.days)

	kwargs = {}

	if options.severities:

		severities = []
		validSeverities = reader.getSeverities()

		for c in options.severities:
			if c == '^':
				kwargs[ "negate_severity" ] = True
			elif c in validSeverities.keys():
				severities.append( validSeverities[ c ] )
			elif c in mlcat.SEVERITY_FLAGS_TO_SEVERITIES.keys():
				severities.append( mlcat.SEVERITY_FLAGS_TO_SEVERITIES[ c ] )
			else:
				log.error( "Unsupported severity level: %s", c )
				return 1

		kwargs[ "severities" ] = severities

	if options.summaryFlags and \
		not mlcat.checkSummaryFlags( options.summaryFlags ):
			return 1

	# name -> uid
	allUsers = reader.getUsers()
	allUsersReverse = dict( (str(uid), name) for (name, uid) in allUsers.items() )

	users = []
	if options.allUsers:
		users = allUsers.keys()
	elif options.uid in allUsersReverse:
		users = [allUsersReverse[options.uid]]
	elif options.uid in allUsers:
		users = [options.uid]
	else:
		try:
			users = [allUsersReverse[str( os.getuid() )]]
		except KeyError:
			log.error( "No log entries for user %s. Unable to continue",
						os.getuid() )
			return 1
	users.sort()

	for user in users:
		kwargs['serveruser'] = user
		print >> output, "==== Summary for user %s ====\n" % user
		mlcat.summary( reader, options.summaryFlags, options.summaryMin,
			kwargs, False, output )
		print >> output, "\n\n"

	if not options.mailToAddrs is None:
		headers = dict()
		if not options.mailFromAddr is None:
			headers["From"] = options.mailFromAddr

		intervalString = "%d %s" % (timeValue, timeUnit)
		if timeValue != 1:
			intervalString += 's'

		subject = "Summary for last %s" % (intervalString)

		headers["Subject"] = "%s %s" % (options.mailSubjectPrefix, subject )
		headers["To"] = options.mailToAddrs

		msg = "%s\r\n\r\n%s" % ("\r\n".join(
				"%s: %s" % (key, value)
					for key, value in headers.items()),
			output.getvalue())
		smtpServer = smtplib.SMTP( options.mailSmtpHost )

		sendResult = None
		try:
			sendResult = smtpServer.sendmail( 
				options.mailFromAddr, options.mailToAddrs, msg )
		except smtplib.SMTPSenderRefused, e:
			log.error( "Unable to send email from %s. SMTP error %d: %s." % \
				( e.sender, e.smtp_code, e.smtp_error ) )
		except smtplib.SMTPRecipientsRefused, e:
			reportRecipientErrors( e.recipients )
		except smtplib.SMTPException, e:
			log.error( "Unable to send email: %s" % e )
			
		# sendmail returns details of failed sends if any occurred.
		# Note that this will only happen if more than one recipient has been
		# given and at least one fails. Multiple recipients isn't supported 
		# but the help text of mlsum implies it is, so: BWT-31508
		if sendResult:
			reportRecipientErrors( sendResult )
			
		smtpServer.quit()
	else:
		print output.getvalue()
# main


def reportRecipientErrors( recipients ):
	"""Outputs one error log line for each item in dict recipients."""
	
	for email, errorDict in recipients.iteritems():
		log.error( "Unable to send email to %s. SMTP error %d: %s." % \
			( email, errorDict[0], errorDict[1] ) )
# reportRecipientError


if __name__ == "__main__":
	main()
