#this script will test batch_compiler 

import sys
import os
import pipes
import subprocess
import re
import shutil
import stat
import unittest

VERBOSE = True

PACKAGE_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","..","..")


DATA_DIR = os.path.join( os.path.dirname( os.path.realpath(__file__) ), "data" )
CLIENT_SCRIPT_DIR= os.path.join( PACKAGE_ROOT, "game", "res", "fantasydemo", "scripts", "client" )

BATCH_COMPILER_EXE = os.path.join(PACKAGE_ROOT, "game", "bin", "tools", "asset_pipeline_release", "batch_compiler.exe")
INTERMEDIATE_PATH = os.path.join(PACKAGE_ROOT, "intermediate")
OUTPUT_PATH_DIR = os.path.join(PACKAGE_ROOT, "packed", "Client")
CACHE_PATH = os.path.join(PACKAGE_ROOT, "Assetcache")
REPORT_PATH = os.path.join(PACKAGE_ROOT, "bigworld_report.html")

RES_TEST_DIR = os.path.join(PACKAGE_ROOT, "game", "res", "fantasydemo", "batch_compiler_tests")

MAIN_CMD = "%s %s -intermediatePath %s -outputPath %s -cachePath %s -report %s -j 4" % (BATCH_COMPILER_EXE , PACKAGE_ROOT, INTERMEDIATE_PATH, OUTPUT_PATH_DIR, CACHE_PATH, REPORT_PATH)

os.chdir(PACKAGE_ROOT)	

def runCommand(	cmd ):
	# run a command, print the output to the screen, and to a file
	if VERBOSE:
		print cmd	
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	
	output = []
	
	for line in iter(p.stdout.readline, ''):
		if VERBOSE:
			print line
			
		output.append(line)
	p.stdout.close()
	return output
	
def deleteIfExists( file ):
	def remove_readonly(func, path, excinfo):
		os.chmod(path, stat.S_IWRITE)
		func(path)
	
	if os.path.exists(file):
		os.chmod( file, stat.S_IWRITE )
		if os.path.isdir(file):
			shutil.rmtree(file, onerror=remove_readonly)	
		else:
			os.remove(file)
		print "Delete " + file
		
