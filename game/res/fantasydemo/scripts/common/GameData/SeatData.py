# --------------------------------------------------------------------------
# This module contains all the data that describes the different 
# Seat types. It is used by the client, server and tools.
# --------------------------------------------------------------------------

############################################################################
# The following are some local member variables.  They are not defined in  #
# the Entity Definition Script, hence not available to BigWorld.  However, #
# they are available to all other scripts and external components as per a #
# normal Python script.                                                    #
############################################################################


# --------------------------------------------------------------------------
# The type of the seat is the look and feel of the seat.
#
# The UNKNOWN type value means that the exact fixture has not yet been
# determined. It means that the server will change the type later as
# more information is allowed to the client.
# --------------------------------------------------------------------------
UNKNOWN			= -1	# This seat's type has not yet been identified.
STANDARD		= 0		# Ordinary sitzplatz - no model of own
WOODEN_STOOL	= 2		# The three-legged wooden stool.
LOSPEC_STOOL	= 3		# Lospec version of the wooden stool.


# --------------------------------------------------------------------------
# The displayNames list contains the displayable names for the sub-types
# of entities. Every type of effects entity has to have a display name.
# It is safe to check for a valid entity type by looking for it in this
# dictionary. That is, if the type is found, the entity has a valid type.
# --------------------------------------------------------------------------
displayNames = {
	UNKNOWN:		"Unidentified Seat",
	STANDARD:		"Seat",
	WOODEN_STOOL:	"Wooden Stool",
	LOSPEC_STOOL:   "Wooden Stool"
}


# --------------------------------------------------------------------------
# The editorDisplayNames list contains the editor friendly displayable names
# for each seat sub-type.
# --------------------------------------------------------------------------
editorDisplayNames = {
	UNKNOWN:		"Unidentified Seat",
	STANDARD:		"Seat",
	WOODEN_STOOL:	"Wooden Stool",
	LOSPEC_STOOL:   "Wooden Stool (minspec)"
}


# --------------------------------------------------------------------------
# The dictionary of fixture models is listed below. A model name is the
# name of the file containing model information for drawing and animating
# fixtures in the game world.
# --------------------------------------------------------------------------
modelNames = {
	UNKNOWN:		"sets/town/props/t_stool.model",
	STANDARD:		"sets/town/props/t_stool.model",
	WOODEN_STOOL:	"sets/town/props/t_stool.model",
	LOSPEC_STOOL:	"sets/minspec/props/stool/models/stool.model"
}