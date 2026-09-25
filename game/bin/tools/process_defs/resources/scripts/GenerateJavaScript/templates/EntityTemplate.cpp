#include "{{ entityPath }}/{{ entity.name }}.hpp"

#include "{{ extensionsPath }}/{{ entity.name }}Extension.hpp"
#include "EntityExtensionFactory.hpp"

#include "connection_model/bw_connection.hpp"
#include "connection_model/entity_extension.hpp"

#include "cstdmf/binary_stream.hpp"
#include "cstdmf/bit_reader.hpp"
#include "cstdmf/stdmf.hpp"

{% if entity.hasCellMailBox or entity.hasBaseMailBox %}
#ifdef _MSC_VER
#pragma warning( push )
// C4355: 'this' : used in base member initializer list
#pragma warning( disable: 4355 )
#endif // _MSC_VER
{% endif %}

/**
 *	Constructor.
 */
{{ entity.name }}::{{ entity.name }}( BW::BWConnection * pBWConnection ) :
	BW::BWEntity( pBWConnection ){% if entity.hasCellMailBox %},
	cell_( *this ){% endif %}{% if entity.hasBaseMailBox %},
	base_( *this ){% endif %}
{
}

{% if entity.hasCellMailBox or entity.hasBaseMailBox %}
#ifdef _MSC_VER
#pragma warning( pop )
#endif // _MSC_VER
{% endif %}


/**
 *	Destructor.
 */
{{ entity.name }}::~{{ entity.name }}()
{
}


/**
 *	This method is an override from BWEntity.
 */
const BW::string {{ entity.name }}::entityTypeName() const
{
	return "{{ entity.name }}";
}


/**
 *	This method initialises the base {{ entity.name }} player from the stream. At
 *	this point, the player does not have a cell yet, so only BASE_AND_CLIENT
 *	properties are streamed here.
 */
bool {{ entity.name }}::initBasePlayerFromStream( BW::BinaryIStream & data )
{
{% for property in entity.baseToClientProperties %}
	data >> {{ property.name }}_;{% endfor %}

	return !data.error();
}


/**
 *	This method initialises the cell {{ entity.name }} player from stream. At
 *	this point, the OWN_CLIENT, OTHER_CLIENT cell properties are streamed.
 */
bool {{ entity.name }}::initCellPlayerFromStream( BW::BinaryIStream & data )
{
{% if entity.hasCellMailBox %}
{% for property in entity.cellToClientProperties %}
	data >> {{ property.name }}_;{% endfor %}

	return !data.error();
{% else %}
	ERROR_MSG( "Received unexpected Cell Player for {{ entity.name }}\n" );

	return false;
{% endif %}
}


/**
 *	This method restores the {{ entity.name }} player from stream. At
 *	this point, the BASE_AND_CLIENT base properties, then OWN_CLIENT
 *	and OTHER_CLIENT cell properties are streamed.
 */
bool {{ entity.name }}::restorePlayerFromStream( BW::BinaryIStream & data )
{
{% if entity.hasCellMailBox %}
	// Deliberately discarding BASE_AND_CLIENT properties from the stream, as
	// we don't support updating base properties during the life of a
	// server connection
{% for property in entity.baseToClientProperties %}
	{{ property.type|ctype }} dummy{{ property.name }};
	data >> dummy{{ property.name }};
{% endfor %}

	// Apply cell properties and call the reset_ callback if required.
{% for property in entity.cellToClientProperties %}
	{{ property.type|ctype }} old{{ property.name }} = {{ property.name }}_;
	data >> {{ property.name }}_;
	if (!BW::isEqual( {{ property.name }}_, old{{ property.name }} ))
	{
		BW::EntityExtensions::iterator iter = entityExtensions_.begin();

		while (iter != entityExtensions_.end())
		{
			{{ entity.name }}Extension * pExt = static_cast< {{ entity.name }}Extension * >( *iter );
			pExt->reset_{{ property.name }}( old{{ property.name }} );

			++iter;
		}
	}
{% endfor %}

	return !data.error();
{% else %}
	ERROR_MSG( "Received unexpected Player restore for {{ entity.name }}\n" );

	return false;
{% endif %}
}


/**
 *	This method is called in response to receiving a single property value
 *	change. This can be a standard change, a nested single-element change, or a
 *	nested slice change.
 */
void {{ entity.name }}::onProperty( int propertyID, BW::BinaryIStream & data, 
		bool isInitialising )
{
	//DEBUG_MSG( "{{ entity.name }}::onProperty: %d\n", propertyID );

{% if entity.cellToClientProperties|length != 0 %}
	switch (propertyID)
	{
{%- for property in entity.cellToClientProperties %}
	case {{ property.clientServerFullIndex }}: // {{ property.name }}
	{
		{{ property.type|ctype }} oldValue = {{ property.name }}_;
		data >> {{ property.name }}_;

		if (!isInitialising)
		{
			BW::EntityExtensions::iterator iter = entityExtensions_.begin();

			while (iter != entityExtensions_.end())
			{
				{{ entity.name }}Extension * pExt = static_cast< {{ entity.name }}Extension * >( *iter );
				pExt->set_{{ property.name }}( oldValue );

				++iter;
			}
		}
		break;
	}
{% endfor %}

	default:
		ERROR_MSG( "Invalid property change on {{ entity.name }}, index = %d\n",
			propertyID );
		break;
	}
{% else %}
	ERROR_MSG( "Invalid property change on {{ entity.name }}, index = %d\n",
		propertyID );
{% endif %}
}


