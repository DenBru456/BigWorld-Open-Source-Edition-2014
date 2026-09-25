#!/usr/bin/env python


import sys
import syslog
import string
import re
import optparse
import smtplib
import datetime
import os
import time
import ConfigParser



# Status.
STATUS_SUCCESS			= 0
STATUS_ERROR 			= 1


class Summary:
	"""
	A class that creates a summary for each of the Server Tools.
	"""

	# File names.
	MSG_LOGGER 				= "Message_Logger"
	STAT_LOGGER			 	= "Stat_Logger"
	WEB_CONSOLE		 		= "Web_Console"

	# Used to process log messages in different server tools log.
	WEB_CONSOLE_MAX_SPLIT	= 4
	WEB_CONSOLE_LOG_LVL_COL = 3
	STAT_LOGGER_MAX_SPLIT	= 3
	STAT_LOGGER_LOG_LVL_COL = 2
	MSG_LOGGER_MAX_SPLIT	= 3
	MSG_LOGGER_LOG_LVL_COL 	= 2

	# Constants to represent different log messages level.
	# Used as key to dictionaries used.
	KEY_STATS_EXCEPTION		= 0 
	KEY_STATS_TRACEBACK 	= 1
	KEY_STATS_ERROR 		= 2
	KEY_STATS_WARNING 		= 3
	KEY_STATS_NOTICE 		= 4
	KEY_STATS_INFO			= 5
	KEY_STATS_DEBUG 		= 6
	KEY_STATS_TRACE 		= 7
	KEY_STATS_OTHERS        = 8
	KEY_STATS_NUM_OF_KEYS	= 9

	# String format of each log level.
	statsName = \
		{
			KEY_STATS_EXCEPTION		: "EXCEPTION",
			KEY_STATS_TRACEBACK 	: "TRACEBACK",
			KEY_STATS_ERROR 		: "ERROR",
			KEY_STATS_WARNING 		: "WARNING",
			KEY_STATS_NOTICE 		: "NOTICE",
			KEY_STATS_INFO			: "INFO",
			KEY_STATS_DEBUG 		: "DEBUG",
			KEY_STATS_TRACE 		: "TRACE",
			KEY_STATS_OTHERS        : "OTHERS"
		}

	# Used to match format of log messages.
	CMP_STRING_LENGTH 		= 8

	processesName = \
		[
			"baseappmgr", "baseapp", "cellappmgr", "cellapp", \
			"dbappmgr", "dbapp", "loginapp", "bots", "reviver"
		]

	# Used in a dictionary that stores occurrences of a particular
	# format of log message.
	KEY_LOG_SUMMARY_MSG 	= 0
	KEY_LOG_SUMMARY_COUNT 	= 1

	# Used to display number of log messages logged per hour.
	# This is a percentage of total number of log messages logged.
	BAR_WIDTH 				= 0.05

	# Useful general constants.
	HOURS_IN_A_DAY 			= 24

	# Regular expressions.
	REG_EXP_TIME = re.compile( "([0-9]+):([0-9]+):([0-9])" )
	REG_EXP_DATE = re.compile( "([0-9]+)-([0-9]+)-([0-9])" )



	def __init__( self, numMsgsToDisplay ):
		"""
		Constructor.
		"""

		# Find location of Server Tools log files.
		config = ConfigParser.SafeConfigParser()
		config.read( "/etc/bigworld.conf" )
		globalConf = dict( config.items( "tools" ) )
		self.logsLocation = "/var/log/bigworld"

		# Specifies the top "numMsgsTopDispaly" most frequently logged log 
		# message formats to be shown in the summary.
		self.numMsgsToDisplay = numMsgsToDisplay

		# Location of where summary files are.  Updated in _writeDataToFile 
		# method.
		self.summariesDir = self.logsLocation + "/summaries"

		# Get current date and time and use it as prefix to the file name of 
		# the summary files written.  Users can then sort the summaries files 
		# using this prefix.
		dateTimeObj = datetime.datetime.now()
		self.fileNamePrefix = "%04d-%02d-%02d-%02d%02d-" % \
			(dateTimeObj.year, dateTimeObj.month, dateTimeObj.day, 
			 dateTimeObj.hour, dateTimeObj.minute)

		# Used to time approximately how long the script took to run.
		self.startTime = time.time()



	def genSummaries( self, args ):
		"""
		Generates a summary for each of the Server Tools log files.

		Top level function.
		"""

		# To summarise all Server Tool log files.
		if (len( args ) == 0) or ("all" in args):
			args = [
				string.lower( Summary.WEB_CONSOLE ), \
				string.lower( Summary.STAT_LOGGER ), \
				string.lower( Summary.MSG_LOGGER ) ]


		# Initialisation.
		statusWebConsole = True
		statusStatLogger = True
		statusMsgLogger = True


		# Create summary file.  
		# Summarise WebConsole log file.
		if string.lower( Summary.WEB_CONSOLE ) in args:
			self._initData()
			statusWebConsole = self._summariseLog( \
				Summary.WEB_CONSOLE, Summary.WEB_CONSOLE_MAX_SPLIT, \
				Summary.WEB_CONSOLE_LOG_LVL_COL )


		# Summarise StatLogger log file.
		if string.lower( Summary.STAT_LOGGER ) in args:
			self._initData()
			statusStatLogger = self._summariseLog( \
				Summary.STAT_LOGGER, Summary.STAT_LOGGER_MAX_SPLIT, \
				Summary.STAT_LOGGER_LOG_LVL_COL )


		# Summarise MessageLogger log file.
		if string.lower( Summary.MSG_LOGGER ) in args:
			self._initData()
			statusMsgLogger = self._summariseLog( \
				Summary.MSG_LOGGER, Summary.MSG_LOGGER_MAX_SPLIT, \
				Summary.MSG_LOGGER_LOG_LVL_COL )


		if not (statusWebConsole and statusStatLogger and statusMsgLogger):
			return STATUS_ERROR

		return STATUS_SUCCESS



	def _initData( self ):
		"""
		Initialise data structures used to record statitics about a 
		certain log file.
		"""

		# Stores log level statstics for a log file.
		# Format: { <hour_of_day>: { <log_level>: <count>}, ...}
		self.stats = {}
		for i in xrange( Summary.HOURS_IN_A_DAY ):
			hourlyStats = {}
			hourlyStats[Summary.KEY_STATS_EXCEPTION] = 0
			hourlyStats[Summary.KEY_STATS_TRACEBACK] = 0
			hourlyStats[Summary.KEY_STATS_ERROR] = 0
			hourlyStats[Summary.KEY_STATS_WARNING] = 0
			hourlyStats[Summary.KEY_STATS_NOTICE] = 0
			hourlyStats[Summary.KEY_STATS_INFO] = 0
			hourlyStats[Summary.KEY_STATS_DEBUG] = 0
			hourlyStats[Summary.KEY_STATS_TRACE] = 0
			hourlyStats[Summary.KEY_STATS_OTHERS] = 0

			self.stats[i] = hourlyStats


		# Stores log message format statistics.  That is, the occurrences of a 
		# particular format of log message.  Note that the comparison of 
		# two log messages (to see if they are of the same format), is 
		# heuristic based, since we do not have the exact format.  Therefore 
		# occurrences of a particular log message in the summary is only an 
		# approximation.
		# 
		# Format: 
		# { <logMsgCmp>: { <msg_key>: <msg>, <count_key>: <count> }, ...}
		#
		# <logMsgCmp> : Representation of the format of <msg> log message.  
		#               Used to compare two log messages to see if they are 
		#               of the same format.
		# <msg_key>   : Summary.KEY_LOG_SUMMARY_MSG.
		# <msg>       : A log message in log file.  Used to demonstrate the
		#               format of the log message.
		# <count_key> : Summary.KEY_LOG_SUMMARY_COUNT.
		# <count>     : Occurrences of this particular format of log messages 
		#               in the log file.
		self.logMsgsErrorStats = {}
		self.logMsgsWarningStats = {}


		# Hour part of the timestamp of the last processed log message.
		self.lastProcessedHour = -1

		return



	def _summariseLog( self, logType, maxSplit, logLvlCol ):
		"""
		Summarise a particular Server Tool log file.

		@param logType: Type of log file to summarise.  One of 
		                {Summary.WEB_CONSOLE, Summary.STAT_LOGGER, 
						 Summary.MSG_LOGGER}.
		@param maxSplit: The maximum number of splits (based on whitespaces) 
						 to be performed on a log message.  See Python 
						 split string method.
		@param logLvlCol: The column in a log entry that shows the log level.
		"""

		# Open specified Server Tool log file.
		fileName = self.logsLocation + "/" + \
			string.lower( logType )  + ".log"
		try:
			logFile = open( fileName )

		except IOError:
			errMsg = \
				"bigworld: Could not open '%s' for reading, " \
				"and thus cannot generate summary for this log file." % \
				fileName

			syslog.syslog( syslog.LOG_ERR, errMsg )

			return False


		# Process each log message and update statistics.
		for line in logFile:
			logMsgSegments = line.split( None, maxSplit )

			(shouldPassToNextFilter, logLevel) = \
				self._updateStats( logMsgSegments, logLvlCol )

			if not shouldPassToNextFilter:
				continue

			self._updateLogMsgsStats( line, logMsgSegments, logLevel )


		# Write summary for this log file to summary file on disk.
		status = self._writeDataToFile( logType )


		return status



	def _updateStats( self, logMsgSegments, logLvlCol ):
		"""
		Update statistics based on given log entry.

		Returns the tuple (shouldPassToNextFilter, logLevel).  The 
		"shouldPassToNextFilter" value indicates whether further processing is 
		required.  The "logLevel" value is the log level of the log message 
		being processed.  It is passed back for optimisation reason.

		@param logMsgSegments: Segments of a log message/entry in log file.
		@param logLvlCol: The column in a log entry that shows the log level.
		"""

		shouldPassToNextFilter = False

		# Nothing to do.
		if (len( logMsgSegments ) == 0):
			return (shouldPassToNextFilter, "")


		# Process log messages that starts with "Exception", 
		# and "Traceback", and those that do not start with 
		# timestamp.
		if string.upper( logMsgSegments[0] ) == \
			Summary.statsName[Summary.KEY_STATS_EXCEPTION]:

			self.stats[self.lastProcessedHour] \
				[Summary.KEY_STATS_EXCEPTION] += 1
			return (shouldPassToNextFilter, "")

		elif string.upper( logMsgSegments[0] ) == \
			Summary.statsName[Summary.KEY_STATS_TRACEBACK]:

			self.stats[self.lastProcessedHour] \
				[Summary.KEY_STATS_TRACEBACK] += 1
			return (shouldPassToNextFilter, "")

		elif not Summary.REG_EXP_DATE.match( logMsgSegments[0] ):
			# Ignore lines that does not start with "Exception", "Traceback" 
			# or a timestamp.  These are most likely, for example, part of 
			# the "Exception" or "Traceback" message.
			return (shouldPassToNextFilter, "")


		# Make sure the log level column exists and that there is 
		# one segment after that, which is the actual contents of 
		# the log message.
		if len( logMsgSegments ) <= (logLvlCol+1): 
			return (shouldPassToNextFilter, "")

		# Get log level (e.g. "ERROR") of this log message.	
		logLevel = string.upper( logMsgSegments[logLvlCol] )

		# Work out in which hour was the log entry logged.
		time = logMsgSegments[1]
		hour = int( Summary.REG_EXP_TIME.match( time ).groups()[0] )

		# For MessageLogger, logLevel has a suffix ":".  E.g. "ERROR:".
		if logLevel[-1] == ":":
			logLevel = logLevel[0:-1]

		# Update statistics.
		hasUpdated = False
		for i in xrange( Summary.KEY_STATS_ERROR, \
			Summary.KEY_STATS_NUM_OF_KEYS-1 ):

			if logLevel == Summary.statsName[i]:
				self.stats[hour][i] += 1
				hasUpdated = True
				break

		if not hasUpdated:
			# Unknown log level.
			self.stats[hour][Summary.KEY_STATS_OTHERS] += 1

		else:
			# If log level is error or warning, mark it so the log message 
			# will be further processed.
			if (logLevel == Summary.statsName[Summary.KEY_STATS_ERROR]) or \
				(logLevel == Summary.statsName[Summary.KEY_STATS_WARNING]):

				shouldPassToNextFilter = True

		# Remember which hour the log message was logged.
		if hour != self.lastProcessedHour:
			self.lastProcessedHour = hour


		# Pass back "logLevel" for optimisation reason.
		return (shouldPassToNextFilter, logLevel)



	def _updateLogMsgsStats( self, logMsg, logMsgSegments, logLevel ):
		"""
		Update statistics regarding occurrences of log messages of a  
		particular format.

		@param logMsg: The log message being processed.
		@param logMsgSegments: Segments of the log message, split 
		                       using whitespace.
		@param logLevel: The log level (e.g. ERROR) of the logMsg log message.
		"""

		# Compute a string based on actual content of the log message so 
		# that it can be used to compare to another log message to see 
		# if they are of the same format.  
		# The algorithm or heuristic is that by removing digits and  
		# space in the string first, and then remove BigWorld process 
		# name, the remaining part will be a good representation of 
		# the format of this log message. 
		updatedLine = []
		msgPart = logMsgSegments[-1]
		for c in msgPart:
			if not (c.isdigit() or c.isspace()):
				updatedLine.append( c )

		updatedLine = "".join( updatedLine )

		for process in Summary.processesName:
			updatedLine = updatedLine.replace( process, "" )


		# Make the comparison and update statistics.
		statsToUpdate = None
		if (logLevel == Summary.statsName[Summary.KEY_STATS_ERROR]):
			statsToUpdate = self.logMsgsErrorStats

		else:
			statsToUpdate = self.logMsgsWarningStats


		# The algorithm for comparing two log messages using computed 
		# representation. 
		# Two log messages are considered as same format if any one
		# of the followings is true:
		#    - The computed representations are equal.
		#    - The first Summary.CMP_STRING_LENGTH characters of the 
		#      computed representation are equal.
		#    - The last Summary.CMP_STRING_LENGTH characters of the 
		#      computed representation are equal.
		hasUpdated = False
		for logMsgCmpStr, dataDict in statsToUpdate.items():

			if (logMsgCmpStr[0:Summary.CMP_STRING_LENGTH] == \
					updatedLine[0:Summary.CMP_STRING_LENGTH]) or \
				(logMsgCmpStr[-Summary.CMP_STRING_LENGTH:] == \
					updatedLine[-Summary.CMP_STRING_LENGTH:]):

				statsToUpdate[logMsgCmpStr]\
					[Summary.KEY_LOG_SUMMARY_COUNT] += 1
				hasUpdated = True	
				break

		if not hasUpdated:
			# Encountered new format of log message.
			statsToUpdate[updatedLine] = \
				{
					Summary.KEY_LOG_SUMMARY_MSG: logMsg,
					Summary.KEY_LOG_SUMMARY_COUNT: 1
				}


		return



	def _writeDataToFile( self, toolName ):
		"""
		Write collected statistics to summary file for the specified
		Server Tool's log file.

		Returns True if summary written to file successfully; else False.

		@param toolName: Name of the Server Tool.  One of 
					     {Summary.WEB_CONSOLE, Summary.STAT_LOGGER, 
						  Summary.MSG_LOGGER}
		"""

		# Create a summaries directory if it does not exist.
		if not os.path.isdir( self.summariesDir ):
			os.mkdir( self.summariesDir )

		# Create output file.
		fileName = self.summariesDir + "/" + self.fileNamePrefix + \
			string.lower( toolName ) + ".summary"
		try:
			outputFile = open( fileName, "w" )

		except IOError:
			# Could not open file for writing.  Log this in syslog.
			errMsg = \
				"bigworld: Could not open BigWorld Server Tools " \
				"summary file '%s' in '%s' directory for writing." % \
				(fileName, self.logsLocation)

			syslog.syslog( syslog.LOG_ERR, errMsg )

			return False


		# Process statistics sorted by log level.  Examples of log level 
		# are "ERROR", "WARNING", etc.
		totals = {}
		msgsStatsByHour = {}
		for i in xrange( Summary.KEY_STATS_NUM_OF_KEYS ):
			for j in xrange( Summary.HOURS_IN_A_DAY ):
				# Update totals statistics.			
				try:
					totals[i] += self.stats[j][i]

				except KeyError:
					totals[i] = self.stats[j][i]


				# Update hourly-based statistics.
				try:
					msgsStatsByHour[j] += self.stats[j][i]

				except KeyError:
					msgsStatsByHour[j] = self.stats[j][i]


		# Compute total number of log messages.
		totalNumLogMsgs = 0
		for (logLevel, count) in totals.items():
			totalNumLogMsgs += count

		# Writes title and then totals statistics.
		outputFile.write(
			("=" * 15) + " " + toolName + " " + ("=" * 15) + ("\n" * 3) )

		# Process totals statistics.
		outputFile.write( \
			("-" * 40) + "\n" + "Statistics By Totals" + "\n" + \
			("-" * 40) + "\n\n")

		for i in xrange( Summary.KEY_STATS_NUM_OF_KEYS ):
			outputFile.write( "%-20s: %s\n" % \
				(Summary.statsName[i], totals[i]) )
		outputFile.write( "\n" )
		outputFile.write( "%-20s: %s\n\n" % ("Total", totalNumLogMsgs) ) 
		outputFile.write( ("-" * 40) + ("\n" * 5) )


		# Display the top self.numMsgsToDisplay most frequently 
		# occurred error log message (i.e. log message format).
		self._writeMostFreqLogMsgs( outputFile, Summary.KEY_STATS_ERROR )
		self._writeMostFreqLogMsgs( outputFile, Summary.KEY_STATS_WARNING ) 


		# Write out the number of log messages logged on hourly basis.
		self._writeLogMsgsHourlyDistribution( \
			outputFile, totalNumLogMsgs, msgsStatsByHour )


		# Close the summary file.
		outputFile.write( "\n" * 3 )
		outputFile.close()

		return True



	def _writeMostFreqLogMsgs( self, fileStream, type ):
		"""
		Writes the top self.numMsgsToDisplay most frequently 
		logged log message format.  The actual number of format
		displayed may be greater than self.numMsgsToDisplay 
		since formats of a particular number of occurrences are 
		written out together to provide a more complete view of 
		data.

		@param fileStream: file object to write summary to.
		@param type: One of 
		             { Summary.KEY_STATS_ERROR, Summary.KEY_STATS_WARNING }


		Notes: Do not close off fileStream.
		"""

		# Write section heading.
		stats = {}	
		heading = "Most frequently logged "
		if type == Summary.KEY_STATS_ERROR:
			heading += "ERROR "
			stats = self.logMsgsErrorStats

		elif type == Summary.KEY_STATS_WARNING:
			heading += "WARNING "
			stats = self.logMsgsWarningStats

		else:
			# This should only happen when there is a programming error.
			errMsg = \
				"bigworld: _writeMostFreqLogMsgs: Invalid value for 'type' " \
				"argument."

			syslog.syslog( syslog.LOG_ERR, errMsg )		

			print "\n%s\n" % errMsg

			sys.exit( STATUS_ERROR )


		heading += "log message format (decending order)   \n"

		fileStream.write( \
			("-" * len( heading )) + "\n" + heading + \
			("-" * len( heading )) + "\n\n")


		# Put log message format occurrences statistics into a new 
		# dictionary so that log message format can be sorted based 
		# on occurrences.
		statsForSorting = {}
		for (key, dataDict) in stats.items():

			count = dataDict[Summary.KEY_LOG_SUMMARY_COUNT]
			logMsg = dataDict[Summary.KEY_LOG_SUMMARY_MSG]

			try:
				statsForSorting[count] += [logMsg]

			except KeyError:
				statsForSorting[count] = [logMsg]


		# Write most frequently logged log message format.
		count = 0
		for logMsgCount in sorted( statsForSorting, reverse=True ):

			# All log messages with 'logMsgCount' occurrences.
			logMsgs = statsForSorting[logMsgCount]

			for logMsg in logMsgs:
				fileStream.write( logMsg + "\n" )
				count += 1

			if count >= self.numMsgsToDisplay:
				break

		fileStream.write( "\n" * 3 )

		return



	def _writeLogMsgsHourlyDistribution( self, fileStream, \
			totalNumLogMsgs, msgsStatsByHour ):
		"""
		Writes a histogram of log messages logged on a hourly basis.

		@param fileStream: file object to write summary to.
		@param totalNumLogMsgs: Total number of log message in the log file.
		@param msgStatsByHour: A dictionary containing the number of log 
		                       messges logged for each hour.
							   Format: {<hour>: <count>, ...}

		Notes: Do not close the fileStream.
		"""

		# Compute the number of log messages represented by a bar in 
		# the histogram.
		barSize = totalNumLogMsgs * Summary.BAR_WIDTH


		# Write section heading and useful information.
		fileStream.write( 
			("-" * 35) + "\n" + "Log Messages Per Hour" + "\n" + \
			("-" * 35) + "\n\n" )

		fileStream.write( \
			"Each bar ('=') represents a range of 0% - " + \
			"%s%% of the total number of log messages.\n\n" % \
			(int( Summary.BAR_WIDTH * 100 ))) 


		# Write the histogram.
		for (hour, count) in msgsStatsByHour.items():

			if count == 0:
				numBars = 0

			else:
				numBars = int( (count / barSize) + 1 )

				if (numBars == 0) and (count > 0):
					numBars = 1

			fileStream.write( \
				"%02s:00 - %02s:00 | %s\n" % 
				(hour, hour + 1, ("=" * numBars)) )


		fileStream.write( "\n" * 3 )


		# Write the script running time.
		scriptRunningTime = time.time() - self.startTime
		fileStream.write( 
			"The summarise script took %.2f seconds to run." % \
			scriptRunningTime )

		fileStream.write( "\n" * 3 )


		return	



