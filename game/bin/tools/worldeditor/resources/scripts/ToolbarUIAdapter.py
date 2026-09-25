import WorldEditor
from WorldEditorDirector import bd
import Personality

def actUndoExecute():
	what = WorldEditor.undo(0)
	if what:
		msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/UNDOING", what )
		WorldEditor.addCommentaryMsg( msg )
	WorldEditor.undo()

	bd.itemTool.functor.script.selUpdate()

def actUndoUpdate():
	return (WorldEditor.undo(0) != "", 0)


def actRedoExecute():
	what = WorldEditor.redo(0)
	if what:
		msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/REDOING", what )
		WorldEditor.addCommentaryMsg( msg )
	WorldEditor.redo()

	bd.itemTool.functor.script.selUpdate()


def actRedoUpdate():
	return (WorldEditor.redo(0) != "", 0)


def actSaveProjectExecute():
	"""This function forces a full save and process all operation."""
	Personality.preFullSave()
	WorldEditor.save()

def actQuickSaveExecute():
	"""This function forces a quick save operation."""
	Personality.preQuickSave()
	WorldEditor.quickSave()


def actLightAmbientOnlyExecute():
	WorldEditor.romp.setTime( 12.0 )

def actLightAmbientDirectionalExecute():
	WorldEditor.romp.setTime( 16.0 )

def actLightGameExecute():
	WorldEditor.romp.setTime( 18.0 )

#---------------------snaps------------------------------

def itemMode():
	return ( WorldEditor.tool() == bd.itemTool )

def actShellSnapsExecute():
	WorldEditor.setOptionVector3( "snaps/movement", WorldEditor.getOptionVector3( "shellSnaps/movement" ) )
	WorldEditor.setOptionFloat( "snaps/angle", WorldEditor.getOptionFloat( "shellSnaps/angle" ) )
	newSnaps = WorldEditor.getOptionVector3( "snaps/movement" )
	msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/MOVEMENT_SNAPS", str( newSnaps[0] ), str( newSnaps[1] ), str( newSnaps[2] ) )
	WorldEditor.addCommentaryMsg( msg )
	msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/ROTATION_SNAPS", str( WorldEditor.getOptionFloat( "snaps/angle" ) ) )
	WorldEditor.addCommentaryMsg( msg )

def actFreeSnapsExecute():
	newSnaps = ( 0.1, 0.1, 0.1 )
	WorldEditor.setOptionVector3( "snaps/movement", newSnaps )
	WorldEditor.setOptionFloat( "snaps/angle", 1 )
	msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/MOVEMENT_SNAPS", str( newSnaps[0] ), str( newSnaps[1] ), str( newSnaps[2] ) )
	WorldEditor.addCommentaryMsg( msg )
	msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/ROTATION_SNAPS", str( WorldEditor.getOptionFloat( "snaps/angle" ) ) )
	WorldEditor.addCommentaryMsg( msg )

def spdMiscSnapsXAdjust( value, min, max ):
	snaps = WorldEditor.getOptionVector3( "snaps/movement" )
	newSnaps = (value, snaps[1], snaps[2])
	WorldEditor.setOptionVector3( "snaps/movement", newSnaps )
	msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/MOVEMENT_SNAPS", str( newSnaps[0] ), str( newSnaps[1] ), str( newSnaps[2] ) )
	WorldEditor.addCommentaryMsg( msg )

def spdMiscSnapsYAdjust( value, min, max ):
	snaps = WorldEditor.getOptionVector3( "snaps/movement" )
	newSnaps = (snaps[0], value, snaps[2])
	WorldEditor.setOptionVector3( "snaps/movement", newSnaps )
	msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/MOVEMENT_SNAPS", str( newSnaps[0] ), str( newSnaps[1] ), str( newSnaps[2] ) )
	WorldEditor.addCommentaryMsg( msg )

