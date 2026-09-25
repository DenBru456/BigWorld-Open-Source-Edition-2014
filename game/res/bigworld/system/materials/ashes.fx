// Auto variables
float4x4 worldViewProj :  WorldViewProjection;
float4	 factor : GUIColour;
float4	 resolution : Screen;	//w,h,halfw,halfh
bool pixelSnapEnabled : GUIPixelSnap;

// Manual variables
texture diffuseMap = NULL;
float4  diffuseColour = (1,1,1,1);
int     filterType = 2; // linear filtering

// Data types
struct VertexXYZDUV2
{
   float4 pos:		POSITION;
   float4 diffuse:	COLOR;
   float2 tc:		TEXCOORD0;
   float2 tc2:		TEXCOORD1;
};


sampler clampSampler = sampler_state
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


struct OutputDiffuseLighting
{
	float4 pos:     POSITION;
	float2 tc:		TEXCOORD0;
	float2 tc2:		TEXCOORD1;
	float4 diffuse: COLOR;
};


float4 snapPosition( float4 clipPos )
{
	clipPos.x = (clipPos.x * resolution.z) + resolution.z;
	clipPos.y = (clipPos.y * resolution.w) + resolution.w;
	clipPos.x = round(clipPos.x);
	clipPos.y = round(clipPos.y);
	clipPos.x -= 0.5f;
	clipPos.y += 0.5f;
	clipPos.x = (clipPos.x - resolution.z) / resolution.z;
	clipPos.y = (clipPos.y - resolution.w) / resolution.w;
	return clipPos;
}


OutputDiffuseLighting vs_main( VertexXYZDUV2 input, uniform bool pixelSnap )
{
	OutputDiffuseLighting o = (OutputDiffuseLighting)0;

	float4 clipPos = mul(input.pos, worldViewProj);
	
	if ( pixelSnap )
	{
		o.pos = snapPosition( clipPos );
	}
	else
	{
		o.pos = clipPos;
	}
		
	o.tc = input.tc;
	o.tc2 = input.tc2;
	o.diffuse = diffuseColour * input.diffuse;
	
	return o;
}

VertexShader vertexShaders_2_0[2] = {
	compile vs_1_1 vs_main( false ),
	compile vs_1_1 vs_main( true )
};


// Define for common states used in all blending modes
#define COMMONSTATES\
ZENABLE = FALSE;\
FOGENABLE = FALSE;\
CULLMODE = NONE;

// The pixel operation defines
#define COMMONPARTS\
TexCoordIndex[0] = 0;\
TexCoordIndex[1] = 1;\
Texture[0] = (diffuseMap);\
ADDRESSU[0] = CLAMP;\
ADDRESSV[0] = CLAMP;\
ADDRESSW[0] = CLAMP;\
MAGFILTER[0] = (filterType);\
MINFILTER[0] = (filterType);\
MIPFILTER[0] = (filterType);\
MAXMIPLEVEL[0] = 0;\
MIPMAPLODBIAS[0] = 0;\
ColorOp[1] = MODULATE;\
ColorArg1[1] = TFACTOR;\
ColorArg2[1] = CURRENT;\
AlphaOp[1] = MODULATE;\
AlphaArg1[1] = TFACTOR;\
AlphaArg2[1] = CURRENT;\
ColorOp[2] = DISABLE;\
AlphaOp[2] = DISABLE;\
TextureFactor = (factor);\
PixelShader = NULL;

#define PIXELOPMOD1 \
ColorOp[0] = MODULATE;\
ColorArg1[0] = TEXTURE;\
ColorArg2[0] = DIFFUSE;\
AlphaOp[0] = MODULATE;\
AlphaArg1[0] = TEXTURE;\
AlphaArg2[0] = DIFFUSE;\
COMMONPARTS

#define PIXELOPMOD2 \
ColorOp[0] = MODULATE2X;\
ColorArg1[0] = TEXTURE;\
ColorArg2[0] = DIFFUSE;\
AlphaOp[0] = MODULATE2X;\
AlphaArg1[0] = TEXTURE;\
AlphaArg2[0] = DIFFUSE;\
COMMONPARTS

//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique FX_ADD
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = ONE;
      ALPHABLENDENABLE = TRUE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD1
   }

}

technique FX_BLEND
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = INVSRCALPHA;
      ALPHABLENDENABLE = TRUE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD1
   }

}

technique FX_BLEND_COLOUR
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCCOLOR;
      DESTBLEND = INVSRCCOLOR;
      ALPHABLENDENABLE = TRUE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD1
   }

}

technique FX_BLEND_INVERSE_COLOUR
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = INVSRCCOLOR;
      DESTBLEND = SRCCOLOR;
      ALPHABLENDENABLE = TRUE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD1
   }

}

technique FX_SOLID
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = ONE;
      DESTBLEND = ZERO;
      ALPHABLENDENABLE = FALSE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD1
   }

}

technique FX_MODULATE2X
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = ONE;
      DESTBLEND = ZERO;
      ALPHABLENDENABLE = FALSE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD2
   }
}

technique FX_ALPHA_TEST
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = TRUE;
      ALPHAREF = 1;
      SRCBLEND = ONE;
      DESTBLEND = ZERO;
      ALPHABLENDENABLE = FALSE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD1
   }
}

technique FX_BLEND_INVERSE_ALPHA
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = INVSRCALPHA;
      DESTBLEND = SRCALPHA;
      ALPHABLENDENABLE = TRUE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD2
   }

}

technique FX_BLEND2X
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = INVSRCALPHA;
      ALPHABLENDENABLE = TRUE;

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD2
   }

}

technique FX_ADD_SIGNED
{
   pass Pass_0
   {
      COMMONSTATES
      ALPHATESTENABLE = FALSE;
      SRCBLEND = DESTCOLOR;
      DESTBLEND = SRCCOLOR;
      ALPHABLENDENABLE = TRUE;	  

      VertexShader = (vertexShaders_2_0[ pixelSnapEnabled ]);
      PIXELOPMOD1
   }
}
