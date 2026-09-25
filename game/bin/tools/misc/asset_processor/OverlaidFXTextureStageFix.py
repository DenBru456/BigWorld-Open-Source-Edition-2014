from LogFile import errorLog
from FileUtils import fullName

#------------------------------------------------------------------------------
# Any Individual Asset Processor must have
#
# a list of extensions that the processor applies to
# a process( dbEntry ) method
#
# the process method returns true iff the file was updated.
#------------------------------------------------------------------------------


#This class fixes up texture stages to allow stage 2 to be the cloud shadow map
#If "stdinclude.fxh" is not included, then put it at the top of the file, as it
#contains the defineable constants 'CLOUDMAP_STAGE_PLUS1' etc.
class OverlaidFXTextureStageFix:
	def __init__( self ):
		self.description = "Overlaid FX Texture Stage Fix"
		
	def appliesTo( self ):
		return ("fx",)
		
	def process( self, dbEntry ):
		output = []
		filename = fullName(dbEntry.name)		
		
		#Citizen Zero specific - do not apply cloud shadows
		#to GUI models and GUI materials
		#if "gui/m" in filename:
		#	return False
		
		inOverrideTechniques = False
		foundTStage1 = False
		foundStdInclude = False
		needStdInclude = False
		changed = False
		warning = False		
		additive = False
		additiveDefined = False
		
		try:
			f = open(filename,'r')
		except IOError:		
			errorLog.errorMsg("Could not open %s for reading" % (filename,))
			return False
			
		lines = f.readlines()
		for line in lines:				
			if "#include" in line:
				if "stdinclude.fxh" in line:
					foundStdInclude = True
				elif "stdinclude.fx" in line:
					line = '#include "stdinclude.fxh"'
			if "DestBlend = ONE;" in line:
				additive = True
			if "#define ADDITIVE_EFFECT 1" in line:
				additiveDefined = True
			if "technique EffectOverride" in line: inOverrideTechniques = True
			if "[1] = " in line: foundTStage1 = True
			if inOverrideTechniques and foundTStage1:
				if "[1] = " in line:
					line = self.incrementTextureStage(line)
					changed = True
					needStdInclude = True
				elif "[2] = " in line:
					line = self.incrementTextureStage(line)
					changed = True
					needStdInclude = True
				elif "[3] = " in line:
					line = self.incrementTextureStage(line)
					changed = True					
					#This is probably an error, as it is unlikely any effect uses 4 texture stages.
					#The probable cause of this error is a hand-fixed effect file that has just now
					#been incorrectly processed and incremented past stage 3.
					#Note we only flag this after a call to incrementTextureStage from 3 to 4
					warning = True					
			output.append(line)
		f.close()
		
		#output	
		if changed and len(output) > 0:
			f = open(filename,'w+')
			if f == None:
				errorLog.errorMsg("Could not open %s for writing" % (filename,))
				changed = False
			else:
				if additive and not additiveDefined:
					f.write( '#define ADDITIVE_EFFECT 1\n' )
				if needStdInclude and not foundStdInclude:
					f.write( '#include "stdinclude.fxh"\n' )
				f.writelines(output)
				f.close()
				
		if warning:
			errorLog.warningMsg( "Probable Error applying Overlaid FX Texture Stage Fix to %s" % (dbEntry.name,) )
					
		return changed
		
		
	def incrementTextureStage( self, line ):		
		newCoord = 0
		
		idx = line.find("[1] = ")
		if idx != -1: newCoord = "CLOUDMAP_STAGE_PLUS1"
		
		if newCoord == 0 :
			idx = line.find("[2] = ")
			if idx != -1: newCoord = "CLOUDMAP_STAGE_PLUS2"
			
		if newCoord == 0 :
			idx = line.find("[3] = ")
			if idx != -1: newCoord = 4
				
		if newCoord != 0:
			s = str(newCoord)	
			
			#update the index			
			line = line[0:idx] + "[" + s + "] = " + line[idx+6:]
			
			#update the tex coord index too
			if "TexCoordIndex" in line:
				sc = line.find(";")
				if sc != -1: line = line[:sc-1] + s + ";"
			
		return line