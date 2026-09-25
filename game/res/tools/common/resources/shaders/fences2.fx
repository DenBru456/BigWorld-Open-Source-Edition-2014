#include "stdinclude.fxh"

float4x4 world;
float4 color;

void vs_main(float4 pos : POSITION, out float4 oPos : POSITION)
{
	float4 wPos = mul( pos, world);
	oPos = mul( wPos, g_viewProjMat );
}

float4 ps_main() : COLOR
{
	return color;
}

technique standard
<
	bool skinned = false;
>
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;
		CULLMODE = NONE;
		FOGENABLE = FALSE;
		STENCILENABLE = FALSE;
		COLORWRITEENABLE = RED | GREEN | BLUE | ALPHA;

		VertexShader = compile vs_1_1 vs_main();
		PixelShader = compile ps_1_1 ps_main();
	}
}