#ifndef ENTITY_FACTORY_HPP
#define ENTITY_FACTORY_HPP

#include "connection_model/bw_entity_factory.hpp"


namespace BW
{

class BWEntity;

} // namespace BW


/**
 *	This class is responsible for creating instances of BWEntity with the
 *	correct sub-class, based on the entity type ID.
 */
class EntityFactory : public BW::BWEntityFactory
{
private:
	// From BWEntityFactory
	virtual BW::BWEntity * doCreate( BW::EntityTypeID type,
			BW::BWConnection * pBWConnection );
};


#endif // ENTITY_FACTORY_HPP

