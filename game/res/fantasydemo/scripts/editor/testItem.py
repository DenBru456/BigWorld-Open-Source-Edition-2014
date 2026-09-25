
# Importing WorldEditor is not mandatory, it's imported because it's used to add
# commentary messages below.
import WorldEditor


class testItem:

	# This method is called by WorldEditor to get the model used in the editor for
	# this UserDataObject.
	def modelName( self, props ):
		try:
			return "resources/models/user_data_object.model"
		except:
			return "helpers/props/standin.model"

	# This method is called by WorldEditor to determine if this UserDataObject can
	# be cloned.
	def showAddGizmo( self, propName, thisInfo ):
		if propName[0:9] == "nextNode":
			return False			
		return True
		
	# This method is called by WorldEditor to determine if this UserDataObject can
	# be linked to another UserDataObject.
	def canLink( self, propName, thisInfo, otherInfo ):
		thisProps = thisInfo["properties"]
		otherProps = otherInfo["properties"]
		
		if propName[0:9] == "nodeArray":
			# It's the array property
			if len(thisProps["nodeArray"]) >= 8:
				# Too many array items, limiting to 8
				return False
			elif thisProps["nodeArray"].__contains__( ( otherInfo["guid"], otherInfo["chunk"] ) ):
				# The array already contains that item
				return False
			else:
				# The array items can link to anything
				return True
				
		elif otherInfo["type"] == thisInfo["type"] and propName == "nextNode":
			# "nextNode" only accepts UDOs of the same type.
			return True
			
		return False
