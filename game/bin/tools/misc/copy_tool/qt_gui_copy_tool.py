from PyQt4 import QtCore, QtGui

import sys

import widgetPy


import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "src"))
import time
import create_list
import create_build_number_list
import actions
from log import *
from filter import *
from revision_control import *

os.chdir(os.path.dirname(os.path.realpath(__file__)))
CLIENT_SERVER = os.path.join( "\\\\ba01", "BuildArchive" )

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
		
		
class MainDialog(QtGui.QDialog, widgetPy.Ui_Widget):
	def __init__(self, parent=None):
		super(MainDialog, self).__init__(parent)
		self.setupUi(self)
		
		#add p4 button only if p4 is installed from the command line
		self.perforceObj = Perforce()
		if self.perforceObj.validatePerforce():			
			self.changelistNumber = "0"
			self.setP4ButtonText()
		else:
			self.checkBox_SyncUser.setEnabled(False)
			
		# comboBox_ClientConfig
		self.actionsList = actions.ActionList()
		self.setSelectConfigurationLabel()
		self.connect(self.pushButton_GenerateAction, QtCore.SIGNAL("clicked()"), self.makeList)	
		self.connect(self.pushButton_BeginCopying, QtCore.SIGNAL("clicked()"), self.startCopy)	
			
	def setP4ButtonText(self):	
		if self.perforceObj.validatePerforce():
			if "0" == str(self.changelistNumber):
				self.checkBox_SyncUser.setText( "Sync " + self.perforceObj.getWorkspace() + " to latest revision" )
			else:
				self.checkBox_SyncUser.setText(  "Sync " + self.perforceObj.getWorkspace() + " to @" + str(self.changelistNumber) )
				
	def clearActionList(self):
		self.listWidget_Actions.clear()
		
	def clearClientAndToolsLists(self):
		self.listWidget_CopyClient.clear()
		self.listWidget_CopyTools.clear()
		self.clearActionList()

	def clearClientSelectProjectLabel(self):	
		self.disconnect(self.comboBox_ClientProject, QtCore.SIGNAL("currentIndexChanged(QString)"), self.setClientAndToolsLists)
		self.comboBox_ClientProject.clear()
			
		self.clearClientAndToolsLists()
	
	def clearServerLists(self):
		self.listWidget_CopyServer.clear()
		self.clearActionList()
		
	def clearServerSelectProjectLabel(self):	
		self.disconnect(self.comboBox_ServerProject, QtCore.SIGNAL("currentIndexChanged(QString)"), self.setServerList)
		self.comboBox_ServerProject.clear()
			
		self.clearServerLists()
						
	def clearAllLists(self):
		self.clearClientSelectProjectLabel()
		self.clearServerSelectProjectLabel()
		
	def setSelectConfigurationLabel(self):
			
		def addToList(buildConfigurationArray, dir):
			if not (dir in buildConfigurationArray):
				buildConfigurationArray.append( dir )
		
		# reset everything
		self.clearAllLists()
		
		def setLable(app):
			buildConfigurationArray = []
			
			buildList = create_list.buildList(app)
			for dir in buildList:
				if "2_current" in dir:
					addToList( buildConfigurationArray, prefixMapping[app] + "2_current")
				else:
					addToList( buildConfigurationArray, prefixMapping[app] + (dir.split("_"))[1])
				
			buildConfigurationArray = sorted(buildConfigurationArray, reverse=True)
			if app == CLIENT:
				comboBox = self.comboBox_ClientConfig
				func = self.setSelectClientProjectLabel
			else:
				comboBox = self.comboBox_ServerConfig
				func = self.setSelectServerProjectLabel
				
			comboBox.addItem("")	
			for configurationName in buildConfigurationArray:
				comboBox.addItem(configurationName)
							
			self.connect(comboBox, QtCore.SIGNAL("currentIndexChanged(QString)"), func)		
			
			func()
			
		setLable(CLIENT)
		setLable(SERVER)
		

	def setSelectServerProjectLabel (self ):
		self.clearServerSelectProjectLabel()
		
		buildNameArray = []
		prefix =  str(self.comboBox_ServerConfig.currentText()) + "_"
		for dir in create_list.buildList(SERVER):
			if dir.startswith( prefix ):
				buildNameArray.append((dir[len(prefix):].split(".xml"))[0])
			
		buildNameArray = sorted(buildNameArray)
		self.comboBox_ServerProject.addItem("")
		for buildName in buildNameArray:
			self.comboBox_ServerProject.addItem(buildName)
			
		self.connect(self.comboBox_ServerProject, QtCore.SIGNAL("currentIndexChanged(QString)"), self.setServerList)	
		self.setServerList()
	
	def setServerList (self ):
		# Clear lists
		self.clearServerLists()
		if self.comboBox_ServerConfig.currentText() and self.comboBox_ServerProject.currentText():
			buildName = str(self.comboBox_ServerConfig.currentText() + "_" + self.comboBox_ServerProject.currentText())
			self.setBuildList(self.listWidget_CopyServer, os.path.join(CLIENT_SERVER,buildName) )
				
	def setSelectClientProjectLabel (self ):
		self.clearClientSelectProjectLabel()
		
		buildNameArray = []
		prefix =  str(self.comboBox_ClientConfig.currentText()) + "_"
		for dir in create_list.buildList(CLIENT):
			if dir.startswith( prefix ):
				buildNameArray.append((dir[len(prefix):].split(".xml"))[0])
			
		buildNameArray = sorted(buildNameArray)
		self.comboBox_ClientProject.addItem("")
		for buildName in buildNameArray:
			self.comboBox_ClientProject.addItem(buildName)
			
		self.connect(self.comboBox_ClientProject, QtCore.SIGNAL("currentIndexChanged(QString)"), self.setClientAndToolsLists)	
		self.setClientAndToolsLists()
		
	def setClientAndToolsLists (self ):
		# Clear lists
		self.clearClientAndToolsLists()
		if self.comboBox_ClientConfig.currentText() and self.comboBox_ClientProject.currentText():
			buildName = str(self.comboBox_ClientConfig.currentText() + "_" + self.comboBox_ClientProject.currentText())

			self.setBuildList(self.listWidget_CopyClient, os.path.join(CLIENT_SERVER,buildName + "_client")) 
			self.setBuildList(self.listWidget_CopyTools, os.path.join(CLIENT_SERVER,buildName + "_tools")) 		
		
	def setBuildList (self , targetListBox, basePath ):
		list = sorted(create_build_number_list.createBuildsArray(basePath), reverse=True)
		for build in list:
			targetListBox.addItem((build.getBuildNumber()).split()[0] + " (" +str(build.getTriggerBuild()) + ")  |  %s" % build.getDate())

	def getSelectedFromListBox(self, listBox):
		if (int(listBox.curselection()[0])) == 0:
			return None
		return listBox.get(int(listBox.curselection()[0]))
		
	def getChangelistNumber(self):
		def returnMaxChangelist(changelistNumber, listWidget):
			if listWidget:
				return max(changelistNumber, int((str(listWidget.text()).split("(")[1]).split(")")[0]))
			return changelistNumber
			
		changelistNumber = 0
		# server
		if self.groupBox_2.isChecked():
			if self.groupBox_CopyClient.isChecked():
				changelistNumber = returnMaxChangelist(changelistNumber, self.listWidget_CopyClient.currentItem())
			if self.groupBox_CopyTools.isChecked():
				changelistNumber = returnMaxChangelist(changelistNumber, self.listWidget_CopyTools.currentItem())
		if self.groupBox.isChecked():
			changelistNumber = returnMaxChangelist(changelistNumber, self.listWidget_CopyServer.currentItem())
		
		return changelistNumber
	
	def getBuildNumber(self, item, isChecked):
		if item == None or isChecked == False:
			return -1
		return (str(item.text())).split()[0]	
		
	def makeList( self ):
		# happen when we click on Generate an action list button
		self.clearActionList()
		
		serverNumber =  self.getBuildNumber(self.listWidget_CopyServer.currentItem(), self.groupBox.isChecked())

		
		if self.groupBox_2.isChecked():
			clientNumber = self.getBuildNumber(self.listWidget_CopyClient.currentItem(), self.groupBox_CopyClient.isChecked())
			toolsNumber = self.getBuildNumber(self.listWidget_CopyTools.currentItem(), self.groupBox_CopyTools.isChecked())
		else:
			clientNumber = -1
			toolsNumber = -1
		
		self.changelistNumber = self.getChangelistNumber()

		
		self.setP4ButtonText()		
	
		filter = FilterList()
		if not self.checkBox_CopyDebug.isChecked():
			#don't copy *_d.*
			filter.add(ExcludeFilter(r'\S+_d\.\S+$'))
		if not self.checkBox_CopyPDB.isChecked():
			filter.add(ExcludeFilter(r'\S*\.pdb$'))
		if not self.checkBox_CopyExporters.isChecked():
			filter.add(ExcludeFilter(r'^game/bin/tools/exporter/(maya|3dsmax)'))
			
		buildName = str(self.comboBox_ClientConfig.currentText() + "_" + self.comboBox_ClientProject.currentText())
		serverBuildName  = str(self.comboBox_ServerConfig.currentText() + "_" + self.comboBox_ServerProject.currentText())
		
		self.actionsList = create_list.makeList(CLIENT_SERVER, BIGWORLD_DIR, buildName, \
							clientNumber, toolsNumber, serverNumber, filterList = filter,  serverBuildName = serverBuildName )				
		
		self.createActionList()
			
	def createActionList( self ) :
		self.listWidget_Actions.clear()
		for k in self.actionsList.actionList:
			item = QtGui.QListWidgetItem()
			item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
			item.setCheckState(QtCore.Qt.Checked)
			item.setText(widgetPy._translate("Widget", k.description(), None))
			self.listWidget_Actions.addItem(item)
							
				
	def startCopy(self):
		#start executing the action list
	
		if self.checkBox_SyncUser.isChecked():
			self.perforceObj.run(self.changelistNumber, FormattingPrinter(output = CombinedOutput()))
		
		tmpActionsList = self.actionsList
		unChecks = []
		for i in range(0, self.listWidget_Actions.count()):
			if not self.listWidget_Actions.item(i).checkState():
				unChecks.append(i)
		unChecks = sorted(unChecks, reverse=True)
		for i in unChecks:
			tmpActionsList.deleteByIndex(i)
			
		ret = tmpActionsList.execute(FormattingPrinter(output = CombinedOutput()) )
			
				
app = QtGui.QApplication(sys.argv)
form = MainDialog()
form.show()
app.exec_()
