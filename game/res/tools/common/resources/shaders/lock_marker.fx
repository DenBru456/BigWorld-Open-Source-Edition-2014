#include "stdinclude.fxh"
#include "read_g_buffer.fxh"

//-------------------------------------------------------------------------------------------------
struct InputVertex
{
	float3 pos	  :	POSITION;

	//-- instance data.
	InstancingStream instance;
};

struct BBox
{
	float3 m_pos;
	float3 m_scale;
	float3 m_axisX;
	float3 m_axisY;
	float3 m_axisZ;
	float4 m_color;
};

//--------------------------------------------------------------------------------------------------
struct VS2PS_STENCIL
{
	float4 pos : POSITION;
};

//--------------------------------------------------------------------------------------------------
struct VS2PS
{
	float4 pos		 : POSITION;
	float4 color	 : COLOR;

	//-- decal's VP matrix.
	float4 row0		 : TEXCOORD0;
	float4 row1		 : TEXCOORD1;
	float4 row2		 : TEXCOORD2;
	float4 row3		 : TEXCOORD3;

};

//-- pixel shader output
//--------------------------------------------------------------------------------------------------
struct PS_OUT
{
	float4 color0 : COLOR0;
};

//--------------------------------------------------------------------------------------------------
BBox unpackInput(const InstancingStream i)
{
	BBox o = (BBox)0;

	o.m_pos	  = i.v1.xyz;
	o.m_scale = i.v3.xzy;
	o.m_axisZ = normalize(i.v0.xyz);
	o.m_axisY = normalize(i.v2.xyz);
	o.m_axisX = cross(o.m_axisY, o.m_axisZ);

	o.m_color = float4(i.v2.w, i.v1.w, i.v0.w, i.v3.w);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4x4 calcBBoxWorldMat(const BBox i)
{
	//-- compute world matrix.
	//-- world = scale * rotateTranslate.

	float4x4 worldMat = 
	{
		{i.m_axisX * i.m_scale.x, 0},
		{i.m_axisY * i.m_scale.y, 0},
		{i.m_axisZ * i.m_scale.z, 0},
		{i.m_pos,   1}
	};

	//-- final world matrix.
	return worldMat;
}

//--------------------------------------------------------------------------------------------------
float4x4 calcBBoxViewProjMat(const BBox i)
{
	//-- 1. compute data for the decal view matrix.
	//--
	//-- zaxis = normal(dir)
	//-- xaxis = normal(cross(Up, zaxis))
	//-- yaxis = cross(zaxis, xaxis)
	//--
	//-- xaxis.x           yaxis.x           zaxis.x          0
	//-- xaxis.y           yaxis.y           zaxis.y          0
	//-- xaxis.z           yaxis.z           zaxis.z          0
	//-- -dot(xaxis, pos)  -dot(yaxis, pos)  -dot(zaxis, pos) l
	//--
	float4x4 lookAtMat = 
	{
		{i.m_axisX.x,				i.m_axisY.x,				i.m_axisZ.x,				0},
		{i.m_axisX.y,				i.m_axisY.y,				i.m_axisZ.y,				0},
		{i.m_axisX.z,				i.m_axisY.z,				i.m_axisZ.z,				0},
		{-dot(i.m_axisX, i.m_pos),  -dot(i.m_axisY, i.m_pos),	-dot(i.m_axisZ, i.m_pos),	1}
	};
	
	//-- 2. compute data for the decal proj matrix.
	//--
	//-- 2/w   0        0       0
	//-- 0     2/h      0       0
	//-- 0     0    1/(zf-zn)   0
	//-- 0     0    -zn/(zf-zn) l
	//--
	// zn = -0.5f * scale.z;
	// zf = +0.5f * scale.z;
	//--
	float4x4 projMat = 
	{
		{2.0f / i.m_scale.x,	0,						0,					0},
		{0,				 		2.0f / i.m_scale.y,		0,					0},
		{0,				 		0,						1.0f / i.m_scale.z,	0},
		{0,  			 		0,						0.5f,				1}
	};
	
	//-- 3. caclulate final view-projection decal matrix.
	return mul(lookAtMat, projMat);
}

//--------------------------------------------------------------------------------------------------
VS2PS_STENCIL VS_STENCIL(const InputVertex i)
{
	VS2PS_STENCIL o = (VS2PS_STENCIL)0;

	//-- 1. unpack input bbox data.
	BBox bbox = unpackInput(i.instance);
	
	//-- 2. calculate world matrix.
	float4x4 worldMat = calcBBoxWorldMat(bbox);

	//-- 3. Now do regular vertex shader with usage of the previous calculated data.
	float4 wPos	= mul(float4(i.pos, 1.0f), worldMat);

	//-- 4.
	o.pos = mul(wPos, g_viewProjMat);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 PS_STENCIL(VS2PS_STENCIL i) : COLOR0
{
	//-- is not important what we send to the buffer, because writing to the color buffer disabled
	//-- by the render state.
	return float4(0,0,0,0);
}

//--------------------------------------------------------------------------------------------------
VS2PS VS(const InputVertex i)
{
	VS2PS o = (VS2PS)0;

	//-- 1. retrieve instance data.
	BBox bbox = unpackInput(i.instance);
	
	//-- 2. calculate decal matrices.
	float4x4 viewProjMat = calcBBoxViewProjMat(bbox);
	float4x4 worldMat	 = calcBBoxWorldMat(bbox);

	//-- 3. Now do regular vertex shader with usage of the previous calculated data.
	float4 wPos	= mul(float4(i.pos, 1.0f), worldMat);

	//-- 4. write decal view-proj matrix.
	o.pos  = mul(wPos, g_viewProjMat);
	o.color = bbox.m_color;
	o.row0 = viewProjMat[0];
	o.row1 = viewProjMat[1];
	o.row2 = viewProjMat[2];
	o.row3 = viewProjMat[3];

	return o;
}


//--------------------------------------------------------------------------------------------------
float Cut(in float2 tc)
{
	float2 clampedAtlasUV = saturate(tc);
	return 1.0f - (float)any(clampedAtlasUV - tc);
}

//--------------------------------------------------------------------------------------------------
PS_OUT PS_OVERDRAW(const VS2PS i, in float2 vPos : VPOS)
{
	PS_OUT o = (PS_OUT)0;

	float2 screenXY = SC2TC(vPos);

	//-- read GBuffer properties.
	float3 wPos    = g_buffer_readWorldPos(screenXY, g_nvStereoParams.w);

	//-- reconstruct decal projection matrix.
	float4x4 decalViewProjMat = { i.row0, i.row1, i.row2, i.row3 };

	//-- calculate texture coordinates for projection texture.
	float4 cPos = mul(float4(wPos, 1.0f), decalViewProjMat);
	cPos.xy /= cPos.w;

	//-- calculate uv
	float2 uv = CS2TS(cPos.xy);

	//-- alpha value for blending. cuts pixels out of destination surface
	float alpha = i.color.w * Cut(uv);

	//-- write output.	
	//-- Note: we doesn't write alpha into any of the final buffers. Alpha used only for doing correct
	//--	   alpha blending operations.
	o.color0 = float4(i.color.xyz, alpha);

	return o;
}

technique STENCIL
{
	//-- clear stencil.
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		CULLMODE = NONE;
		ZENABLE = TRUE;
		ZFUNC = ALWAYS;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = FALSE;
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE = 0x00;
		COLORWRITEENABLE1 = 0x00;

		STENCILENABLE = TRUE;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILFUNC = ALWAYS;
		STENCILPASS = REPLACE;
		STENCILFAIL = REPLACE;
		STENCILZFAIL = REPLACE;
		STENCILREF = 0x00;
										
		VertexShader = compile vs_3_0 VS_STENCIL();
		PixelShader  = compile ps_3_0 PS_STENCIL();
	}

	//-- fill stencil.
	pass Pass_1
	{
		CULLMODE = CW;
		ZENABLE = TRUE;
		ZFUNC = GREATEREQUAL;

		STENCILENABLE = TRUE;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILFUNC = ALWAYS;
		STENCILPASS = INCR;
		STENCILFAIL = KEEP;
		STENCILZFAIL = KEEP;
										
		VertexShader = compile vs_3_0 VS_STENCIL();
		PixelShader  = compile ps_3_0 PS_STENCIL();
	}
}

//--------------------------------------------------------------------------------------------------

// Note that the stencil-based increment/decrement technique for determining
// fragment coverage of the bounding boxes fails in highly overlapped fragments
// due to limited stencil bits. In these cases, stencil gets saturated decremented to 
// zero and no shading occurs for those highly overlapped fragments. This is also
// dependent on instance evaluation order z (incr/decr). these operations have
// a clamped/truncated total and so do not work in areas of high overlap.

technique DIFFUSE
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		CULLMODE = CCW;
		ZENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = SRCALPHA;				
		DESTBLEND = INVSRCALPHA;
		BLENDOP = ADD;	
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE  = 0xFF;
		COLORWRITEENABLE1 = 0x00;

		STENCILENABLE = TRUE;
		STENCILFUNC = LESS;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILPASS = KEEP;
		STENCILZFAIL = DECRSAT;
		STENCILFAIL = KEEP;
		STENCILREF = 0;
										
		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS_OVERDRAW();
	}
}