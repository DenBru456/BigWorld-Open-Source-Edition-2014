#include "patrol_path_common.fxh"

float4x4    worldViewProjection;
float       vOffset1;
float       vOffset2;

texture     patrolTexture;

sampler linkSampler = sampler_state
{
	Texture = (patrolTexture);
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = NONE;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

struct VS_INPUT
{
    float4 pos		: POSITION;
    float3 normal   : NORMAL;
    float2 tex1     : TEXCOORD0;
    float2 tex2     : TEXCOORD1;
};

struct VS_OUTPUT
{
    float4 pos		: POSITION;
    float2 tex1     : TEXCOORD0;
    float2 tex2     : TEXCOORD1;
};

VS_OUTPUT vs_main(const VS_INPUT v)
{
	VS_OUTPUT o = (VS_OUTPUT)0;
    o.pos    = mul(v.pos, worldViewProjection);
    o.tex1   = v.tex1;
    o.tex2   = v.tex2;
    o.tex1.y += vOffset1;
    o.tex2.y += vOffset2;
	return o;
};

float4 ps_main(const VS_OUTPUT v) : COLOR0
{
	float4 colour = tex2D( linkSampler, v.tex1 );
	colour *= tex2D( linkSampler, v.tex2 );
	if ( colourise )
	{
		colour.rgb *= 1.0f - colouriseBlend;
		colour.rgb += colouriseColour.rgb * colouriseBlend;
	}
	return colour;
};

technique standard
{
	pass Pass_0
	{
		VertexShader = compile vs_1_1 vs_main();
		PixelShader  = compile ps_2_0 ps_main();
		
        ALPHATESTENABLE = FALSE;
	    ALPHABLENDENABLE = TRUE;
	    SRCBLEND         = SRCALPHA;
	    DESTBLEND        = INVSRCALPHA;
        FOGENABLE        = FALSE    ;
        LIGHTING         = FALSE    ;
        ZENABLE          = TRUE     ;
        ZFUNC            = LESSEQUAL;
        ZWRITEENABLE     = TRUE     ;
        CULLMODE         = NONE     ;
        TextureFactor    = 0xffffffff;
	}
}

