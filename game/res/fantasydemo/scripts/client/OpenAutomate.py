import BigWorld
import FantasyDemo
import MenuScreenSpace
from Math import *
import math
import os
import OpenAutomateWrapper
import sys
import inspect
from functools import partial
from Helpers.BWCoroutine import *

from Helpers.VideoModeUtils import enumVideoModes

#globals
#mark if we call run from the open automate main loop
runFromOpenAutomate = False
#callback handle
openAutomateCallbackHandle = 0
#Mark if we are running open automate mode (meaning open autmate main loop is running and things are being run from it)
openAutomateMode = False
commandCounter = 0
#These flags are used to run benchmarks multiple times, this is important as the first run of a benchmark is 
#suffering from bad performance due to disk load
benchmarkBeingLogged = False
shouldRerunTest = False
testToRun = None
#For video window mode options constants
OPTION_VIDEO_WINDOWED_OR_FULL_SCREEN="WindowedMode"
VIDEO_WINDOWED_MODE_ON = "ON"
VIDEO_WINDOWED_MODE_OFF = "OFF"
#for video modes
OPTION_VIDEO_MODE="VideoMode"


DEBUG_OPEN_AUTOMATE=True
def debug_print(*args):
	if DEBUG_OPEN_AUTOMATE:
		currentFrame=inspect.currentframe()
		upperFrame=currentFrame.f_back
		line=upperFrame.f_lineno
		fullPathFile=upperFrame.f_code.co_filename
		file=fullPathFile.rpartition("/")[2]
		print "%s:%d " % (file,line), args


class OpenAutomateTests:
	def __init__(self):
		#tests are a map from test name to:
		# 1. test callback
		# 2. test params
		# 3. whether test should be run twice and logged only on the second stage
		self.tests = {
			"RunProfilerMinspec": (FantasyDemo.runProfiler, ["spaces/minspec", "minspecOutput", False],True),
#Just for testing (allowing to run min spec twice)
			"RunProfilerMinspec1": (FantasyDemo.runProfiler, ["spaces/minspec", "minspecOutput", False],False),
			}

		#add the highlands test space only on high spec machines
		if os.environ.keys().count("LOW_SPEC") == 0:
			self.tests["RunProfilerHighlands"] = (FantasyDemo.runProfiler, ["spaces/highlands", "highlandsOutput", False],True)
			self.tests["RunProfilerRuinberg"] = (FantasyDemo.runProfiler, ["spaces/08_ruinberg", "ruinbergOutput", False],True)
			self.tests["RunProfilerLoadtimeHighlands"] = (FantasyDemo.loadTimerStart, ["spaces/highlands"],True)
			self.tests["RunProfilerLoadtimeMinspec"] = (FantasyDemo.loadTimerStart, ["spaces/minspec"],True)
			self.tests["RunProfilerLoadtimeArctic"] = (FantasyDemo.loadTimerStart, ["spaces/arctic"],True)
			self.tests["RunProfilerLoadtimeRuinberg"] = (FantasyDemo.loadTimerStart, ["spaces/08_ruinberg"],True)
			
		allOfflineSpaces = FantasyDemo.enumOfflineSpaces()
		for space in allOfflineSpaces:
			if space[0] == "spaces/main10":
				self.tests["RunProfilerMain10"] = (FantasyDemo.runProfiler, ["spaces/main10", "main10Output", False],True)
	
	def runTest(self, testName):
		global rds
		debug_print ("testName %s " % testName)
		test = self.tests[testName]
		if test != None:
			logging = True
			#check if the test should be run twice (logged only on the second run)
			if test[2]:
				global shouldRerunTest
				global testToRun
				shouldRerunTest = True
				testToRun = test
				logging = False
			self.runTestWithLogging(test, logging)
			
	# Use logging if we call open automate start end and log benchmark
	def runTestWithLogging(self, test, logging):
			if test[0] == FantasyDemo.runProfiler:
				FantasyDemo.rds.addListener( "flyThroughModeActivated", self.flyThroughModeActivated )
			if logging:
				OpenAutomateWrapper.bwOAStartBenchmark()
				global benchmarkBeingLogged
				benchmarkBeingLogged = True
			debug_print ("tests %s %s logging %s" % (test[0], test[1], logging))
			BigWorld.clearSpaces()
			MenuScreenSpace.clear()
			test[0](*test[1])
						 

	def getTests(self):
		return self.tests.keys()


	def flyThroughModeActivated( self, activated, resultList ):
		FantasyDemo.rds.removeListener( "flyThroughModeActivated", self.flyThroughModeActivated )
		OpenAutomateTests.flyThroughModeActivatedInternal(activated, resultList).run()
			
	@BWCoroutine
	def flyThroughModeActivatedInternal( activated, resultList ):
		if not activated:
			if resultList != None:
				if benchmarkBeingLogged:
					for elem in resultList:
						debug_print ("result %s %s " % (elem[0], elem[1]))
						OpenAutomateWrapper.bwOAAddResultValue(elem[0], elem[1])
					OpenAutomateWrapper.bwOAEndBenchmark()
			#we might need to rerun another test here.
			global shouldRerunTest
			if shouldRerunTest:
				shouldRerunTest = False
				global testsClass
				testsClass.runTestWithLogging(testToRun, True)
				return
			else:
				BigWorld.clearSpaces()
				MenuScreenSpace.clear()
				yield BWWaitForCoroutine( FantasyDemo.coHandleDisconnectionFromServer() )
			#rerun open automate loop
			setupOpenAutomateMainLoop ( 10, True, False).run()
				

