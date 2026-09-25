import ModelEditorDirector
import ModelEditor
import ResMgr

import Actions
reload( Actions )
from Actions import *

import ToolbarUIAdapter
reload( ToolbarUIAdapter )
from ToolbarUIAdapter import *

import MenuUIAdapter
reload( MenuUIAdapter )
from MenuUIAdapter import *

import UIExt
reload( UIExt )
from UIExt import *

def slrCurrentTimeAdjust( value, min, max ):
	# to stop the slider wrapping around when set to the right, minus 1 minute to limit the sliders maximum.
	if value == max: 
		value = max-1
	percent = (value-min) / (max-min) * 24.0
	ModelEditor.romp.setTime( percent )
