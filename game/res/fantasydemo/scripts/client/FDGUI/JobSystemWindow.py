import BigWorld
import GUI
import Math
import Helpers.PyGUI as PyGUI

from Helpers.PyGUI import PyGUIEvent

GRAPH_GUI_NAME = "gui/job_system_graph.gui"
POLL_INTERVAL = 0.5
GRAPH_SPACING = 5

GRAPHS = [
	( "Overall CPU Usage", "Job System/Percent - Sum of Cores" ),
	( "Main Core", "Job System/Percent - Main Core" ),
	( "Direct3D Core", "Job System/Percent - D3D Core" ),			
	( "Loading Core", "Job System/Percent - Loading Core" ),			
	( "Loading Thread", "Job System/Percent - Loading Thread" ),			
	( "Job Core 1", "Job System/Percent - Job Core 0" ),
	( "Job Core 2", "Job System/Percent - Job Core 1" ),
	( "Job Core 3", "Job System/Percent - Job Core 2" ),
	( "Job Core 4", "Job System/Percent - Job Core 3" ),
	( "Job Core 5", "Job System/Percent - Job Core 4" ),
]

CORE_COUNT_WATCHER = "Job System/Number of Cores"

def jobSystemEnabled():
	try:
		BigWorld.getWatcher( "Job System" )
		return True
	except TypeError:
		return False


class JobSystemWindow( PyGUI.DraggableWindow ):

	factoryString = "FDGUI.JobSystemWindow"
	
	def __init__( self, component ):
		PyGUI.DraggableWindow.__init__( self, component )
		self.component.script = self
		self._callbackHandle = None


	@PyGUIEvent( "closeBox", "onClick" )
	def onCloseBoxClick( self ):
		self.active( False )
	
	
	def _poll( self ):
		counter = 0
		for name, watcher in GRAPHS:
			try:
				BigWorld.getWatcher( watcher )
			except TypeError:
				continue
				
			g = getattr( self.component.container, 'graph%d' % counter )
			value = float( BigWorld.getWatcher( watcher ) ) / 100.0
			g.graph.input = Math.Vector4( value, value, value, value )
			counter += 1
			
		self._callbackHandle = BigWorld.callback( POLL_INTERVAL, self._poll )
		
		
	def onBound( self ):
		PyGUI.DraggableWindow.onBound( self )
		
		try:
			coreCount = int( BigWorld.getWatcher( CORE_COUNT_WATCHER ) )
		except TypeError:
			coreCount = 0
			
		if coreCount > 0:
			self.component.coreCountLabel.text += " " + str(coreCount)
		else:
			self.component.coreCountLabel.visible = False
		
		
		if jobSystemEnabled():
			self.constructGraphs()
		else:
			self.component.jobSystemDisabledLabel.visible = True


	def constructGraphs( self ):
		counter = 0
		for name, watcher in GRAPHS:
			# Make sure the watcher exists, if not skip this graph.
			try:
				BigWorld.getWatcher( watcher )
			except TypeError:
				continue
		
			g = GUI.load( GRAPH_GUI_NAME )
			g.title.text = name
			self.component.container.addChild( g, 'graph%d' % counter )
			counter += 1
			
		# Go through and reposition and size them based on how many we got
		totalGraphs = counter
		graphHeight = (float(self.component.container.height) / float(totalGraphs)) - GRAPH_SPACING
		
		for i in range(totalGraphs):
			g = getattr( self.component.container, 'graph%d' % i )
			g.height = graphHeight
			g.position.y = (graphHeight + GRAPH_SPACING) * i
			
		self._poll()
		