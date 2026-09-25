import os
import sys

import cluster_constants

import logging
log = logging.getLogger( __name__ )


# We have to do all this crap because Windows can't load bwlog.so
MESSAGE_LOGGER_MSG = 107
MESSAGE_LOGGER_REGISTER = MESSAGE_LOGGER_MSG + 1
MESSAGE_LOGGER_PROCESS_DEATH = MESSAGE_LOGGER_REGISTER + 2

# Log severity levels from debug.hpp
MESSAGE_PRIORITY_TRACE, \
MESSAGE_PRIORITY_DEBUG, \
MESSAGE_PRIORITY_INFO, \
MESSAGE_PRIORITY_NOTICE, \
MESSAGE_PRIORITY_WARNING, \
MESSAGE_PRIORITY_ERROR, \
MESSAGE_PRIORITY_CRITICAL, \
MESSAGE_PRIORITY_HACK, \
MESSAGE_PRIORITY_SCRIPT, \
NUM_MESSAGE_PRIORITY = range( 10 )


def validateBWLogModule():
		assert _bwlog.MESSAGE_LOGGER_MSG == MESSAGE_LOGGER_MSG
		assert _bwlog.MESSAGE_LOGGER_REGISTER == MESSAGE_LOGGER_REGISTER
		assert _bwlog.MESSAGE_LOGGER_PROCESS_DEATH == \
			   MESSAGE_LOGGER_PROCESS_DEATH


import bw_shared_object_path
import _bwlog

validateBWLogModule()

SEVERITY_LEVELS = _bwlog.SEVERITY_LEVELS

# bwlog.py
