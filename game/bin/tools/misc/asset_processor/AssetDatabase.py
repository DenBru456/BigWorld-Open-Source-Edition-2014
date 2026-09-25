import os
import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
import traceback
import FileProvider
from LogFile import errorLog
from FileUtils import BW_RES_PATH
from FileUtils import extension

import VisualFileProcessor
import MFMFileProcessor
import ModelFileProcessor
import FXFileProcessor
import ChunkFileProcessor
import GraphFileProcessor
import XMLFileProcessor
import ImageFileProcessor
import AnimationFileProcessor
import ParticleFileProcessor
import GuiFileProcessor
import ScriptFileProcessor
import FontFileProcessor

fileDatabase = None

class FileDatabaseEntry:
	def __init__( self, name ):
		self.name = name
		self.dependencies = []
		self.usedBys = []
		
	def section( self ):
		return ResMgr.openSection(self.name)
		
	def flagHasMoreThanOneFX( self, extraFX ):
		self.fxError = True
		self.extraFX = []
		for i in xrange(1,len(extraFX)):
			fxName = extraFX[i].asString
			if not fxName in self.extraFX:
				self.extraFX.append( fxName )
		
	def output( self ):
		if len(self.dependencies):
			#for i in self.dependencies:	
			#	errorLog.infoMsg( "-->%s" % (i,) )
			pass
		if len(self.usedBys):
			#for i in self.usedBys:	
			#	errorLog.infoMsg( "<--%s" % (i,) )
			pass
		else:
			pass
			#if not self.name in FileProvider.ignoreList:
			#	if ".fx" in self.name:
			#		errorLog.errorMsg( "%s is not used by anything" % (self.name,) )
			#	if ".mfm" in self.name:
			#		errorLog.errorMsg( "%s is not used by anything" % (self.name,) )
		if hasattr(self,"fxError"):
			pass
			#errorLog.errorMsg( "%s has more than one .fx file" % (self.name,) )
			#for fxName in self.extraFX:
			#	errorLog.errorMsg( "...%s" % (fxName,) )
				
	def load( self, sect ):
		self.name = sect.asString
		
		deps = sect.readStrings( "dependency" )
		for name in deps: self.addDependency( name )
		
		ubys = sect.readStrings( "usedBy" )
		for name in ubys: self.addUsedBy( name )
		
		self.extraFX = sect.readStrings( "extraFX" )
		if sect.has_key("fxError"):
			self.fxError = sect.readBool("fxError")				
		if sect.has_key("alphaRef"):
			self.alphaRef = sect.readString("alphaRef")
		if sect.has_key("alphaTestEnabled"):
			self.alphaTestEnabled = sect.readBool("alphaTestEnabled")
		if sect.has_key("doubleSided"):
			self.doubleSided = sect.readBool("doubleSided")
		
	def save( self, sect ):
		sect.asString = self.name
		
		deps = []
		for entry in self.dependencies: deps.append( entry.name )
		sect.writeStrings( "dependency", tuple(deps) )
		
		ubys = []
		for entry in self.usedBys: ubys.append( entry.name )
		sect.writeStrings( "usedBy", tuple(ubys) )
		
		if hasattr(self,"extraFX"):
			sect.writeStrings( "extraFX", tuple(self.extraFX) )
		if hasattr(self,"fxError"):
			sect.writeBool( "fxError", self.fxError )
		if hasattr(self,"alphaTestEnabled"):
			sect.writeBool( "alphaTestEnabled", self.alphaTestEnabled )
		if hasattr(self,"alphaRef"):
			sect.writeString( "alphaRef", self.alphaRef )
		if hasattr(self,"doubleSided"):
			sect.writeBool( "doubleSided", self.doubleSided )
				
	def addDependency( self, name ):
		global fileDatabase
		entry = fileDatabase.get(name)
		if not entry in self.dependencies:
			self.dependencies.append(entry)
		entry.addUsedBy( self.name )
		
	def addUsedBy( self, name ):
		global fileDatabase
		entry = fileDatabase.get(name)
		if not entry in self.usedBys:
			self.usedBys.append(entry)
			

