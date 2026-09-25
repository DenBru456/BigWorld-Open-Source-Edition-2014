#ifndef ENTITY_EXTENSION_FACTORY_HPP
#define ENTITY_EXTENSION_FACTORY_HPP

#include "connection_model/bw_entity.hpp"
#include "connection_model/entity_extension_factory_base.hpp"


{% for entity in entityDescriptions %}
class {{ entity.name }};
class {{ entity.name }}Extension;
{%- endfor %}

/**
 *	This class is responsible for creating instances of BWEntity with the
 *	correct sub-class, based on the entity type ID.
 */
class EntityExtensionFactory : public BW::EntityExtensionFactoryBase
{
public:
{%- for entity in entityDescriptions %}
	virtual {{ entity.name }}Extension * createForEntity( const {{ entity.name }} & entity ) = 0;
{%- endfor %}
};


#endif // ENTITY_EXTENSION_FACTORY_HPP

