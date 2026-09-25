#ifndef {{ entity.name }}_HPP
#define {{ entity.name }}_HPP

#include "cstdmf/bw_string.hpp"
#include "connection_model/bw_entity.hpp"

#include "GeneratedTypes.hpp"


{%- if entity.hasBaseMailBox %}
#include "{{ entityMailBoxPath }}/{{ entity.name }}_BaseMB.hpp"
{%- endif %}
{%- if entity.hasCellMailBox %}
#include "{{ entityMailBoxPath }}/{{ entity.name }}_CellMB.hpp"
{%- endif %}


/**
 *	This class is the base class for the {{ entity.name }} entity type.
 */
class {{ entity.name }} : public BW::BWEntity
{
public:
	{{ entity.name }}( BW::BWConnection * pBWConnection );
	virtual ~{{ entity.name }}();

	// Property accessors
{%- for property in entity.clientProperties %}
	const {{ property.type|ctype|ljust( "25" ) }} & {{ property.name }}() const;
{%- endfor %}

	// Mailboxes (if any)
{%- if entity.hasCellMailBox %}
	const CellMB::{{ entity.name }} & cell() const 
	{
		return cell_;
	}
{%- endif %}
{%- if entity.hasBaseMailBox %}
	const BaseMB::{{ entity.name }} & base() const
	{
		return base_;
	}
{%- endif %}

	// BWEntity overrides
	virtual const BW::string entityTypeName() const;
	virtual bool initBasePlayerFromStream( BW::BinaryIStream & data );
	virtual bool initCellPlayerFromStream( BW::BinaryIStream & data );
	virtual bool restorePlayerFromStream( BW::BinaryIStream & data );

	virtual void onProperty( int propertyID, BW::BinaryIStream & data,
		bool isInitialising );
	virtual void onMethod( int methodID, BW::BinaryIStream & data );

	virtual void onNestedProperty( BW::BinaryIStream & data, bool isSlice,
			bool isInitialising );

	virtual int getMethodStreamSize( int methodID ) const;
	virtual int getPropertyStreamSize( int propertyID ) const;

	virtual BW::EntityExtension *
		createExtension( BW::EntityExtensionFactoryBase * pFactory );

	// Local entity creation helper
	static BW::BWEntity * createLocalEntity( BW::BWConnection * pBWConnection,
		BW::SpaceID spaceID, BW::EntityID vehicleID,
		const BW::Position3D & position, const BW::Direction3D & direction
{%- for property in entity.cellToClientProperties if property.isOtherClientData %},
		const {{ property.type|ctype }} & {{ property.name }}
{%- endfor %} );

	// Player entity creation helpers
	static BW::EntityTypeID generateBasePlayerStream(
		BW::BinaryOStream & outputStream
{%- for property in entity.baseToClientProperties %},
		const {{ property.type|ctype }} & {{ property.name }}
{%- endfor %} );
{%- if hasCellMailbox %}

	static void generateCellPlayerStream( BW::BinaryOStream & outputStream
{%- for property in entity.cellToClientProperties %},
		const {{ property.type|ctype }} & {{ property.name }}
{%- endfor %} );
{% endif %}

private:
	void onSinglePropertyChange( BW::BinaryIStream & data, bool isInitialising );
	void onSlicedPropertyChange( BW::BinaryIStream & data, bool isInitialising );

{% if entity.hasCellMailBox %}	CellMB::{{ entity.name }} cell_;{% endif %}
{% if entity.hasBaseMailBox %}	BaseMB::{{ entity.name }} base_;{% endif %}

	// Property data members
{% for property in entity.clientProperties %}
	{{ property.type|ctype|ljust( "20" ) }} {{ property.name }}_;
{%- endfor %}
};


{% for property in entity.clientProperties %}
/**
 *	This method is a getter method for the {{ entity.name }}.{{ property.name }} property.
 */
inline const {{ property.type|ctype }} & {{ entity.name }}::{{ property.name }}() const
{
	return {{ property.name }}_;
}


{% endfor %}


#endif // {{ entity.name }}_HPP

