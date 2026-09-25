#include "{{ className }}.hpp"


// -----------------------------------------------------------------------------
// Section: ClientMethod implementations 
// -----------------------------------------------------------------------------
{%- for method in entity.clientMethods %}

/**
 *	This method implements the ClientMethod {{ method.name }}.
 */
void {{ className }}::{{ method.name }}( {% for arg in method.args %}
			const {{ arg.1|ctype }} & {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}{% if not loop.last %},{% endif %}{% endfor %} )
{
	// DEBUG_MSG( "{{ className }}::set_{{ method.name }}\n" );
}

{% endfor -%}


// -----------------------------------------------------------------------------
// Section: Property setter callbacks
// -----------------------------------------------------------------------------
{%- for property in entity.cellToClientProperties %}

/**
 *	This method implements the setter callback for the property {{ property.name }}.
 */
void {{ className }}::set_{{ property.name }}( const {{ property.type|ctype }} & oldValue )
{
	// DEBUG_MSG( "{{ className }}::set_{{ property.name }}\n" );
}

/**
 *	This method implements the reset callback for the property {{ property.name }}.
 */
void {{ className }}::reset_{{ property.name }}( const {{ property.type|ctype }} & oldValue )
{
	// DEBUG_MSG( "{{ className }}::reset_{{ property.name }}\n" );
	// By default, we pass it back to set_{{ property.name }},
	// which is also what happens if this method is not overriden.
	this->set_{{ property.name }}( oldValue );
}
{%- if not property.isConst %}

/**
 *	This method implements the property setter callback method for the
 *	property {{ property.name }}. 
 *	It is called when a single sub-property element has changed. The
 *	location of the element is described in the given change path.
 */
void {{ className }}::setNested_{{ property.name }}( const NestedPropertyChange::Path & path, 
		const {{ property.type|ctype }} & oldValue )
{
	this->set_{{ property.name }}( oldValue );
}

/**
 *	This method implements the property setter callback method for the
 *	property {{ property.name }}. 
 *	It is called when a single sub-property slice has changed. The
 *	location of the ARRAY element is described in the given change path,
 *	and the slice within that element is described in the two given slice
 *	indices. 
 */
void {{ className }}::setSlice_{{ property.name }}( const NestedPropertyChange::Path & path,
		int startIndex, int endIndex, 
		const {{ property.type|ctype }} & oldValue )
{
	this->set_{{ property.name }}( oldValue );
}
{% endif -%}

{% endfor %}


// {{ className }}.{{ entityTemplateSourceExtension }}

