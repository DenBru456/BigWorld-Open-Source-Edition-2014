#include "stdinclude.fxh"

float4x4 world;

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
struct VertexInput
{
   float4 pos:		POSITION;
   float3 normal:   NORMAL;
   float4 diffuse:	COLOR0;
};

struct VertexOutput
{
   float4 pos:		POSITION;
   float4 normalZLinear:   NORMAL;
   float4 diffuse:	COLOR0;
};

//--------------------------------------------------------------------------------------------------
VertexOutput vs_deferred_3_0(const VertexInput i)
{
	VertexOutput o = (VertexOutput)0;
	o.diffuse = i.diffuse;
	float4 wPos = mul( i.pos, world);
	o.pos = mul( wPos, g_viewProjMat );
	o.normalZLinear.xyz = mul(i.normal, (float3x3)world);
	o.normalZLinear.w = o.pos.w;
	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(const VertexOutput i)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	float4 oColor = i.diffuse;
	
	g_buffer_writeObjectKind(o, G_OBJECT_KIND_STATIC);
	g_buffer_writeNormal(o, i.normalZLinear.xyz);
	g_buffer_writeDepth(o, i.normalZLinear.w);
	g_buffer_writeAlbedo(o, oColor.xyz);


	return o;
}

//--------------------------------------------------------------------------------------------------
technique DS
{
	pass P0
	{
		ALPHABLENDENABLE 	= FALSE;
		ALPHATESTENABLE = FALSE;		
		ZENABLE 			= TRUE;
		ZWRITEENABLE 		= TRUE;
		ZFUNC 				= LESSEQUAL;
		CULLMODE 			= CCW;

		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = compile ps_3_0 ps_deferred_3_0();
	}
}

#else

//--------------------------------------------------------------------------------------------------
struct VertexIO
{
   float4 pos:		POSITION;
   float4 diffuse:	COLOR;
};


//--------------------------------------------------------------------------------------------------
VertexIO vs_main_2_0(const VertexIO i)
{
	VertexIO o = (VertexIO)0;
	o.diffuse = i.diffuse;
	float4 projPos = mul( i.pos, mul(world, g_viewProjMat) );
	o.pos = projPos;
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(const VertexIO i) : COLOR
{
	float4 oColor = i.diffuse;
	oColor.w = 1.0f;
	return oColor;
}

//--------------------------------------------------------------------------------------------------
technique FS
{
	pass P0
	{
		ALPHABLENDENABLE 	= FALSE;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
		ALPHATESTENABLE 	= FALSE;
		ZENABLE = TRUE;
		ZWRITEENABLE 		= TRUE;
		ZFUNC = LESSEQUAL;
		CULLMODE = NONE;

		//-- render target mask.
		COLORWRITEENABLE  = 0x07;
		
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
	}

#endif //-- BW_DEFERRED_SHADING