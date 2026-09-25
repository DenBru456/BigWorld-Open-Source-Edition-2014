# This module automatically sets up the path of the pycommon directory
# for the test scripts to use.

import os
import sys

localPath = os.path.dirname( os.path.abspath( __file__ ) )
pycommonPath = os.path.abspath(
					localPath + "/../../bigworld/tools/server" )
sys.path.append( pycommonPath )
