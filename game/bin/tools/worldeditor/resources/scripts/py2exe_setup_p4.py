#
# Simple setup script for py2exe to compile p4_stub.py into an executable.
#

from distutils.core import setup
import py2exe

setup(console=['p4_stub.py'])