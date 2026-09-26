#ifndef _BW_DEFERRED_SHADING_FXH_
#define _BW_DEFERRED_SHADING_FXH_

#include "stdinclude.fxh"

//--------------------------------------------------------------------------------------------------
struct BW_DS_VS_DIFFUSE2_OUT
{
	float4 pos		: POSITION;
	float  linerZ	: TEXCOORD0;
	float2 tc		: TEXCOORD1;
	float2 tc2		: TEXCOORD2;
	float3 normal	: TEXCOORD3;
};

//--------------------------------------------------------------------------------------------------
struct BW_DS_VS_DIFFUSE_OUT
{
	float4 pos		: POSITION;
	float  linerZ	: TEXCOORD0;
	float2 tc		: TEXCOORD1;
#if DUAL_UV
	float2 tc2		: TEXCOORD2;
#endif //-- DUAL_UV
	float3 normal	: TEXCOORD3;
};

//--------------------------------------------------------------------------------------------------
struct BW_DS_VS_BUMP_OUT
{
	float4 pos		: POSITION;
	float  linerZ	: TEXCOORD0;
	float2 tc		: TEXCOORD1;
#if DUAL_UV
	float2 tc2		: TEXCOORD2;
#endif //-- DUAL_UV
	float3 normal	: TEXCOORD3;
	float3 tangent	: TEXCOORD4;
	float3 binormal	: TEXCOORD5;
};

