import os
import sys

bwPycommonFilePath = os.path.dirname( os.path.realpath( __file__ ) )
bwSitePackages = os.path.abspath(
	os.path.join( bwPycommonFilePath, "../", "site-packages" ) )

if os.path.isdir( bwSitePackages ):
	sys.path.append( bwSitePackages )

else:

	# If we are running from a source checkout try and find the binary location
	# for the tools compilation.

	# check whether we have ../../../src/build
	# (to potentially import platform_info.py)


	# should map to BW_ROOT/bigworld/tools/server/pycommon
	bwPycommonFilePath = os.path.dirname( os.path.realpath( __file__ ) )
	bwBigWorld = os.path.abspath( os.path.join( bwPycommonFilePath,
												"../../../.." ) )
	bwRootBuild = os.path.join( bwBigWorld, 
								"../programming/bigworld/build/make" )
	bwPlatformInfoPath = os.path.join( bwRootBuild, "platform_info.py" )

	if not os.path.isfile( bwPlatformInfoPath ):
		raise ImportError( "Cannot import platform_info.py from %s"
				% bwRootBuild )
	else:
		oldSysPath = list( sys.path )
		sys.path.append( bwRootBuild )
		import platform_info

		platformName = platform_info.findPlatformName()

		if not platformName:
			raise ImportError( "Unable to determine current platform name "
				"to locate BigWorld binaries." )

		# Replace sys.path with the old paths
		sys.path = oldSysPath

		# Add the tools binary directory to the sys.path to allow import
		bwBinTools = os.path.join( bwBigWorld, "bin", "server", 
								platformName, "tools" )
		
		if not os.path.exists( bwBinTools ):
			import cluster_constants
			bwBinTools = None
			for bwConfig in cluster_constants.BW_SUPPORTED_CONFIGS:
				bwBinToolsTest = os.path.join( bwBigWorld, "bin", "server", 
							"tools", "%s_%s" % (platformName, bwConfig) )

				if os.path.exists( bwBinToolsTest ):
					bwBinTools = bwBinToolsTest
					break

			if not bwBinTools:
				raise ImportError( "Tools binary directory " 
						"did not exist to locate BigWorld binaries" )
		sys.path.append( bwBinTools )


