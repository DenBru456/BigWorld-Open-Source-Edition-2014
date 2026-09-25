macroScript MungeNormals
	category:"BigWorld"
	toolTip:"Munge Normals"
	Icon:#("bigworld_icons", 9)

(
	-- BigWorld Munge Normals
	-- 
	-- Version: 2.0
	-- Date: 2010
	--
	-- Description:
	-- Causes the normals of a selected object (with an Edit Normals modifier) to be splayed away from the position of a chosen object
	--
	-- Info:
	-- Used mostly on custom trees and billboards to ensure that an even lighting is provided by daylight illuminations.
	
	messagebox "Select an object as the center for normal calculations"
	a = pickObject message: "Select an object as the center for normal calculations"
	if a != undefined then
	(
		center = a.transform.row4
		
		mySelection = #()
		for i in selection do
		(
			mySelection += i
		)
		for i in mySelection do
		(
			select i
			if i.modifiers[#edit_normals] != undefined then
			( 
				inv = inverse( i.transform )
				localcenter = center * inv
				tm = snapshotasmesh i
				a = i.Edit_Normals
				for j = 1 to a.getnumnormals() do
				(
					a.setnormalexplicit j explicit:true
				)
				nVerts = tm.numverts
				for j = 1 to nVerts do
				(
					position = getvert tm j
					normal = normalize( (position * inv ) - localcenter )
					trans = random (eulerangles -10 -10 -10) (eulerangles 10 10 10) as matrix3
					normal = normal * trans
					verts=#{j}
					normals=#{}
					a.convertVertexSelection &verts &normals
					for k = 1 to normals.count do
					(
						if normals[k] == true do
						(
							a.SetNormal k &normal node:i
						)
					)
				)
			)
			else
			(
				messagebox "No Edit Normals modifier detected."
			)
		)
		select mySelection
	)
)

-- macros.run "BigWorld" "MungeNormals"