/**
 *	This method is called when a nested property change has been sent from
 *	the server.
 */
void {{ entity.name }}::onNestedProperty( BW::BinaryIStream & data, bool isSlice,
	   bool isInitialising )
{
	if (isSlice)
	{
		this->onSlicedPropertyChange( data, isInitialising );
	}
	else
	{
		this->onSinglePropertyChange( data, isInitialising );
	}
}


/**
 *	This method handles a single property nested change.
 */
void {{ entity.name }}::onSinglePropertyChange( BW::BinaryIStream & data,
	bool isInitialising )
{
	BW::NestedPropertyChange change( BW::NestedPropertyChange::SINGLE, data );

	static const int NUM_PROPERTIES = {{ entity.clientProperties | count }};
	int propertyID = change.readNextIndex( NUM_PROPERTIES );

	if (change.isFinished())
	{
		this->onProperty( propertyID, data, false );
		return;
	}

{%- for property in entity.cellToClientProperties if not property.isConst -%}
{%- if loop.first %}

	switch (propertyID)
	{
{%- endif %}
	case {{ property.clientServerFullIndex }}: // {{ property.name }}
	{
		{{ property.type|ctype }} oldValue;
		oldValue = {{ property.name }}_;

		if (!change.apply( {{ property.name }}_ ))
		{
			ERROR_MSG( "Failed to set %s from stream\n",
					"{{ entity.name }}::{{ property.name }}" );
			return;
		}

		if (!isInitialising)
		{
			BW::EntityExtensions::iterator iter = entityExtensions_.begin();

			while (iter != entityExtensions_.end())
			{
				{{ entity.name }}Extension * pExt = static_cast< {{ entity.name }}Extension * >( *iter );
				pExt->setNested_{{ property.name }}( change.path(), oldValue );

				++iter;
			}
		}
		break;
	}
{% if loop.last %}
	default:
		ERROR_MSG( "Invalid property change on {{ entity.name }}, index = %d\n", 
			propertyID );
		break;
	}
{%- endif -%}
{%- else %}
	ERROR_MSG( "Invalid property change on {{ entity.name }}, index = %d\n", 
		propertyID );
{%- endfor %}
}


/**
 *	This method handles a nested property slice change.
 */
void {{ entity.name }}::onSlicedPropertyChange( BW::BinaryIStream & data,
	bool isInitialising )
{
	BW::NestedPropertyChange change( BW::NestedPropertyChange::SLICE, data );

	const int NUM_PROPERTIES = {{ entity.clientProperties | count }};
	int propertyID = change.readNextIndex( NUM_PROPERTIES );

	// Entity-level is not slice-able.
	MF_ASSERT( !change.isFinished() );

{%- for property in entity.cellToClientProperties if not property.isConst -%}
{%- if loop.first %}

	switch (propertyID)
	{
{%- endif %}
	case {{ property.clientServerFullIndex }}: // {{ property.name }}
	{
		{{ property.type|ctype }} oldValue;
		oldValue = {{ property.name }}_;

		if (!change.apply( {{ property.name }}_ ))
		{
			ERROR_MSG( "Failed to set slice for %s from stream\n",
				"{{ entity.name }}::{{ property.name }}" );
			return;
		}

		const BW::NestedPropertyChange::Slice & oldSlice = change.oldSlice();

		if (!isInitialising)
		{
			BW::EntityExtensions::iterator iter = entityExtensions_.begin();

			while (iter != entityExtensions_.end())
			{
				{{ entity.name }}Extension * pExt = static_cast< {{ entity.name }}Extension * >( *iter );
				pExt->setSlice_{{ property.name }}( change.path(), oldSlice.first, oldSlice.second,
					oldValue );

				++iter;
			}
		}
		break;
	}
{%- if loop.last %}

	default:
		ERROR_MSG( "Invalid slice property change on {{ entity.name }}, index = %d\n",
			propertyID );
		break;
	}
{%- endif -%}
{%- else %}

	ERROR_MSG( "Invalid slice property change on {{ entity.name }}, index = %d\n", 
		propertyID );
{%- endfor %}
}


/**
 *	This method is called to dispatch a remote method request from the server.
 */
