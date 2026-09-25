using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.Text;

{% if generatedNamespace != "BW" -%}
using BW;{% endif %}
using BW.Types;

namespace {{ generatedNamespace }}
{
/// <summary>
/// This class implements the app-specific logic for the {{ name }} entity.
/// </summary>
public interface I{{ className }} : IEntityExtension
{
{#	#region Public properties
	{{ parentName }} parent { get; set; }
	#endregion Public properties
#}	
	#region Client methods
{% for method in clientMethods %}
	void {{ method.name }}( {% for arg in method.args -%}
			{{ arg.1|ctype }} {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}
			{%- if not loop.last %}, 
			{% endif %}{% endfor %} );
{% endfor %}
	#endregion Client methods

	#region Client property callback
	void onPropertyChange( string propertyName );
	#endregion Client property callback
}
} // namespace {{ generatedNamespace }}
