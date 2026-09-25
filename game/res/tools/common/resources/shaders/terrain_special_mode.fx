#include "stdinclude.fxh"
#include "terrain_common.fxh"

// -----------------------------------------------------------------------------
// Constants needed to transform the vertices
// -----------------------------------------------------------------------------

USE_TERRAIN_BLEND_TEXTURE
float4 layer0ReplacementColor;
float4 layer1ReplacementColor;
float4 layer2ReplacementColor;
float4 layer3ReplacementColor;

// The mask used to set which layers are in use
float	overlayAlpha			= 0.5f;
bool	useMultipassBlending	= false;
float4	layerMask				= float4( 1, 1, 1, 1 );

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
struct TerrainVS_out
{
	float4 pos				: POSITION;
	float3 blendUVLinearZ	: TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
TerrainVS_out vs_deferred_3_0(const TerrainVertex i)
{
	TerrainVS_out o = (TerrainVS_out)0;

	//-- calculate the position of the vertex.
	float4 wPos = terrainVertexPosition(i);
	o.pos		= mul(wPos, g_viewProjMat);
	
	//-- calculate the texture coordinate for the blend map.
	o.blendUVLinearZ.xy = inclusiveTextureCoordinate(i.xz, float2(blendMapSize, blendMapSize));
	o.blendUVLinearZ.z  = o.pos.w;

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(const TerrainVS_out i)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	float4 blend = tex2D(blendMapSampler, i.blendUVLinearZ.xy);
	blend *= layerMask;

	float4 ret;
	if (blend.x > blend.y && blend.x > blend.z && blend.x > blend.w)
		ret = layer0ReplacementColor * blend.x;
	else if (blend.y > blend.z && blend.y > blend.w)
		ret = layer1ReplacementColor * blend.y;
	else if (blend.z > blend.w)
		ret = layer2ReplacementColor * blend.z;
	else
		ret = layer3ReplacementColor * blend.w;

	//-- fill GBuffer.
	g_buffer_writeDepth(o, i.blendUVLinearZ.z);
	g_buffer_writeObjectKind(o, G_OBJECT_KIND_TERRAIN);
	g_buffer_writeNormal(o, float3(0,1,0));
	g_buffer_writeAlbedo(o, ret.xyz * overlayAlpha);
	g_buffer_writeSpecAmount(o, 0.0f);
	g_buffer_writeUserData1(o, 0.0f);

	return o;
}

//--------------------------------------------------------------------------------------------------
technique DS
{
	pass Pass_0
	{
		//-- Turn on alpha blend and set dest blend to 1 if using multiple passes.
		ALPHATESTENABLE		= FALSE;
        ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= ONE;
        DESTBLEND			= (useMultipassBlending ? BW_BLEND_ONE : BW_BLEND_ZERO);
        ZWRITEENABLE		= (useMultipassBlending ? 0 : 1);
        ZFUNC				= (useMultipassBlending ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;

		//-- render target mask.
		//-- Note: these mask should be in sync with the g-buffer layout.
		COLORWRITEENABLE	= (useMultipassBlending ? 0x00 : 0xFF);
		COLORWRITEENABLE1	= (useMultipassBlending ? 0x03 : 0xFF);
		COLORWRITEENABLE2	= (useMultipassBlending ? 0x07 : 0xFF);
		
		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = compile ps_3_0 ps_deferred_3_0();
	}
}

#else

//--------------------------------------------------------------------------------------------------
struct TerrainVS_out
{
	float4 pos		: POSITION;
	float2 blendUV	: TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
TerrainVS_out vs_main_2_0(const TerrainVertex i)
{
	TerrainVS_out o = (TerrainVS_out)0;

	//-- calculate the position of the vertex.
	float4 wPos = terrainVertexPosition(i);
	o.pos		= mul(wPos, g_viewProjMat);
	
	//-- calculate the texture coordinate for the blend map.
	o.blendUV = inclusiveTextureCoordinate(i.xz, float2(blendMapSize, blendMapSize));

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(const TerrainVS_out i) : COLOR
{
	float4 blend = tex2D(blendMapSampler, i.blendUV);
	blend *= layerMask;

	float4 ret;
	if (blend.x > blend.y && blend.x > blend.z && blend.x > blend.w)
		ret = layer0ReplacementColor * blend.x;
	else if (blend.y > blend.z && blend.y > blend.w)
		ret = layer1ReplacementColor * blend.y;
	else if (blend.z > blend.w)
		ret = layer2ReplacementColor * blend.z;
	else
		ret = layer3ReplacementColor * blend.w;

	return ret * overlayAlpha;
}

//--------------------------------------------------------------------------------------------------
technique FS
{
	pass Pass_0
	{
        // Turn on alpha blend and set dest blend to 1 if using
        // multiple passes
        ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= ONE;
        DESTBLEND			= (useMultipassBlending ? BW_BLEND_ONE : BW_BLEND_ZERO);
        ALPHATESTENABLE		= FALSE;
        ZWRITEENABLE		= (useMultipassBlending ? 0 : 1);
        ZFUNC				= (useMultipassBlending ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;
        FOGENABLE			= FALSE;
		
		VertexShader = compile vs_3_0 vs_main_2_0();
		PixelShader  = compile ps_3_0 ps_main_2_0();
	}
}

#endif //-- BW_DEFERRED_SHADING