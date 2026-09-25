uniform float4x4 worldViewProj;
uniform float4 color;

void vs_main(float4 pos : POSITION, out float4 oPos : POSITION)
{
	oPos = mul(pos, worldViewProj);
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
		ALPHABLENDENABLE = FALSE;
		SRCBLEND = ONE;
		DESTBLEND = ZERO;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;
		CULLMODE = NONE;
		FOGENABLE = FALSE;
		COLORWRITEENABLE = RED | GREEN | BLUE;

		VertexShader = compile vs_1_1 vs_main();
		PixelShader = compile ps_1_1 ps_main();
	}
	pass Pass_1
	{
		ALPHATESTENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = GREATEREQUAL;
		CULLMODE = NONE;
		FOGENABLE = FALSE;
		COLORWRITEENABLE = RED | GREEN | BLUE;

		VertexShader = compile vs_1_1 vs_main();
		PixelShader = compile ps_1_1 ps_main();
	}
}
