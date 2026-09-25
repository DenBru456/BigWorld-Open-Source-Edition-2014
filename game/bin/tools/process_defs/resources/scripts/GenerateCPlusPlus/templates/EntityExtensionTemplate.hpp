#ifndef {{ entity.name }}_ENTITY_EXTENSION_HPP
#define {{ entity.name }}_ENTITY_EXTENSION_HPP

#include "{{ entityPath }}/{{ entity.name }}.hpp"

#include "connection_model/entity_extension.hpp"
#include "GeneratedTypes.hpp"


/**
 *	This class implements the app-specific logic for the {{ entity.name }} entity.
 */
class {{ entity.name }}Extension : public BW::EntityExtension
{
public:
	{{ entity.name }}Extension( const {{ entity.name }} * pEntity ) :
		EntityExtension( pEntity )
	{
	}

	const {{ entity.name }} * pEntity() const
	{
		return static_cast< const {{ entity.name }} * >( this->EntityExtension::pEntity() );
	}

	// Client methods
{% for method in entity.clientMethods %}
	virtual void {{ method.name }}(
			{%- for arg in method.args %}
			const {{ arg.1|ctype }} & {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}{% if not loop.last %},{% endif %}
			{%- endfor %} ) {};
{% endfor %}


	// Cell to Client property callbacks (optional)
{% for property in entity.cellToClientProperties %}

	virtual void set_{{ property.name }}( const {{ property.type|ctype }} & oldValue ) {};

	virtual void reset_{{ property.name }}( const {{ property.type|ctype }} & oldValue )
		{ this->set_{{ property.name }}( oldValue ); };

{%- if not property.isConst %}

	/**
	 *	This method implements the property setter callback method for the
	 *	property {{ property.name }}. 
	 *	It is called when a single sub-property element has changed. The
	 *	location of the element is described in the given change path.
	 */
	virtual void setNested_{{ property.name }}( const BW::NestedPropertyChange::Path & path,
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
	virtual void setSlice_{{ property.name }}( const BW::NestedPropertyChange::Path & path,
			int startIndex, int endIndex, 
			const {{ property.type|ctype }} & oldValue )
	{
		this->set_{{ property.name }}( oldValue );
	}

{% endif -%}
{%- endfor %}

	typedef {{ entity.name }} EntityType;
};


#endif // {{ entity.name }}_ENTITY_EXTENSION_HPP

