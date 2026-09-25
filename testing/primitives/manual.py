"""
This module provides basic functionality for manual (semi-automatic)
testing. 
"""

from bwtest import log

HEADER_STR = "\n****** Manual Step *******" 
RESUME_STR = "****** Test resumed ******\n" 
INPUT_STR = "> "

def input( prompt ):
	"""
	Print a prompt and wait for user input
	@param prompt:	Text to display
	
	@return 		entered string
	"""
	
	print HEADER_STR
	print prompt
	res = raw_input( INPUT_STR )
	print RESUME_STR
	return res
	
	
def input_choice( prompt, choices ):
	"""
	Print a prompt with choices and wait for user input
	@param prompt:	Text to display
	@param choices:	Iterable with tuples of (expected_value, description)
	
	@return 		expected_value of selected choice
	"""

	prompt = prompt.strip()
	
	if not choices:
		raise ValueError( "input_choice(): choices must be non-empty "
					"iterable with tuples of (expected_value, description)" )
	
	choiceValues = [c[0] for c in choices]
	
	print HEADER_STR
	print prompt
	for choice in choices:
		print "%s - %s" % (choice[0], choice[1])
	
	while True:
		res = raw_input( INPUT_STR )
		
		if res in choiceValues:
			print RESUME_STR
			return res
		
		print "Please enter one of the following: %s" % ', '.join( choiceValues )


def input_yesno( prompt ):
	"""
	Print a prompt with yes/no choices and wait for user input
	@param prompt:	Text to display
	
	@return 		True or False
	"""
	
	res = input_choice( prompt, [("y", "yes"), ("n", "no")] )
	if res == "y":
		return True
	else:
		return False
		
		
def input_passfail( prompt ):
	"""
	Print a prompt with pass/fail choices and wait for user input
	@param prompt:	Text to display
	
	@return 		True or False
	"""

	res = input_choice( prompt, [("p", "passed"), ("f", "failed")] )
	if res == "p":
		return True
	else:
		return False

