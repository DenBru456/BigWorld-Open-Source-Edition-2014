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

%define name					bigworld-bwmachined
%define bwmachined_dir			%{bigworld_dir}/bwmachined
%define bwmachined_name  		bwmachined2
%define bwmachined_initd_dir	%{bwmachined_dir}/init.d
%define bwmachined_initd_file	%{bwmachined_initd_dir}/%{bwmachined_name}
%define bwmachined_sbin_dir		%{bwmachined_dir}/sbin
%define bwmachined_sbin_file	%{bwmachined_sbin_dir}/%{bwmachined_name}
## PLACEHOLDER: PACKAGE SPECIFIC MACROS 


Name:		%{name}
Version:	%{bw_version}.%{bw_patch}
Release:	%{bw_patch}.%{bw_revision}%{?dist}
Group:		Middleware/MMOG
Vendor:		BigWorld Pty Ltd
URL:		http://www.bigworldtech.com/
Packager:	BigWorld Support <support@bigworldtech.com>
License:	BigWorld License
Summary:	The BWMachined component of the BigWorld server tools.
## ExcludeArch: <arch1>, <arch2>, ..., <archN>
ExclusiveArch: i386 x86_64
## Excludeos: <os1>, <os2>, ..., <osN>
Exclusiveos: linux
## The next line is used for generating the actual BuildRoot line from script
## please do not remove it.
## PLACEHOLDER: BUILDROOT
Provides: bigworld-bwmachined-%{bw_version}
Requires(pre):  /sbin/service, /sbin/chkconfig
Requires(post): /sbin/service, /sbin/chkconfig
## Requires: 
## Obsoletes:
## Conflicts:


%description
This package contains the BWMachined component of the BigWorld Server.  The
BWMachined component is run on every machine that runs a BigWorld process.  


# This is pre-install script.
%pre 

if [ -f %{_initrddir}/%{bwmachined_name} ]; then
	/sbin/service %{bwmachined_name} stop > /dev/null 2>&1
	/sbin/chkconfig --del %{bwmachined_name}
fi

# Delete old bwmachined, if any.
if [ -f /usr/local/sbin/bwmachined2 ]; then
	rm -rf /usr/local/sbin/bwmachined2
fi


# This is post-install script. 
%post

# Buffer kernel variables
SYSCTL="/etc/sysctl.conf"
AUTO_INCREASE_ENTRIES=true
echo "  Checking $SYSCTL for socket buffer size variable entries..."

for VAR_SUFFIX in 'rmem_max' 'wmem_max' 'wmem_default'; do
	VAR=net.core.$VAR_SUFFIX
	ENTRY=`grep "$VAR" $SYSCTL`
	case $VAR_SUFFIX in
		rmem_max     ) VAR_MIN=16777216 ;;
		wmem_max     ) VAR_MIN=1048576 ;;
		wmem_default ) VAR_MIN=1048576 ;;
	esac
	
	# If there is no entry for the variable in sysctl.conf, add one.
	if [[ ! $ENTRY ]]; then
		echo "    Adding entry for $VAR to $SYSCTL"
		echo "$VAR = $VAR_MIN" >> $SYSCTL
		/sbin/sysctl $VAR=$VAR_MIN &> /dev/null
		
	# If there is an entry with a value that is too small, give a warning
	elif [[ ${ENTRY#*=} -lt $VAR_MIN ]]; then
		echo "    WARNING: Entry for $VAR in $SYSCTL is too low."
		echo "      Value of ${ENTRY#*=} found. Expecting at least $VAR_MIN."
	fi
done

/sbin/chkconfig --add %{bwmachined_name}
/sbin/service %{bwmachined_name} start


# This is pre-uninstall script.
%preun 
# Only run this when the software is being uninstalled, rather than
# upgraded/updated. $1 is an argument passed to script automatically 
# which stores the count of version of the software installed after
# the installation or uninstall. 
if [ "$1" -eq 0 ]; then
	/sbin/service %{bwmachined_name} stop > /dev/null 2>&1
	/sbin/chkconfig --del %{bwmachined_name}
fi

exit 0


# Files to include in binary RPM.
%files 

## PLACEHOLDER: FILES FOR RPM


%changelog
* Tue Aug 08 2008 BigWorld Support
- Version 1.0.


