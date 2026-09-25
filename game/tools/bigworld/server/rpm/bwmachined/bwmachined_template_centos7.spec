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
%define pid_dir					/var/run/bigworld

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
ExclusiveArch: x86_64
## Excludeos: <os1>, <os2>, ..., <osN>
Exclusiveos: linux
## The next line is used for generating the actual BuildRoot line from script
## please do not remove it.
## PLACEHOLDER: BUILDROOT
Provides: bigworld-bwmachined-%{bw_version}
Requires(pre):  /usr/bin/systemctl
Requires(post): /usr/bin/systemctl
## Requires: 
## Obsoletes:
## Conflicts:


%description
This package contains the BWMachined component of the BigWorld Server.  The
BWMachined component is run on every machine that runs a BigWorld process.  


# This is pre-install script.
%pre 

if [ -f %{bwmachined_initd_dir}/%{bwmachined_name} ]; then
	/usr/bin/systemctl stop %{bwmachined_name} > /dev/null 2>&1
	/usr/bin/systemctl disable %{bwmachined_name}
fi

# Delete old bwmachined, if any.
if [ -f /usr/local/sbin/bwmachined2 ]; then
	rm -rf /usr/local/sbin/bwmachined2
fi


# This is post-install script. 
%post


/usr/bin/systemctl daemon-reload
/usr/bin/systemctl enable %{bwmachined_name}
/usr/bin/systemctl start %{bwmachined_name}


# This is pre-uninstall script.
%preun 
# Only run this when the software is being uninstalled, rather than
# upgraded/updated. $1 is an argument passed to script automatically 
# which stores the count of version of the software installed after
# the installation or uninstall. 
if [ "$1" -eq 0 ]; then
	/usr/bin/systemctl stop %{bwmachined_name} > /dev/null 2>&1
	/usr/bin/systemctl disable %{bwmachined_name}
fi

exit 0


# Files to include in binary RPM.
%files 

## PLACEHOLDER: FILES FOR RPM


#%changelog

