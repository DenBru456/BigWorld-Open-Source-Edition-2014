"""
Condense the given allocation dump into a CSV spreadsheet.

usage: %(name)s <myfile>.memallocs [callstack_depth] [flags]
flags:
	-ignoreslot
	-ignorecallstack
	-mergesizes
"""
import sys
import os
import csv
import math
import operator
import alloc_parser

def writeCondensedCSV( outName, allocs, ignoreSlotFlag,
					 ignoreCallstacksFlag, mergeSizesFlag ):
	# write condensed file
	outFile = open(outName, "wb")

	csvwriter = csv.writer( outFile )

	# build header
	header = []
	if not ignoreSlotFlag:
		header.append( "SlotId" )
	if not mergeSizesFlag:
		header.append( "Size" )

	header.append( "NumAllocs" )
	header.append( "TotalMem")

	if not ignoreCallstacksFlag:
		header.append( "Callstack" )

	csvwriter.writerow( header )

	totalAllocs = 0
	totalAllocatedSize = 0

	# sort by number of allocations
	sorted_x = sorted(allocs.iteritems(), key=operator.itemgetter(1), reverse=True)
	
	for (callstack, size), (num, slotId, totalMem) in sorted_x:
		totalAllocs += num
		totalAllocatedSize += totalMem

		# build data line
		dataLine = []
		if not ignoreSlotFlag:
			dataLine.append( slotId )
		if not mergeSizesFlag:
			dataLine.append( size )

		dataLine.append( num )
		dataLine.append( totalMem)

		if not ignoreCallstacksFlag:
			dataLine.append( callstack )

		csvwriter.writerow( dataLine )

	#print "Number of tracked allocations %d" % totalAllocs
	#print "Allocated size %d" % totalAllocatedSize

	outFile.close()

if __name__ == "__main__":
	# Make sure we have at least one input file
	if len(sys.argv) < 2:
		print __doc__ % { "name": os.path.basename(__file__) }
		exit()

	srcName = sys.argv[1]

	setArgs = set(sys.argv)
	# bunch of ignore flags. Useful to control granularity
	# Examples
	# use "-mergesizes -ignorecallstack" to get high level statistics per slot
	# use "-mergesizes -ignoreslot" and depthlevel 1 to see number of allocations per function
	ignoreSlotFlag =  "-ignoreslot" in setArgs
	ignoreCallstacksFlag = "-ignorecallstack" in setArgs
	mergeSizesFlag = "-mergesizes" in setArgs

	callstackDepth = 0

	if len(sys.argv) > 2:
		try:
			callstackDepth = int(sys.argv[2])
		except:
			callstackDepth = 0

	outName = os.path.splitext(srcName)[0] + ".csv"

	print "Reading", srcName, "..."
	allocations = alloc_parser.readAllocs( srcName, callstackDepth,
		 ignoreSlotFlag, ignoreCallstacksFlag, mergeSizesFlag )

	print "Writing", outName, "..."
	writeCondensedCSV( outName, allocations, ignoreSlotFlag,
					 ignoreCallstacksFlag, mergeSizesFlag )
