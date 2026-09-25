#ifndef {{ className }}_HPP
#define {{ className }}_HPP

#include "{{ extensionsPath }}/{{ entity.name }}Extension.hpp"


/**
 *	This class implements the app-specific logic for the {{ entity.name }} entity.
 */
class {{ className }} : public {{ entity.name }}Extension
{
public:
	{{ className }}( const {{ entity.name }} * pEntity ) : {{ entity.name }}Extension( pEntity ) {}

	// Client methods
{% for method in entity.clientMethods %}
	virtual void {{ method.name }}(
			{%- for arg in method.args %}
			const {{ arg.1|ctype }} & {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}{% if not loop.last %},{% endif %}
			{%- endfor %} );
{% endfor %}


	// Client property callbacks (optional)
{% for property in entity.cellToClientProperties %}

	virtual void set_{{ property.name }}( const {{ property.type|ctype }} & oldValue );
	virtual void reset_{{ property.name }}( const {{ property.type|ctype }} & oldValue );
{%- if not property.isConst %}

	virtual void setNested_{{ property.name }}( const BW::NestedPropertyChange::Path & path,
			const {{ property.type|ctype }} & oldValue );

	virtual void setSlice_{{ property.name }}( const BW::NestedPropertyChange::Path & path,
			int startIndex, int endIndex, 
			const {{ property.type|ctype }} & oldValue );
{%- endif %}
{%- endfor %}
};


#endif // {{ className }}_HPP

