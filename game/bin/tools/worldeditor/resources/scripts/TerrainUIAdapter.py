import WorldEditor
import Functor
from WorldEditorDirector import bd

def pgcTerrainTabSelect( value ):
	if value == "tabTerrainTextures":
		bd.enterMode( "TerrainTexture" )
	elif value == "tabTerrainBrushes":
		bd.enterMode( "TerrainHeight" )
	elif value == "tabTerrainFilters":
		bd.enterMode( "TerrainFilter" )
	elif value == "tabTerrainTools":
		bd.enterMode( "TerrainHoleCut" )
	elif value == "tabFences":
		bd.enterMode( "Fences" )
	elif value == "tabTerrainRuler" or value == "Ruler":
		bd.enterMode( "TerrainRuler" )
	else:
		msg = ResMgr.localise( "SCRIPT/TERRAIN_UI_ADAPTER/UNKNOWN_TAB", value )
		WorldEditor.addCommentaryMsg( msg, 1 )

# ------------------------------------------------------------------------------
# Section: Terrain texture page
# ------------------------------------------------------------------------------
def brwTexturesItemSelect( value ):
	bd.setTerrainAlphaTexture( value )
	
def textureUProjection( value ):
	bd.setTerrainTextureUProjection( value )
	
def textureVProjection( value ):
	bd.setTerrainTextureVProjection( value )	

def importMaskTopLeft( value ):
	bd.setImportMaskTopLeft( value )
	
def importMaskBottomRight( value ):
	bd.setImportMaskBottomRight( value )
	
def setTerrainPaintMode( value ):
	bd.setTerrainPaintMode( value )
	
def setTerrainPaintBrush( value ):
	bd.setTerrainPaintBrush( value )
	
# ------------------------------------------------------------------------------
# Section: Terrain height page
# ------------------------------------------------------------------------------
def slrHeightSizeAdjust( value, min, max ):
	bd.heightTool.size = value

def slrHeightSizeUpdate():
	return bd.heightTool.size

def slrHeightStrengthAdjust( value, min, max ):
	bd.heightTool.strength = value

def slrHeightStrengthUpdate():
	return bd.heightTool.strength

def actHeightFlatExecute():
	bd.heightFunctor.falloff = 0

def actHeightLinearExecute():
	bd.heightFunctor.falloff = 1

def actHeightCurveExecute():
	bd.heightFunctor.falloff = 2

def actHeightFlatUpdate():
	return (1, bd.heightFunctor.falloff == 0)

def actHeightLinearUpdate():
	return (1, bd.heightFunctor.falloff == 1)

def actHeightCurveUpdate():
	return (1, bd.heightFunctor.falloff == 2)
	
def slrSetHeightAdjust( value, min, max ):
	bd.setHeightFunctor.height = value

def actSetHeightRelativeExecute():
	bd.setHeightFunctor.relative = 1

def actSetHeightAbsoluteExecute():
	bd.setHeightFunctor.relative = 0

def actSetHeightRelativeUpdate():
	return (1, bd.setHeightFunctor.relative)

def actSetHeightAbsoluteUpdate():
	return (1, not bd.setHeightFunctor.relative)

# ------------------------------------------------------------------------------
# Section: Terrain filters page
# ------------------------------------------------------------------------------
def slrFilterSizeAdjust( value, min, max ):
	bd.filterTool.size = value

def slrFilterSizeUpdate():
	return bd.filterTool.size

def slrFilterStrengthAdjust( value, min, max ):
	bd.filterTool.strength = value * 25.0

def slrFilterStrengthUpdate():
	return bd.filterTool.strength / 25.0

def slrFilterConstantAdjust( value, min, max ):
	bd.filterTool.functor.constant = value

def slrFilterConstantUpdate():
	return bd.filterTool.functor.constant

def actFilterFlatExecute():
	bd.filterTool.functor.falloff = 0

def actFilterLinearExecute():
	bd.filterTool.functor.falloff = 1

def actFilterCurveExecute():
	bd.filterTool.functor.falloff = 2

def actFilterFlatUpdate():
	return (1, bd.filterTool.functor.falloff == 0)

def actFilterLinearUpdate():
	return (1, bd.filterTool.functor.falloff == 1)

def actFilterCurveUpdate():
	return (1, bd.filterTool.functor.falloff == 2)

def lstFiltersItemSelect( index ):
	bd.filterTool.functor.index = index
	bd.currentTerrainFilter = index

def lstFiltersUpdate():
	if bd.currentTerrainFilter != bd.filterTool.functor.index:
		bd.currentTerrainFilter = bd.filterTool.functor.index
		return bd.currentTerrainFilter
	return -1

# ------------------------------------------------------------------------------
# Section: Terrain mesh ops page
# ------------------------------------------------------------------------------
def slrMeshSizeAdjust( value, min, max ):
	bd.holeTool.size = value

def slrMeshSizeUpdate():
	return bd.holeTool.size

def actTerrainHoleCutterExecute():
	bd.holeTool.functor.fillNotCut = 0

def actTerrainHoleRepairExecute():
	bd.holeTool.functor.fillNotCut = 1

def actTerrainHoleCutterUpdate():
	return (1, not bd.holeTool.functor.fillNotCut)

def actTerrainHoleRepairUpdate():
	return (1, bd.holeTool.functor.fillNotCut)
