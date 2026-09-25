import chapters

CURRENT_CHAPTER = chapters.BASIC_NPC

# ------------------------------------------------------------------------------
# Section: Exposed interface
# ------------------------------------------------------------------------------

# The predicates and constants in this section should be used in various
# resource files to selectively include text only in particular stages of the
# tutorial.  At the moment, we only support a linear chapter progression
# (i.e. there is no branching of tutorial streams at the moment) however, that
# could easily be supported at a later date using the existing interface
# (tutorial.includes()).

# The chapter that we're running by default.  This should always be the 'head'
# version, if you are planning to run an earlier version you need to strip the
# resources prior to running.


def excludes( chapter ):
	return not includes( chapter )

def includes( chapter ):
	if chapter == chapters.NEVER:
		return False

	if chapter < 0:
		return not excludes( -chapter )

	return chapter <= CURRENT_CHAPTER


def setChapter( chapter ):
	global CURRENT_CHAPTER
	CURRENT_CHAPTER = chapter

# tutorial.py
