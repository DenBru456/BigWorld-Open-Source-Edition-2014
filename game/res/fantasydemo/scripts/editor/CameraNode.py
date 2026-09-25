
class CameraNode:

	# return the patrol node model
	def modelName( self, props ):
		try:
			return "resources/models/camera_node.model"
		except:
			return "helpers/props/standin.model"

	# camera nodes always show the "+" gizmo
	def showAddGizmo( self, propName, thisInfo ):
		return True
