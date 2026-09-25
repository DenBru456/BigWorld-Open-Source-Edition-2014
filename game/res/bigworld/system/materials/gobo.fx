// Auto variables
float4x4 worldViewProj :  WorldViewProjection;
float4	 factor : GUIColour;
texture diffuseMap;
texture secondMap;

// Manual variables
float4  diffuseColour = (1,1,1,1);

// Data types
struct VertexXYZDUV2
{
   float4 pos:		POSITION;
   float4 diffuse:	COLOR;
   float2 tc1:		TEXCOORD0;
   float2 tc2:		TEXCOORD1;
};

struct OutputDiffuseLighting
{
	float4 pos:     POSITION;
	float2 tc1:     TEXCOORD0;
	float2 tc2:     TEXCOORD1;
	float4 diffuse: COLOR;
};


sampler diffuseSampler = sampler_state
{
	Texture = (diffuseMap);
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
	ADDRESSW = CLAMP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

sampler secondSampler = sampler_state
{
	Texture = (secondMap);
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
	ADDRESSW = CLAMP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};


OutputDiffuseLighting vs_main( VertexXYZDUV2 input )
{
	OutputDiffuseLighting o = (OutputDiffuseLighting)0;

	o.pos = mul(input.pos, worldViewProj);
	o.tc1 = input.tc1;
	o.tc2 = input.tc2;
	o.diffuse = diffuseColour;
	
	return o;
}


float4 ps_main( OutputDiffuseLighting input ) : COLOR0
{
	float4 diffuseMap = tex2D( diffuseSampler, input.tc1 );	
	float4 secondMap = tex2D( secondSampler, input.tc2 );
	float4 colour;
	colour = input.diffuse * diffuseMap * secondMap;
	return colour * factor;
	//return diffuseMap;
}


float4 ps_main_x2( OutputDiffuseLighting input ) : COLOR0
{
	float4 diffuseMap = tex2D( diffuseSampler, input.tc1 );	
	float4 secondMap = tex2D( secondSampler, input.tc2 );
	float4 colour;
	colour = input.diffuse * diffuseMap * secondMap * 2;
	return colour * factor;
	//return diffuseMap;
}



//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique FX_ADD
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = ONE;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main();
   }

}

technique FX_BLEND
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = INVSRCALPHA;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main();
   }

}

technique FX_BLEND_COLOUR
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCCOLOR;
      DESTBLEND = INVSRCCOLOR;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main();
   }

}

technique FX_BLEND_INVERSE_COLOUR
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = INVSRCCOLOR;
      DESTBLEND = SRCCOLOR;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main();
   }

}

technique FX_SOLID
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = ONE;
      DESTBLEND = ZERO;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = FALSE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main();
   }

}

technique FX_MODULATE2X
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = ONE;
      DESTBLEND = ZERO;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = FALSE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main_x2();
   }
}

technique FX_ALPHA_TEST
{
   pass Pass_0
   {
      ALPHATESTENABLE = TRUE;
      ALPHAREF = 1;
      SRCBLEND = ONE;
      DESTBLEND = ZERO;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = FALSE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main();
   }
}

technique FX_BLEND_INVERSE_ALPHA
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = INVSRCALPHA;
      DESTBLEND = SRCALPHA;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main_x2();
   }

}

technique FX_BLEND2X
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = INVSRCALPHA;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main_x2();
   }

}