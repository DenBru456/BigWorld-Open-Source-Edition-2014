#!/bin/sh

# Defaults
export BW_TOOLS_PIDDIR="/var/run/bigworld"
export BW_TOOLS_WORKING_DIR="/var/run/bigworld"
export BW_CONFIG="/etc/bigworld.conf"

# This magical regex is used to match a key / value pair from
# configuration files and is intended to be used by sed in 
# extended regular expression mode (sed -r).
export BW_VAL_REGEX="^[[:alnum:]_]+[ 	]*=[ 	]*(.*)[ 	]*$"


if [ ! -f "$BW_CONFIG" ]; then
	echo "ERROR: Unable to find configuration file '$BW_CONFIG'."
	exit 1
fi

# NB: This matching may have issues if the expected keyname appears
#     in any other lines (either as part of another keyword or in
#     a value.
export BW_TOOLS_USERNAME=`grep username $BW_CONFIG | sed -r -e "s/$BW_VAL_REGEX/\1/"`
export BW_TOOLS_GROUPNAME=`grep groupname $BW_CONFIG | sed -r -e "s/$BW_VAL_REGEX/\1/"`
export BW_TOOLS_DIR=`grep location $BW_CONFIG | sed -r -e "s/$BW_VAL_REGEX/\1/"`
export BW_TOOLS_BIN="$BW_TOOLS_DIR/bin"
export BW_TOOLS_LOG_DIR="/var/log/bigworld"
export BW_TOOLS_SUMMARY_MAIL_TO=`grep mail_to $BW_CONFIG | grep -v ^# | sed -r -e "s/$BW_VAL_REGEX/\1/"`
export BW_TOOLS_SUMMARY_MAIL_FROM=`grep mail_from $BW_CONFIG | grep -v ^# | sed -r -e "s/$BW_VAL_REGEX/\1/"`
TMP_PIDDIR=`grep piddir $BW_CONFIG | sed -r -e "s/$BW_VAL_REGEX/\1/"`
if [ ! -z $TMP_PIDDIR ]; then
	export BW_TOOLS_PIDDIR=$TMP_PIDDIR
fi

if [ -z $BW_TOOLS_USERNAME ]; then
	echo "ERROR: No username to run tools as defined in '$BW_CONFIG'."
	exit 1
fi

if [ -z $BW_TOOLS_DIR ]; then
	echo "ERROR: No tools directory defined in '$BW_CONFIG'."
	exit 1
fi

if [ ! -d $BW_TOOLS_DIR ]; then
	echo "ERROR: '$BW_TOOLS_DIR' does not appear to be a directory."
	exit 1
fi

if [ ! -d $BW_TOOLS_PIDDIR ]; then
	mkdir -p $BW_TOOLS_PIDDIR
	if [ $? != 0 ]; then
		echo "ERROR: Unable to create PID directory '$BW_TOOLS_PIDDIR'."
		exit 1
	fi
	
	chown -R $BW_TOOLS_USERNAME:$BW_TOOLS_GROUPNAME $BW_TOOLS_PIDDIR
	if [ $? != 0 ]; then
		echo "ERROR: Unable to change owner of PID directory '$BW_TOOLS_PIDDIR'."
		exit 1
	fi
fi

if [ ! -d $BW_TOOLS_WORKING_DIR ]; then
	mkdir -p $BW_TOOLS_WORKING_DIR
	if [ $? != 0 ]; then
		echo "ERROR: Unable to create working directory '$BW_TOOLS_WORKING_DIR'."
		exit 1
	fi
fi

# It would be good to always make sure the PID directory has the correct owner
# and group, as this directory may be shared by bwmachined.
chown -R $BW_TOOLS_USERNAME:$BW_TOOLS_GROUPNAME $BW_TOOLS_WORKING_DIR
if [ $? != 0 ]; then
	echo "ERROR: Unable to change owner of working directory '$BW_TOOLS_WORKING_DIR'."
	exit 1
