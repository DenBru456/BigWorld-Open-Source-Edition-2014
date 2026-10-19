#include "pch.hpp"
#include "effect_parameter_cache.hpp"
#include "cstdmf/debug.hpp"

DECLARE_DEBUG_COMPONENT2( "Romp", 0 )

#include <set>

BW_BEGIN_NAMESPACE

/*static*/ EffectParameterCache::MissingParameterHandler
	EffectParameterCache::s_missingParameterHandler = NULL;

/**
 *	This method (un)registers the UI handler for missing parameters.
 */
/*static*/ void EffectParameterCache::missingParameterHandler(
	MissingParameterHandler handler )
{
	s_missingParameterHandler = handler;
}

EffectParameterCache::~EffectParameterCache()
{
	BW_GUARD;
	this->spEffect_ = NULL;
}

void EffectParameterCache::cache(const BW::string& name )
{		
	BW_GUARD;
	D3DXHANDLE handle = spEffect_->GetParameterByName(NULL,name.c_str());
	if (handle)
	{
		parameters_[name] = handle;
	}
	else
	{
		{
			static BW::set< BW::string > s_consoleReportedParams;
			if (s_consoleReportedParams.insert( name ).second)
			{
				ERROR_MSG( "Could not find parameter %s in EffectMaterial "
					"(further lookups of this parameter are silent)\n",
					name.c_str() );
			}
		}
		if (s_missingParameterHandler != NULL)
		{
			BW::string msg = "EffectMaterial: missing parameter '" + name + "'";
			s_missingParameterHandler( msg );
		}
		parameters_[name] = NULL;
	}
}

BW_END_NAMESPACE

// effect_parameter_cache.cpp
