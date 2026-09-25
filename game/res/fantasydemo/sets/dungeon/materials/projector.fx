#include "stdinclude.fxh"

// Auto variables
float4x4 worldViewProj : WorldViewProjection;
#ifdef IN_GAME
float fogStart : FogStart = 0.0;
float fogEnd : FogEnd = 1.0;
float4 fogColour : FogColour = {0,0,0,0};
#endif

// Exposed artist editable variables.
texture diffuseMap 
< 
string UIName = "Diffuse Map";
bool artistEditable = true; 
 
>;

texture otherMap
<
string UIName = "Reflection Map";
bool artistEditable = true;
 
>;

texture otherMap2
<
string UIName = "Reflection Map2";
bool artistEditable = true;
 
>;

float4 uTransform
<
string UIWidget = "Spinner";
string UIName = "U Transform";
float UIMax = 100;
float UIMin = -100;
bool artistEditable = true;
 
> = {1,0,0,0};

float4 vTransform
<
string UIWidget = "Spinner";
float UIMax = 100;
float UIMin = -100;
string UIName = "V Transform";
bool artistEditable = true;
 
> = {0,1,0,0};

float4 uTransform2
<
string UIWidget = "Spinner";
string UIName = "U Transform2";
float UIMax = 100;
float UIMin = -100;
bool artistEditable = true;
 
> = {1,0,0,0};

float4 vTransform2
<
string UIWidget = "Spinner";
float UIMax = 100;
float UIMin = -100;
string UIName = "V Transform2";
bool artistEditable = true;
 
> = {0,1,0,0};

float selfIllumination
< 
string UIName = "Self Illumination";
bool artistEditable = true; 
 
float UIMin = 0;
float UIMax = 1;
int UIDigits = 1;
> = 0.0;

BW_ARTIST_EDITABLE_ALPHA_TEST
BW_NON_EDITABLE_ADDITIVE_BLEND
BW_ARTIST_EDITABLE_ADDRESS_MODE(BW_WRAP)

float time : Time;

#ifdef IN_GAME

bool staticLighting : StaticLighting = false;

struct OutputVertex
{
	float4 pos:     POSITION;
	float2 tc:      TEXCOORD0;
	float2 tc2:     TEXCOORD1;
	float2 tc3:     TEXCOORD2;
	float4 diffuse: COLOR;
	float  fog: FOG;
};

OutputVertex vs_main( VertexXYZNUV input )
{
	OutputVertex o = (OutputVertex)0;

	o.pos = mul(input.pos, worldViewProj);
	o.tc = input.tc;
	float4 tc = float4(input.tc, 1, 1);
	o.tc2.x = dot( tc, uTransform * float4(1,1,time,1) );
	o.tc2.y = dot( tc, vTransform * float4(1,1,time,1) );
	o.tc3.x = dot( tc, uTransform2 * float4(1,1,time,1) );
	o.tc3.y = dot( tc, vTransform2 * float4(1,1,time,1) );
	
	float4 diffuse = g_sunLight.m_ambient + selfIllumination;
	
	o.diffuse = diffuse;
	float2 fogging = float2((-1.0 / (fogEnd - fogStart)), (fogEnd / (fogEnd - fogStart)));
	o.fog = o.pos.w * fogging.x + fogging.y;

	return o;
}


//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique standard
<
	string channel = "sorted";
>
{
	pass Pass_0
	{
		BW_BLENDING_ADD
		BW_FOG_ADD
		BW_TEXTURESTAGE_DIFFUSEONLY(0, diffuseMap)
		BW_TEXTURESTAGE_ADDTEXTUREMULALPHA(1, otherMap)
		BW_TEXTURESTAGE_ADDTEXTUREMULALPHA(2, otherMap2)
		BW_TEXTURESTAGE_TERMINATE(3)
		COLOROP[1] = MODULATE;
		COLORARG1[1] = TEXTURE;
		COLORARG2[1] = CURRENT;
		COLOROP[2] = MODULATE;
		COLORARG1[2] = TEXTURE;
		COLORARG2[2] = CURRENT;
		CULLMODE = NONE;
		
		VertexShader = compile vs_1_1 vs_main();
		PixelShader = NULL;
	}
}

#else

// 3d studio max lighting values
float4 lightDir : Direction 
<
string UIName = "Light Direction";
string Object = "TargetLight";
int RefID = 0;
> = {-0.577, -0.577, 0.577,1.0};

float4 lightColour : LightColor 
<
int LightRef = 0;
> = float4( 1.0f, 1.0f, 1.0f, 1.0f );    // diffuse

OutputVertex vs_main( VertexXYZNUV input )
{
	OutputVertex o = (OutputVertex)0;

	o.pos = mul(input.pos, worldViewProj);
	o.tc = input.tc;

	float4 tc = float4(input.tc, 1, 1);
	o.tc2.x = dot( tc, uTransform * float4(1,1,time,1) );
	o.tc2.y = dot( tc, vTransform * float4(1,1,time,1) );
	
	float4 diffuse = float4(0.1, 0.1, 0.1, 1) + selfIllumination;
	
	DirectionalLight dLight;
	dLight.colour = lightColour;
	dLight.direction = lightDir.xyz;
	diffuse.xyz += directionalLight( input.normal, dLight );
	
	o.diffuse = diffuse;
	return o;
}

//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique standard
{
	pass Pass_0
	{
		BW_BLENDING_ADD
		BW_TEXTURESTAGE_DIFFUSEONLY(0, diffuseMap)
		BW_TEXTURESTAGE_ADDTEXTUREMULALPHA(1, otherMap)
		BW_TEXTURESTAGE_ADDTEXTUREMULALPHA(2, otherMap2)
		BW_TEXTURESTAGE_TERMINATE(3)
		COLOROP[1] = MODULATE;
		COLORARG1[1] = TEXTURE;
		COLORARG2[1] = CURRENT;
		COLOROP[2] = MODULATE;
		COLORARG1[2] = TEXTURE;
		COLORARG2[2] = CURRENT;
		CULLMODE = NONE;
		
		VertexShader = compile vs_1_1 vs_main();
		PixelShader = NULL;
	}
}

// This value is there so that the bool check boxes work properly.
string ParamID = "0x0001";
#endif