def startOpenAutomate():
	# fantasydemo.exe -openautomate arg
	versionStruct = OpenAutomateWrapper.CreateOAVersionStructWrapper() 
	bwTestMode = False
	oaInitParam = sys.argv[2]
	if sys.argv[2] == OpenAutomateWrapper.getOpenAutomateTestArgument():
		bwTestMode = True
		if (len(sys.argv) > 3):
			oaInitParam = sys.argv[3]
	OpenAutomateWrapper.bwOAInit(oaInitParam, versionStruct, bwTestMode)
	debug_print ("OpenAutomate initialised versionStruct %s" % versionStruct)
	setupOpenAutomateMainLoop(2, False, False).run()
	global testsClass
	testsClass = OpenAutomateTests()

	
@BWCoroutine
def setupOpenAutomateMainLoop(delay, testEnded, runEnded):
	"""
	start the open automate main loop.
	testEnded - True at the end of a test
	runEnded - True at the end of running the client within the openAutomate test
	"""
	#testEnded will be true when a test ends.
	global benchmarkBeingLogged
	global shouldRerunTest
	if testEnded:
		if shouldRerunTest:
			raise AssertionError, "shouldn't get here"
	#if we are here we aren't rerunning the test so clear the flags	
	benchmarkBeingLogged = False
	#If running has ended we set runFromOpenAutomate to false
	if runEnded:
		global runFromOpenAutomate
		runFromOpenAutomate = False
		# run has ended so prepare ourself for more work
		yield BWWaitForCoroutine(FantasyDemo.coSetMainMenuActive( False ))
		BigWorld.worldDrawEnabled( True )
	else:
		global openAutomateMode
		openAutomateMode = True

	global openAutomateCallbackHandle
	openAutomateCallbackHandle = BigWorld.callback(delay, _runOpenAutomate)
	#mark that we are running in open automate
	

def cancelOpenAutomateMainLoop():
	BigWorld.cancelCallback(openAutomateCallbackHandle)


