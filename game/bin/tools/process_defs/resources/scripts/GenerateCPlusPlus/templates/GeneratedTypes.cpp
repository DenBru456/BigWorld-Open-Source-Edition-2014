#include "{{ entityPath }}GeneratedTypes.hpp"

#include "cstdmf/binary_stream.hpp"


{% for fixedDictType in fixedDictTypes %}


// -----------------------------------------------------------------------------
// Section: {{ fixedDictType.name }} FIXED_DICT property type
// -----------------------------------------------------------------------------


/**
 *	This method initialises the {{ fixedDictType.name }} from a stream.
 */
bool {{ fixedDictType.name }}::initFromStream( BW::BinaryIStream & data )
{
{% for member in fixedDictType.members %}	data >> this->{{ member.name }};
{% endfor %}

	return !data.error();
}


/**
 *	This method writes the {{ fixedDictType.name }} to a stream.
 */
bool {{ fixedDictType.name }}::addToStream( BW::BinaryOStream & data ) const
{
{% for member in fixedDictType.members %}	data << this->{{ member.name }};
{% endfor %}

	return true;
}


/**
 *	This method applies a given nested property change.
 */
bool {{ fixedDictType.name }}::applyChange( BW::NestedPropertyChange & change )
{
	static const int NUM_PROPERTIES = {{ fixedDictType.members | count }};
	int index = change.readNextIndex( NUM_PROPERTIES );

	MF_ASSERT( index >= 0 );

	switch (index)
	{
	{% for member in fixedDictType.members %}
	case {{ loop.index0 }}:
	{
		if (!change.isFinished())
		{
			// Sub-property change.
			return change.apply( this->{{ member.name }} );
		}
		else
		{
			// Change at this level.
			change.data() >> this->{{ member.name }};
			return !change.data().error();
		}
		break;
	}
	{% endfor %}
	default:
		return false;
		break;
	}
}
{% endfor %}


// GeneratedTypes.cpp