fi

# Load the redhat utility functions
if [ -f "/etc/redhat-release" ]; then
	. /etc/init.d/functions
fi


bw_print_success() {
	if [ -f "/etc/redhat-release" ]; then
		echo_success; echo
	else
		echo "OK"
	fi

}

bw_print_failure() {

	if [ -f "/etc/redhat-release" ]; then
		echo_failure; echo
	else
		echo "FAILED"
	fi

}


# Check if a process is running as user $3 with pid file $1, and as a fallback
# check if any entry in the running process list matches $2.
bw_is_running() {

	# If a PID file exists, then any inconsitency regarding the pid file
	# such as being unable to read from it, or not being able to find a
	# running process matching the pid in the file is a fatal error.
	if [ -f $1 ]; then
		read pid < $1
		if [ $? != 0 ]; then
			echo "Failed to read PID from '$1'"
			bw_print_failure
			exit 1
		fi

		ps --no-headers --pid=$pid > /dev/null
		if [ $? != 0 ]; then
			echo "Existing .pid file found ($1), but no process with pid $pid running"
			echo "Removing $1"
			rm -f "$1"
			return 0
		fi
		return 1
	fi

#	NUMPROCS=`ps -U $3 -u $3 ux | grep "$2" |grep -v grep | wc -l`
#	if [ $NUMPROCS -ge 1 ]; then
#		return 1
#	fi

	return 0
}


# Wait for a maximum of STATE_TIMER seconds to check whether a process is still
# alive. arguments $2, $3, $4 are passed on to bw_is_running.
bw_check_running_state() {

	STATE_TIMER=5
	loopcounter=$STATE_TIMER
	while [ $loopcounter != 0 ];
	do
		loopcounter=`expr $loopcounter - 1`

		bw_is_running "$2" "$3" "$4"
		# If the process is no longer running, jump out and notify the
		# caller the process has died.
		if [ $? == $1 ]; then
			return 1
		fi
		sleep 1
	done

	return 0
}


bw_has_started() {
	bw_check_running_state 1 "$1" "$2" "$3"
	return $?
}

bw_has_stopped() {
	bw_check_running_state 0 "$1" "$2" "$3"
	return $?
}


bw_stop_process() {

	# $1 = procname
	# $2 = pidfile
	# $3 = process string
	# $4 = process user

	echo -n "Stopping $1: "

	if [ ! -f "$2" ]; then
		bw_print_failure
		echo "$1 not running or pid file '$2' missing"
		return 1
	else

		# Read the PID from the pid file
		read pid < "$2"
		if [ $? != 0 ]; then
			echo -n "Failed to read PID from '$2'"
			bw_print_failure
			return 1
		fi


		# Try a kill -INT first
		kill -s INT $pid > /dev/null
		if [ $? != 0 ]; then
			bw_print_failure
			echo "Failed to send INT signal to process $pid. "
			return 1
		fi

		bw_has_stopped "$2" "$3" "$4"
		if [ $? == 0 ]; then

			# If the kill -INT failed to terminate the process as a final
			# resort we try to send kill -KILL (ie: kill -9). This should
			# terminate the process, and if not we can't deal with it any
			# more.
			
			kill -s KILL $pid > /dev/null
			if [ $? != 0 ]; then
				bw_print_failure
				echo "Failed to send KILL signal to process $pid. "
				return 1
			else
				echo -n "Sent SIGKILL (forced shutdown). "
			fi

			bw_has_stopped "$2" "$3" "$4"
			if [ $? == 0 ]; then
				bw_print_failure
				echo "All attempts to terminate $1 failed."
				return 1
			fi

			# If the PID file still exists which may occur after sending
			# a SIGKILL, forceably remove the .pid file.
			if [ -f $2 ]; then
				rm -f $2
			fi
		fi
	fi

	bw_print_success
	return 0
}

