#include "stdinclude.fxh"

float4x4 worldViewProjection;

struct VS_INPUT
{
    float4 pos		: POSITION;
    float4 colour   : COLOR;
};

struct VS_OUTPUT
{
    float4 pos		: POSITION;
    float4 colour   : COLOR;
};


//----------------------------------------------------------------------------
// Shader body 
//----------------------------------------------------------------------------

// This shader applies the wvp and passes the tex coords straight through
VS_OUTPUT vs_main(const VS_INPUT v)
{
	VS_OUTPUT o = (VS_OUTPUT) 0;
    o.pos    = mul( v.pos, worldViewProjection );        
    o.colour = v.colour;
	return o;
};

//--------------------------------------------------------------//
// 
//--------------------------------------------------------------//
technique standard
{
	pass Pass_0
	{
		VertexShader        = compile vs_1_1 vs_main();
		PixelShader         = NULL; 
		
        LIGHTING            = FALSE;
        CLIPPING            = TRUE;
        CULLMODE            = NONE;
        ALPHATESTENABLE     = FALSE;
        ALPHABLENDENABLE    = TRUE;
        DESTBLEND           = INVSRCALPHA;
        SRCBLEND            = SRCALPHA;
        LIGHTING            = FALSE;
        FOGENABLE           = FALSE;
        
        COLOROP  [0]        = SELECTARG1;
        COLORARG1[0]        = DIFFUSE;
        COLORARG2[0]        = DIFFUSE;
        ALPHAOP  [0]        = SELECTARG1;
        ALPHAARG1[0]        = DIFFUSE;
        
        BW_TEXTURESTAGE_TERMINATE(1)
	}
}

