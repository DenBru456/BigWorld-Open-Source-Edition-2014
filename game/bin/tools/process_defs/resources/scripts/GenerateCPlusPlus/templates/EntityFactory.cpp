#include "EntityFactory.hpp"


{% for entity in entityDescriptions %}
#include "{{entityPath}}/{{ entity.name }}.hpp"{% endfor %}


/**
 *	This method creates the appropriate sub-class instance of BWEntity based on
 *	the given entity type ID.
 *
 *	@param typeID	The ID of the entity type to create.
 *	@param pBWConnection A pointer to the connection to the BigWorld server.
 *
 *	@return 	An instance of the appropriate sub-class of BWEntity, or NULL
 *				if the entity type ID is invalid.
 */
BW::BWEntity * EntityFactory::doCreate( BW::EntityTypeID entityTypeID,
		BW::BWConnection * pBWConnection )
{
	BW::BWEntity * pEntity = NULL;

	switch (entityTypeID)
	{
{% for entity in entityDescriptions %}		case {{ entity.clientIndex|rjust( "3" ) }}: pEntity = new {{ entity.name }}( pBWConnection ); break;
{% endfor %}	}

	return pEntity;
}


// EntityFactory.cpp

