import subprocess

class MacroExpander( object ):
	"""
	A class to expand RPM macros in strings. Macros are of the form
	%{MACRO_NAME}. Custom macros can be added using the subscript
	operator. When expanding a macro, if it is not a custom macro, the
	"rpm --eval" command is used instead to expand it.
	"""
	def __init__( self, **kwargs ):
		"""
		Constructor.

		@param kwargs 	The initial set of custom macros.
		"""
		self.macroDict = kwargs
	def __setitem__( self, key, value ):
		self.macroDict[key] = value

	def __delitem__( self, key ):
		del self.macroDict[key]

	@staticmethod
	def rpmExpand( macro ):
		"""
		Uses "rpm --eval" to evaluate a macro.
		"""
		cmd = ['rpm', '--eval', macro ]

		pipe = subprocess.Popen( cmd, shell=False, 
			stdout=subprocess.PIPE, stderr=None )

		output, _ = pipe.communicate()

		err = pipe.wait()
		if err != 0:
			raise ValueError, \
				"rpm returned error while evaluating string"

		return output.strip()

	def customMacros( self ):
		"""
		Return the custom macro dictionary.
		"""
		return self.macroDict

	def expand( self, string ):
		"""
		Return a new string, taking the given string and expanding macros
		contained within.

		@param string 	The input string.
		"""

		expansionPerformed = True

		while expansionPerformed:
			head = ''
			tail = string
			expansionPerformed = False

			while tail:
				start = tail.find( '%{' );
				end = tail.find( '}', start ) 
				macro = tail[start:end + 1]

				keyword = None

				if start >= 0 and end > 0:
					keyword = macro[2:-1]
					head += tail[:start]
					expansionPerformed = True
				else:
					# we're done
					head += tail
					break

				if start >= 0:
					if keyword in self.macroDict:
						head += self.macroDict[keyword]

					else:
						rpmExpanded = self.rpmExpand( macro )
						head += rpmExpanded

				tail = tail[end + 1:]
			string = head

		return string

# macro_expander.py

