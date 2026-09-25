import re

class IncludeFilter:
	def __init__(self, regExpression):
		self._filter = regExpression
		
	def check(self, file):
		matchObj = re.match( self._filter, file)
		if matchObj:
			return True
		return False

class ExcludeFilter:
	def __init__(self, regExpression):
		self._filter = regExpression
		
	def check(self, file):
		matchObj = re.match( self._filter, file)
		if matchObj:
			return False
		return True	
		
class FilterList:
	def __init__(self):
		self._filterList = []

	def add(self, filter):
		self._filterList.append(filter)
		
	def check(self, file):
		for filter in self._filterList:
			if not filter.check(file):
				return False
		return True