# -----------------------------------------------------------------------------
# Method: _runOpenAutomate
# Description:
#	- This is called to begin the OpenAutomate command loop
# -----------------------------------------------------------------------------
def _runOpenAutomate( ):
	global openAutomateMode
	openAutomateMode = True
	global openAutomateCallbackHandle
	openAutomateCallbackHandle = BigWorld.callback(0, _runOpenAutomate)
	command = OpenAutomateWrapper.CreateOACommandWrapper()
	currentCommand = OpenAutomateWrapper.bwOAGetNextCommand(command)
	global commandCounter
	debug_print ("command %s %d" % (currentCommand, commandCounter))
	commandCounter = commandCounter + 1
	#Check for restarting after setting multiple options
	if currentCommand == "CMD_EXIT":
		OpenAutomateWrapper.bwOAPrepareForQuit()
		FantasyDemo.quitGame()
	elif currentCommand == "CMD_RUN":
		cancelOpenAutomateMainLoop()
		FantasyDemo.disconnectFromServer()
		openAutomateMode = False
		global runFromOpenAutomate
		runFromOpenAutomate = True
		FantasyDemo.internalStart()
	elif currentCommand == "CMD_GET_ALL_OPTIONS":
		_enumerateOpenAutomateOptions(False)
	elif currentCommand == "CMD_GET_CURRENT_OPTIONS":
		_enumerateOpenAutomateOptions(True)
	elif currentCommand == "CMD_SET_OPTIONS":
		_setOptions()
	#BigWorld based command not currently used
	elif currentCommand == "CMD_SET_OPTIONS_ENDED":
		if BigWorld.graphicsSettingsNeedRestart():
			debug_print ("restarting app")
			BigWorld.restartGame()
	elif currentCommand == "CMD_GET_BENCHMARKS":
		testsList = testsClass.getTests()
		for test in testsList:
			debug_print ("Adding benchmark %s " % test)
			OpenAutomateWrapper.bwOAAddBenchmark(test)
	elif currentCommand == "CMD_RUN_BENCHMARK":
		cancelOpenAutomateMainLoop()
		testsClass.runTest(command.benchmark)
	#Internal command for testing only
	elif currentCommand == "CMD_RESTART":
		BigWorld.restartGame()
	elif currentCommand == "CMD_AUTO_DETECT":
		BigWorld.autoDetectGraphicsSettings()
		#set full screen
		BigWorld.changeVideoMode(BigWorld.videoModeIndex(), False)
		#set the video resolution (video mode)
		allModes = BigWorld.listVideoModes()
		mode = allModes[len(allModes) - 1]
		BigWorld.changeVideoMode(mode[0], False)
		#Set the aspect ratio (currently done just based on the video mode - I assume the aspect ratio fits the highest video resolution)
		BigWorld.changeFullScreenAspectRatio(mode[1] / float(mode[2]))
	else:
		debug_print ("Illegal command %s " % currentCommand)
		raise AssertionError, "illegal command %s " % currentCommand


def _enumerateOpenAutomateOptions(enumCurrentOptions) :
	"""
	Enumerate all options available to be set on the client or all current options currently set
	"""
	for featureKey, active, options, desc, advanced, needsRestart, delayed in BigWorld.graphicsSettings():
		#can't use SHADER_VERSION_CAP as low values do not have terrain and due to multiple dependencies.
		if featureKey != "SHADER_VERSION_CAP":
			if options:
				if enumCurrentOptions:
					#In this case we enum the current values for the options
					OpenAutomateWrapper.bwOAAddOptionValue(featureKey, "TYPE_ENUM", options[active][0])
				else:
					oaNamedOptionWrapper = OpenAutomateWrapper.CreateOANamedOptionWrapper() 
					oaNamedOptionWrapper.dataType = "TYPE_ENUM"
					oaNamedOptionWrapper.name = featureKey;             
					#In this case we enum all options
					for option in options:
						if option[1]:
							oaNamedOptionWrapper.enumValue = option[0];     
							debug_print ("OAAddOption %s %s %s" % (oaNamedOptionWrapper.dataType, oaNamedOptionWrapper.name, oaNamedOptionWrapper.enumValue))
							OpenAutomateWrapper.bwOAAddOption(oaNamedOptionWrapper)

	#add the video windowed mode option
	if enumCurrentOptions:
		if BigWorld.isVideoWindowed():
			currValue = VIDEO_WINDOWED_MODE_ON
		else:
			currValue = VIDEO_WINDOWED_MODE_OFF
		OpenAutomateWrapper.bwOAAddOptionValue(OPTION_VIDEO_WINDOWED_OR_FULL_SCREEN, "TYPE_ENUM", currValue)
	else:
		oaNamedOptionWrapper = OpenAutomateWrapper.CreateOANamedOptionWrapper() 
		oaNamedOptionWrapper.dataType = "TYPE_ENUM"
		oaNamedOptionWrapper.name = OPTION_VIDEO_WINDOWED_OR_FULL_SCREEN;             
		oaNamedOptionWrapper.enumValue = VIDEO_WINDOWED_MODE_ON;     
		OpenAutomateWrapper.bwOAAddOption(oaNamedOptionWrapper)
		oaNamedOptionWrapper.enumValue = VIDEO_WINDOWED_MODE_OFF;     
		OpenAutomateWrapper.bwOAAddOption(oaNamedOptionWrapper)

	#add the video modes
	if enumCurrentOptions:
		modes, current = enumVideoModes()
		OpenAutomateWrapper.bwOAAddOptionValue(OPTION_VIDEO_MODE, "TYPE_ENUM", modes[current][4])
	else:
		oaNamedOptionWrapper = OpenAutomateWrapper.CreateOANamedOptionWrapper() 
		oaNamedOptionWrapper.dataType = "TYPE_ENUM"
		oaNamedOptionWrapper.name = OPTION_VIDEO_MODE
		modes, current = enumVideoModes()
		for mode in modes:
			oaNamedOptionWrapper.enumValue = mode[4]
			debug_print ("Adding option %s %s " % (oaNamedOptionWrapper.name, oaNamedOptionWrapper.enumValue))
			OpenAutomateWrapper.bwOAAddOption(oaNamedOptionWrapper)