def sendEmail( options, summariesDir, fileNamePrefix, \
	toolName ):
	"""
	Send email notification for a Server Tool's summary.
	"""

	# Assemble headers.
	headers = dict()

	headers["From"] = options.mailFromAddr

	subject = "Summary for %s log file" % toolName
	headers[ "Subject" ] = "%s %s" % \
		( options.mailSubjectPrefix, subject )
	headers[ "To" ] = options.mailToAddrs


	# Send notification for generated summary.
	try:
		fileName = summariesDir + "/" + fileNamePrefix + \
			string.lower( toolName ) + ".summary"
		fileDesc = open( fileName )

		msg = "%s\r\n\r\n%s" % \
			("\r\n".join( "%s: %s" % (key, value) \
				for key, value in headers.items()), 
			fileDesc.read()) 	

		fileDesc.close()


		smtpServer = smtplib.SMTP( options.mailSmtpHost )
		smtpServer.sendmail( \
			options.mailFromAddr, options.mailToAddrs, msg )
		smtpServer.quit()


	except IOError:
		# Could not open summary file.
		# Do nothing.
		errMsg = \
			"bigworld: Could not open '%s' for reading, " \
			"and thus cannot send email notification for this summary." % \
			fileName

		syslog.syslog( syslog.LOG_ERR, errMsg )

	except smtplib.SMTPRecipientsRefused:
		# Could not open summary file.
		# Do nothing.
		errMsg = \
			"bigworld: Could not send server tools summary email " \
			"notification, exception SMTPRecipientsRefused raised " \
			"(failed to send notification to specified recipient)."

		syslog.syslog( syslog.LOG_ERR, errMsg )

	except smtplib.SMTPHeloError:
		# Could not open summary file.
		# Do nothing.
		errMsg = \
			"bigworld: Could not send server tools summary email " \
			"notification, exception SMTPHeloError raised." 

		syslog.syslog( syslog.LOG_ERR, errMsg )

	except smtplib.SMTPSenderRefused:
		# Could not open summary file.
		# Do nothing.
		errMsg = \
			"bigworld: Could not send server tools summary email " \
			"notification, exception SMTPSenderRefused raised." 

		syslog.syslog( syslog.LOG_ERR, errMsg )

	except smtplib.SMTPDataError:
		# Could not open summary file.
		# Do nothing.
		errMsg = \
			"bigworld: Could not send server tools summary email " \
			"notification, exception SMTPDataError raised." 	

		syslog.syslog( syslog.LOG_ERR, errMsg )


	return



