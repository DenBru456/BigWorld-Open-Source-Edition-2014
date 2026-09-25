#!/bin/sh
#
# Redhat service management information
# description: The bwlockd daemon maintains locks for editing world chunks in WorldEditor.
# processname: bwlockd
# chkconfig: 2345 90 40

if [ -f "/etc/redhat-release" ]; then
        . /etc/init.d/functions
fi
. /etc/init.d/bw_functions


PROCNAME=bwlockd
SOURCE_SCRIPT_NAME="$PROCNAME.sh"
SCRIPT_NAME=bw_lockd
EXEC=bwlockd.py
INIT_RD_DIR=/etc/init.d
PORT=8168
BIND_IP=0.0.0.0
BWLOCKD_DATA_DIR="/var/lib/bigworld/$PROCNAME"
BWLOCKD_LOG_PATH="$BW_TOOLS_LOG_DIR/bwlockd.log"

# Include bwlockd defaults if available
if [ -f /etc/default/$PROCNAME ] ; then
	. /etc/default/$PROCNAME
fi


case "$1" in

  start)
	BWLOCKD_HOME=$BW_TOOLS_DIR/../bwlockd
	PIDFILE="$BW_TOOLS_PIDDIR/$SCRIPT_NAME.pid"
	
	echo -n "Starting $SCRIPT_NAME: "

	cd $BWLOCKD_HOME
	if [ $? != 0 ]; then
		echo "Could not chdir into bwlockd home: $BWLOCKD_HOME"
		bw_print_failure
		exit 1
	fi
	
	# Check for an existing service running
	bw_is_running "$PIDFILE" "bwlockd.py --daemon" $BW_TOOLS_USERNAME
	if [ $? != 0 ]; then
		bw_print_failure
		exit 1
	fi

	cd $BWLOCKD_HOME

	su $BW_TOOLS_USERNAME -c "./$EXEC --daemon --pid $PIDFILE \
				-o \"$BWLOCKD_LOG_PATH\" \
				--bind-ip=$BIND_IP \
				--port=$PORT \
				--chdir \"$BW_TOOLS_WORKING_DIR\" \
				--data-dir=\"$BWLOCKD_DATA_DIR\""

	if [ $? != 0 ]; then
		bw_print_failure
	else
		bw_print_success
	fi
	;;

  stop)
	PIDFILE="$BW_TOOLS_PIDDIR/$SCRIPT_NAME.pid"

	bw_stop_process "$SCRIPT_NAME" \
					"$PIDFILE" \
					"bwlockd.py --daemon" \
					"$BW_TOOLS_USERNAME"
	RETVAL=$?
	;;

  status)
	PIDFILE="$BW_TOOLS_PIDDIR/$SCRIPT_NAME.pid"

	echo -n "Status of $SCRIPT_NAME: "
	if [[ ! -e $PIDFILE ]]; then
		echo "stopped"
		RETVAL=0
	else
		# Extract the PID from the PID file 
		PID=`head -n 1 $PIDFILE 2>/dev/null`
		if [ $? != 0 ]; then 
			echo "Unable to read PID from '$PIDFILE'"
			RETVAL=1
		else

			# Check if the PID is in the process list
			ps -p $PID > /dev/null 2>&1
			if [ $? == 0 ]; then
				echo "running"
				RETVAL=0
			else
				echo "pid file exists, but no process running as $PID"
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


