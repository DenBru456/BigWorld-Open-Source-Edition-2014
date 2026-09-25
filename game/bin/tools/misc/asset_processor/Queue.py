class Queue:
	"""A sample implementation of a First-In-First-Out data structure."""
	def __init__(self):
		self.in_stack = []
		self.out_stack = []

	def push(self, obj):
		self.in_stack.append(obj)

	def pop(self):
		if not self.out_stack:
			self.in_stack.reverse()
			self.out_stack = self.in_stack
			self.in_stack = []
		return self.out_stack.pop()

	def front( self ):
		if not self.out_stack:
			self.in_stack.reverse()
			self.out_stack = self.in_stack
			self.in_stack = []
		return self.out_stack[-1]

	def display( self ):
		for x in self.out_stack[::-1] + self.in_stack:
			print(x)


	def clear(self):
		self.in_stack = []
		self.out_stack = []

	def isEmpty( self ):
		return not ( len(self.in_stack) or len(self.out_stack)  )

	def __len__( self ):
		return len(self.in_stack) + len(self.out_stack)