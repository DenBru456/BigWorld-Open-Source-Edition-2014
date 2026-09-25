using System;
using System.Collections.Generic;
using System.Text;

{% if generatedNamespace != "BW" -%}
using BW;{% endif %}

namespace {{ generatedNamespace }}
{
public static class DefsDigest
{
	static public EntityDefConstants get()
	{
		return new EntityDefConstants( "{{ digest }}",
			{{ constants.maxExposedClientMethodCount }}, // numClientMethods
			{{ constants.maxExposedBaseMethodCount }}, // numBaseMethods
			{{ constants.maxExposedCellMethodCount }} ); // numCellMethods
	}
}
} // namespace {{ generatedNamespace }}


