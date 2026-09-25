#ifndef {{ className }}_HPP
#define {{ className }}_HPP

#include "EntityExtensionFactory.hpp"


namespace BW
{

{% for entity in entityDescriptions %}
class {{ entity.name }};
class {{ entity.name }}Extension;
{%- endfor %}

} // namespace BW


/**
 *	This class is responsible for creating instances of BWEntity with the
 *	correct sub-class, based on the entity type ID.
 */
class {{ className }} : public EntityExtensionFactory
{
public:
{%- for entity in entityDescriptions %}
	virtual {{ entity.name }}Extension * createForEntity( const {{ entity.name }} & entity );
{%- endfor %}
};


#endif // {{ className }}_HPP

