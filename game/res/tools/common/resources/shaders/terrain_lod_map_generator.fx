#include "terrain_common.fxh"

//-- blend map and 4 layers.
USE_TERRAIN_BLEND_TEXTURE
TERRAIN_TEXTURE( layer0 )
TERRAIN_TEXTURE( layer1 )
TERRAIN_TEXTURE( layer2 )
TERRAIN_TEXTURE( layer3 )

//--------------------------------------------------------------------------------------------------
struct TerrrainVS_out
{
	float4 pos			: POSITION;
	float4 layer01UV	: TEXCOORD0; //-- layer0.uv = xy, layer1.uv = zw
	float4 layer23UV	: TEXCOORD1; //-- layer2.uv = xy, layer3.uv = zw
	float2 blendUV		: TEXCOORD2; //-- blend.uv = zw
};

//--
bool	useMultipassBlending	= false;
float4	layerMask				= float4(1,1,1,1);

//--------------------------------------------------------------------------------------------------
TerrrainVS_out vs_main(const TerrainVertex i)
{
	TerrrainVS_out o = (TerrrainVS_out)0;
	
	// Calculate the position of the vertex
	float3 wPos = terrainVertexPosition(i).xyz;
	o.pos		= mul(float4(wPos, 1.0f), g_viewProjMat);

	//-- calculate the texture coordinate for the blend map.
	o.blendUV = inclusiveTextureCoordinate(i.xz, float2(blendMapSize, blendMapSize));

	//-- calculate the texture coordinates for our texture layers
	o.layer01UV.xy = float2(0.5f, 0.5f) + float2(+1, -1) * float2(dot(layer0UProjection, wPos), dot(layer0VProjection, wPos));
	o.layer01UV.zw = float2(0.5f, 0.5f) + float2(+1, -1) * float2(dot(layer1UProjection, wPos), dot(layer1VProjection, wPos));
	o.layer23UV.xy = float2(0.5f, 0.5f) + float2(+1, -1) * float2(dot(layer2UProjection, wPos), dot(layer2VProjection, wPos));
	o.layer23UV.zw = float2(0.5f, 0.5f) + float2(+1, -1) * float2(dot(layer3UProjection, wPos), dot(layer3VProjection, wPos));

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main(const TerrrainVS_out i) : COLOR
{
	half4 oColor = half4(0,0,0,0);

	//-- retrieve blend mask.
	half4 blendMask = tex2D(blendMapSampler, i.blendUV) * layerMask;

	//-- calculate final diffuse color.
	oColor += tex2D(layer0Sampler, i.layer01UV.xy) * blendMask.x;
	oColor += tex2D(layer1Sampler, i.layer01UV.zw) * blendMask.y;
	oColor += tex2D(layer2Sampler, i.layer23UV.xy) * blendMask.z;
	oColor += tex2D(layer3Sampler, i.layer23UV.zw) * blendMask.w;

	return oColor;
};

//--------------------------------------------------------------------------------------------------
technique LOD_MAP_GENERATION
{
	pass Pass0
	{
        ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= ONE;
        DESTBLEND			= (useMultipassBlending ? BW_BLEND_ONE : BW_BLEND_ZERO);
        ZWRITEENABLE		= (useMultipassBlending ? 0 : 1);
        ZFUNC				= (useMultipassBlending ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;
		FOGENABLE			= FALSE;
        
        VertexShader = compile vs_2_0 vs_main();
		PixelShader  = compile ps_2_0 ps_main();
	}
}