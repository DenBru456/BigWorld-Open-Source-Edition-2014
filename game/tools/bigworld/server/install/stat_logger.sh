#!/bin/sh
#
# Redhat service management information
# chkconfig: 2345 90 40
# description: The stat_logger daemon collects machine and process statistics, \
#		from BigWorld processes.
# processname: stat_logger.py
### BEGIN INIT INFO
# Provides:          stat_logger
# Required-Start:    $local_fs $network $syslog $time bwmachined2
# Should-Start:
# Required-Stop:     $local_fs $syslog
# Default-Start:     3 4 5
# Default-Stop:      0 1 2 6
# Short-Description: Start BigWorld Statistics Logger
# Description:       Start BigWorld Statistics Logger, a service that queries \
#                    BigWorld server processes for their watcher values and \
#                    saves / aggregates the data for historical analysis.
### END INIT INFO

if [ -f "/etc/redhat-release" ]; then
	. /etc/init.d/functions
fi

. /etc/init.d/bw_functions


STAT_LOGGER_HOME=$BW_TOOLS_DIR/stat_logger
SCRIPT_NAME=stat_logger
PIDFILE="$BW_TOOLS_PIDDIR/$SCRIPT_NAME.pid"
STAT_LOGGER_CONF="preferences.xml"
LOGFILE="$BW_TOOLS_LOG_DIR/stat_logger.log"

# Include stat_logger defaults if available
if [ -f /etc/default/$SCRIPT_NAME ] ; then
	. /etc/default/$SCRIPT_NAME
fi


case "$1" in
  start)
	echo core.%e.%h.%p > /proc/sys/kernel/core_pattern
	ulimit -c unlimited

	# Check for an existing service running
	bw_is_running "$PIDFILE" "stat_logger.py --daemon" "$BW_TOOLS_USERNAME"
	if [ $? != 0 ]; then
		if [ -f "/etc/debian-version" ]; then
			echo -n "already running"
			bw_print_success
		else
			echo "already running"
		fi
		exit 0
	fi

	cd $STAT_LOGGER_HOME
	if [ $? != 0 ]; then
		if [ -f "/etc/debian-version"]; then
			bw_print_failure
		fi
		exit 1
	fi

	if [ -f "/etc/redhat-release" ]; then
		echo -n "Starting bw_stat_logger: "
		daemon su "-c \"./stat_logger.py --daemon \
			--pid \"$PIDFILE\" \
			-o \"$LOGFILE\" \
			-e \"$LOGFILE\" \
			--chdir \"$BW_TOOLS_WORKING_DIR\" \
			--config-file \"$STAT_LOGGER_CONF\" \
			\" $BW_TOOLS_USERNAME"
		echo
	else
		su -c "./stat_logger.py --daemon \
			--pid \"$PIDFILE\" \
			-o \"$LOGFILE\" \
			-e \"$LOGFILE\" \
			--chdir \"$BW_TOOLS_WORKING_DIR\" \
			--config-file \"$STAT_LOGGER_CONF\" \
			" $BW_TOOLS_USERNAME
	fi

	if [ $? != 0 ]; then
		if [ -f "/etc/debian-version" ]; then
			bw_print_failure
		fi
		exit 1
	else

		bw_has_started "$PIDFILE" "stat_logger.py --daemon" "$BW_TOOLS_USERNAME"
		if [ $? == 0 ]; then
			if [ -f "/etc/debian-version" ]; then
				bw_print_failure
			fi
			echo "Check '$LOGFILE' for errors"
			exit 1
		fi
	fi

	if [ -f "/etc/debian-version" ]; then
		bw_print_success
	fi
	RETVAL=0
	;;

  stop)
	bw_stop_process "stat_logger" \
					"$PIDFILE" \
					"stat_logger.py --daemon" \
					"$BW_TOOLS_USERNAME"
	RETVAL=$?
	;;

  # This is provided to initialise the log file from RPM. As StatLogger
  # isn't started on installation due to MySQL username/password needing
  # to be configured first, we must create the empty log file so that
  # log rotate won't fail.
  log_init)
	touch $LOGFILE
	;;

  # Notify the stat_logger process to close and re-open its logfile(s)
  logrotate)
	echo -n "Re-opening stat_logger logfile: "
	if [ -f $PIDFILE ]; then
		read pid < $PIDFILE
		if [ $? != 0 ]; then
			echo "Failed to read PID from '$PIDFILE'"
			bw_print_failure
			exit 1
		fi

		kill -s HUP $pid > /dev/null 2>&1
		if [ $? != 0 ]; then
			bw_print_failure
			echo "Failed to send HUP signal to process $pid. "
			RETVAL=1
		else
			bw_print_success
			RETVAL=0
		fi

	else
		bw_print_failure
		echo "pid file ($PIDFILE) doesn't exist."
		RETVAL=1
	fi
    ;;

  # Summarise log file.
  summarise_log)

	echo -n "Summarising WebConsole log file: " 
	SUMMARISE_OPTIONS=" "
	if [ ! -z $BW_TOOLS_SUMMARY_MAIL_FROM ]; then
		if [ ! -z $BW_TOOLS_SUMMARY_MAIL_TO ]; then
			SUMMARISE_OPTIONS="$SUMMARISE_OPTIONS \
				--mail-to=$BW_TOOLS_SUMMARY_MAIL_TO \
				--mail-from=$BW_TOOLS_SUMMARY_MAIL_FROM"
		fi
	fi

	SUMMARY_CMD="./summarise_logs.py$SUMMARISE_OPTIONS \
		stat_logger"

	su - $BW_TOOLS_USERNAME -c "cd $BW_TOOLS_DIR/misc; $SUMMARY_CMD"	
	
	if [ $? != 0 ]; then
		bw_print_failure
		RETVAL=1
	else
		bw_print_success
		RETVAL=0
	fi
	echo
  ;;

  status)
	echo -n "Status of stat_logger: "
	if [[ ! -e $PIDFILE ]]; then
		echo "stopped"
		RETVAL=1
	else
		# Extract the PID from the PID file
		PID=`head -n 1 $PIDFILE 2>/dev/null`
		if [ $? != 0 ]; then
			echo "Unable to read pid from '$PIDFILE'."
			RETVAL=1
		else

			# Check if the pid is in the process list
			ps -p $PID > /dev/null 2>&1
			if [ $? == 0 ]; then
				echo "running"
				RETVAL=0
			else
				echo "pid file exists, but no process running as `head -n 1 $PIDFILE`"
				RETVAL=1
			fi
		fi
	fi
	;;

  restart|reload)
	$0 stop
	RETVAL=$?

	$0 start
	RETVAL=$[ $RETVAL + $? ]
	;;

  *)
	echo "Usage: $0 {start|stop|status|restart|reload}"
	exit 1
	;;
esac

exit $RETVAL
