import ParticleEditorDirector
import ParticleEditor
import ResMgr

import ToolbarUIAdapter
reload( ToolbarUIAdapter )
from ToolbarUIAdapter import *

import MenuUIAdapter
reload( MenuUIAdapter )
from MenuUIAdapter import *

def slrCurrentTimeAdjust( value, min, max ):
	percent = (value-min) / (max-min) * 24.0
	ParticleEditor.romp.setTime( percent )
