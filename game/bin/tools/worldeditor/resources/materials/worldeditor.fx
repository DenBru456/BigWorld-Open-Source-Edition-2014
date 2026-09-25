#include "stdinclude.fxh"

// Auto variables
texture diffuseMap < bool artistEditable = true;  >;

// Manual variables
float4  diffuseColour = (1,1,1,1);

sampler diffuseSampler = sampler_state
{
	Texture = (diffuseMap);
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
	ADDRESSW = CLAMP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

//--------------------------------------------------------------------------------------------------
struct OutputDiffuseLighting
{
	float4 pos		:	POSITION;
	float2 tc		:	TEXCOORD0;
#if DUAL_UV
	float2 tc2		:	TEXCOORD1;
#endif
	float3 normal	:	TEXCOORD2;
	float4 worldPos	:	TEXCOORD3;
	float  fog		:	FOG;
};

float4 ps_spaceMap( OutputDiffuseLighting input ) : COLOR0
{
	float4 colour;
	colour.xyz = tex2D( diffuseSampler, input.tc.xy );
	colour.w = 1;
	return colour;
}

float4 ps_spaceMapDebug( OutputDiffuseLighting input ) : COLOR0
{
	float4 colour;
	colour = input.worldPos;
	return colour;
}


OutputDiffuseLighting vs_editorChunkPortal( VertexXYZL input )
{
	OutputDiffuseLighting o = (OutputDiffuseLighting)0;

	o.pos = mul(input.pos, g_projMat);
	o.worldPos = input.diffuse;
	
	return o;
}

float4 ps_editorChunkPortal( OutputDiffuseLighting input ) : COLOR0
{
	float4 colour;
	colour = float4(input.worldPos.xyz, 1);
	return colour;
}



//--------------------------------------------------------------//
// Space Map Technique
//--------------------------------------------------------------//
technique spaceMap
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = ONE;
      DESTBLEND = ZERO;
      ZENABLE = FALSE;
      ZWRITEENABLE = FALSE;
      ZFUNC = LESSEQUAL;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = FALSE;
      COLORWRITEENABLE = RED | GREEN | BLUE | ALPHA;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;
      CULLMODE = NONE;

      VertexShader = NULL;
      PixelShader = compile ps_1_1 ps_spaceMap();
   }
}

technique spaceMapDebug
{
   pass Pass_0
   {
		ALPHATESTENABLE = FALSE;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;
		FOGENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		POINTSPRITEENABLE = FALSE;
		STENCILENABLE = FALSE;
		CULLMODE = NONE;		

		VertexShader = NULL;
		PixelShader = NULL;

		MipFilter[0] = LINEAR;
		MagFilter[0] = LINEAR;
		MinFilter[0] = LINEAR;

		ColorOp[0] = SELECTARG2;
		ColorArg1[0] = TFACTOR;
		ColorArg2[0] = DIFFUSE;

		AlphaOp[0] = SELECTARG2;
		AlphaArg1[0] = TFACTOR;
		AlphaArg2[0] = DIFFUSE;

		TexCoordIndex[0] = 0;

		AlphaOp[1] = DISABLE;
		ColorOp[1] = DISABLE;
   }
}

technique editorChunkPortal
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCCOLOR;
      DESTBLEND = ONE;
      ZENABLE = TRUE;
      ZWRITEENABLE = FALSE;
      ZFUNC = LESSEQUAL;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;
      CULLMODE = NONE;

      VertexShader = compile vs_1_1 vs_editorChunkPortal();
      PixelShader = compile ps_1_1 ps_editorChunkPortal();
   }

}

