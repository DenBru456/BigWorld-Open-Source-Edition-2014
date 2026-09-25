macroScript Object_Divider
	category:"BigWorld"
	toolTip:"Object Divider"
	Icon:#("bigworld_icons", 12)
	
(
	-- BigWorld Object_Divider
	-- 
	-- Version: 1.0
	-- Date: 2011
	-- Author: Adam Maxwell
	-- Website: http://www.bigworldtech.com
	-- Tested with: MAX 2011 
	--
	-- Description
	-- Cuts up an object pieces defined in max size. 
	-- Puts each object on a new layer, ready for the prefab assembler script
	--
	-- Known Bugs
	-- If you try to divide a cube, sometimes the polyop.slice function will slice perfectly along a face and result in the face disapearing. This rarely happens with game assets that I have tested and can be fixed by small changes in the size sliders
	
	include "BigWorld_Common.ms"
	
	global MODEL_LAYER_SUFFIX = "_bw_model_layer"
		
	global obj
	rollout BigWorldObjectDivider "BigWorld Object Divider" width:310
	(		
		fn editPolyFilter obj = --check is edit poly
		(
			classof obj==Editable_Poly
		)
		
		fn roundUp objSize maxDivisionSize =
		(
			div = objSize/maxDivisionSize
			divRoundUp = ceil(div)		
			return divRoundUp
		)
		
		label label1 "This macro will divide an object,"
		label label2 "so that it is less than the maximum export size"
		pickbutton pickObj "Pick Editable Poly!" width:240 filter:editPolyFilter
		group "Maximum object size after division (meters)"
		(
			spinner spin_maxXsize "Maximum X size:" type:#integer range:[50,1200,70]
			spinner spin_maxYsize "Maximum Y size:" type:#integer range:[50,1200,70]
			spinner spin_maxZsize "Maximum Z size:" type:#integer range:[50,2400,70]
			label label3 "Object size restricted to chunk size"
			label label4 "Recommended max setting is 70m for default 100m chunks"
		)		
		
		checkbox cb_placeOnLayers "Place divided objects on separate layers (recommended)" checked:true offset:[0,0]
		label label5 "Automatically places models on specially named layers" align:#left
		label label6 "for the Prefab Assembler script" align:#left
		checkbox cb_hideOriginal "Hide original object (recommended)" checked:true offset:[0,0]
		button beginDivide "Divide" width:240 height:40 enabled:false
		
		progressbar division_prog
				
		on pickObj picked x do -- Is edit poly?
		(
			obj=x
			pickObj.text=obj.name
			beginDivide.enabled=true
		)
		
		on BigWorldObjectDivider open do -- find first edit poly in selection for division
		(			
			for i in selection do 
			(
				if classof i==Editable_Poly then 
				(
					pickObj.text=i.name
					obj=i
					beginDivide.enabled=true
					exit
				)
			)
		)
		
		on beginDivide pressed do
		(
			-- Read spinners
			maxXsize=spin_maxXsize.value -- user is inputing max size in meters regardless of current unit setting
			maxYsize=spin_maxYsize.value
			maxZsize=spin_maxZsize.value
			
			-- Takes the maximum size of each dimension. Divides the object by that size and rounds it up by 1 to give number of times obj needs to be divided along that dimension
			objSize = obj.max-obj.min -- in current units
			objSizeM = convertToMeters objSize -- in meters
			maxXsizeRounded = roundUp objSizeM.x maxXsize -- round up the number to ensure that objects are divided enough to not exceed maximum object size.
			maxYsizeRounded = roundUp objSizeM.y maxYsize
			maxZsizeRounded = roundUp objSizeM.z maxZsize
			
			xval=objSize.x/maxXsizeRounded			
			zval=objSize.z/maxZsizeRounded			
			yval=objSize.y/maxYsizeRounded
			
			division_prog.value = 0
			
			-- hide original object if checkbox is selected
			if cb_hideOriginal.state then hide obj -- hide the original object
			
			-- some variables
			zobj=#()
			yobj=#()
			xobj=#()
			
			-- Divide Z			
			for i=1 to maxZsizeRounded do
			(
				division_prog.value = 33.*i/maxZsizeRounded
				local tmp=copy obj -- copy the object 
				polyop.slice tmp tmp.faces (ray [obj.pos.x,obj.pos.y,obj.min.z+zval*(i-1)] [0,0,1])	 -- slice bottom of new section
				polyop.slice tmp tmp.faces (ray [obj.pos.x,obj.pos.y,obj.min.z+zval*i] [0,0,1])	 -- slice top of new section
				fces=for i in tmp.faces collect i.index	 -- collect ALL the faces into an array
				discardFaces=#() -- deleteFaces empty array
				for f in fces do if (polyop.getfacecenter tmp f).z<(obj.min.z+(zval*(i-1))) then append discardFaces f	 -- if face centre is below slice put in discardFaces array				
				for f in fces do if (polyop.getfacecenter tmp f).z>(obj.min.z+(zval*i)) then append discardFaces f	 -- if face centre is above slice put in discardFaces array
				if discardFaces.count>0 then polyop.deletefaces tmp (discardFaces as bitarray) delisoverts:true	-- Delete the faces and stray verts
				append zobj tmp				
			)	
			-- Divide Y
			counter = 0
			for z in zobj do -- must be done for each Z cut object as they may exceed the Y division
			(
				counter += 1
				for i=1 to maxYsizeRounded do
				(
					local tmp=copy z
					polyop.slice tmp tmp.faces (ray [obj.pos.x,obj.min.y+yval*(i-1),obj.pos.z] [0,1,0])
					polyop.slice tmp tmp.faces (ray [obj.pos.x,obj.min.y+yval*i,obj.pos.z] [0,1,0])
					fces=for i in tmp.faces collect i.index
					discardFaces=#()
					for f in fces do if (polyop.getfacecenter tmp f).y<(obj.min.y+(yval*(i-1))) then append discardFaces f					
					for f in fces do if (polyop.getfacecenter tmp f).y>(obj.min.y+(yval*i)) then append discardFaces f					
					if discardFaces.count>0 then polyop.deletefaces tmp (discardFaces as bitarray) delisoverts:true
					append yobj tmp					
				)
				division_prog.value = (33 + 33.*counter/zobj.count)
			)			
			-- X Divide
			counter = 0
			for y in yobj do
			(
				counter += 1
				for i=1 to maxXsizeRounded do
				(
					local tmp=copy y
					polyop.slice tmp tmp.faces (ray [obj.min.x+xval*(i-1),obj.pos.y,obj.pos.z] [1,0,0])
					polyop.slice tmp tmp.faces (ray [obj.min.x+xval*i,obj.pos.y,obj.pos.z] [1,0,0])
					fces=for i in tmp.faces collect i.index
					discardFaces=#()
					for f in fces do if (polyop.getfacecenter tmp f).x<(obj.min.x+(xval*(i-1))) then append discardFaces f
					for f in fces do if (polyop.getfacecenter tmp f).x>(obj.min.x+(xval*i)) then append discardFaces f
					if discardFaces.count>0 then polyop.deletefaces tmp (discardFaces as bitarray) delisoverts:true
					append xobj tmp
				)
				division_prog.value = (66 +33.*counter/yobj.count)
			)		
			
			-- remove the temporary slices 
			delete zobj
			delete yobj
			select xobj	-- select new objects			
			
			if cb_placeOnLayers.state do
			(
				for obj in selection do
				(	
					newLayerName = obj.name + MODEL_LAYER_SUFFIX
					n = LayerManager.newLayerFromName newLayerName
					n.addnode obj
				)
			)
			division_prog.value = 100
			
			messagebox "Object division complete"
			destroydialog BigWorldObjectDivider
		)		
	)
	createdialog BigWorldObjectDivider
)