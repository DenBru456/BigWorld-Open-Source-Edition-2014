#ifndef {{ entity.name }}_{{ component }}MB_HPP
#define {{ entity.name }}_{{ component }}MB_HPP

#include "GeneratedTypes.hpp"

#include "connection_model/server_entity_mail_box.hpp"


namespace {{ component }}MB
{

/**
 *	This class describes the interface to the {{ component }} part of the
 *	{{ entity.name }} entity.
 */
class {{ entity.name }} : public BW::ServerEntityMailBox
{
public:
	/**
	 *	Constructor.
	 */
	{{ entity.name }}( BW::BWEntity & entity ) : ServerEntityMailBox( entity )
	{
	}

	// {{ component }} methods
{% for method in methods %}{% if method.isExposed %}	{{ method|methodDeclaration }} const;
{% endif %}{% endfor %}
};

} // namespace {{ component }}MB

#endif // {{ entity.name }}_{{ component }}MB_HPP

