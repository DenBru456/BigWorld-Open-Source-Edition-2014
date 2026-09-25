import sys
import platform

# Add path required for importing based on architecture.
architecture = platform.architecture();
if architecture[1] == "WindowsPE":
	if architecture[0] == "32bit":
		sys.path.append("../../../tools/assetprocessor/win32")
	elif architecture[0] == "64bit":
		sys.path.append("../../../tools/assetprocessor/win64")

# Path to common scripts for importing.
sys.path.append("../../../../res/bigworld/scripts/common")

# Attempt to import.
from _AssetProcessor import *
