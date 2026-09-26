#ifndef _BW_WRITE_G_BUFFER_FXH_
#define _BW_WRITE_G_BUFFER_FXH_

#include "deferred_shading.fxh"

//-- Represent g-buffer layout.
//-- Note: channel #1 is stored in an A16B16G16R16F render target (see
//--       DeferredPipeline::createUnmanagedObjects). RG hold octahedral encoded
//--       world space normal, B - specular amount, A - user data #2.
//--------------------------------------------------------------------------------------------------
struct G_BUFFER_LAYOUT
{
	float4 color0 : COLOR0; //-- RGBA8: RGB - depth. A - object kind.
	float4 color1 : COLOR1; //-- RGBA16F: RG - octahedral encoded normal. B - specular amount. A - user data #2
	float4 color2 : COLOR2; //-- RGBA8: RGB - albedo (diffuse) color, A - user data #1.
};

//--------------------------------------------------------------------------------------------------
void g_buffer_writeNormal(inout G_BUFFER_LAYOUT o, in float3 normal)
{
	o.color1.rg = octEncode(normalize(normal));
}

//-- write into g-buffer already packed (i.e. octahedral encoded) normal without implicit encoding.
//--------------------------------------------------------------------------------------------------
void g_buffer_writePackedNormal(inout G_BUFFER_LAYOUT o, in half2 packedNormal)
{
	o.color1.rg = packedNormal;
}

//--------------------------------------------------------------------------------------------------
void g_buffer_writeSpecAmount(inout G_BUFFER_LAYOUT o, in half amount)
{
	o.color1.b = amount;
}

//--------------------------------------------------------------------------------------------------
void g_buffer_writeDepth(inout G_BUFFER_LAYOUT o, in float depth)
{
	o.color0.rgb = packFloatToVec3(depth * g_farPlane.y);
}

//-- write material kind of the pixel. We have up to 256 different materials.
//--------------------------------------------------------------------------------------------------
void g_buffer_writeObjectKind(inout G_BUFFER_LAYOUT o, in half id)
{
	static const half invByte = 1.0f / 255.0f;
	o.color0.a = id * invByte;
}

//-- write diffuse color.
//--------------------------------------------------------------------------------------------------
void g_buffer_writeAlbedo(inout G_BUFFER_LAYOUT o, in half3 color)
{
	o.color2.rgb = color;
}

//-- write material id #1. May be used differently for different sub-systems. See SpeedTree sub-system
//-- for example.
//--------------------------------------------------------------------------------------------------
void g_buffer_writeUserData1(inout G_BUFFER_LAYOUT o, in half id, uniform const bool isPacked = true)
{
	//-- Note: compile-time branching.
	if (isPacked)
	{
		static const half invByte = 1.0f / 255.0f;
		o.color2.a = id * invByte;
	}
	else
	{
		o.color2.a = id;
	}
}

//-- write material id #2. May be used differently for different sub-systems. See SpeedTree sub-system
//-- for example.
//--------------------------------------------------------------------------------------------------
void g_buffer_writeUserData2(inout G_BUFFER_LAYOUT o, in half id, uniform const bool isPacked = true)
{
	//-- Note: compile-time branching.
	if (isPacked)
	{
		static const half invByte = 1.0f / 255.0f;
		o.color1.a = id * invByte;
	}
	else
	{
		o.color1.a = id;
	}
}

#endif //-- _BW_WRITE_G_BUFFER_FXH_
