#include "{{ entityPath }}GeneratedTypes.hpp"

#include "cstdmf/binary_stream.hpp"


{%- for fixedDictType in fixedDictTypes %}
// -----------------------------------------------------------------------------
// Section: {{ fixedDictType.className }} FIXED_DICT property type
// -----------------------------------------------------------------------------


/**
 *	This method initialises the {{ fixedDictType.className }} from a stream.
 */
bool {{ fixedDictType.className }}::initFromStream( BW::BinaryIStream & data )
{
{%- for memberName, memberType in fixedDictType.members %}
	data >> {{ memberName }};
{%- endfor %}

	return !data.error();
}


/**
 *	This method writes the {{ fixedDictType.className }} to a stream.
 */
bool {{ fixedDictType.className }}::addToStream( BW::BinaryOStream & data ) const
{
{%- for memberName, memberType in fixedDictType.members %}
	data << {{ memberName }};
{%- endfor %}

	return true;
}


/**
 *	This method applies a given nested property change.
 */
bool {{ fixedDictType.className }}::applyChange( BW::NestedPropertyChange & change )
{
	static const int NUM_PROPERTIES = {{ fixedDictType.members | count }};
	int index = change.readNextIndex( NUM_PROPERTIES );

	MF_ASSERT( index >= 0 );

	switch (index)
	{
	{%- for memberName, memberType in fixedDictType.members %}
	case {{ loop.index0 }}:
	{
		if (!change.isFinished())
		{
			// Sub-property change.
			return change.apply( {{ memberName }} );
		}
		else
		{
			// Change at this level.
			change.data() >> {{ memberName }};
			return !change.data().error();
		}
		break;
	}
	{%- endfor %}
	default:
		return false;
		break;
	}
}


{%- endfor %}



// GeneratedTypes.cpp

