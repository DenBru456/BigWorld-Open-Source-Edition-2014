#ifndef GENERATED_TYPES_HPP
#define GENERATED_TYPES_HPP

#include "cstdmf/stdmf.hpp"
#include "cstdmf/unique_id.hpp"
#include "cstdmf/value_or_null.hpp"

#include "connection_model/nested_property_change.hpp"
#include "connection_model/sequence_value_type.hpp"

#include "math/vector2.hpp"
#include "math/vector3.hpp"
#include "math/vector4.hpp"


{% for fixedDictType in fixedDictTypes %}
// -----------------------------------------------------------------------------
// Section: {{ fixedDictType.name }} FIXED_DICT property type
// -----------------------------------------------------------------------------

/**
 *	This class represents {{ fixedDictType.name }} 
 *	FIXED_DICT property values.
 */
class {{ fixedDictType.name }}
{
public:
	bool initFromStream( BW::BinaryIStream & data );
	bool addToStream( BW::BinaryOStream & data ) const;
	bool applyChange( BW::NestedPropertyChange & change );

	// Sub-property members
{% for member in fixedDictType.members %}
	{{ member.type }} {{ member.name }};{% endfor %}
};


/**
 *	Incoming streaming operators for {{ fixedDictType.name }}.
 */
inline BW::BinaryIStream & operator>>( BW::BinaryIStream & stream,
		{{ fixedDictType.name }} & fixedDict )
{
	if (!fixedDict.initFromStream( stream ))
	{
		ERROR_MSG( "{{ fixedDictType.name }}::initFromStream: Failed\n" );
	}

	return stream;
}


/**
 *	Outgoing streaming operators for {{ fixedDictType.name }}.
 */
inline BW::BinaryOStream & operator<<( BW::BinaryOStream & stream,
		const {{ fixedDictType.name }} & fixedDict )
{
	if (!fixedDict.addToStream( stream ))
	{
		ERROR_MSG( "{{ fixedDictType.name }}::addToStream: Failed\n" );
	}

	return stream;
}


/**
 *	Equality operator for {{ fixedDictType.name }}.
 */
inline bool operator==( const {{ fixedDictType.name }} & left,
		const {{ fixedDictType.name }} & right )
{
{% for member in fixedDictType.members %}
	if (left.{{ member.name }} != right.{{ member.name }})
	{
		return false;
	}
{% endfor %}
	return true;
}


/**
 *	Inequality operator for {{ fixedDictType.name }}.
 */
inline bool operator!=( const {{ fixedDictType.name }} & left,
		const {{ fixedDictType.name }} & right )
{
	return !(left==right);
}


namespace BW
{

/**
 *	Template specialisation for property changes for {{ fixedDictType.name }}.
 */
template<>
inline bool NestedPropertyChange::apply( {{ fixedDictType.name }} & value )
{
	return value.applyChange( *this );
}

} // namespace BW

{% endfor %}


#endif // GENERATED_TYPES_HPP

