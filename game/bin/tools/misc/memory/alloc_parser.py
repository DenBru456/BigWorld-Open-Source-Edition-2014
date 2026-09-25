import os

# trim callstack by given depth level
# if depth level set to one we use only 1 bottom level function
# useful to control granularity
# depth level can be negative, in this case we'll go backwards
def trimCallstack(callstack, callstackDepth):
	functions = callstack.split(" <- ")
	callstack = ""

	goBackwards = False
	if callstackDepth < 0:
		callstackDepth = -callstackDepth;
		goBackwards = True

	numCallstacks = len( functions )
	numToProcess = min( callstackDepth, numCallstacks )

	for i in range( numToProcess ):
		if goBackwards:
			callstack += functions[numCallstacks - i - 1] + " <- "
		else:
			callstack += functions[i] + " <- "

	# remove last " <- "
	callstack = callstack[:-4]
	return callstack

#
# Parses the given raw memory dump file into a dictionary of the form:
# {
#	"callstack1 size": (num, slotId, totalSize),
#	"callstack2 size": (num, slotId, totalSize),
#	...
#
#
def readAllocs( fname, callstackDepth, 
				ignoreSlotFlag, ignoreCallstacksFlag, mergeSizesFlag ):
				
	# Open the input file
	inFileSize = os.path.getsize( fname )
	inFile = open( fname,"r" )
	
	# read raw file
	allocs = dict()
	callstacks = dict()

	# read callstack hashes and string data
	numHashes = int(inFile.readline())

	for i in range(numHashes):
		data = inFile.readline().split(";")
		try:
			hashId = long(data[0], 16)
			stringData = data[1].strip()
			callstacks[hashId] = stringData
		except:
			print "invalid data ", data
			exit()

	# read allocation data
	allocation = inFile.readline().strip()

	while len(allocation) != 0:
		data = allocation.split(";")
		try:
			# read callstack hash as long and size as int to validate data
			slotId = data[0]
			if ignoreSlotFlag:
				slotId = ""
			callstackHash = long(data[1], 16)
			callstack = callstacks[callstackHash]
			if ignoreCallstacksFlag:
				callstack = slotId
			size = int(data[2])
		except:
			print "invalid data ", allocation
			exit()

		# trim callstack, callstackDepth == 0 is a default 'leave as is ' case
		if callstackDepth != 0:
			callstack = trimCallstack( callstack, callstackDepth )
		# combine callstack and size and use it as a key
		if mergeSizesFlag:
			key = (callstack, 0)
		else:
			key = (callstack, size)
		# add / update allocation data
		if allocs.has_key( key ):
			allocs[key][0] += 1
			allocs[key][2] += size
		else:
			allocs[key] = [1, slotId, size]
		# read next string
		allocation = inFile.readline().strip()

	inFile.close()
	return allocs
