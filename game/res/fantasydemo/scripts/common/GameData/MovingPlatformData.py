# --------------------------------------------------------------------------
# This module contains all the data that describes the different
# MovingPlatform types. It is used by the client, server and tools.
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# The type of the platform.
# --------------------------------------------------------------------------
DEFAULT			= 0		# The default type.
LOSPEC			= 1		# The lospec platform type.

# --------------------------------------------------------------------------
# The dictionary of models for each platform type.
# --------------------------------------------------------------------------
modelNames = {
	DEFAULT:		"sets/items/platform.model",
	LOSPEC:			"sets/items/platform.model",
}

# --------------------------------------------------------------------------
# The dictionary of display names for each platform type.
# --------------------------------------------------------------------------
displayNames = {
	DEFAULT:			"Moving Platform",
	LOSPEC:				"Moving Platform",
}

# --------------------------------------------------------------------------
# The dictionary of editor friendly display names for each platform type.
# --------------------------------------------------------------------------
editorDisplayNames = {
	DEFAULT:			"Moving Platform",
	LOSPEC:				"Moving Platform (minspec)",
}