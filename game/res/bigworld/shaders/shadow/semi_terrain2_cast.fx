#include "terrain_common.fxh"

//--------------------------------------------------------------------------------------------------
struct VS_CASTER_OUTPUT
{
	float4 pos	 : POSITION;
	float2 depth : TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
VS_CASTER_OUTPUT vs_main_2_0(const TerrainVertex i)
{
	VS_CASTER_OUTPUT o = (VS_CASTER_OUTPUT) 0;
	o.pos   = mul(terrainVertexPosition(i), g_viewProjMat);
	o.depth = o.pos.zw;
	return o;
};

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(const VS_CASTER_OUTPUT i) : COLOR
{
    float depth = i.depth.x / i.depth.y;
	// Crop-space bias: 0.0003 * 100000 m z-slab = 30 world metres,
	// the same tolerance vanilla had with 0.01 * 3000 m.
	float d = depth + 0.0003f;
    return float4(d, d, d, d);
}

//--------------------------------------------------------------------------------------------------
technique SHADOW_CAST
{
	pass Pass_0
	{
		COLORWRITEENABLE    = RED;
		ALPHATESTENABLE		= FALSE;
		ALPHABLENDENABLE	= FALSE;
		ZENABLE				= TRUE;									
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		FOGENABLE			= FALSE;
		CULLMODE			= CCW; 
				
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}