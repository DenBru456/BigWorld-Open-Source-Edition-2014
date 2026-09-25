// include file for adapting rt/shader created .fx files

#include "stdinclude.fxh"

float2x3 LightArray(		
		float4 surfPos,
		float3 surfNorm,
		float4 eyePos,
		float specPow)
{
	float2x3 illum = float2x3(0, 0, 0, 0, 0, 0);	
	float3 eyeVec = normalize(eyePos.xyz-surfPos);

	float3 lightVect = g_sunLight.m_dir;
	float3 halfVec = normalize(lightVect+eyeVec);
	float NdotL = dot(lightVect, surfNorm);
	float NdotH = dot(surfNorm, halfVec);
	float4 l = lit(NdotL, NdotH, specPow);
	illum[0] = (illum[0]+(l.y*g_sunLight.m_color.xyz));
	illum[1] = (illum[1]+(l.z*g_sunLight.m_color.xyz));
	
	return illum;
}