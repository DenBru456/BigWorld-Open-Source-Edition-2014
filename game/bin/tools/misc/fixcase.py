#!/usr/bin/env python
"""
This script takes a directory as an argument and then recursively modifies
any filename with uppercase letters (changing to lowercase)

python fixnames.py d:\mf
Note: You must supply the FULL PATH not a relative path.
"""

import os 
import string
import re
import stat
from sys import *


def fixNames( dir ):
	try:
		os.chdir( dir )
	except:
		return

	for file in os.listdir( dir ):
		if file == "CVS":
			continue

		st = os.stat(dir + "/" + file)
		if stat.S_ISDIR( st[stat.ST_MODE] ):
			fixNames( dir + "/" + file )

		if re.search(re.compile("[A-Z]"), file) != None:
			print "\n" + dir + "\\" + file
			s = raw_input("Convert to lcase? ")
			if len(s) > 0 and (s[0] == "y" or s[0] == "Y"): 
				newfile = string.lower(file)
				print "Converted..."
				os.rename(file, newfile)



if len(argv) != 2:
	print "Usage: ", argv[0], "dir-name"
	print "Note: the directory must be a FULL PATH"
	exit()

fixNames( argv[1] )
exit()

#fixcase.py
