#include "stdinclude.fxh"

float4x4    worldViewProjection;

texture     handDrawnMap;
texture     heightMap;

float       minHeight;
float       invScaleHeight;

float       alpha           = 1.0;

sampler handDrawnMapSampler = sampler_state
{
	Texture = (handDrawnMap);

	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;

	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
};

sampler heightMapSampler = sampler_state
{
	Texture = (heightMap);

	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;

	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
};

struct VS_INPUT
{
    float4 pos		: POSITION;
    float2 tex      : TEXCOORD0;
    float2 tex2     : TEXCOORD1;
};

struct VS_OUTPUT
{
    float4 pos      : POSITION;
    float2 tex      : TEXCOORD0;
    float2 tex2     : TEXCOORD1;
};


//----------------------------------------------------------------------------
// Shader body 
//----------------------------------------------------------------------------

// This shader applies the wvp and passes the tex coords straight through
VS_OUTPUT vs_main(const VS_INPUT v)
{
	VS_OUTPUT o = (VS_OUTPUT) 0;
    o.pos  = mul( v.pos, worldViewProjection );        
    o.tex  = v.tex;
    o.tex2 = v.tex2;
	return o;
};

// This shader scales the second texture into the range defined by
// [minHeight, 1.0/invScale + minHeight] and alpha blends with the
// first texture based on the value of alpha
float4 ps_main(const VS_OUTPUT i) : COLOR0
{   
	float4 handDrawnSample  = tex2D(handDrawnMapSampler, i.tex);
	float  heightSample     = tex2D(heightMapSampler, i.tex2).r;
	float  normHeight       = (heightSample - minHeight)*invScaleHeight;
	float4 heightColour     = float4(normHeight, normHeight, normHeight, 1);		
    return lerp(handDrawnSample, heightColour, alpha);
};

//--------------------------------------------------------------//
// 
//--------------------------------------------------------------//
technique standard
{
	pass Pass_0
	{
		VertexShader = compile vs_1_1 vs_main();
		PixelShader  = compile ps_2_0 ps_main();
		
        LIGHTING            = FALSE;               
        CLIPPING            = TRUE;
        CULLMODE            = CCW;
        ALPHATESTENABLE     = FALSE;
        ALPHABLENDENABLE    = FALSE;
        LIGHTING            = FALSE;               
        FOGENABLE           = FALSE;            
	}
}