class FileDatabase:
	def __init__( self ):
		global fileDatabase
		fileDatabase = self
		self.entries = {}
		self.readOnly = False		
		
		self.databaseCompilers = {}
		self.databaseCompilers["mfm"] = MFMFileProcessor.MFMFileProcessor()
		self.databaseCompilers["visual"] = VisualFileProcessor.VisualFileProcessor()
		self.databaseCompilers["model"] = ModelFileProcessor.ModelFileProcessor()
		self.databaseCompilers["fx"] = FXFileProcessor.FXFileProcessor()
		self.databaseCompilers["chunk"] = ChunkFileProcessor.ChunkFileProcessor()	
		self.databaseCompilers["graph"] = GraphFileProcessor.GraphFileProcessor()	
		self.databaseCompilers["xml"] = XMLFileProcessor.XMLFileProcessor()
		self.databaseCompilers["xml"] = ParticleFileProcessor.ParticleFileProcessor()
		self.databaseCompilers["gui"] = GuiFileProcessor.GuiFileProcessor()
		self.databaseCompilers["tga"] = ImageFileProcessor.ImageFileProcessor()
		self.databaseCompilers["bmp"] = ImageFileProcessor.ImageFileProcessor()
		self.databaseCompilers["jpg"] = ImageFileProcessor.ImageFileProcessor()
		self.databaseCompilers["dds"] = ImageFileProcessor.ImageFileProcessor()
		self.databaseCompilers["png"] = ImageFileProcessor.ImageFileProcessor()
		self.databaseCompilers["texanim"] = ImageFileProcessor.ImageFileProcessor()
		self.databaseCompilers["animation"] = AnimationFileProcessor.AnimationFileProcessor()
		self.databaseCompilers["py"] = ScriptFileProcessor.ScriptFileProcessor()
		self.databaseCompilers["font"] = FontFileProcessor.FontFileProcessor()
		
	def get( self, name ):
		if not self.entries.has_key( name ):
			if self.readOnly:
				errorLog.errorMsg( "Tried to create database entry for %s during processing stage" % (name,) )
			self.entries[name] = FileDatabaseEntry(name)			
			
		return self.entries[name]
		
		
	def remove( self, name ):
		if self.entries.has_key( name ):
			dbEntry = self.entries[name]
			del self.entries[name]
			
			for dependency in dbEntry.dependencies:
				depname = dependency.name
				if self.entries.has_key(depname):
					self.remove(depname)
			
			for usedBy in dbEntry.usedBys:
				if self.entries.has_key(usedBy.name):
					usedEntry = self.entries[usedBy.name]
					for depEntry in usedEntry.dependencies[:]:
						if depEntry.name == dbEntry.name:
							usedEntry.dependencies.remove(depEntry)	
					

	def output( self ):
		for (key,value) in self.entries.items():
			#errorLog.infoMsg( "%s" % (key,) )		
			value.output()
			
	def compile( self ):
		self.readOnly = False
		extensionList = self.databaseCompilers.keys()		
		self.fileProvider = FileProvider.FileProvider(extensionList)
		self.fileProvider.begin()
		(ext,fileName) = self.fileProvider.next()
		while fileName != None:
			dbEntry = self.get( fileName )
			self.databaseCompilers[ext].buildDatabase(dbEntry)
			(ext,fileName) = self.fileProvider.next()
			
	def process( self, fileProcessors ):	
		fileProcessors
		self.readOnly = True	
		for fileProcessor in fileProcessors:
			for dbEntry in self.entries.values():
				try:
					ext = extension(dbEntry.name)					
					if ext in fileProcessor.appliesTo():
						if dbEntry.section() != None:					
							applied = fileProcessor.process(dbEntry)							
							if applied:
								errorLog.infoMsg( "%s applied to %s" % (fileProcessor.description, dbEntry.name) )															
						else:
							errorLog.errorMsg( "%s does not exist" % (dbEntry.name,) )
				except:
					errorLog.errorMsg( "Script Error processing %s" % (dbEntry.name,) )
					traceback.print_exc()
					traceback.print_stack()

	def save( self, dbName ):
		db = ResMgr.openSection( dbName, False )
		if db:
			for i in db.keys():
				db.deleteSection(i)
		else:
			db = ResMgr.openSection( dbName, True )
		for (key,entry) in self.entries.items():
			sect = db.createSection( "entry" )
			entry.save(sect)
		db.save()
		errorLog.infoMsg( "Saved asset database %s" % (dbName,) )
		
	def load( self, dbName ):
		sect = ResMgr.openSection( dbName )
		if not sect:
			errorLog.errorMsg( "Could not load asset database %s" % (dbName,) )
			return False
		for i in sect.values():			
			dbEntry = FileDatabaseEntry(i.asString)
			dbEntry.load(i)
			self.entries[dbEntry.name] = dbEntry
		errorLog.infoMsg( "Loaded asset database %s" % (dbName,) )
		return True
