#
# Simple setup script for py2exe to compile svn_stub.py into an executable.
#

from distutils.core import setup
import py2exe

setup(console=['svn_stub.py'])