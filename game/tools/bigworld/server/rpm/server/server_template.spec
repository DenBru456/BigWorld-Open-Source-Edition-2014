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

%define name					bigworld-server
%define bigworld_server_dir		%{bigworld_dir}/server
%define bw_server_user			bwserver
## PLACEHOLDER: PACKAGE SPECIFIC MACROS 


Name:		%{name}
Version:	%{bw_version}.%{bw_patch}
Release:	%{bw_patch}.%{bw_revision}%{?dist}
Group:		Middleware/MMOG
Vendor:		BigWorld Pty Ltd
URL:		http://www.bigworldtech.com/
Packager:	BigWorld Support <support@bigworldtech.com>
License:	BigWorld License
Summary:	BigWorld server binaries.
## ExcludeArch: <arch1>, <arch2>, ..., <archN>
ExclusiveArch: x86_64
## Excludeos: <os1>, <os2>, ..., <osN>
Exclusiveos: linux
## The next line is used for generating the actual BuildRoot line from script
## please do not remove it.
## PLACEHOLDER: BUILDROOT

## config(bigworld-server) is required for the server, and would be provided by
## Autoprov if it were enabled.
Provides: bigworld-server-%{bw_version}, config(bigworld-server)
Autoprov: 0

## Requires(pre):  
## Requires(post): 
Requires: bigworld-bwmachined mysql >= 5.0
## Obsoletes:
## Conflicts:


%description
This package contains the BigWorld Server binary executables and the common
resources.

# This is pre-install script.
%pre 

if ! id %{bw_server_user} > /dev/null 2>&1; then
	adduser -r --shell /sbin/nologin %{bw_server_user}
fi

# This is post-install script. 
%post


# This is pre-uninstall script.
%preun 

# Files to include in binary RPM.
%files 

## PLACEHOLDER: FILES FOR RPM


%changelog
* Tue Aug 08 2008 BigWorld Support
- Version 1.0.


