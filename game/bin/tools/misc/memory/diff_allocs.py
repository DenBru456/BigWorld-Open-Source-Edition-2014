"""
Calculates the difference between two allocation dumps.

usage: %(name)s dumpfile1 dumpfile2 output
"""
import os
import sys
import copy

import alloc_parser
from condense_allocs import writeCondensedCSV

#
# Returns tuple({diff_snapshot}, {slot_summaries: [allocCounts, allocBytes, deallocCounts, deallocBytes] }
def calculateDiff( allocs1, allocs2 ):
	result = copy.copy( allocs1 )
	
	allocCountTotal = 0
	allocBytesTotal = 0
	deallocCountTotal = 0
	deallocBytesTotal = 0
	
	statsBySlot = {}
	
	for callstack, (num, slotId, totalSize) in allocs2.iteritems():
		if slotId not in statsBySlot:
			statsBySlot[slotId] = [0,0,0,0]
				
		if callstack in result:
			# Exists in both
			result[callstack][0] = allocs2[callstack][0] - allocs1[callstack][0]
			result[callstack][2] = allocs2[callstack][2] - allocs1[callstack][2]
			
			if result[callstack][0] > 0:
				allocCountTotal += result[callstack][0]
				allocBytesTotal += result[callstack][2]
				statsBySlot[slotId][0] += result[callstack][0]
				statsBySlot[slotId][1] += result[callstack][2]
			else:
				deallocCountTotal += result[callstack][0]
				deallocBytesTotal += result[callstack][2]
				statsBySlot[slotId][2] += abs(result[callstack][0])
				statsBySlot[slotId][3] += abs(result[callstack][2])
		else:
			# Brand new callstack
			result[callstack] = [num, slotId, totalSize]
			allocCountTotal += num
			allocBytesTotal += totalSize
			statsBySlot[slotId][0] += num
			statsBySlot[slotId][1] += totalSize
	
	# Scan for items which are entirely deallocated
	for callstack, (num, slotId, totalSize) in allocs1.iteritems():
		if slotId not in statsBySlot:
			statsBySlot[slotId] = [0,0,0,0]
		
		if callstack not in allocs2:
			result[ callstack ][0] = -result[ callstack ][0]
			result[ callstack ][2] = -result[ callstack ][2]
			deallocCountTotal += -result[ callstack ][0]
			deallocBytesTotal += -result[ callstack ][2]
			statsBySlot[slotId][2] += abs(result[callstack][0])
			statsBySlot[slotId][3] += abs(result[callstack][2])
	
	# Clear out things which haven't changed at all
	for callstack, (num, slotId, totalSize) in allocs1.iteritems():
		if result[callstack][0] == 0:
			del result[callstack]
			
	return result, statsBySlot


#
# Formats the given slot summary (as returned from calculateDiff) into
# human readable text table (e.g. to write to disk).
def formatSlotSummary( slotSummary ):
	s = ""
	
	totalAllocCount = 0
	totalAllocBytes = 0
	totalDeallocCount = 0
	totalDeallocBytes = 0
	
	
	template = "{0:30} {1:30} {2:30} {3:30}"
	headerLine = template.format( "SLOT", "INCREASE", "DECREASE", "DELTA" )
	s += "=" * len(headerLine) + "\n"
	s += headerLine + "\n"
	s += "=" * len(headerLine) + "\n"
	
	for slotId, (allocCount, allocBytes, deallocCount, deallocBytes) in slotSummary.iteritems():
		inc = "%+d (%+d bytes)" % (allocCount, allocBytes)
		dec = "%+d (%+d bytes)" % (-deallocCount, -deallocBytes)
		delta = "%+d (%+d bytes)" % (allocCount - deallocCount, allocBytes - deallocBytes)
		s += template.format( slotId, inc, dec, delta )
		s += "\n"
		
		totalAllocCount += allocCount
		totalAllocBytes += allocBytes
		totalDeallocCount += deallocCount
		totalDeallocBytes += deallocBytes
	

	# totals
	s += "\n"
	inc = "%+d (%+d bytes)" % (totalAllocCount, totalAllocBytes)
	dec = "%+d (%+d bytes)" % (-totalDeallocCount, -totalDeallocBytes)
	delta = "%+d (%+d bytes)" % (totalAllocCount - totalDeallocCount, totalAllocBytes - totalDeallocBytes)
	s += template.format( "Totals", inc, dec, delta )
	
	s += "\n"
		
	return s
	
	
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print __doc__ % { "name": os.path.basename(__name__) }
		sys.exit()
		
	srcName1 = sys.argv[1]
	srcName2 = sys.argv[2]
	destName = sys.argv[3]
	
	# TODO: Read optional options
	callstackDepth = 0
	mergeSizesFlag = False
	ignoreSlotFlag =  False
	ignoreCallstacksFlag = False
	mergeSizesFlag = False
	
	print "Reading", srcName1, "..."
	allocations1 = alloc_parser.readAllocs( srcName1, callstackDepth,
		 ignoreSlotFlag, ignoreCallstacksFlag, mergeSizesFlag )
	
	print "Reading", srcName2, "..."	
	allocations2 = alloc_parser.readAllocs( srcName2, callstackDepth,
		 ignoreSlotFlag, ignoreCallstacksFlag, mergeSizesFlag )
		
	result, slotSummaries = calculateDiff( allocations1, allocations2 )
	
	open( "summary.txt", "w").write( formatSlotSummary( slotSummaries ) )
		
	print "Writing", destName, "..."
	writeCondensedCSV( destName, result, ignoreSlotFlag, ignoreCallstacksFlag, mergeSizesFlag )


