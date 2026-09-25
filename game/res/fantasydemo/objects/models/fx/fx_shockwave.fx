#include "stdinclude.fxh"

// Auto variables
float4x4 worldViewProj : WorldViewProjection;
float4x4 worldView : WorldView;
float fogStart : FogStart = 0.0;
float fogEnd : FogEnd = 1.0;
float4 fogColour : FogColour = {0,0,0,0};

// Exposed artist editable variables.
texture diffuseMap 
< 
bool artistEditable = true; 
 
>;

texture otherMap
<
bool artistEditable = true;
 
>;

float3 uTransform
<
bool artistEditable = true;
 
> = {1,0,0};

float3 vTransform
<
bool artistEditable = true;
 
> = {0,1,0};

float selfIllumination
< 
bool artistEditable = true; 
 
float UIMin = 0;
float UIMax = 1;
int UIDigits = 1;
> = 0.0;

float4 colour
<
bool artistEditable = true;
 
> = {0.1,0.5,0.0,1};

float time : Time;
bool staticLighting : StaticLighting = false;

struct OutputShockWave
{
	float4 pos:     	POSITION;
	float2 tc:			TEXCOORD0;
	float2 tc2:     	TEXCOORD1;
	float4 sunlight: 	COLOR;
	float4 diffuse: 	COLOR1;
	float  fog: 		FOG;
};


OutputShockWave vs_main( VertexXYZNUV input )
{
	OutputShockWave o = (OutputShockWave)0;

	o.pos = mul(input.pos, worldViewProj);
	o.tc = input.tc;
	float3 tc = float3(input.tc, 1);


	float3x3 normalisedWorldView;
	normalisedWorldView[0] = normalize(worldView[0].xyz);
	normalisedWorldView[1] = normalize(worldView[1].xyz);
	normalisedWorldView[2] = normalize(worldView[2].xyz);
	

	//transform normal to the coordinate system we want
	float4 ut = float4(mul( normalisedWorldView, uTransform).xyz, 1) * 0.5;
	float4 vt = float4(mul( normalisedWorldView, -vTransform).xyz, 1) * 0.5;
	
	// output to second texture coordinate
	o.tc2.x = dot( ut, float4(input.normal,1) );
	o.tc2.y = dot( vt, float4(input.normal,1) );

	float4 diffuse = g_sunLight.m_ambient + selfIllumination;	
	o.sunlight = diffuse;

	float2 fogging = float2((-1.0 / (fogEnd - fogStart)), (fogEnd / (fogEnd - fogStart)));
	o.fog = o.pos.w * fogging.x + fogging.y;

	return o;
}


sampler diffuseSampler = sampler_state
{
	Texture = (diffuseMap);
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
	ADDRESSW = WRAP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

sampler otherSampler = sampler_state
{
	Texture = (otherMap);
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
	ADDRESSW = WRAP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

float4 ps_main( OutputShockWave input ) : COLOR0
{
	//  Output constant color:
	float4 diffuseMap = tex2D( diffuseSampler, input.tc );
	float4 otherMap = tex2D( otherSampler, input.tc2 );
	return colour * diffuseMap * input.sunlight + colour * otherMap * diffuseMap.a;
}


//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique standard
<
	string channel = "shimmer";
>
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;
		FOGENABLE = TRUE;
		FOGSTART = 1.0;
		FOGEND = 0.0;
		FOGCOLOR = float4(0,0,0,0);
		FOGTABLEMODE = NONE;
		FOGVERTEXMODE = LINEAR;
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = ONE;
		DESTBLEND = ONE;
		COLORWRITEENABLE = RED | GREEN | BLUE | ALPHA;
		POINTSPRITEENABLE = FALSE;
		STENCILENABLE = FALSE;
		CULLMODE = NONE;
		
		VertexShader = compile vs_1_1 vs_main();
		PixelShader = compile ps_1_1 ps_main();
	}
}


