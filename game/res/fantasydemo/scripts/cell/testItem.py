import BigWorld
class testItem(BigWorld.UserDataObject):
	def __init__(self):
		BigWorld.UserDataObject.__init__(self)
		self.pythonTestProperty = "testing"

