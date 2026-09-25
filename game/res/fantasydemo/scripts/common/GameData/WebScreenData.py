# --------------------------------------------------------------------------
# This module contains all the data that describes the different 
# WebScreen types. It is used by the client and tools.
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# The type of the WebScreen.
# --------------------------------------------------------------------------
OUTSIDE			= 0		# The outside WebScreen.
INSIDE			= 1		# The inside WebScreen.

# --------------------------------------------------------------------------
# The dictionary of models for each WebScreen
# --------------------------------------------------------------------------
modelNames = {
	OUTSIDE:		"sets/urban/props/tv/models/tv.model",
	INSIDE:			"sets/urban/props/tv/models/tv_small.model"
}

# --------------------------------------------------------------------------
# The dictionary of display names for each WebScreen type.
# --------------------------------------------------------------------------
displayNames = {
	OUTSIDE:			"Outside WebScreen",
	INSIDE:				"Inside WebScreen"
}

# --------------------------------------------------------------------------
# The dictionary of editor friendly display names for each WebScreen type.
# --------------------------------------------------------------------------
editorDisplayNames = {
	OUTSIDE:			"Outside WebScreen",
	INSIDE:				"Inside WebScreen"
}

# --------------------------------------------------------------------------
# The effect of graphics settings on the WebScreen.
# --------------------------------------------------------------------------
EFFECT_QUALITY			= 0		# Different Graphics Settings effect quality
EFFECT_SCROLLING		= 1		# Different Graphics Settings effect scrolling

# --------------------------------------------------------------------------
# The dictionary of editor friendly display names for each WebScreen 
# graphics setting.
# --------------------------------------------------------------------------
editorDisplayGraphicsSettingsBehaviour = {
	EFFECT_QUALITY:			"Effect Quality",
	EFFECT_SCROLLING:		"Effect Scrolling"
}