void {{ entity.name }}::onMethod( int methodID, BW::BinaryIStream & data )
{
	//DEBUG_MSG( "{{ entity.name }}::onMethod: %d\n", methodID );

{% if entity.clientMethods|length != 0 %}
	switch (methodID)
	{
{%- for method in entity.clientMethods %}
	case {{ method.exposedIndex }}: // {{ method.name }}
	{
{%- for arg in method.args %}
		{{ arg.1|ctype }} {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %};
		data >> {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %};
{%- endfor %}

		//DEBUG_MSG( "Calling {{ entity.name }}::{{ method.name }}\n" );

		BW::EntityExtensions::iterator iter = entityExtensions_.begin();

		while (iter != entityExtensions_.end())
		{
			{{ entity.name }}Extension * pExt = static_cast< {{ entity.name }}Extension * >( *iter );
			pExt->{{ method.name }}( {% for arg in method.args %}{% if not loop.first %},
				{% endif %}{% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}{% endfor %} );

			++iter;
		}

		break;
	}
{% endfor %}

	default:
		ERROR_MSG( "{{ entity.name }}::onMethod: Unknown method %d\n",
				methodID );
		break;
	}
{% else %}
	ERROR_MSG( "{{ entity.name }}::onMethod: Unknown method %d\n",
			methodID );
{% endif %}
}


/**
 *	This method is called when the network layer needs to know how big
 *	a given method message is.
 */
int {{ entity.name }}::getMethodStreamSize( int methodID ) const
{
{% if entity.clientMethods|length != 0 %}
	switch (methodID)
	{
{% for method in entity.clientMethods %}
	case {{ method.exposedIndex }}: // {{ method.name }}
		return {{ method.streamSize }};
{% endfor %}
	default:
		CRITICAL_MSG( "{{ entity.name }}::getMethodStreamSize: Unknown method %d\n",
				methodID );
		break;
	}
{% else %}
	CRITICAL_MSG( "{{ entity.name }}::getMethodStreamSize: Unknown method %d\n",
			methodID );
{% endif %}

	return 0;
}


/**
 *	This method is called when the network layer needs to know how big
 *	a given property message is.
 */
int {{ entity.name }}::getPropertyStreamSize( int propertyID ) const
{
{% if entity.cellToClientProperties|length != 0 %}
	switch (propertyID)
	{
{% for property in entity.cellToClientProperties %}
	case {{ property.clientServerFullIndex }}: // {{ property.name }}
		return {{ property.streamSize }};
{%endfor%}
	default:
		CRITICAL_MSG( "{{ entity.name }}::getPropertyStreamSize: Unknown property %d\n",
				propertyID );
		break;
	}
{% else %}
	CRITICAL_MSG( "{{ entity.name }}::getPropertyStreamSize: Unknown property %d\n",
			propertyID );
{% endif %}

	return 0;
}


/**
 *	This method creates the appropriate EntityExtension for a given entity
 *	extension factory.
 */
BW::EntityExtension *
	{{ entity.name }}::createExtension( BW::EntityExtensionFactoryBase * pFactory )
{
	return static_cast< EntityExtensionFactory * >(
			pFactory )->createForEntity( *this );
}


/**
 *	This static method creates a new Local entity on the given BWConnection of
 *	this type.
 */
/* static */ BW::BWEntity * {{ entity.name }}::createLocalEntity(
	BW::BWConnection * pConnection, BW::SpaceID spaceID, BW::EntityID vehicleID,
	const BW::Position3D & position, const BW::Direction3D & direction
{%- for property in entity.cellToClientProperties if property.isOtherClientData %},
		const {{ property.type|ctype }} & {{ property.name }}
{%- endfor %} )
{
	BW::MemoryOStream propertyStream;
{%- for property in entity.cellToClientProperties if property.isOtherClientData %}
{%- if loop.first %}

	// Tagged property stream for cell entity creation:
	// uint8 property count, then each property with uint8 tag
	propertyStream << (BW::uint8){{ entity.cellToClientProperties|length }};
{%- endif %}

	propertyStream << (BW::uint8){{ property.clientServerFullIndex }};
	propertyStream << {{ property.name }};

{%- endfor %}

	return pConnection->createLocalEntity( {{ entity.clientIndex }}, spaceID,
		vehicleID, position, direction, propertyStream );
}


/**
 *	This static method populates the given stream with the neccessary data to
 *	create a new Base Player entity of the given type.
 *
 *	@return	The EntityTypeID for the generated stream.
 */
/* static */ BW::EntityTypeID {{ entity.name }}::generateBasePlayerStream(
	BW::BinaryOStream & outputStream
{%- for property in entity.baseToClientProperties %},
		const {{ property.type|ctype }} & {{ property.name }}
{%- endfor %} )
{
{% for property in entity.baseToClientProperties %}
	outputStream << {{ property.name }};{% endfor %}

	return {{ entity.clientIndex }};
}


{% if hasCellMailbox -%}
/**
 *	This static method populates the given stream with the neccessary data to
 *	create a new Cell Player entity of the given type.
 */
/* static */ void {{ entity.name }}::generateCellPlayerStream(
	BW::BinaryOStream & outputStream
{%- for property in entity.cellToClientProperties %},
		const {{ property.type|ctype }} & {{ property.name }}
{%- endfor %} )
{
{% for property in entity.cellToClientProperties %}
	outputStream << {{ property.name }};{% endfor %}
}


{% endif -%}
// {{ entity.name }}.cpp

