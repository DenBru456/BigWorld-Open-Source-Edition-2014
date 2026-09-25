#include "stdinclude.fxh"

float4 colour
<
	bool artistEditable = true;
	string UIWidget = "Color";
	string UIName = "Colour";
	string UIDesc = "The colour tint of the portal";
> = { 0.0, 0.0, 1.0, 0.25 };

technique standard
{
   pass Pass_0
   {
      ALPHATESTENABLE = TRUE;
      ALPHABLENDENABLE = TRUE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = INVSRCALPHA;
      
      CULLMODE = NONE;
      LIGHTING = FALSE;
      ZWRITEENABLE = FALSE;
      ZENABLE = TRUE;
      ZFUNC = LESSEQUAL;
      FOGENABLE = FALSE;
      TEXTUREFACTOR = (colour);
      
      COLOROP[0] = SELECTARG1;
			COLORARG1[0] = TFACTOR;
			ALPHAOP[0] = SELECTARG1;
			ALPHAARG1[0] = TFACTOR;
			
			COLOROP[1] = DISABLE;
			ALPHAOP[1] = DISABLE;
			
			COLOROP[2] = DISABLE;
			ALPHAOP[2] = DISABLE;
			
			COLOROP[3] = DISABLE;
			ALPHAOP[3] = DISABLE;

      VertexShader = NULL;
      PixelShader = NULL;
   }

}
