import os, sys
from bwtest import config

modules = ["bwtest", "helpers", "primitives"]

currentDir = os.getcwd()
outputDir = os.path.abspath( "docs" )
sys.path.append( os.path.abspath( "../doc/gen/python" ))
os.chdir( "../doc/gen/python" )

import generate_python
generate_python.generate( { 'testing': { 'name': 'Testing Framework' } }, 
						modules, currentDir, outputDir)