def _setOptions() :
	setOption = OpenAutomateWrapper.bwOAGetNextOption()
	while setOption != None:
		debug_print ("%s %s %s" % (setOption.dataType, setOption.name, setOption.enumValue))
		if setOption.dataType != "TYPE_ENUM":
			raise AssertionError, "illegal setOption data type %s " % setOption.dataType
		for featureKey, active, options, desc, advanced, needsRestart, delayed in BigWorld.graphicsSettings():
			if featureKey == setOption.name:
				appliedOption = False
				for counter, option in enumerate(options):
					if option[0] == setOption.enumValue:
						if option[1]:
							debug_print ("Selecting option %s" % option[0])
							BigWorld.setGraphicsSetting( featureKey, counter )
							appliedOption = True
							break
						else:
							debug_print ("not setting option as not supported %s" % option[0])
				if not appliedOption:
					raise AssertionError, "Didn't apply option correctly for %s value %s " % (setOption.name, setOption.enumValue)
		#for the video windowed mode option
		if setOption.name == OPTION_VIDEO_WINDOWED_OR_FULL_SCREEN:
			if (setOption.enumValue == VIDEO_WINDOWED_MODE_ON and not BigWorld.isVideoWindowed()) or (setOption.enumValue == VIDEO_WINDOWED_MODE_OFF and BigWorld.isVideoWindowed()):
				BigWorld.changeVideoMode(BigWorld.videoModeIndex(), not BigWorld.isVideoWindowed())

		#for the video mode option
		if setOption.name == OPTION_VIDEO_MODE:
			modes, current = enumVideoModes()
			for mode in modes:
				if mode[4] == setOption.enumValue:
					if not BigWorld.isVideoWindowed():
						FantasyDemo.enableAutomaticAspectRatio( True )
					changeMode( mode )					

		#get next option
		setOption = OpenAutomateWrapper.bwOAGetNextOption()
	BigWorld.commitPendingGraphicsSettings()
#TBD might be used in the future to restart after setting the values
#	if BigWorld.graphicsSettingsNeedRestart():
#		debug_print ("restarting app")
#		BigWorld.restartGame()

def changeMode( mode ):
	wasWindowed = True
	if not BigWorld.isVideoWindowed():
		wasWindowed = False
		BigWorld.changeVideoMode( BigWorld.videoModeIndex(), not BigWorld.isVideoWindowed() )
	#now we are windowed
	BigWorld.resizeWindow( mode[1], mode[2] )
	BigWorld.changeVideoMode( BigWorld.videoModeIndex(), not BigWorld.isVideoWindowed() )
	#now we are fullscreen
	BigWorld.changeVideoMode( mode[0], BigWorld.isVideoWindowed() )
	#revert back if required
	if wasWindowed:
		BigWorld.changeVideoMode( BigWorld.videoModeIndex(), not BigWorld.isVideoWindowed() )
	
