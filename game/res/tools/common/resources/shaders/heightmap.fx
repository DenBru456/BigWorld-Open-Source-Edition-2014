#include "stdinclude.fxh"

float4x4    worldViewProjection;

texture     handDrawnMap;
texture     heightMap;
float       alpha           = 1.0;

struct VS_INPUT
{
    float4 pos		: POSITION;
    float2 tex      : TEXCOORD0;
    float2 tex2     : TEXCOORD1;
};

struct VS_OUTPUT
{
    float4 pos      : POSITION;
    float4 diffus   : COLOR;
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
    o.pos    = mul( v.pos, worldViewProjection );
    o.diffus = alpha;      
    o.tex    = v.tex;
    o.tex2   = v.tex2;
	return o;
};

//--------------------------------------------------------------//
// 
//--------------------------------------------------------------//
technique standard
{
	pass Pass_0
	{
		VertexShader = compile vs_1_1 vs_main();
		PixelShader  = NULL;  
		
        LIGHTING            = FALSE;               
        CLIPPING            = TRUE;
        CULLMODE            = NONE;
        ALPHATESTENABLE     = FALSE;
        ALPHABLENDENABLE    = FALSE;
        LIGHTING            = FALSE;               
        FOGENABLE           = FALSE; 
        
        COLOROP      [0]    = SELECTARG1;
        COLORARG1    [0]    = TEXTURE ;
        COLORARG2    [0]    = DIFFUSE ;
        ALPHAOP      [0]    = SELECTARG2 ;  
        ALPHAARG1    [0]    = TEXTURE ;
        ALPHAARG2    [0]    = DIFFUSE ; 
        Texture      [0]    = (heightMap);
        ADDRESSU     [0]    = CLAMP;
        ADDRESSV     [0]    = CLAMP;
        MINFILTER    [0]    = LINEAR;
        MAGFILTER    [0]    = LINEAR;
        TexCoordIndex[0]    = 1;
        
        COLOROP      [1]    = BLENDDIFFUSEALPHA;
        COLORARG1    [1]    = CURRENT ;
        COLORARG2    [1]    = TEXTURE ;
        ALPHAOP      [1]    = DISABLE ;      
        Texture      [1]    = (handDrawnMap);
        ADDRESSU     [1]    = CLAMP;
        ADDRESSV     [1]    = CLAMP;
        MINFILTER    [1]    = LINEAR;
        MAGFILTER    [1]    = LINEAR; 
        TexCoordIndex[1]    = 0;        
        
        BW_TEXTURESTAGE_TERMINATE(2)                 
	}
}
