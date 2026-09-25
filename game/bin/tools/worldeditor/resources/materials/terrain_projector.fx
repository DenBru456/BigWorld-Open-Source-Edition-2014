#include "stdinclude.fxh"
#include "shaders/terrain/terrain_common.fxh"

// variables
texture diffuse;
bool alphaTestEnable = false;
int alphaReference = 0;
bool zEnable = true;

float4x4 projtextransform;

int wrap = BW_WRAP;	//D3DTADDRESS_WRAP
BW_NON_EDITABLE_ADDITIVE_BLEND

struct VS_OUTPUT
{
    float4 pos			: POSITION;
    float2 t0			: TEXCOORD0;
    float2 t1			: TEXCOORD1;
    float2 t2			: TEXCOORD2;
    float2 t3			: TEXCOORD3;
    float4 diffuse		: COLOR0;
    float4 blend		: COLOR1;
    float3 reflection	: TEXCOORD4;
    float3 view     	: TEXCOORD5;
    float fog			: FOG;
};


//----------------------------------------------------------------------------
// Shader body 
//----------------------------------------------------------------------------

//This shader sets up the standard diffuse pixel shader
VS_OUTPUT vs_main(const TerrainVertex v)
{
	VS_OUTPUT o = (VS_OUTPUT) 0;
	
	// get transformed terrain vertex
	float4 worldPos = terrainVertexPosition( v );
	
	// had to hard-code the planar terrain vertex without world xform here
	float4 texPos = float4( v.xz.x * terrainScale, 0, v.xz.y * terrainScale, 1 );
	
	// calc tex coords
	float2 tc;
	tc.x = dot( texPos, projtextransform[0] );
	tc.y = dot( texPos, projtextransform[2] );
	
	// output
	o.pos = mul( worldPos, viewProj );
	o.t0.xy = tc.xy;
	o.diffuse.xyzw = (1.0,1.0,1.0,1.0);
	return o;
};

sampler diffuseSampler = sampler_state
{
	Texture = (diffuse);
	ADDRESSU = (wrap);
	ADDRESSV = (wrap);
	ADDRESSW = (wrap);
	BORDERCOLOR = 0;
	MAGFILTER = LINEAR;
	MINFILTER = ANISOTROPIC;
	MIPFILTER = LINEAR;
	MAXANISOTROPY = 16;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};


float4 ps_main( const VS_OUTPUT input ) : COLOR0
{	
	float4 diffuse = tex2D( diffuseSampler, input.t0 );
	return diffuse;
};


technique shader_version
{
	pass Pass_0
	{
		BW_BLENDING_ADD
		FOGENABLE = FALSE;
		SPECULARENABLE = TRUE;
		CULLMODE = CCW;
		ZENABLE = (zEnable);
		
		VertexShader = compile vs_2_0 vs_main();
		PixelShader = compile ps_2_0 ps_main();
	}
}