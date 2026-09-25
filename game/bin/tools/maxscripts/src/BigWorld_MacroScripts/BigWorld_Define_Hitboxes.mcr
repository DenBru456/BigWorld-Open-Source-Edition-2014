macroScript Attach_HitBox
	category:"BigWorld"
	toolTip:"Attach HitBox"
	Icon:#("bigworld_icons", 10)
	
	-- Description
	-- Adds (parents and aligns) hitboxes to selected limbs
	-- Hitbox names are nodename_bwhitbox
	-- Sets hitboxes to non renderable so they dont export as part of visual mesh
	-- Assigns a BSP material colour to the hitboxes
	
(	
	parentName = ""
	box_suffix = "_bwhitbox"	
	magicLimbWidth = 2.5
	
	for i in 1 to selection.count do
	(
		hasChild = true
		
		newHitbox = box length:10 width:10 height:10
		newHitbox.renderable = off
		parentName = selection[i].name
		newHitbox.name = (parentName + box_suffix)
		newHitbox.transform = selection[i].transform
			
		parentPos = selection[i].transform[4]
			
		if selection[i].children[1] != undefined then -- test for existance of child node
		(
			hasChild = true
			childPos = selection[i].children[1].transform[4] -- Im only taking the first child 
		)		
		else -- there is no child node, this is a leaf, usually the head.
		(
			hasChild = false
		)
		
		newHitbox.parent = selection[i]
		
		if hasChild == true then
		(			
			vectToChild = childPos - ParentPos -- vector to the child from the parent.
			normVectToChild = normalize(vectToChild)
			invParentTrans = inverse selection[i].transform
			invParentTrans[4] = [0,0,0]  -- strip out any movement, only want rotation
			x =  normVectToChild * invParentTrans -- transform into local space. 
			newHitbox.transform = matrixFromNormal x * newHitbox.transform -- orient the hitbox along this vector
			
			-- When there is a child node the box height is derived from that distance, width and length are derived from distance / magicLimbWidth
			newHitbox.height = distance parentPos childPos
			
			-- Possibly a better way to do this would be to get all the lengths and then do some guesswork based on analysis of all their lengths. 
			-- Initially I was extracting length and with from the parent nodes bounding box, but this would only work on rigs where the skeleton has been adjusted aproximate the size of the rigged mesh.
			newHitbox.length = (distance parentPos childPos) / magicLimbWidth
			newHitbox.width = (distance parentPos childPos) / magicLimbWidth			
		)
		else -- has no child
		(	
			-- This expects the rig to be pointing local X from parent to child. This section will generate incorrect hitBox's for leaf nodes on rigs that do not use local X to child
			in coordsys local rotate newHitbox (angleaxis 90 [0,1,0])
			
			--This will generate a hitbox the shape of the leaf nodes X extents bounding box,
			bounds = nodeGetBoundingBox selection[i] selection[i].transform
			newHitbox.height = abs(bounds[1][1] - bounds[2][1])
			newHitbox.length = newHitbox.height / magicLimbWidth
			newHitbox.width = newHitbox.height / magicLimbWidth				
		)
		
		-- Currently uses bsp material. Possibly add HitBox material in future
		newHitbox.material = currentMaterialLibrary["bsp_material"]
		newHitbox.wirecolor = color 255 192 0 -- orange		
	)

	if parentName == "" then
	(
		messagebox "No nodes were selected to add BigWorld HitBox's to. \nPlease select the nodes you would like to add hitBoxes and try again."
	)
	else
	(
		messagebox "Adjust HitBox parameters as desired. \nHitBox's must remain attached to the rigs node or they will be ignored on export. \nThe HitBox suffix \"_bwhitbox\" should not be modified. \nUse the \"Export HitBox to XML\" macroscript to generate your skeleton collider."		
	)
)