//--------------------------------------------------------------------------------------------------
struct VS_CASTER_OUTPUT
{
	float4 pos	 : POSITION;
	float2 depth : TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VS_CASTER_OUTPUT_ALPHA_TESTED
{
	float4 pos	 : POSITION;
	float2 tc	 : TEXCOORD0;
#if DUAL_UV || (defined UV_TRANSFORM_OTHER)
	float2 tc2	 : TEXCOORD1;
#endif
	float2 depth : TEXCOORD2;
};

//-- vertex layout for deferred shading's lighting pass.
//--------------------------------------------------------------------------------------------------
struct BW_DS_LIGHT_PASS_VS
{
	float4 pos	:	POSITION;
	float2 tc	:	TEXCOORD0;
};

//-- from VS to PS for deferred shading's lighting pass.
//--------------------------------------------------------------------------------------------------
struct BW_DS_LIGHT_PASS_VS2PS
{
	float4 pos	:	POSITION;
	float2 tc	:	TEXCOORD0;
};

//-- convert screen space position to texture space.
//-- I.e. from XY[screen width, screen height] -> UV[0, 1]
//--------------------------------------------------------------------------------------------------
float2 SC2TC(float2 vPos)
{
	return (vPos + float2(+0.5f, +0.5f)) * g_invScreen.zw;
}

//-- converts clip space position to texture space. I.e. from XY[-1, +1] -> UV[0, 1]
//--------------------------------------------------------------------------------------------------
float2 CS2TS(in float2 cs)
{
	return cs * float2(+0.5f, -0.5f) + float2(+0.5f, +0.5f);
}

//-- converts texture coordinates to clip space position. I.e. UV[0,1] -> XY[-1, +1]
//--------------------------------------------------------------------------------------------------
float2 TS2CS(in float2 ts)
{
	return ts * float2(-2.0f, +2.0f) + float2(+1.0f, -1.0f);
}

//--------------------------------------------------------------------------------------------------
//--
//-- FIX (banding): the old normal encoding packed theta through an 8-bit atan2 LUT
//-- (256x256, POINT sampled) and stored it into an 8-bit channel, giving ~1.4 degree
//-- buckets and up to ~5 degrees of compounded angular error. On smooth, low-curvature
//-- surfaces the resulting NdotL steps showed up as hard "topographic" contour rings in
//-- deferred mode (spherical encoding via g_atan2LUTMap / cartesianToSpherical /
//-- sphericalToCartesian has been removed).
//--
//-- The replacement is octahedral normal encoding (Cigolle et al., "A Survey of Efficient
//-- Representations for Normal Unit Vectors", JCGT 2014). The g-buffer's normal channel is
//-- now an A16B16G16R16F render target (see DeferredPipeline::createUnmanagedObjects), so
//-- each octahedral coordinate carries ~11 bits of precision: max angular error ~0.05
//-- degrees, far below what an 8-bit backbuffer can display.
//--
//-- Note: encode/decode deliberately use float, not half, precision.
//--------------------------------------------------------------------------------------------------
float2 octEncode(in float3 n)
{
	n /= (abs(n.x) + abs(n.y) + abs(n.z));

	if (n.z < 0.0f)
	{
		//-- wrap the lower hemisphere onto the octahedron's diagonals.
		//-- sign(v): +1 when v >= 0, -1 otherwise (component-wise).
		float2 sgn = 1.0f - 2.0f * step(n.xy, 0.0f);
		n.xy = (1.0f - abs(n.yx)) * sgn;
	}

	return n.xy * 0.5f + 0.5f;
}

//--------------------------------------------------------------------------------------------------
float3 octDecode(in float2 enc)
{
	enc = enc * 2.0f - 1.0f;

	float3 n = float3(enc.xy, 1.0f - abs(enc.x) - abs(enc.y));

	if (n.z < 0.0f)
	{
		//-- mirror of the encode wrap: recover the lower hemisphere.
		float2 sgn = 1.0f - 2.0f * step(enc.xy, 0.0f);
		n.xy = (1.0f - abs(n.yx)) * sgn;
	}

	return normalize(n);
}

//-- from ShaderX5 "2.6 Normal Mapping without Pre-Computed Tangents".
//--------------------------------------------------------------------------------------------------
float3x3 computeTangentFrame(float3 N, float3 p, float2 uv)
{
    //-- get edge vectors of the pixel triangle
    float3 dp1  = ddx(p);
    float3 dp2  = ddy(p);
    float2 duv1 = ddx(uv);
    float2 duv2 = ddy(uv);

    //-- solve the linear system
    float3x3 M = float3x3(dp1, dp2, cross(dp1, dp2));
    float2x3 inversetransposeM = float2x3(cross(M[1], M[2]), cross(M[2], M[0]));
    float3   T = mul(float2(duv1.x, duv2.x), inversetransposeM);
    float3   B = mul(float2(duv1.y, duv2.y), inversetransposeM);

    //-- construct tangent frame 
    return float3x3(normalize(T), normalize(B), N);
}

//-- compute desired LOD for sampling based on the incoming UV coordinate and texture dimension.
//--------------------------------------------------------------------------------------------------
float computeTextureLOD(in float2 uv, in float2 texDim)
{
	uv *= texDim;
	
	float2 ddx_ = ddx(uv);
	float2 ddy_ = ddy(uv);
	float2 mag  = abs(ddx_) + abs(ddy_);
	float  lod = log2(max(mag.x, mag.y));

	return lod;
}

//-- encode a float value into 3 bytes (input value should be in the range of [0, 1])
//--------------------------------------------------------------------------------------------------
float3 packFloatToVec3(const float value)
{
	static const float  invByte  = 1.0f / 255.0f;
	static const float  max24int = 256*256*256-1;
	static const float3 bitSh    = float3(max24int/(256*256), max24int/256, max24int);
	static const float3 bitMsk   = float3(0.0, 256.0, 256.0);

	float3 decomp = floor(value * bitSh) * invByte;
	decomp -= decomp.xxy * bitMsk;
	return decomp;
}

//--------------------------------------------------------------------------------------------------
float unpackFloatFromVec3(const float3 value)
{
	static const float3 bitSh = float3(255.0/256, 255.0/(256*256), 255.0/(256*256*256));

	return dot(value, bitSh);
}

//--------------------------------------------------------------------------------------------------
float almostZero(float f, float epsilon = 0.0004f)
{
	return f < epsilon && f > -epsilon;
}

#endif //-- _BW_DEFERRED_SHADING_FXH_
