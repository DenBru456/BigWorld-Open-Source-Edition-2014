#define DUAL_UV 1
#include "stdinclude.fxh"
#include "unskinned_effect_include.fxh"

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

#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
BW_DS_VS_DIFFUSE_OUT vs_deferred_3_0(VERTEX_FORMAT i)
{
	BW_DS_VS_DIFFUSE_OUT o = (BW_DS_VS_DIFFUSE_OUT)0;

	BW_DS_PROJECT_POSITION(o)
	BW_DS_CALCULATE_UVS(o)

    o.tc.y += vOffset1;
    o.tc2.y += vOffset2;

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(BW_DS_VS_DIFFUSE_OUT i)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	half4 colour = tex2D( linkSampler, i.tc );
	colour *= tex2D( linkSampler, i.tc2 );
	
	if ( colourise )
		colour.rgb =
			colouriseColour.rgb * colouriseBlend +
			colour.rgb * (1.0f - colouriseBlend);
	else if ( highlight )
		colour.rgb =
			highlightColour.rgb * colouriseBlend +
			colour.rgb * (1.0f - colouriseBlend);

	g_buffer_writeAlbedo(o, colour.rgb);

	g_buffer_writeDepth(o, i.linerZ);
	g_buffer_writeNormal(o, float3(0.0f, 1.0f, 0.0f));
	g_buffer_writeObjectKind(o, g_objectID ? G_OBJECT_KIND_DYNAMIC : G_OBJECT_KIND_STATIC);

	return o;
}

BW_COLOR_TECHNIQUE( false, false )
{
	pass Pass_0
	{
		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = compile ps_3_0 ps_deferred_3_0();

	    ALPHABLENDENABLE = FALSE    ;
	    SRCBLEND         = ONE      ;
        FOGENABLE        = FALSE    ;
        LIGHTING         = FALSE    ;
        ZENABLE          = TRUE     ;
        ZFUNC            = LESSEQUAL;
        ZWRITEENABLE     = TRUE     ;
        CULLMODE         = NONE     ;
        TextureFactor    = 0xffffffff;
	}
}

#else

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
		colour.rgb =
			colouriseColour.rgb * colouriseBlend +
			colour.rgb * (1.0f - colouriseBlend);
	else if ( highlight )
		colour.rgb =
			highlightColour.rgb * colouriseBlend +
			colour.rgb * (1.0f - colouriseBlend);
	
	return colour;
};

technique standard
{
	pass Pass_0
	{
		VertexShader = compile vs_1_1 vs_main();
		PixelShader  = compile ps_2_0 ps_main();

	    ALPHABLENDENABLE = FALSE    ;
	    SRCBLEND         = ONE      ;
        FOGENABLE        = FALSE    ;
        LIGHTING         = FALSE    ;
        ZENABLE          = TRUE     ;
        ZFUNC            = LESSEQUAL;
        ZWRITEENABLE     = TRUE     ;
        CULLMODE         = NONE     ;
        TextureFactor    = 0xffffffff;
	}
}

#endif
