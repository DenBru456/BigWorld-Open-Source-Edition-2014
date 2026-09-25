# interpret_memory_map.py
#
# This script interprets the output of BigWorld.saveMemoryMap
# It outputs two .raw/tga files which contain the distribution of memory

import sys
import struct
import math

def saveTGA(outname):
	print "saving TGA file %s.tga" % outname
	outTGA = open( outname + ".tga","wb+" )
	#read binary data and calculate width and height
	inRGB = open( outname + ".raw","rb+" )
	inAlpha = open( outname + ".a.raw","rb+" )

	rgdData = inRGB.read()
	alphaData = inAlpha.read()
	sz = len(alphaData)
	height = int(math.sqrt(sz))
	width = int(math.ceil(sz / float(height)))
	#write TGA header
	outTGA.write( struct.pack("BBBBBBBBBBBB", 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0  ))
	outTGA.write( struct.pack("BBBB", width & 0x00FF, (width & 0xFF00) / 256, height & 0x00FF, (height & 0xFF00) / 256 ))
	outTGA.write( struct.pack("BB", 32, 0 ))
	# write data
	for i in range(sz):
		rgbStr = rgdData[i * 3 : i * 3 + 3]
		r, g, b = struct.unpack( "BBB", rgbStr )
		(a,) = struct.unpack( "B", alphaData[i] )
		outTGA.write( struct.pack("BBBB", b, g, r, a) )

	reminder = width * height - sz
	for i in range(reminder):
		outTGA.write(struct.pack("BBBB", 0, 0, 0, 255))

	inRGB.close()
	inAlpha.close()
	outTGA.close()

def saveRAW(outname):
	# Open the input file
	try:
		inFile = open(sys.argv[1],"rb")
	except IOError:
		print "usage: " + sys.argv[0] + " <myfile>.mem"
		exit()

	outRGB = open( outname + ".raw","wb+" );
	outAlpha = open( outname + ".a.raw","wb+" );

	# Red the first two bytes of the memory map
	s = inFile.read(2)

	count = 0
	fragmentation = 0.0
	memory = 0

	# Keep reading until the end of the file
	while len(s) != 0:
		# Read the first uint16
		(mVal,) = struct.unpack("H", s)
		
		# the top 3 bits are the location specifier
		# bit 0 is memory that is reserved by us but not necessarily used through VirtualAlloc
		# bit 1 is memory that has been allocated using the MemTracker
		# bit 2 is memory that has been allocated on the heap outside our control (i.e d3d heap allocations, web integration)
		location = mVal >> 13
		
		# mask out the location bits
		mVal = mVal & 0x1fff

		# init our rgb values
		# We output the following:
		# r = VirtualAlloced memory
		# g = Our allocations that have gone through the MemTracker
		# b = Heap allocations done outside our code
		# a = 255 if the 4k block of memory is full, 0 if empty and 128 if neither full nor empty, this is to visualise 
		#	memory fragmentation better

		a = 128
		r = 0
		g = 0
		b = 0
		
		if mVal == 0:
			a = 0
		elif mVal == 4096:
		    a= 255
		    mVal = 4095
		val = mVal / 16
		if location & 4:
			r = val
		if location & 2:
			g = val
		if location & 1:
			b = val
		
		# Fragmentation value
		if mVal != 0:
			count += 1
			fragmentation += (4096.0 - mVal) / 4096.0
			memory = memory + mVal

		outRGB.write( struct.pack("BBB", r, g, b));
		outAlpha.write( struct.pack("B", a));
		s = inFile.read(2)

	print "Overall fragmentation", fragmentation / count
	print "Memory used (in MB)", memory / (1024*1024)

	#close files
	outAlpha.close()
	outRGB.close()
	inFile.close()

if __name__ == "__main__":
	# Make sure we have at least one input file
	if len(sys.argv) < 2:
		print "usage1: " + sys.argv[0] + " <myfile>.mem"
		exit()

	# Open the output files
	outname = sys.argv[1].split(".")

	saveRAW( outname[0] )
	# creates TGA from raw files
	saveTGA( outname[0] )

