#include "terrain_common.fxh"

#define TERRAIN_OVERLAY_MODE_DEFAULT 0
#define TERRAIN_OVERLAY_MODE_COLORIZE_GROUND_STRENGTH 1
#define TERRAIN_OVERLAY_MODE_TEXTURE_OVERLAY 2
#define TERRAIN_OVERLAY_MODE_GROUND_TYPES_MAP 3

// Layer blend map
USE_TERRAIN_BLEND_TEXTURE

// The mask used to set which layers are in use
float4 layerMask = float4(1, 1, 1, 1);

// Need this for blending setup (TODO - remove?)
BW_NON_EDITABLE_ALPHA_TEST

// Common constants
int overlayMode = TERRAIN_OVERLAY_MODE_DEFAULT;
float4 overlayBounds; // (minX, minZ, sizeX, sizeZ)
float overlayAlpha;

// Constants for TERRAIN_OVERLAY_MODE_COLORIZE_GROUND_STRENGTH mode
float4 layer0OverlayColor;
float4 layer1OverlayColor;
float4 layer2OverlayColor;
float4 layer3OverlayColor;

// Constants for TERRAIN_OVERLAY_MODE_TEXTURE_OVERLAY mode
float4 overlayColor;
texture texOverlay;
sampler smpOverlay = sampler_state
{
	texture = <texOverlay>;
	MIPFILTER = POINT;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
	MIPMAPLODBIAS = -32;
};

// The output from the vertex shader.

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
struct TerrainVertexOutput
{
	float4 pos		: POSITION;
	float4 wPos		: TEXCOORD0;
	float3 blendUV	: TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
TerrainVertexOutput vs_deferred_3_0(const TerrainVertex i)
{
	TerrainVertexOutput o = (TerrainVertexOutput)0;
	
	//-- calculate the position of the vertex.
	o.wPos = terrainVertexPosition(i);
	o.pos  = mul(o.wPos, g_viewProjMat);
	
	//-- calculate the texture coordinate for the blend map.
	o.blendUV.xy = inclusiveTextureCoordinate(i.xz, float2(blendMapSize, blendMapSize));

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(const TerrainVertexOutput i)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	float4 blend = tex2D(blendMapSampler, i.blendUV);
	blend *= layerMask;

	float4 oColor = float4(0,0,0,0);
	
	if (overlayMode == TERRAIN_OVERLAY_MODE_TEXTURE_OVERLAY)
	{
		float2 texCoord = (i.wPos.xz - overlayBounds.xy) / overlayBounds.zw;
		texCoord.y = 1.0 - texCoord.y;

		float4 ret = tex2D(smpOverlay, texCoord);
		ret.rgb = overlayColor.rgb;
		ret.a *= overlayAlpha;

		oColor = ret;
	}
	else if (overlayMode == TERRAIN_OVERLAY_MODE_COLORIZE_GROUND_STRENGTH)
	{
		float4 ret;
		if (blend.x > blend.y && blend.x > blend.z && blend.x > blend.w)
			ret = layer0OverlayColor;
		else if (blend.y > blend.z && blend.y > blend.w)
			ret = layer1OverlayColor;
		else if (blend.z > blend.w)
			ret = layer2OverlayColor;
		else
			ret = layer3OverlayColor;

		ret.a *= overlayAlpha;

		oColor = ret;
	}
	else if (overlayMode == TERRAIN_OVERLAY_MODE_GROUND_TYPES_MAP)
	{
		float2 texCoord = (i.wPos.xz - overlayBounds.xy) / overlayBounds.zw;
		float4 ret = tex2D(smpOverlay, texCoord);
		ret.a = overlayAlpha;
		
		oColor = ret;
	}
	
	g_buffer_writeAlbedo(o, oColor.xyz);
	
	//-- correct blending.
	o.color0.a = oColor.a;
	o.color1.a = oColor.a;
	o.color2.a = oColor.a;

	return o;
}

//--------------------------------------------------------------------------------------------------
technique DS
{
	pass P0
	{
		ALPHABLENDENABLE 	= TRUE;
		SRCBLEND 			= SRCALPHA;
		DESTBLEND 			= INVSRCALPHA;
		ALPHATESTENABLE 	= FALSE;
		ZENABLE 			= TRUE;
		ZWRITEENABLE 		= FALSE;
		ZFUNC 				= LESSEQUAL;
		CULLMODE 			= BW_CULL_CCW;
        
		//-- render target mask.
		//-- Note: these mask should be in sync with the g-buffer layout.
		COLORWRITEENABLE  = 0x00;
		COLORWRITEENABLE1 = 0x00;
		COLORWRITEENABLE2 = 0x07;
		
		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = compile ps_3_0 ps_deferred_3_0();
	}
}

#else

//--------------------------------------------------------------------------------------------------
struct TerrainVertexOutput
{
	float4 pos		: POSITION;
	float4 wPos		: TEXCOORD0;
	float2 blendUV	: TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
TerrainVertexOutput vs_main_2_0(const TerrainVertex i)
{
	TerrainVertexOutput o = (TerrainVertexOutput)0;

	//-- calculate the position of the vertex.
	o.wPos = terrainVertexPosition(i);
	o.pos  = mul(o.wPos, g_viewProjMat);
	
	//-- calculate the texture coordinate for the blend map.
	o.blendUV = inclusiveTextureCoordinate(i.xz, float2(blendMapSize, blendMapSize));

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(const TerrainVertexOutput i) : COLOR
{
	float4 blend = tex2D(blendMapSampler, i.blendUV);
	blend *= layerMask;

	float4 oColor = float4(0,0,0,0);
	
	if (overlayMode == TERRAIN_OVERLAY_MODE_TEXTURE_OVERLAY)
	{
		float2 texCoord = (i.wPos.xz - overlayBounds.xy) / overlayBounds.zw;
		texCoord.y = 1.0 - texCoord.y;

		float4 ret = tex2D(smpOverlay, texCoord);
		ret.rgb = overlayColor.rgb;
		ret.a *= overlayAlpha;

		oColor = ret;
	}
	else if (overlayMode == TERRAIN_OVERLAY_MODE_COLORIZE_GROUND_STRENGTH)
	{
		float4 ret;
		if (blend.x > blend.y && blend.x > blend.z && blend.x > blend.w)
			ret = layer0OverlayColor;
		else if (blend.y > blend.z && blend.y > blend.w)
			ret = layer1OverlayColor;
		else if (blend.z > blend.w)
			ret = layer2OverlayColor;
		else
			ret = layer3OverlayColor;

		ret.a *= overlayAlpha;

		oColor = ret;
	}
	else if (overlayMode == TERRAIN_OVERLAY_MODE_GROUND_TYPES_MAP)
	{
		float2 texCoord = (i.wPos.xz - overlayBounds.xy) / overlayBounds.zw;
		float4 ret = tex2D(smpOverlay, texCoord);
		ret.a = overlayAlpha;
		
		oColor = ret;
	}

	return oColor;
}

//--------------------------------------------------------------------------------------------------
technique FS
{
	pass P0
	{
		ALPHABLENDENABLE 	= TRUE;
		SRCBLEND 			= SRCALPHA;
		DESTBLEND 			= INVSRCALPHA;
		ALPHATESTENABLE 	= FALSE;
		ZENABLE 			= TRUE;
		ZWRITEENABLE 		= FALSE;
		ZFUNC 				= LESSEQUAL;
		CULLMODE 			= BW_CULL_CCW;
        
		//-- render target mask.
		COLORWRITEENABLE  = 0x07;
		
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}

#endif //-- BW_DEFERRED_SHADING
