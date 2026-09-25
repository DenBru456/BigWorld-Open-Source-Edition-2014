#include "{{ entityMailBoxPath }}/{{ entity.name }}_{{ component }}MB.hpp"

#include "cstdmf/binary_stream.hpp"


namespace {{ component }}MB
{

// -----------------------------------------------------------------------------
// This implements the interface to the {{ component }} part of the entity.
// -----------------------------------------------------------------------------
{% for method in methods %}{% if method.isExposed %}


/**
 *	This method implements calling the {{ method.name }}() {{ component }} method.
 */
{{ method|methodDeclaration( className )}} const
{
	bool shouldDrop;
	{% if method.args %}BW::BinaryOStream * pStream = {% endif -%}
	this->startMessage( {{ method.exposedIndex }}, {% if component == "Base" %}true{% else: %}false{% endif %}, shouldDrop );
{%- if method.args %}

	if (shouldDrop)
	{
		return;
	}

	if (pStream)
	{
{%- for arg in method.args %}
		*pStream << {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %};
{%- endfor %}
	}
{%- endif %}
}
{% endif %}{% endfor %}

} // namespace {{ component }}MB


// {{ entity.name }}_{{ component }}MB.cpp

