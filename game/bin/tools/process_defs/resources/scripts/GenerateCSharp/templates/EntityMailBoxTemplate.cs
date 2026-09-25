using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.Text;

using BW;
using BW.Types;
{% if generatedNamespace != "BW" -%}
using {{ generatedNamespace }};{% endif %}

namespace {{ generatedNamespace }}.{{ component }}MB
{
/// <summary>
/// This class describes the interface to the {{ component }} part 
/// of the {{ entity.name }} entity.
/// FIXED_DICT property values.
/// </summary>
public class {{ entity.name }} : ServerEntityMailBox
{
	public {{ entity.name }}( Entity entity ) : base( entity )	{}

	// Section: {{ component }} methods

{% for method in methods %}{% if method.isExposed %}
	/// <summary>
	/// This method implements calling the {{ method.name }}() {{ component }} method.
	/// </summary>
	public {{ method|methodDeclaration }}
	{
		{% if method.args %}BinaryOStream stream = {% endif -%}
		this.startMessage( {{ method.exposedIndex }}, {% if component == "Base" %}true{% else %}false{% endif %} );
{%- if method.args %}

		if (stream != null)
		{
{%- for arg in method.args %}
			stream.write( {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %} );
{%- endfor %}
		}
{%- endif %}
	}
{% endif %}{% endfor %}
};

} // namespace {{ generatedNamespace }}.{{ component }}MB
