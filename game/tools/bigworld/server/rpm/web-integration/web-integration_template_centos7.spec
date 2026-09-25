# ========== IMPORTANT ==========
# 
# DO NOT BUILD PACKAGES AS ROOT USER!!!!!!
#
# Doing so may damage the system (i.e. render the system unusable) if 
# the RPM spec file contains error, since the error may delete system 
# files.



# Macros. 
%define name					bigworld-web-integration
## PLACEHOLDER: PACKAGE SPECIFIC MACROS 


Name:		%{name}
Version:	%{bw_version}.%{bw_patch}
Release:	%{bw_patch}.%{bw_revision}%{?dist}
Group:		Middleware/MMOG
Vendor:		BigWorld Pty Ltd
URL:		http://www.bigworldtech.com/
Packager:	BigWorld Support <support@bigworldtech.com>
License:	BigWorld License
Summary:	Packages required by the BigWorld server Web Integration.
## ExcludeArch: <arch1>, <arch2>, ..., <archN>
ExclusiveArch: i386 x86_64
## Excludeos: <os1>, <os2>, ..., <osN>
Exclusiveos: linux
## The next line is used for generating the actual BuildRoot line from script
## please do not remove it.
## PLACEHOLDER: BUILDROOT
Provides: bigworld-web-integration-%{bw_version}
Requires: epel-release, httpd, curl
%if "%{dist}" == ".el5"
Requires: php53, php53-gd
%else
Requires: php >= 5.4, php-gd >= 5.4
%endif
## Requires(pre):
## Requires(post):

## Obsoletes:
## Conflicts:

%description
This package provides no direct files but is used to pull in dependancies
which are commonly used for PHP WebIntegration with the BigWorld Server.


# This is pre-install script.
#%pre 

# This is post-install script. 
#%post


# This is pre-uninstall script.
#%preun 

# Files to include in binary RPM.
%files 

## PLACEHOLDER: FILES FOR RPM

#%changelog

