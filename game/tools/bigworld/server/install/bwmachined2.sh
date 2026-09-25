#!/bin/sh
#
# description: The bwmachined daemon reports machine usage statistics, \
#		including processes MicroForte is interested in.
# processname: bwmachined
# chkconfig: 2345 80 50
# description: BigWorld server - machine monitoring daemon \
#             http://www.bigworldtech.com
#
### BEGIN INIT INFO
# Provides:          bwmachined2
# Required-Start:    $local_fs $network $syslog $time
# Should-Start:
# Required-Stop:     $local_fs $network $syslog
# Default-Start:     3 4 5
# Default-Stop:      0 1 2 6
# Short-Description: Start BigWorld machine daemon
# Description:       Start BigWorld Machined Daemon, the service that enables \
#                    a host machine to run services within a BigWorld cluster.
### END INIT INFO

# Prepare the PID directory.
PIDDIR="/var/run/bigworld"
BW_CONFIG="/etc/bigworld.conf"
BW_VAL_REGEX="^[[:alnum:]_]+[ 	]*=[ 	]*(.*)[ 	]*$"

if [ -f $BW_CONFIG ]; then
	TMP_PIDDIR=`grep piddir $BW_CONFIG | sed -r -e "s/$BW_VAL_REGEX/\1/"`
	if [ ! -z $TMP_PIDDIR ]; then
		PIDDIR=$TMP_PIDDIR
	fi
fi

if [ ! -d $PIDDIR ]; then
	mkdir -p $PIDDIR
	if [ $? != 0 ]; then
		echo "ERROR: Unable to create PID directory '$PIDDIR'."
		exit 1
	fi
fi

SBINDIR=/usr/sbin
EXE=$SBINDIR/bwmachined2
BASE=`basename $EXE`
PROCNAME="bwmachined2"
PIDFILE="$PIDDIR/$PROCNAME.pid"
ARGS="--pid $PIDFILE"

# Note that any processes started by machined will also get this nice value
NICE=-10

# Set this to change the coredump output path. By default, it is empty, which
# means the current working directory of the process. BWMachined spawns
# processes from their containing directory, e.g. bigworld/bin/Hybrid64.
#
# Note: Changing this affects all processes on this machine, not just BigWorld
# processes that output coredumps.

CORE_PATH=

# Check linux distribution redhat or debian
if [ -f /etc/debian_version ]; then
	PLOCK=/var/run/$BASE.pid
else
	PLOCK=/var/lock/subsys/$BASE
	. /etc/rc.d/init.d/functions
fi

# Check for trailing slash in CORE_PATH, add if necessary.
if [ ! -z $CORE_PATH ]; then
	if [ ! -d $CORE_PATH ]; then
		echo "CORE_PATH not set to a directory"
		exit 1
	fi
	CORE_PATH="${CORE_PATH}/"
fi

do_debian_start()
{
	start-stop-daemon --start --quiet --exec /usr/bin/nice -- -n $NICE $EXE $ARGS
	RETVAL=$?
	ps aux | grep $EXE | grep -v grep | awk '{ print $2 }' > $PLOCK
	echo "."
}

do_redhat_start()
{
	daemon nice -n $NICE $EXE $ARGS
	RETVAL=$?
	echo
	[ $RETVAL -eq 0 ] && touch $PLOCK
}

do_debian_stop()
{
	start-stop-daemon --stop --pidfile $PLOCK --exec $EXE
	RETVAL=$?
	echo "."
}

do_redhat_stop()
{
	killproc $BASE
	RETVAL=$?
	echo
	[ $RETVAL -eq 0 ] && rm -f $PLOCK
}

case "$1" in
  start)
	echo -n "Starting $BASE: "
	(echo ${CORE_PATH}core.%e.%h.%p > /proc/sys/kernel/core_pattern) 2> /dev/null ||
		echo "INFO: Unable to update /proc/sys/kernel/core_pattern"
	ulimit -c unlimited
	if [ -f /etc/debian_version ]; then
		do_debian_start
	else
		do_redhat_start
	fi
	;;
  stop)
  	echo -n "Stopping $BASE: "
	if [ -f /etc/debian_version ]; then
		do_debian_stop
	else
		do_redhat_stop
	fi
	;;
  status)
	status $BASE
	RETVAL=$?
	;;
  restart|reload)
	$0 stop
	RETVAL=$?
	$0 start
	RETVAL=$[ $RETVAL + $? ]
	;;

  install)
	if [ `uname -m` == "x86_64" ]; then
		MF_CONFIG="Hybrid64"
	else
		MF_CONFIG="Hybrid"
	fi

	BW_TOOLS_BIN=`dirname $0`"/../bin/$MF_CONFIG"
	if [ ! -d $BW_TOOLS_BIN ]; then
		echo "ERROR: Installation must be performed within the directory bigworld/tools/server/install"
		exit 1
	fi

	$0 remove
	shift 
 	awk -v v="$*" '{print} /^ARGS=/{print $0 "\"" v "\""}' < $0 > /etc/init.d/$BASE
	chmod +x /etc/init.d/$BASE
	
	# copy bwmachined2 binary
	mkdir  -p $SBINDIR
	cp "$BW_TOOLS_BIN/$BASE" $EXE

	# install into runlevel script dirs
	if [ -x /usr/sbin/update-rc.d ]; then # Debian system
		/usr/sbin/update-rc.d $BASE defaults 21
	elif [ -x /sbin/chkconfig ]; then # RedHat system
		/sbin/chkconfig --add $BASE
	else
		ln -s /etc/init.d/$BASE /etc/rc1.d/K21$BASE
		ln -s /etc/init.d/$BASE /etc/rc2.d/S21$BASE
		ln -s /etc/init.d/$BASE /etc/rc3.d/S21$BASE
		ln -s /etc/init.d/$BASE /etc/rc4.d/S21$BASE
		ln -s /etc/init.d/$BASE /etc/rc5.d/S21$BASE
		ln -s /etc/init.d/$BASE /etc/rc6.d/K21$BASE
	fi
	/etc/init.d/$BASE start
	;;

  remove)
	if [ -f /etc/init.d/$BASE ]; then
		$0 stop
		rm -f $EXE
		if [ -x /usr/sbin/update-rc.d ]; then
			/usr/sbin/update-rc.d -f $BASE remove
		elif [ -x /sbin/chkconfig ]; then
			/sbin/chkconfig --del $BASE
		else
			rm -f /etc/rc[1-6].d/[SK][0-9][0-9]$BASE
		fi
	  	rm -f /etc/init.d/$BASE
	fi
	RETVAL=0
	;;

  version)
	$EXE --version
	;;

  *)
	echo "Usage: $BASE.sh {start|stop|status|restart|reload|install|remove}"
	exit 1
	;;
esac

exit $RETVAL
