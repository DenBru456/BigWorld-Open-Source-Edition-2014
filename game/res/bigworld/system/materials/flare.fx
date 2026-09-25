texture diffuseMap 
< 
	bool artistEditable = true; 
	string UIName = "Diffuse Map";
	string UIDesc = "The diffuse map for the material";
>;

texture visibilityMap : FlareVisibilityMap;

technique EffectOverride
{
	pass Pass_0
	{
		TextureFactor = -1;
		StencilEnable = FALSE;
		PointSpriteEnable = FALSE;
		ZWriteEnable = FALSE;
		AlphaRef = 1;
		CullMode = CCW;
		SrcBlend = SRCALPHA;
		AlphaBlendEnable = TRUE;
		ColorWriteEnable = RED | GREEN | BLUE;
		DestBlend = ONE;
		AlphaTestEnable = TRUE;
		ZEnable = False;
		FogEnable = FALSE;
		ZFunc = NEVER;

		MipFilter[0] = LINEAR;
		MinFilter[0] = LINEAR;
		AlphaOp[0] = SELECTARG1;
		MagFilter[0] = LINEAR;
		ColorArg1[0] = CURRENT;
		ColorArg2[0] = TEXTURE;
		ColorOp[0] = MODULATE2X;
		AddressW[0] = WRAP;
		AddressV[0] = WRAP;
		Texture[0] = (diffuseMap);
		AddressU[0] = WRAP;
		AlphaArg1[0] = CURRENT;
		AlphaArg2[0] = TEXTURE;
		TexCoordIndex[0] = 0;

		MipFilter[1] = POINT;
		MinFilter[1] = POINT;
		MagFilter[1] = LINEAR;
		ColorOp[1] = SELECTARG1;
		ColorArg1[1] = CURRENT;
		ColorArg2[1] = TEXTURE;
		AlphaOp[1] = MODULATE;
		AlphaArg1[1] = CURRENT;
		AlphaArg2[1] = TEXTURE;
		AddressW[1] = CLAMP;
		AddressV[1] = CLAMP;
		Texture[1] = (visibilityMap);
		AddressU[1] = CLAMP;
		TexCoordIndex[1] = 1;

		AlphaOp[2] = DISABLE;
		ColorOp[2] = DISABLE;

		PixelShader = NULL;
	}
}

