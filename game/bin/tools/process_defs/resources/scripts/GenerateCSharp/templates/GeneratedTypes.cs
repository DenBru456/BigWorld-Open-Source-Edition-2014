using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.Text;

{% if generatedNamespace != "BW" -%}
using BW;{% endif %}
using BW.Types;

namespace {{ generatedNamespace }}
{
{% for fixedDictType in fixedDictTypes %}

/// <summary>
/// This class represents {{ fixedDictType.name }}
/// FIXED_DICT property values.
/// </summary>
public class {{ fixedDictType.name }} : IEntityProperty
{
	public bool initFromStream( BinaryIStream stream )
	{
{%- for member in fixedDictType.members -%}
{#	//object obj = {{ member.name }};
	//stream.readObject( ref obj );#}		
		stream.read({% if member.shouldRef %} ref{% endif %} {{ member.name }} );
{%- endfor %}
		return !stream.error;
	}
	
	public bool addToStream( BinaryOStream stream )
	{
{%- for member in fixedDictType.members -%}
{#		object obj = {{ member.name }};
		stream.writeObject( obj ); #}
		stream.write( {{ member.name }} );
{%- endfor %}
		return !stream.error;
	}

	public bool applyChange( NestedPropertyChange change )
	{
		const uint NUM_PROPERTIES = {{ fixedDictType.members | count }};
		uint index = change.readNextIndex( NUM_PROPERTIES );

		switch (index)
		{
		{% for member in fixedDictType.members %}
		case {{ loop.index0 }}:
		{
			if (!change.isFinished)
			{
				// Sub-property change.
				object obj = {{ member.name }};
				bool res = change.apply( ref obj );
				if (res)
				{
					{{ member.name }} = ({{ member.type }})obj;
				}
				return res;
			}
			else
			{
				// Change at this level.
				change.stream.read({% if member.shouldRef %} ref{% endif %} {{ member.name }} );
				return !change.stream.error;
			}
		}
		{% endfor %}
		default:
			break;
		}
		return false;
	}
	// Sub-property members
{%- for member in fixedDictType.members %}
	public {{ member.type }} {{ member.name }}{% if not member.shouldRef %} = new {{ member.type -}}
		({% if member.arraySize > 0 %} {{ member.arraySize }} {% endif %})
	{%- endif -%};
{%- endfor %}
}
{#
template<>
inline bool NestedPropertyChange::apply( {{ fixedDictType.name }} & value )
{
	return value.applyChange( *this );
}
#}
{% endfor %}
} // namespace {{ generatedNamespace }}