def spdMiscSnapsZAdjust( value, min, max ):
	snaps = WorldEditor.getOptionVector3( "snaps/movement" )
	newSnaps = (snaps[0], snaps[1], value)
	WorldEditor.setOptionVector3( "snaps/movement", newSnaps )
	msg = ResMgr.localise( "SCRIPT/TOOLBAR_UI_ADAPTER/MOVEMENT_SNAPS", str( newSnaps[0] ), str( newSnaps[1] ), str( newSnaps[2] ) )
	WorldEditor.addCommentaryMsg( msg )

# Putting these here for now. They were stripped out of fMain.dfm
"""
actDebugMessages
actDeleteExecute
actDeselectAll
actDeselectAllExecute
actDeselectRoot
actDeselectRootExecute
actExit
actExitExecute
actForceDraw
actForceDrawExecute
actHelp
actHelpExecute
actKeyboard
actKeyboardExecute
actList
actMoveFast
actMoveMedium
actMoveSlow
actMoveSuperFast
actNewProject
actNewProjectExecute
actOpenProject
actOpenProjectExecute
actPreferences
actPreferencesExecute
actRedo
actRedoExecute
actSaveProject
actToggleSnaps
actToggleSnapsExecute
actUndo
actUndoExecute

akBottom
akLeft
akRight
akTop
alClient
alNone
alRight
alTop
alTop	Alignment
barTools
bdLeftToRight
bkFlat
blGlyphLeft
bLock Object Selection (N)|Lock the object selections. You cannot select/deselect while lock is on.
brOnlyTopLine

brwObjectEntityBaseClasses
brwObjectEntityTemplates
brwObjectMarkersWayPoints
brwObjectModels
brwObjectModelsChangeDirectory
brwObjectShells
brwObjectShellsChangeDirectory
brwObjectSounds
brwObjectSoundsChangeDirectory
brwObjectSoundsDblClick
brwTextures

bsLeftLine
bsNone
bsRaised
btnLinkSelected
bvlObjectEntity
bvlProjectCyclesTimeLine
bvlTerrainBrushes
bvNone
bvNone	BevelKind
bvRaised
cdAnyColor
cdFullOpen
childPanel

chkAnimateScene
chkContinousUpdate
chkDrawDetail
chkDrawGradientSkyDome
chkDrawObjectTerrainCursor
chkDrawSky
chkDrawStars
chkDrawSunMoon
chkFogEnabled
chkGameAnimationSpeed
chkLightEnabled
chkLightEnabledClick
chkLightsFlareColourize
chkLightsFlareColourizeClick
chkLinkLightToCamera
chkProjectAnimateDayNightCycle
chkShowAreaOfEffect
chkShowLightModels
chkShowTargetLinks
chkShowTargetModels
chkTerrainTextureUseFastTiling

cl3DDkShadow
clBlack
clBlue
clBtnHighlight
clBtnHighlight	ColorDown
clBtnShadow
clBtnShadow	ColorDown
clBtnShadow	ColorFlat
clBtnShadow	PopupMenu
clHighlight
clHighlightText
clRed
clWhite
clWindow
clWindow	ColorDown
clWindowFrame
clWindowText

cmbLightsChange
cmbLightsFlareOptions
cmbLightsFlareOptionsChange
cmbPaths
cmbProjectDayNightEnvironments
cmbTargets
cmdAreaSize1
cmdAreaSize1Click
cmdAreaSize2
cmdAreaSize3
cmdAreaSize4
cmdAreaSize5
cmdAreaSize6
cmdAreaSize7
cmdBrushNew
cmdHoleCutter
cmdHoleRepair

crArrow
crHandPoint
csDropDownList
dlgAbout
dlgColor
dlgOpen
dlgSave

edtBrushFalloffRate
edtBrushFalloffRateExit
edtBrushFalloffRateKeyPress
edtBrushSize
edtBrushSizeExit
edtBrushSizeKeyPress
edtBrushStrength
edtBrushStrengthExit
edtBrushStrengthKeyPress
edtConeSize
edtConeSizeExit
edtConeSizeKeyPress
edtCutArea
edtFarPlane
edtFieldOfView
edtFilterSize
edtFilterSizeExit
edtFilterSizeKeyPress
edtFogDensity
edtFogStart
edtInnerRadius
edtInnerRadiusExit
edtInnerRadiusKeyPress
edtLightDirection
edtLightLocation
edtLightTemplateConeSize
edtLightTemplateConeSizeExit
edtLightTemplateDirection
edtLightTemplateDirectionExit
edtLightTemplateInnerRadius
edtLightTemplateInnerRadiusExit
edtLightTemplateName
edtLightTemplateNameExit
edtLightTemplateNameKeyPress
edtLightTemplateOuterRadius
edtLightTemplateOuterRadiusExit
edtNearPlane
edtOuterRadius
edtOuterRadiusExit
edtOuterRadiusKeyPress
edtProjectDayNightCurrentTime
edtProjectDayNightHourDuration
edtProjectDayNightMaxMoonAngle
edtProjectDayNightMaxSunAngle
edtProjectDayNightStartTime
edtProjectTerrainInnerRadius
edtProjectTerrainOuterRadius
edtSceneRoot
edtTerrainFilterHeight
edtTerrainFilterHeightExit
edtTerrainFilterHeightKeyPress
edtTerrainMeshHoleSize
edtTileWidth

esNone
esNone	EdgeOuter
ffFixed
fileInfo
frmTipOfTheDay
frmView
fsBold
fsUnderline

grpHeightFilter
grpLightAttributes
grpLightsFlare
grpLightsStyle
grpLightTemplateProperties
grpLightTemplateType
grpLightTemplateTypeMouseDown
grpLightTemplateTypeMouseMove	OnMouseUp
grpLightTemplateTypeMouseUp
grpMiscSnapsCellSize
grpMiscSnapsRotation
grpMiscSnapsSpeedSnaps
grpMiscSnapsTranslation
grpNeighbours
grpProjectColorCycles
grpProjectEnvironments
grpProjectFog
grpProjectInitialSettings
grpProjectParameters
grpRenderLights
grpRenderMisc
grpRenderScenery
grpRenderShell
grpRenderShellModel
grpRenderShellMouseDown
grpRenderShellMouseMove
grpRenderShellMouseMove	OnMouseUp
grpRenderShellMouseUp
grpRenderTargets
grpRenderTerrain
grpTerrainBrushesInformation
grpTerrainBrushesShape
grpTerrainBrushesStyle
grpTerrainTextureSelection
grpTerrainTextureTilingArea
grpTerrainTilingPattern
grpTerrainToolsGridSize
grpTerrainToolsRenderMode
grpUndo

hatNone
hhhhhh
hh:mm:ss
hmHint
hsThickButtons
imgBrush
imgColdButtons
imgHotButtons
imgHotButtons	MultiLine
imgLightTemplates
imgReadWrite
imgTreeImages
jjjjjj

lbl12AM
lbl12PM
lbl1AM
lbl6AM
lbl6PM
lblAmbientKeyTime
lblBrushFalloffRate
lblConeSize
lblFallOffRadius
lblFogKeyTime
lblFullRadius
lblLightColor
lblLightDirection
lblLightLocation
lblLightTemplateColor
lblLightTemplateConeSize
lblLightTemplateDirection
lblLightTemplateInnerRadius
lblLightTemplateName
lblLightTemplateOuterRadius
lblMiscPathXML
lblMiscSnapsMetric
lblMiscSnapsRotationAngle
lblMiscSnapsSpeedFree
lblMiscSnapsSpeedShells
lblMiscSnapsX
lblMiscSnapsY
lblMiscSnapsZ
lblMoonKeyTime
lblProjectAmbientColor
lblProjectBackgroundColor
lblProjectDayTime
lblProjectTerrainInnerRadius
lblProjectTerrainOuterRadius
lblSceneCameraFarPlane
lblSceneCameraFOV
lblSceneCameraNearPlane
lblSceneFogColor
lblSceneFogDensity
lblSceneFogEnd
lblSceneFogStart
lblSkyTime
lblSunKeyTime
lblTerrainDimensions
lblTerrainFiltersFilters
lblTerrainFiltersSize
lblTerrainOptionsHighest
lblTerrainOptionsLowest
lblTerrainOptionsSize
lblTerrainOptionsStrength
lblTerrainSize
lblTerrainTexture
lblTerrainTextures
lblUndoMemory
lblUndoSteps

lgeAmbientCycle
lgeCopy
lgeFogCycle
lgeMoonCycle
lgeSunCycle
lgeSunCycleChange
lgeSunCycleChange	PopupMenu
lgeSunCycleMouseMove

lstFilters
lstFiltersClick

maTopToBottom
mgeCopy
mgeSkyCycle
mgeSkyCycleChange
mgeSkyCycleChange	PopupMenu
mgeSkyCycleMouseMove
mm/dd/yyyy

mnu10Degrees
mnu10DegreesClick
mnu1Degree
mnu1DegreeClick
mnu2Degrees
mnu2DegreesClick
mnu30Degrees
mnu30DegreesClick
mnu45Degrees
mnu45DegreesClick
mnu5Degrees
mnu5DegreesClick
mnu60Degrees
mnu60DegreesClick
mnu90Degrees
mnu90DegreesClick
mnuAbout
mnuAboutClick
mnuAddKeyClick
mnuAutoZoomExtents
mnuAutoZoomExtentsClick
mnuCentimetres
mnuCentimetresClick
mnuContextCreation
mnuContextCreationClick
mnuCopy
mnuCopyColor
mnuCopyColorClick
mnuCopyControl
mnuCopyControlClick
mnuCopyKey
mnuCopyKeyClick
mnuCut
mnuCutControl
mnuCutControlClick
mnuCutKeyClick
mnuDeleteControl
mnuDeleteControlClick
mnuDeleteKey
mnuDeleteKeyClick
mnuDeleteNode
mnuDeselectALL
mnuEdit
mnuExit
mnuFile
mnuFree
mnuFreeClick
mnuGroupSelection
mnuGroupSelectionClick
mnuHelp
mnuHideNode
mnuHideNodeClick
mnuHTMLHelp
mnuKeyboardBindings
mnuKilometres
mnuKilometresClick
mnuMain
mnuMCopyKey
mnuMCopyKeyClick
mnuMCutKey
mnuMCutKeyClick
mnuMergeControl
mnuMergeControlClick
mnuMetresClick
mnuMPasteKey
mnuMPasteKeyClick
mnuMultiAddKey
mnuMultiAddKeyClick
mnuMultiDeleteKey
mnuMultiDeleteKeyClick
mnuOptions
mnuPaste
mnuPasteColor
mnuPasteColorClick
mnuPasteControl
mnuPasteControlClick
mnuPasteKey
mnuPasteKeyClick
mnuPreferences
mnuProjectLoad
mnuProjectNew
mnuProjectSave
mnuRecentProjects
mnuRecentProjects	PopupMenu
mnuRedo
mnuRefreshTextures
mnuRefreshTexturesClick
mnuRefreshTree
mnuRefreshTreeClick
mnuRestoreProjectRevision
mnuSaveProjectAs
mnuSaveProjectAsClick
mnuShowNode
mnuShowNodeClick
mnuSyncAnimations
mnuSyncAnimationsClick
mnuTipOfTheDay
mnuTipOfTheDayClick
mnuUndo
mnuUndoList
mnuUndoListClick
mnuUngroupSelection
mnuUngroupSelectionClick
mnuZoomtoExtent

model
mruProjects
mruProjectsValidate
nSelects highlighted object/light or changes Terrain, applies texture, raise/lower, filter, or cut/repair holes
ofEnableSizing
ofFileMustExist
ofHideReadOnly
ofOverwritePrompt
ofPathMustExist

onBrowserItemSelect
onBtnClick
onChkChange
onPageControlTabSelect
onSlrAdjust
onSpnIntAdjust

pan3DViewContainer
pan3DViewContainerResize
panAmbientLightColor
panAmbientLightColorClick
panBrushPreview
panBrushShades
panFilterList
panFogColour
panLightColor
panLightColorClick
panLightDirection
panLightLocation
panLightOmni
panLightSpot
panLightTemplateColor
panLightTemplateColorClick
panLightTemplateCone
panLightTemplateDirection
panLightTemplatesRadius
panLightTemplateTools
panMiscSnapsRotation
panMiscSnapsTranslationMetric
panObjectEntityBaseClasses
panObjectEntityTemplates
panObjectModelBrowsing
panObjects
panObjectShellBrowsing
panObjectSoundsBrowsing
panProjectBackgroundColor
panProjectCycles
panSceneNodeProperties
panSceneTreeContainer
panSystemTools
panTabs
panTerrainName
panTerrainTextureBrowsing
panTerrainToolbar
panToolbarSceneRoot

pbNone
pgcAllTools
pgcAllToolsChanging
pgcObjectEntity
pgcObjects
pgcObjectsMarkers
pgcTerrain
piPercentage
p	OnExecute
popBrushes
popDeleteBrush
popGradient
popMultiGradient
popProjects
popRefreshBrushes
popRefreshTextures
popRotationSnaps
popTree
popTreePopup
popUnits
poScreenCenter
pppppp
pppppp888888FFFFFF
prgUndoMemory
prgUndoSteps
p	RowHeight
psHTML
psNodeProperty
psNodePropertyItemChange

radAmbient
radAmbientClick
radBrushShapeRound
radBrushShapeSquare
radBrushStyleCurve
radBrushStyleFlat
radBrushStyleLinear
radDirectional
radDirectionalClick
radLightTemplateTypeAmbient
radLightTemplateTypeDirectional
radLightTemplateTypeOmni
radLightTemplateTypeOmniClick
radLightTemplateTypeSpot
radLightTemplateTypeSpotClick
radMiscSnapsAlignmentAbsolute
radMiscSnapsAlignmentRelative
radOmni
radOmniClick
radRenderSceneryHide
radRenderSceneryShow
radRenderSceneryShowRootOnly
radRenderScenerySolid
radRenderSceneryWireframe
radRenderShellModelSolid
radRenderShellModelWireframe
radRenderShellNeighboursHideAll
radRenderShellPortals
radRenderTerrainHide
radRenderTerrainShow
radRenderTerrainSolid
radRenderTerrainWireframe
radSpot
radSpotClick
radTerrainTextureTilingLast
radTerrainTextureTilingNormal
radTerrainTextureTilingRandom
radTerrainToolsRenderSolid
radTerrainToolsRenderWireframe

rNote: These settings override the Game Globals settings above. The Game Global settings are initial settings only.

rollCutArea
rollCutArea	AutoWidth
rollLightProperties
rollLightProperties	AutoWidth
rollLightTemplates
rollMeshDetail
rollMeshDetail	AutoWidth
rollMiscCamera
rollMiscCamera	AutoWidth
rollMiscKeys
rollMiscKeys	AutoWidth
rollMiscPathsXML
rollMiscPathsXML	AutoWidth
rollMiscRender
rollMiscSnaps
rollMiscSnaps	AutoWidth
rollMiscUndoStatus
rollMiscUndoStatus	AutoWidth
rollNodeProperty
rollNodeProperty	AutoWidth
rollProertySheet
rollProjectDayNightCycles
rollProjectDayNightCycles	AutoWidth
rollProjectGlobals
rollPropertySheet
rollSceneGraph
rollTerrainBrushBrushes
rollTerrainBrushOptions
rollTerrainBrushOptions	AutoWidth
rollTerrainFilterFilters
rollTerrainFilterSize
rollTerrainFilterSize	AutoWidth
rollTerrainTextureBrowser
rollTerrainTextureTiling
rollTerrainTextureTiling	AutoWidth
rollTerrainTools

sbmFlat
scpGame
scpLight
scpLightTemplates
scpLightTemplatesClick
scpProject
scpScene
scpTerrainBrush
scpTerrainBrushes
scpTerrainBrushesClick
scpTerrainFilter
scpTerrainTexture
scpTerrainTools
scroller

slrBrushFalloffRate
slrBrushFalloffRateChange
slrBrushSize
slrBrushSizeChange
slrBrushStrength
slrCutArea
slrFarPlane
slrFilterSize
slrFOV
slrInnerRadius
slrInnerRadiusChange
slrLightConeSize
slrLightConeSizeChange
slrNearPlane
slrOuterRadius
slrOuterRadiusChange
slrProjectCurrentTime
slrProjectTerrainInnerRadius
slrProjectTerrainOuterRadius
slrTerrainHeightFilter
slrTerrainMeshHoleSize
slrTerrainTextureTilingSize

spdCut1
spdCut2
spdCut3
spdCut4
spdCut5
spdCut6
spdCut7
spdGridSnap
spdMiscSnapsSpeedFree
spdMiscSnapsSpeedShells
spdMiscSnapsX
spdMiscSnapsY
spdMiscSnapsZ
spdObjectLock
spdPathsNext
spdPathsNextClick
spdPathsPrev
spdPathsPrevClick
spdTerrainSnap
spnTerrainToolsGridSize
spnTerrainToolsGridSizeExit	OnKeyDown
spnTerrainToolsGridSizeKeyDown
spnTerrainToolsVerticalSize

tabLight
tabMisc
tabObjectEntity
tabObjectEntityBaseClasses
tabObjectEntityTemplates
tabObjectMarkers
tabObjectModel
tabObjectShell
tabObjectSounds
tabObjectTarget
tabObjectWayPoints
tabProject
tabScene
tabTerrain
tabTerrainBrushes
tabTerrainFilters
tabTerrainTextures
tabTerrainTools

taCenter
taLeftJustify

tbnConstrainToBox
tbnFast
tbnFastClick
tbnFreeSnaps
tbnHelp
tbnKeyboard
tbnLightAmbientDirectional
tbnLightAmbientOnly
tbnLightGame
tbnLightTemplateDelete
tbnLightTemplateDeleteClick
tbnLightTemplateNew
tbnLightTemplateNewClick
tbnLinkObjects
tbnMediumClick
tbnMiscSnapsMetric
tbnMiscSnapsMetricClick
tbnOptions
tbnOrthoMode
tbnProjectEnvironmentSave
tbnProjectEnvironmentSaveClick
tbnProjectNew
tbnProjectOpen
tbnProjectSave
tbnRedo
tbnRootFollowsCamera
tbnSceneryDefaults
tbnSep00
tbnSep00MouseMove
tbnSep01
tbnSep02
tbnSep03
tbnSep04
tbnSep05
tbnSep06
tbnSep07
tbnSep08
tbnSep09
tbnSep10
tbnSep11
tbnShellDefaults
tbnShellSnap
tbnSlow
tbnSlowClick
tbnSnapShot
tbnSnapsRotation
tbnSnapsRotationClick
tbnSuperFast
tbnSuperFastClick
tbnTerrainDefaults
tbnTerrainTextureAdd
tbnTerrainTextureDelete
tbnTerrainTextureReplace
tbnUndo
tbnUserDefaults
tbnZoomExtents
tbnZoomExtentsClick

tbrDayNightCycles
tbrLightTemplates
tbrLogs
tbrMiscSnapsMetric
tbrProjectTools
tbrTerrainTools
tbsCheck
tbsDropDown
tbsSeparator
tmrAnimation
tmrWindowRefresh

treeSceneChange
treeSceneClick
treeSceneDragDrop	OnGetText
treeSceneDragOver
treeSceneEdited	OnEditing
treeSceneEditing
treeSceneFreeNode
treeSceneGetHint
treeSceneGetImageIndex	OnGetHint
treeSceneGetNodeDataSize
treeSceneGetText
treeSceneInitNode	OnNewText
treeSceneNewText
treeScenePaintText

tsFlatButtons
voAutoDropExpand
voAutoExpand
voAutoScroll
voEditable
voFullRowSelect
voInitOnSave
voLevelSelectConstraint
voMultiSelect
voRightClickSelect
voShowButtons
voShowHorzGridLines
voShowTreeLines
voToggleOnDblClick
vvvvvv
vvvvvvjjjjjj
wsMaximized
"""