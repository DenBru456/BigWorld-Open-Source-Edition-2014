float4x4 worldViewProj : WorldViewProjection;

struct VertexXYZ
{
	float4 pos : POSITION;
};

struct Output
{
	float4 pos : POSITION;
};

Output vs_main( VertexXYZ input )
{
	Output o = (Output)0;

	o.pos = mul(input.pos, worldViewProj);

	return o;
}

float4 ps_main( Output i ) : COLOR
{
	return (float4)0;
}

//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique standard
<
	bool skinned = false;
>
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = ONE;
		DESTBLEND = ZERO;
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		CULLMODE = NONE;
		COLOROP[0] = SELECTARG1;
		COLORARG1[0] = TFACTOR;
		ALPHAOP[0] = SELECTARG1;
		ALPHAARG1[0] = TFACTOR;
		COLOROP[1] = DISABLE;
		ALPHAOP[1] = DISABLE;
		FOGENABLE = FALSE;
		STENCILENABLE = FALSE;
		COLORWRITEENABLE = RED | GREEN | BLUE | ALPHA;
		LIGHTING = FALSE;
//		VertexShader = compile vs_1_1 vs_main();
		VertexShader = NULL;
//		PixelShader = compile ps_1_1 ps_main();
		PixelShader = NULL;
	}
}
