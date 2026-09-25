import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "src"))
from Tkinter import *
import tkMessageBox
import time
import create_list
import create_build_number_list
import actions
from log import *
from filter import *
from revision_control import *

os.chdir(os.path.dirname(os.path.realpath(__file__)))
CLIENT_SERVER = os.path.join( "//ba01", "BuildArchive" )
BIGWORLD_DIR = os.path.realpath(__file__).split("game")[0]

CLIENT = "client"
TOOLS = "tools"

SERVER = "server"
LOCAL = "local"
DONT_COPY = "-1 | Keep local files"

prefixMapping = {CLIENT : 'windows_', 
		SERVER : 'linux64_'};
		
Title = {CLIENT : 'Client', 
		SERVER : 'Server'};

class App( Frame ):
	def __init__( self, master = None ):
		Frame.__init__( self, master )
		frame = Frame( master )
		frame.pack()
		
		#variables 
		self.buildList = []
		self.application = CLIENT
		self.actionsList = actions.ActionList()
			
		#Divide the GUI into frames
		topFrame = Frame( master = frame )
		topFrame.pack()
		botFrame = Frame( master = frame )
		botFrame.pack()	
		leftTopFrame = Frame( master = topFrame )
		leftTopFrame.pack( side = LEFT)	
		rightTopFrame = Frame( master = topFrame )
		rightTopFrame.pack( side = RIGHT )	
		topRightTopFrame = Frame( master = rightTopFrame )
		topRightTopFrame.pack()	
		botRightTopFrame = Frame( master = rightTopFrame )
		botRightTopFrame.pack()
		
		#----leftTopFrame----
			
		# Copy/don't copy specific tools
		frameSpesificApp = LabelFrame( master = leftTopFrame , text = "", borderwidth = 1 )
		frameSpesificApp.pack( padx = 5, pady = 5 )
		
		# debug Files
		self.debugFlag = IntVar()
		exporterButton = Checkbutton( master = frameSpesificApp, text = "Copy debug      ", \
										variable = self.debugFlag, onvalue = 1, offvalue = 0, width = 15)
		exporterButton.pack( anchor = W )
		
		# exporters Files
		self.exportersFlag = IntVar()
		exporterButton = Checkbutton( master = frameSpesificApp, text = "Copy exporters ", \
										variable = self.exportersFlag, onvalue = 1, offvalue = 0, width = 15)
		exporterButton.pack( anchor = W )
		
		# don't copy pdb
		self.pdbFlag = IntVar()
		pdbButton = Checkbutton( master = frameSpesificApp, text = "Copy pdb files  ", \
										variable = self.pdbFlag, onvalue = 0, offvalue = 1, width = 15)
		pdbButton.pack( anchor = W )
		
		# p4 update
		self.p4UpdateFlag = IntVar()	
		#add p4 button only if p4 is installed from the command line
		self.perforceObj = Perforce()
		if self.perforceObj.validatePerforce():
			frameP4 = LabelFrame( master = leftTopFrame , text = "", borderwidth = 1 ) #workspace
			frameP4.pack( padx = 5, pady = 5 )
			
			self.p4UpdateButton = Checkbutton( master = frameP4, variable = self.p4UpdateFlag, onvalue = 1, offvalue = 0)
			self.p4UpdateButton.pack( anchor = W )
			self.changelistNumber = "0"
			self.setP4ButtonText()
			
		
		#----rightTopFrame----
		
		#Set drop down app conf	
		appFrame = Frame( master = topRightTopFrame )
		appFrame.pack()
		
		appText = Label( master = appFrame, text = "Choose Application", justify = LEFT )
		appText.pack( side = LEFT, padx = 5, pady = 5 )
		
		self.appArray = ['']
		self.app = StringVar()
		
		self.appField = OptionMenu(appFrame, self.app, *self.appArray)
		self.appField.config( width = 36 )
		

		self.appField.pack(	side = LEFT, padx = 5, pady = 5 )
		
		self.appField[ 'menu' ].delete( 0, 'end' )
		app = "Client and Tools"
		self.appField['menu'].add_command( label = app, 
					command = lambda app = app: self.setClientProjectList() )
		app = 'Server'	
		self.appField['menu'].add_command( label = app, 
					command = lambda app = app: self.setServerProjectList() )
					
		self.app.set('Client and Tools')		
						

		#Set drop down project list	
		
		configurationFrame = Frame( master = topRightTopFrame )
		configurationFrame.pack()	
		
		projConfigurationText = Label( master = configurationFrame, text = "Select Configuration", justify = LEFT )
		projConfigurationText.pack( side = LEFT, padx = 5, pady = 5 )
		
		self.buildConfigurationArray = ['']
		self.buildConfigurationValue = StringVar()
		self.buildConfigurationValue.set('')
		
		self.proConfigurationField = OptionMenu(configurationFrame, self.buildConfigurationValue, *self.buildConfigurationArray)
		self.proConfigurationField.config( width = 35 )
		self.proConfigurationField.pack(	side = LEFT, padx = 5, pady = 5 )	
		
		#Set drop down project list		
		projText = Label( master = topRightTopFrame, text = "Select Project", justify = LEFT )
		projText.pack( side = LEFT, padx = 5, pady = 5 )
		
		self.buildNameArray = ['']
		self.buildNameValue = StringVar()
		self.buildNameValue.set('')
		
		self.proNameField = OptionMenu(topRightTopFrame, self.buildNameValue, *self.buildNameArray)
		self.proNameField.config( width = 41 )
		self.proNameField.pack(	side = LEFT, padx = 5, pady = 5 )
				
		buildNumberFrame = Frame( master = botRightTopFrame )
		buildNumberFrame.pack()
		
		#clientbuildNumberFrame is a class variable because in the future the title will change from client to server
		self.clientbuildNumberFrame = LabelFrame( master = buildNumberFrame, text = "Client" )
		self.clientbuildNumberFrame.pack(side = LEFT, padx = 5, pady = 5)
		
		clientListScrollbar = Scrollbar( self.clientbuildNumberFrame )
		clientListScrollbar.pack( side = RIGHT, fill = Y )
		clientListScrollbar2 = Scrollbar( self.clientbuildNumberFrame, orient=HORIZONTAL )
		clientListScrollbar2.pack( side = BOTTOM, fill = BOTH )
		
		#set the client/server build number Listbox 
		self.clientListBox = Listbox( master = self.clientbuildNumberFrame, \
										exportselection = 0, height = 14, width = 30 )
		self.clientListBox.pack()	
		self.clientListBox.config( yscrollcommand = clientListScrollbar.set, xscrollcommand = clientListScrollbar2.set )
		clientListScrollbar.config( command = self.clientListBox.yview )
		clientListScrollbar2.config( command = self.clientListBox.xview )		
		#set the tools build number Listbox 
		
		self.toolsbuildNumberFrame = LabelFrame( master = buildNumberFrame, text = "Tools" )
		self.toolsbuildNumberFrame.pack( side = RIGHT, padx = 5, pady = 5 )
		
		toolListScrollbar = Scrollbar( self.toolsbuildNumberFrame )
		toolListScrollbar.pack( side = RIGHT, fill = Y )
		
		self.toolsListBox = Listbox( master = self.toolsbuildNumberFrame, \
										exportselection = 0, height = 15, width= 30)
		self.toolsListBox.pack()

		self.toolsListBox.config( yscrollcommand = toolListScrollbar.set )
		toolListScrollbar.config( command = self.toolsListBox.yview )	
		
		makeList = Button( master = botRightTopFrame, text = "Generate an action list", \
								command = self.makeList )
		makeList.pack(  padx = 10, pady = 10 )
		
		#--botFrame--
		#set the action Listbox 
		frameActionList = LabelFrame( master = botFrame, \
							text = "You are about to execute the following actions:", borderwidth = 1 )
		frameActionList.pack( padx = 5, pady = 5)
		actionListScrollbar = Scrollbar( frameActionList )
		actionListScrollbar.pack( side = RIGHT, fill = Y )
		
		self.actionListBox = Listbox(master = frameActionList, exportselection = 0, \
										height = 20, width = 86)
		self.actionListBox.pack( padx=5, pady=5)
		
		# attach listbox to scrollbar
		self.actionListBox.config( yscrollcommand = actionListScrollbar.set )
		actionListScrollbar.config( command = self.actionListBox.yview )
		
		frameActionButtons = Frame( master = botFrame, borderwidth = 1 )
		frameActionButtons.pack( padx = 5, pady = 5)
		
		# delete an action button
		delButton = Button( master = frameActionButtons, text = "Remove selected action", 
									command = self.deleteAction )
		delButton.pack( side = LEFT, padx = 5, pady = 5 )
		
		#copy button
		copyButton = Button( master = frameActionButtons, text = "Copy", command = self.action )
		copyButton.pack( side = RIGHT, padx = 5, pady = 5 )
		
		#default is the client build
		self.setClientProjectList()
	
	def setP4ButtonText(self):	
		if self.perforceObj.validatePerforce():
			if "0" == str(self.changelistNumber):
				self.p4UpdateButton.config( text = "Sync " + self.perforceObj.getWorkspace() + "\n to latest revision" )
			else:
				self.p4UpdateButton.config(  text = "Sync " + self.perforceObj.getWorkspace() + "\n to @" + self.changelistNumber )
		
	def clearActionList(self):
		self.actionListBox.delete( 0, 'end' )
		self.actionsList = actions.ActionList()
		
	def clearClientAndToolsLists(self):
		self.clientListBox.delete( 0, 'end' )
		self.toolsListBox.delete( 0, 'end' )
		
		self.clearActionList()

	def clearSelectProjectLabel(self):	
		self.buildNameValue.set('')
		self.proNameField[ 'menu' ].delete( 0, 'end' )
		
		self.clearClientAndToolsLists()
						
	def clearAllLists(self):
		# clear the action list box and the copy and delete lists
		self.clientbuildNumberFrame.config( text= Title[self.application] )
		
		#clearSelectConfigurationLabel
		self.buildConfigurationValue.set('')
		self.proConfigurationField[ 'menu' ].delete( 0, 'end' )
		
		self.clearSelectProjectLabel()
			
	def setServerProjectList( self ):
		# change application
		self.application = SERVER
		self.app.set('Server')
		
		#remove the tools list box
		self.toolsbuildNumberFrame.pack_forget()
		self.clientListBox.config(  width = 66 )
		
		# create Select Configuration
		self.setSelectConfigurationLabel()
							
					
	def setClientProjectList( self ):
		# change application
		self.application = CLIENT
		self.app.set('Client and Tools')
		
		#add the tools list box
		self.toolsbuildNumberFrame.pack( side = RIGHT, padx = 5, pady = 5 )
		self.clientListBox.config(  width = 30 )
		
		# create Select Configuration
		self.setSelectConfigurationLabel()
	
	def setSelectConfigurationLabel(self):
	
		def addToList(self, dir):
			if not (dir in self.buildConfigurationArray):
				self.buildConfigurationArray.append( dir )
		
		# reset everything
		self.clearAllLists()
		
		self.buildList = create_list.buildList(self.application)
		self.buildConfigurationArray = []
		for dir in self.buildList:
			if "2_current" in dir:
				addToList( self, prefixMapping[self.application] + "2_current")
			else:
				addToList( self, prefixMapping[self.application] + (dir.split("_"))[1])
			
		self.buildConfigurationArray = sorted(self.buildConfigurationArray)
		for configurationName in self.buildConfigurationArray:
			self.proConfigurationField['menu'].add_command( label = configurationName, 
					command = lambda configurationName = configurationName: self.setSelectProjectLabel( configurationName ) )
		
	def setSelectProjectLabel (self , configurationName ):
			
		self.buildConfigurationValue.set( configurationName )
		self.clearSelectProjectLabel()
		
		self.buildNameArray = []
		
		prefix =  configurationName + "_"
		
		for dir in create_list.buildList(self.application):
			if dir.startswith( prefix ):
				self.buildNameArray.append((dir[len(prefix):].split(".xml"))[0])
			
		self.buildNameArray = sorted(self.buildNameArray)
		for buildName in self.buildNameArray:
			self.proNameField['menu'].add_command( label = buildName, 
					command = lambda buildName = buildName: self.setClientAndToolsLists( buildName ) )
	
	def setClientAndToolsLists (self , buildName ):
	
		self.buildNameValue.set( buildName )	
		self.clearClientAndToolsLists()
		
		if self.application == CLIENT :
			self.setBuildList(self.clientListBox, os.path.join(CLIENT_SERVER,self.buildConfigurationValue.get() + "_" + buildName + "_client"))
			self.setBuildList(self.toolsListBox, os.path.join(CLIENT_SERVER,self.buildConfigurationValue.get() + "_" + buildName + "_tools"))
		else:
			self.setBuildList(self.clientListBox, os.path.join(CLIENT_SERVER,self.buildConfigurationValue.get() + "_" + buildName) )
			
	def setBuildList (self , targetListBox, basePath ):
		# Clear list
		targetListBox.delete(0, 'end')
		targetListBox.insert(END, DONT_COPY)
		list = sorted(create_build_number_list.createBuildsArray(basePath), reverse=True)
		
		if self.application == CLIENT :
			for build in list:
				targetListBox.insert(END, (build.getBuildNumber()).split("_")[0] + " (" +str(build.getTriggerBuild()) + ")  |  %s" % build.getDate())
		else:
			for build in list:
				targetListBox.insert(END, build.getBuildNumber() + " (" +str(build.getTriggerBuild()) + ")")

	def getSelectedFromListBox(self, listBox):
		if (int(listBox.curselection()[0])) == 0:
			return None
		return listBox.get(int(listBox.curselection()[0]))

	def getBuildNumber(self, listBox):
		select = self.getSelectedFromListBox(listBox)
		if None == select:
			return -1
		return select.split()[0]
		
	def getChangelistNumber(self, listBox):
		select = self.getSelectedFromListBox(listBox)
		if None == select:
			return "0"
		return (select.split("(")[1]).split(")")[0]
			
	def makeList( self ):
		# happen when we click on Generate an action list button
		self.clearActionList()
		serverNumber = -1
		clientNumber = -1
		toolsNumber = -1
		
		if self.clientListBox.curselection():
			self.changelistNumber = self.getChangelistNumber(self.clientListBox)
			if self.application == CLIENT:
				clientNumber = self.getBuildNumber(self.clientListBox)
				serverNumber = -1	
			else:
				clientNumber = -1
				serverNumber = self.getBuildNumber(self.clientListBox)
		if self.toolsListBox.curselection():	
			toolsNumber = self.getBuildNumber(self.toolsListBox)
			changelistTool = self.getChangelistNumber(self.toolsListBox)
	
			if changelistTool > self.changelistNumber:
				self.changelistNumber = changelistTool
		
		self.setP4ButtonText()		
	
		filter = FilterList()
		if self.debugFlag.get() == 0 :
			#don't copy *_d.*
			filter.add(ExcludeFilter(r'\S+_d\.\S+$'))
		if self.pdbFlag.get() == 1 :
			filter.add(ExcludeFilter(r'\S*\.pdb$'))
		if self.exportersFlag.get() == 0 :
			filter.add(ExcludeFilter(r'\S*tools\\exporter\\(maya|3dsmax)\S*'))
			filter.add(ExcludeFilter(r'\S*tools/exporter/(maya|3dsmax)\S*'))
			
		buildName = self.buildConfigurationValue.get() + "_" + self.buildNameValue.get()	
		self.actionsList = create_list.makeList(CLIENT_SERVER, BIGWORLD_DIR, buildName, \
							clientNumber, toolsNumber, serverNumber, filter )
		
		self.createActionList()
			
	def createActionList( self ) :
		self.actionListBox.delete(0, 'end')
		for k in self.actionsList.actionList:
			self.actionListBox.insert(END, k.description())
			if k.returnActionType() == actions.DELETE_ACTION:
				self.actionListBox.itemconfig(END, bg='tomato3', fg='white')
		
	def deleteAction( self ):
		# happen when the user select an action and press delete
		if self.actionListBox.curselection():			
			self.actionsList.deleteByIndex(int(self.actionListBox.curselection()[0]))
			#re-print list
			self.createActionList()		
		
	def action(self):
		#start executing the action list
		result = tkMessageBox.askquestion("Warning", "You are about to start the tool, are you sure?", icon='warning')
		if result == 'yes':
			if (self.p4UpdateFlag.get() == 1):
				self.perforceObj.run(self.changelistNumber, FormattingPrinter(output = CombinedOutput()))
			
			ret = self.actionsList.execute(FormattingPrinter(output = CombinedOutput()) )
			if ret:
				tkMessageBox.showinfo( "Congratulations", "Done." )
			else:
				tkMessageBox.showerror( message="p4 sync failed" )
	
root=Tk()
app = App( root )
app.master.title( "Copy tool    " + BIGWORLD_DIR )
root.mainloop()
