# ========== IMPORTANT ==========
# 
# DO NOT BUILD PACKAGES AS ROOT USER!!!!!!
#
# Doing so may damage the system (i.e. render the system unusable) if 
# the RPM spec file contains error, since the error may delete system 
# files.



# Macros. 
%define name					bigworld-devel
## PLACEHOLDER: PACKAGE SPECIFIC MACROS 


Name:		%{name}
Version:	%{bw_version}.%{bw_patch}
Release:	%{bw_patch}.%{bw_revision}%{?dist}
Group:		Middleware/MMOG
Vendor:		BigWorld Pty Ltd
URL:		http://www.bigworldtech.com/
Packager:	BigWorld Support <support@bigworldtech.com>
License:	BigWorld License
Summary:	Packages useful for BigWorld server development.
## ExcludeArch: <arch1>, <arch2>, ..., <archN>
ExclusiveArch: x86_64
## Excludeos: <os1>, <os2>, ..., <osN>
Exclusiveos: linux
## The next line is used for generating the actual BuildRoot line from script
## please do not remove it.
## PLACEHOLDER: BUILDROOT
Provides: bigworld-devel-%{bw_version}
## Requires(pre):
## Requires(post):
Requires: gcc, gcc-c++, gdb, make, python-devel, mariadb-devel, subversion, SDL-devel, MySQL-python, sqlite-devel, readline-devel, gdbm-devel, bzip2, bzip2-devel, ncurses-devel, zlib-devel strace, binutils-devel, patch, unzip, bc
## Obsoletes:
## Conflicts:

%description
This package provides no direct files but is used to pull in dependancies
which are commonly used for developing the BigWorld Server.


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

