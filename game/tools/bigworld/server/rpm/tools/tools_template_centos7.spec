# ========== IMPORTANT ==========
# 
# DO NOT BUILD PACKAGES AS ROOT USER!!!!!!
#
# Doing so may damage the system (i.e. render the system unusable) if 
# the RPM spec file contains error, since the error may delete system 
# files.



# Macros. 
%define bigworld_dir			/opt/bigworld/%{bw_version}
%define bigworld_current_dir	/opt/bigworld/current

%define name					bigworld-tools
%define bigworld_tools_dir		%{bigworld_dir}/tools
%define bigworld_initrd_dir		%{bigworld_tools_dir}/init.d
%define bigworld_conf_dir		%{_sysconfdir}/bigworld
%define message_logger_dir		/var/log/bigworld/message_logger
%define daemon_log_dir			/var/log/bigworld
%define pid_dir					/var/run/bigworld
%define web_console_data_dir	/var/lib/bigworld/web_console
%define web_console_self_profiling_dir %{web_console_data_dir}/self_profiling
%define web_console_upload_dir  %{web_console_data_dir}/uploads
%define bwlockd_data_dir		/var/lib/bigworld/bwlockd
%define cron_hourly_dir			/etc/cron.hourly
%define logrotate_dir			/etc/logrotate.d
%define bw_tools_user			bwtools
%define services				bw_message_logger bw_stat_logger bw_web_console
%define service_bwlockd			bw_lockd
%define current_message_logger_log_format	8
## PLACEHOLDER: PACKAGE SPECIFIC MACROS 


Name:		%{name}
Version:	%{bw_version}.%{bw_patch}
Release:	%{bw_patch}.%{bw_revision}%{?dist}
Group:		Middleware/MMOG
Vendor:		BigWorld Pty Ltd
URL:		http://www.bigworldtech.com/
Packager:	BigWorld Support <support@bigworldtech.com>
License:	BigWorld License
Summary:	The BigWorld server tools.
## ExcludeArch: <arch1>, <arch2>, ..., <archN>
ExclusiveArch: x86_64
## Excludeos: <os1>, <os2>, ..., <osN>
Exclusiveos: linux
## The next line is used for generating the actual BuildRoot line from script
## please do not remove it.
## PLACEHOLDER: BUILDROOT
Provides: bigworld-tools-%{bw_version}
Requires(pre): /usr/bin/systemctl, /usr/bin/id
Requires(post): /usr/bin/systemctl
Requires: bigworld-bwmachined, epel-release, TurboGears < 2.0, MySQL-python >= 1.2.2, python-ldap, python-pymongo, python-dateutil, python-simplejson
## Obsoletes:
## Conflicts:


%description
This package contains the Server Tools component of the BigWorld Server. This
includes WebConsole, MessageLogger and StatLogger.


%package bwlockd
Summary:	BigWorld WorldEditor lock daemon 
Group:		Middleware/MMOG
Requires:	bigworld-tools = %{version}-%{release}

%description bwlockd
This package contains the BigWorld lock daemon which allows multiple artists
to world build within the same space by co-ordinating and 'locking' a region
of the space that is currently being worked on by each artist.

# This is pre-install script.
%pre 

for service in %{services}; do
	if test -f %{bigworld_initrd_dir}/$service; then
		/usr/bin/systemctl stop $service > /dev/null 2>&1
		/usr/bin/systemctl disable $service
	fi
done

# If there is an older version of MessageLogger installed, move it out of the
# way so new logs can be written in place.
if test -f %{message_logger_dir}/version; then

	log_version=`cat %{message_logger_dir}/version | tr -d '\n'`
	# Move it out of the way
	if [ $log_version != %{current_message_logger_log_format} ]; then
		mv %{message_logger_dir} %{message_logger_dir}_v$log_version
		echo "Note: Archiving old message logs to" %{message_logger_dir}_v$log_version
	fi
fi

if ! id %{bw_tools_user} > /dev/null 2>&1; then
	adduser -r %{bw_tools_user}
fi


%pre bwlockd

if test -f %{bigworld_initrd_dir}/%{service_bwlockd}; then
	/usr/bin/systemctl stop %{service_bwlockd} > /dev/null 2>&1
	/usr/bin/systemctl disable %{service_bwlockd}
fi



# This is post-install script. 
%post

# All the directories required to write into for the tools
for dir in %{daemon_log_dir} %{pid_dir} %{message_logger_dir} %{web_console_data_dir}; do
	if ! test -d $dir; then
		mkdir -p $dir
	fi
	chown -R "%{bw_tools_user}:%{bw_tools_user}" $dir
done


# Set the SELinux security context before starting any services that might
# use the file.
if [ -f /usr/sbin/selinuxenabled ]; then

	# Run the command and check the return status (0 == enabled, 1 == disabled)
	/usr/sbin/selinuxenabled
	if [ $? == 0 ]; then
		chcon -t textrel_shlib_t %{bigworld_tools_dir}/site-packages/_bwlog.so
	fi
fi


# Add and start the services
for service in %{services}; do
	/usr/bin/systemctl daemon-reload
	/usr/bin/systemctl enable $service

	if [ $service == "bw_stat_logger" ]; then
		grep --quiet "enable>true<" /etc/bigworld/stat_logger.xml

		# If we didn't find enabled data store, don't start
		if [ $? != 0 ]; then
			echo "***********************************************************"
			echo "NOTE: StatLogger has been installed but must be configured"
			echo "      prior to running. Please refer to the Server"
			echo "      Installation Guide document for information on how to"
			echo "      configure and start StatLogger."
			echo "***********************************************************"
		else
			/usr/bin/systemctl start $service
		fi

	else
		/usr/bin/systemctl start $service
	fi

done

# Initialise the log files so that rotation will work correctly
su -c "%{bigworld_initrd_dir}/bw_message_logger logrotate" %{bw_tools_user} > /dev/null 2>&1 || true
su -c "%{bigworld_initrd_dir}/bw_stat_logger loginit" > /dev/null 2>&1 || true
su -c "%{bigworld_initrd_dir}/bw_web_console logrotate" > /dev/null 2>&1 || true


%post bwlockd

# All the directories required to write into for the tools
if ! test -d %{bwlockd_data_dir}; then
	mkdir -p %{bwlockd_data_dir}
fi
chown -R "%{bw_tools_user}:%{bw_tools_user}" %{bwlockd_data_dir}

# This is pre-uninstall script.
%preun 


# Only run this when the software is being uninstalled, rather than
# upgraded/updated. $1 is an argument passed to script automatically 
# which stores the count of version of the software installed after
# the installation or uninstall. 
if [ "$1" -eq 0 ]; then
	for service in %{services}; do
		/usr/bin/systemctl stop $service > /dev/null 2>&1
		/usr/bin/systemctl disable $service
	done
fi

%preun bwlockd

if [ "$1" -eq 0 ]; then
	/usr/bin/systemctl stop %{service_bwlockd} > /dev/null 2>&1
	/usr/bin/systemctl disable %{service_bwlockd}
fi


# Files to include in binary RPM.
%files 

## PLACEHOLDER: FILES FOR RPM

%files bwlockd

## PLACEHOLDER: FILES FOR RPM: bwlockd


#%changelog

