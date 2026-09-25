import BigWorld
import FantasyDemo

# Enumerates the standard video modes that we want to support.
def enumVideoModes():
	# Filter out all non-32bit modes.
	modes = [ mode for mode in BigWorld.listVideoModes() if mode[3] == 32 ]
	
	# Find the current mode
	current = 0
	#if we can't find the current mode (as on some screens a 
    #WindowedMode gives us a window which is a bit smaller than what we ask)
	#we use the closest mode.
	bestModeFound = 0
	minimalModeDifference = 10000
	foundCurrentMode = False
	
	for idx in range(len(modes)):
		mode = modes[idx]
		if BigWorld.isVideoWindowed():
			w, h = BigWorld.windowSize()
			modeDifference = abs(mode[1]-int(w)) + abs(mode[2]-int(h))
			if modeDifference == 0:
				current = idx
				foundCurrentMode = True
			if modeDifference < minimalModeDifference:
				bestModeFound = idx
				minimalModeDifference = modeDifference
		else:
			if mode[0] == BigWorld.videoModeIndex():
				current = idx
				foundCurrentMode = True
	if not foundCurrentMode:
		current = bestModeFound

	return modes, current

# Enumerates a list of aspect ratios that we want to support.
def enumAspectRatios():
	ratios = [
		(4, 3, None),
		(5, 4, None),
		(16, 9, None),
		(16, 10, None),
	]

	ret = []
	currentlySelected = 0
	current = 0
	currentAspectRatio = BigWorld.getFullScreenAspectRatio()
	for x, y, comment in ratios:
		desc = '%d:%d' % (x, y)
		if comment:
			desc += ' (%s)' % comment
		ratio = float(x)/y
		ret.append( (desc, ratio) )
		if abs(ratio - currentAspectRatio) < 0.01:
			currentlySelected = current
		current += 1
	
	if FantasyDemo.automaticAspectRatioEnabled():
		currentlySelected = -1
	
	return (ret, currentlySelected)
