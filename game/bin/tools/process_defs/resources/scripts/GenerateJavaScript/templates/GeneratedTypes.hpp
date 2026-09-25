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
// Section: {{ fixedDictType.className }} FIXED_DICT property type
// -----------------------------------------------------------------------------

/**
 *	This class represents {{ fixedDictType.className }} 
 *	FIXED_DICT property values.
 *
 *	{{ fixedDictType.desc }}
 *
 *	Depends on {{ fixedDictType.dependantTypes|list }}.
 */
class {{ fixedDictType.className }}
{
public:
	/**
	 *	Constructor (default).
	 */
	{{ fixedDictType.className }}() :
		{%- for memberName, memberType in fixedDictType.members %}
		{{ memberName }}(){%- if not loop.last %},{%- endif %}
		{%- endfor %}
	{}


	/**
	 *	Copy constructor.
	 */
	{{ fixedDictType.className }}( const {{ fixedDictType.className }} & other ) :
		{%- for memberName, memberType in fixedDictType.members %}
		{{ memberName }}( other.{{ memberName }} ){%- if not loop.last %},{%- endif %}
		{%- endfor %}
	{}

	/**
	 *	Assignment operator.
	 */
	{{ fixedDictType.className }} & operator=( const {{ fixedDictType.className }} & other )
	{
		{%- for memberName, memberType in fixedDictType.members %}
		{{ memberName }} = other.{{ memberName }};
		{%- endfor %}

		return *this;
	}


	bool initFromStream( BW::BinaryIStream & data );
	bool addToStream( BW::BinaryOStream & data ) const;
	bool applyChange( BW::NestedPropertyChange & change );


	// Sub-property members
{%- for memberName, memberType in fixedDictType.members %}
	{{ memberType.toCType() }} {{ memberName }};
{%- endfor %}
};


/**
 *	Incoming streaming operators for {{ fixedDictType.className }}.
 */
inline BW::BinaryIStream & operator>>( BW::BinaryIStream & stream,
		{{ fixedDictType.className }} & fixedDict )
{
	if (!fixedDict.initFromStream( stream ))
	{
		ERROR_MSG( "{{ fixedDictType.className }}::initFromStream: Failed\n" );
	}

	return stream;
}


/**
 *	Outgoing streaming operators for {{ fixedDictType.className }}.
 */
inline BW::BinaryOStream & operator<<( BW::BinaryOStream & stream,
		const {{ fixedDictType.className }} & fixedDict )
{
	if (!fixedDict.addToStream( stream ))
	{
		ERROR_MSG( "{{ fixedDictType.className }}::addToStream: Failed\n" );
	}

	return stream;
}


/**
 *	Equality operator for {{ fixedDictType.name }}.
 */
inline bool operator==( const {{ fixedDictType.className }} & left,
		const {{ fixedDictType.className }} & right )
{
{% for memberName, memberType in fixedDictType.members %}
	if (left.{{ memberName }} != right.{{ memberName }})
	{
		return false;
	}
{% endfor %}
	return true;
}


/**
 *	Inequality operator for {{ fixedDictType.name }}.
 */
inline bool operator!=( const {{ fixedDictType.className }} & left,
		const {{ fixedDictType.className }} & right )
{
	return !(left == right);
}


BW_BEGIN_NAMESPACE

/**
 *	Template specialisation for property changes for {{ fixedDictType.className }}.
 */
template<>
inline bool BW::NestedPropertyChange::apply( {{ fixedDictType.className }} & value )
{
	return value.applyChange( *this );
}

BW_END_NAMESPACE


{% endfor %}


#endif // GENERATED_TYPES_HPP