def sendEmails( options, summary, args ):
	"""
	Send email notifications for each Server Tool's summary.
	"""	

	if (len( args ) == 0) or ("all" in args):
		args = [
			string.lower( Summary.WEB_CONSOLE ), \
			string.lower( Summary.STAT_LOGGER ), \
			string.lower( Summary.MSG_LOGGER ) ]


	if string.lower( Summary.WEB_CONSOLE ) in args:
		sendEmail( options, summary.summariesDir, \
			summary.fileNamePrefix, Summary.WEB_CONSOLE )

	if string.lower( Summary.STAT_LOGGER ) in args:
		sendEmail( options, summary.summariesDir, \
			summary.fileNamePrefix, Summary.STAT_LOGGER ) 

	if string.lower( Summary.MSG_LOGGER ) in args:
		sendEmail( options, summary.summariesDir, \
			summary.fileNamePrefix, Summary.MSG_LOGGER )


	return



def main():
	try:

		optionParser = optparse.OptionParser( 
			usage="%prog [all|web_console|stat_logger|message_logger]",
			description ="Generates summary for each of the all Server " \
				"Tools log files." )

		optionParser.add_option( "--mail-to",
			dest="mailToAddrs",
			metavar="MAIL_TO_ADDRS",
			action="store",
			help="if set, mails the log to the given mail addresses",
			default=None
		)

		optionParser.add_option( 
			"--mail-from",
			dest="mailFromAddr",
			metavar="ADDR",
			action="store",
			help="if set, then mail sent has the given from address "\
				"(default '%default')",
			default="bw_tools"
		)


		optionParser.add_option( 
			"--mail-subject-prefix",
			dest="mailSubjectPrefix",
			metavar="PREFIX",
			action="store",
			help="if set, defines the mail subject prefix "
				"(default '%default')",
			default="[bwtools-summary]"
		)

		optionParser.add_option( 
			"--mail-host",
			dest="mailSmtpHost",
			metavar="SMTPHOST",
			action="store",
			default="localhost",
			help="the SMTP host to use when sending mail summaries "
				"(default '%default')"
		)

		optionParser.add_option( 
			"--num-msgs-shown",
			dest="numMsgsToDisplay",
			metavar="NUM_MSGS_SHOWN",
			action="store",
			type="int",
			help="the number of most frequently logged message to display "
				"(default '%default')",
			default=10
		)

		(options, args) = optionParser.parse_args()


		# Generate summary.
		summary = Summary( options.numMsgsToDisplay )
		status = summary.genSummaries( args )


		# Send notifications, if required.
		if (not (options.mailFromAddr is None)) and \
			(not (options.mailToAddrs is None)) :
			sendEmails( options, summary, args )

	except KeyboardInterrupt:
		print ""
		return STATUS_ERROR

	return status



if __name__ == "__main__":
	sys.exit( main() )




