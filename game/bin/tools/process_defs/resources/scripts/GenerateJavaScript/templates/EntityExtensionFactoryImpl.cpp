#include "{{ className }}.hpp"


{%- for entity in entityDescriptions %}
#include "{{ templateExtensionName|format( "" ) }}/{{ templateExtensionName|format( entity.name ) }}.hpp"
{%- endfor %}
{% for entity in entityDescriptions %}
#include "Entities/{{ entity.name }}.hpp"
{%- endfor %}

{% for entity in entityDescriptions %}
{{ entity.name }}Extension * {{ className }}::createForEntity( const {{ entity.name }} & entity )
{
	return new {{ templateExtensionName|format( entity.name ) }}( &entity );
}
{% endfor %}

// {{ className }}.cpp