global_output = ""
class TestBatchCompiler(unittest.TestCase):		

	def test_1_checkOutput( self ):
			
		self.assertTrue( os.path.exists(BATCH_COMPILER_EXE),
		"\n\nCan't find - " + BATCH_COMPILER_EXE + "\n")
		
		self.assertTrue( os.path.exists(os.path.join(PACKAGE_ROOT, "game", "bin", "client", "win32", "bwclient_h.exe")),
		"\n\nCan't find - " + os.path.join(PACKAGE_ROOT, "game", "bin", "client", "win32", "bwclient_h.exe") + "\n")
			
		# clear cache
		deleteIfExists(INTERMEDIATE_PATH)
		deleteIfExists(os.path.join(PACKAGE_ROOT, "packed"))
		deleteIfExists(CACHE_PATH)
		deleteIfExists(REPORT_PATH)
		deleteIfExists(RES_TEST_DIR)
		for i in range(1, 10):
			deleteIfExists(REPORT_PATH.replace(".html", "_" + str(i) + ".html"))
		
		global global_output	
		global_output = (runCommand(MAIN_CMD))[-1]

		m = re.match("========== Conversion: (\d+) succeeded, (\d+) failed, (\d+) converted, (\d+) up-to-date, (\d+) skipped ==========", global_output)
		self.assertTrue(m, "\n\nError: unknown output " + global_output)

		self.assertFalse(int(m.group(1)) < 1 , 
						"\n\nError: BatchCompiler hasn't converted any assets")

		self.assertFalse( int(m.group(2)) > 0,
			 "\n\nError: BatchCompiler has %d failures" % int(m.group(2)))
		
		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_1" ".html"))
		
	def test_2_checkReport( self ):
		output = global_output
		self.assertTrue(os.path.exists(REPORT_PATH),
			"\n\nError: report hasn't been generated " + REPORT_PATH)
			
		f = open( REPORT_PATH, "r" )
		conversionLine = False
		
		searchLine = ((output.split("=========="))[1]).strip()
				
		for line in f:
			if searchLine in line:
				conversionLine = True
				break
		f.close()
		self.assertTrue(conversionLine,
			"\n\nError: report output not matching batchCompiler output\n" + searchLine)
			
		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_2" ".html") )
		
	def test_3_noNewDDS( self ):	
		pathXml = os.path.join(PACKAGE_ROOT, "game", "bin", "client", "win32", "Paths.xml") 
		fantasyDemoResDir = os.path.join(PACKAGE_ROOT, "game", "res", "fantasydemo")  
		testPy = os.path.join(PACKAGE_ROOT, "programming", "bigworld", "build", "bw_internal", "scripts", 
							"testing", "data", "bwclientnavgentest02_highlands.py")
		
		os.chmod( pathXml, stat.S_IWRITE )
		sourceFile = open(pathXml, "r")
		sourceLines = sourceFile.readlines()
		sourceFile.close()
		destFile = open(pathXml, "w")

		for line in sourceLines:
			destFile.write( line )
			if "<Paths>" in line:
				destFile.write( "\t\t<Path>../../../../packed/Client</Path>\n" )	
		destFile.close()
		
		perforceFiles = []
		#delete all .dds files that are not in perforce (not read only)
		for (path, dirs, files) in os.walk(fantasyDemoResDir):
			for file in files:
				file_path = os.path.join(path, file)
				if file_path.endswith(".dds"):	
					try:
						os.unlink(file_path)
					except:
						perforceFiles.append(file_path)
		
		# copy the test script to the resource directory
		test_name = "bwclientnavgentest"
		client = os.path.join(PACKAGE_ROOT, "game", "bin", "client", "win32", "bwclient_h.exe")
		
		test_path = os.path.join(DATA_DIR, test_name + ".py" )
		temp_test_path = os.path.join( CLIENT_SCRIPT_DIR, test_name + ".py" )
		if os.path.exists( temp_test_path ):
			os.chmod( temp_test_path, stat.S_IWRITE )
		shutil.copy( test_path, temp_test_path )
		
		cmd = "%s -noConversion --script %s" % ( client, test_name )
		runCommand( cmd )
		
		error = False
		#search for new .dds files
		for (path, dirs, files) in os.walk(fantasyDemoResDir):
			for file in files:
				if file.endswith(".dds"):
					file_path = os.path.join(path, file)
					if not file_path in perforceFiles:
						print "\n\nError: Bwclient generate the file " + file_path
						error = True
						break
						
		if os.path.exists( temp_test_path ):
			os.chmod( temp_test_path, stat.S_IWRITE )
			os.remove(temp_test_path)
			
		destFile = open(pathXml, "w")
		for line in sourceLines:
			#return to old file
			destFile.write( line )
		destFile.close()

		self.assertFalse(error)

		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_3" ".html") )
		
	def test_4_skippingGeneratedAssets( self ):	
		output = runCommand(MAIN_CMD)
		
		self.assertTrue(os.path.exists(REPORT_PATH),
			"\n\nError: report hasn't been generated " + REPORT_PATH)
			
		f = open( REPORT_PATH, "r" )
		
		warnings = 0
		converted = 0
		for line in f:
			m = re.match("(.*)Warnings \((\d+)", line)
			if m:
				warnings = int(m.group(2))
			else:
				m = re.match("(.*)Converted \((\d+)", line)
				if m:
					converted = int(m.group(2))
		f.close()
		# files with warnings should be re-converted
		self.assertFalse( converted > warnings,
			"\n\nError: %d converted files, should be no more than %d" % (converted, warnings))
			
		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_4" ".html") )
		
	def test_5_deleteDependancies( self ):	
		output = global_output
		deleteIfExists(INTERMEDIATE_PATH)
		deleteIfExists(CACHE_PATH)
		newOutput = runCommand(MAIN_CMD)[-1]
		self.assertTrue(output.strip() == newOutput.strip(),
			"\n\nError: the conversion after cleaning the cache is not the same as before\n" + output )
			
		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_5" ".html") )

	def test_6_relativePaths( self ):	
		os.chdir(os.path.join(PACKAGE_ROOT, "game", "bin", "client", "win64"))

		output = runCommand( "..\\..\\tools\\asset_pipeline_release\\batch_compiler.exe ..\\..\\..\\res\\bigworld\\shaders\\terrain -intermediatePath ..\\..\\..\\..\\intermediate -outputPath ..\\..\\..\\..\\packed\\Client\\ -cachePath ..\\..\\..\\..\\Assetcache -report ..\\..\\..\\..\\bigworld_report.html -j 4")[-1].strip()
		os.chdir(PACKAGE_ROOT)
		m = re.match("========== Conversion: (\d+) succeeded, 0 failed, (\d+) converted, (\d+) up-to-date, (\d+) skipped ==========", output)
		self.assertTrue( m, "\n\nError: failed to convert with relative paths")
		self.assertTrue(int(m.group(1)) > 1,
			"\n\nError: failed to convert with relative paths")

		self.assertTrue( int(m.group(2)) == 0,
				"\n\nError: failed to convert with relative paths")

		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_6" ".html") )
		
	def test_7_modifyAnAsset( self ):	
		modifyAsset = "ranger_face_spec.bmp"
		orgLocation = os.path.join(PACKAGE_ROOT, "game", "res", "fantasydemo", "characters", "avatars", "ranger")
		deleteIfExists(os.path.join(orgLocation, modifyAsset + "_bk"))
		if os.path.exists(os.path.join(orgLocation, modifyAsset)):
			shutil.copy( os.path.join(orgLocation, modifyAsset), os.path.join(orgLocation, modifyAsset + "_bk") )
			deleteIfExists(os.path.join(orgLocation, modifyAsset))
		shutil.copy( os.path.join(DATA_DIR, modifyAsset), os.path.join(orgLocation, modifyAsset) )
		
		cmd = "%s %s -intermediatePath %s -outputPath %s -cachePath %s -report %s -j 4" % \
					(BATCH_COMPILER_EXE , PACKAGE_ROOT, INTERMEDIATE_PATH, OUTPUT_PATH_DIR, CACHE_PATH, REPORT_PATH)
		output = runCommand(cmd)
		error = True
		searchString = modifyAsset + " ->"
		for line in output:
			if searchString in line:
				error = False
				break
		
		deleteIfExists(os.path.join(orgLocation, modifyAsset))
		shutil.copy( os.path.join(orgLocation, modifyAsset  + "_bk" ), os.path.join(orgLocation, modifyAsset) )
		deleteIfExists(os.path.join(orgLocation, modifyAsset + "_bk"))
		
		self.assertFalse( error,
			"\n\nError: " + modifyAsset + " haven't been converted")

		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_7" ".html") )
		
	def test_8_forceFail( self ):
		if not os.path.exists(RES_TEST_DIR):
			os.mkdir(RES_TEST_DIR)       
		failAsset = os.path.join(DATA_DIR, "fail.bmp")
		newLocation = os.path.join(RES_TEST_DIR, "fail.bmp")

		shutil.copy( failAsset, newLocation )
		cmd = "%s %s -report %s " % (BATCH_COMPILER_EXE , newLocation, REPORT_PATH)
		output = runCommand(cmd)[-1]	
		
		self.assertTrue("1 succeeded, 1 failed" in output,
			"\n\nError: batch_compiler should have failed when converting " + newLocation)

		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_8" ".html") )
		
	def test_9_compileSingleAsset( self ):
		def compileAsset(asset):
			failAsset = os.path.join(DATA_DIR, asset)
			
			newLocation = os.path.join(RES_TEST_DIR, asset)

			shutil.copy( failAsset, newLocation )
			cmd = "%s %s " % (BATCH_COMPILER_EXE , newLocation)
			output = runCommand(cmd)
			
		if not os.path.exists(RES_TEST_DIR):
			os.mkdir(RES_TEST_DIR)    
		
		tests = ["test_bmp.bmp", "test_jpg.jpg", "test_tga.tga"]
		for test in tests:
			compileAsset(test)
			
		print "\n\n=========== Batch Compiler test complete =============="
		print "To make sure the test succeeded, please do the following:"
		print "open " + RES_TEST_DIR
		print "and check each of the following: %s" % tests
		print "They should be the same as their matching dds version."
				
		shutil.copy( REPORT_PATH, REPORT_PATH.replace(".html", "_9" ".html") )
		
if __name__ == '__main__':
	unittest.main(failfast=True)