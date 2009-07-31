utility IsoRender "Isometric Render" --aide a la creation de camera isometric
(
	Local Sel_RenderObjet
	Local SquarePath
    Local imageratio = 1.41 as float
	local Target01
	
	group "Camera" 
	(
		PickButton pckBut_RenderObj "Render Objet" align:#left width:140
		Button	BUT_CreatePath04 " 4 Sect square" align:#left width:140 enabled:false
		Spinner SP_RectSize "Path Size" range:[0,10000,50] enabled:false
		Spinner SP_TargetZPos "Look Height" range:[0,10000,0] enabled:false
		Button BUT_CameraCreate " Create Camera" align:#left width:140 enabled:false
	)
	
	Group "Animation"
	(
		Button But_SetAnimRange "Set Animation Range" Align:#left width:140 Enabled:false
	)

	Group "Render"
	(
		
	)
	
	Group "About"
	(
		label creation "Créer par David Bordleau"
		Button But_About "about"
	)
	
	--Fin UI Creation//////////////////////////////////////
	
	
	--UI Group CAMERA
	on pckBut_RenderObj picked Sel_RenderObjet do
	(
		pckBut_RenderObj.text = Sel_RenderObjet.name
	    BUT_CreatePath04.enabled = true
		SP_RectSize.enabled = true
		SP_TargetZPos.enabled = true
	)
		
	on BUT_CreatePath04 pressed  do
	(
		SquarePath = rectangle pos:[0,0,SP_RectSize.value] width:150  length:150 name:"Camera_Path"
		But_CameraCreate.enabled = true
	)


	on But_CameraCreate pressed do
	(
		RenderCamera = targetCamera()
		Target01 = TargetObject pos:[0,0,0]
		RenderCamera.target = Target01
		RenderCamera.pos.controller = Path_Constraint()
		RenderCamera.pos.controller.path = SquarePath
	)
	on SP_RectSize changed val do
	(
		SquarePath.length = val
		SquarePath.Width = val	
		SquarePath.pos.z = val* imageratio
	)
	
	on SP_TargetZPos changed val do
	(
		$Target01.pos.z = val
	)
	
	--UI GROUP ANIMATION
	--UI GROUP RENDER
	--UI GROUP ABOUT
	On But_About pressed do
	(
	messagebox " Ce script est à but instructif seulement \n pour ton besoin conctacter moi Dbordelau@gmail.com" title: "Info "
		)
)