// Auto variables
float4x4 worldViewProj :  WorldViewProjection;

// Manual variables
float4  diffuseColour = (1,1,1,1);

struct VertexXYZL
{
   float4 pos:		POSITION;
   float4 diffuse:	COLOR;   
};


struct OutputDiffuseLighting
{
	float4 pos:     POSITION;	
	float4 diffuse: COLOR;
};


OutputDiffuseLighting vs_main( VertexXYZL input )
{
	OutputDiffuseLighting o = (OutputDiffuseLighting)0;

	o.pos = mul(input.pos, worldViewProj);
	o.diffuse = diffuseColour;
	
	return o;
}

//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique standard
{
   pass Pass_0
   {
      ALPHATESTENABLE = FALSE;
      SRCBLEND = ONE;
      DESTBLEND = ONE;
      ZENABLE = TRUE;
      ZWRITEENABLE = FALSE;
      ZFUNC = LESSEQUAL;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = FALSE;
      COLORWRITEENABLE = RED | GREEN | BLUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;
      
      texture[0] = NULL; 
      texture[1] = NULL;
      // Or set up the filters individually for ATI cards
      //MINFILTER[0] = POINT;
      //MAGFILTER[0] = POINT;
      //MIPFILTER[0] = NONE;
      
      ColorOp[0] = SELECTARG1;
      ColorArg1[0] = DIFFUSE;
      ColorArg2[0] = CURRENT;
      AlphaOp[0] = SELECTARG1;
      AlphaArg1[0] = DIFFUSE;
      AlphaArg2[0] = CURRENT;
      ColorOp[1] = DISABLE;
      AlphaOp[1] = DISABLE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = NULL;
   }
}
