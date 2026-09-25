float4x4 viewProj : ViewProjection;
float4 world[51] : WorldPalette;

float3 transformPos( float4 pos, int index )
{
	float3 ret = {	dot( world[index], pos ),
					dot( world[index + 1], pos ),
					dot( world[index + 2], pos ) };
	return ret;
}

struct VertexXYZI
{
	float4 pos : POSITION;
	float index:	BLENDINDICES;
};

struct Output
{
	float4 pos : POSITION;
	float depth : TEXCOORD;
};

Output vs_main( VertexXYZI input )
{
	Output o = (Output)0;

	float4 worldPos = float4(transformPos( input.pos, input.index ), 1);
	
	o.pos = mul(worldPos, viewProj);
	o.depth = 1.f - o.pos.z;

	return o;
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
		CULLMODE = CCW;
		COLOROP[0] = SELECTARG1;
		COLORARG1[0] = TFACTOR;
		ALPHAOP[0] = SELECTARG1;
		ALPHAARG1[0] = TFACTOR;
		COLOROP[1] = DISABLE;
		ALPHAOP[1] = DISABLE;
		FOGENABLE = FALSE;
		STENCILENABLE = FALSE;
		COLORWRITEENABLE = RED | GREEN | BLUE | ALPHA;

		VertexShader = compile vs_1_1 vs_main();
		PixelShader = NULL;
	}
}
