#include "EntityExtensionFactoryJS.hpp"

#include "EntityExtensionFactory.hpp"

#include "bindings.hpp"

#include <emscripten/bind.h>


{% for entity in entityDescriptions %}
#include "{{ extensionsPath }}/{{ entity.name }}Extension.hpp"
{%- endfor %}

{% for entity in entityDescriptions %}
#include "{{ entityPath }}/{{ entity.name }}.hpp"
{%- if entity.hasBaseMailBox %}
#include "{{ entityMailBoxPath }}/{{ entity.name }}_BaseMB.hpp"
{%- endif %}
{%- if entity.hasCellMailBox %}
#include "{{ entityMailBoxPath }}/{{ entity.name }}_CellMB.hpp"
{%- endif %}
{%- endfor %}


{% for entity in entityDescriptions %}
/**
 *	The JavaScript entity extension class for {{ entity.name }}.
 */
class {{ entity.name }}ExtensionJS : public {{ entity.name }}Extension
{
public:
	/**
	 *	Constructor.
	 */
	{{ entity.name }}ExtensionJS( const {{ entity.name }} * pEntity, 
				emscripten::val delegate ):
			{{ entity.name }}Extension( pEntity ),
			delegate_( delegate )
	{
	}


	/* Override from EntityExtension */
	virtual void onBecomePlayer()
	{
		delegate_.call< void >( "onBecomePlayer" );
	}


	/* Override from EntityExtension */
	virtual void onEnterAoI( const BW::EntityEntryBlocker & rBlocker )
	{
		// TODO: enable blockers
		delegate_.call< void >( "onEnterAoI" );
	}


	/* Override from EntityExtension */
	virtual void onEnterWorld()
	{
		delegate_.call< void >( "onEnterWorld" );
	}


	/* Override from EntityExtension */
	virtual void onChangeSpace()
	{
		delegate_.call< void >( "onChangeSpace" );
	}


	/* Override from EntityExtension */
	virtual void onLeaveWorld()
	{
		delegate_.call< void >( "onLeaveWorld" );
	}


	/* Override from EntityExtension */
	virtual void onLeaveAoI()
	{
		delegate_.call< void >( "onLeaveAoI" );
	}


	/* Override from EntityExtension */
	virtual void onBecomeNonPlayer()
	{
		delegate_.call< void >( "onBecomeNonPlayer" );
	}


	/* Override from EntityExtension */
	virtual void onChangeControl( bool isControlling, bool isInitialising )
	{
		delegate_.call< void >( "onChangeControl",
			isControlling, isInitialising );
	}

{% for method in entity.clientMethods %}
{%- if loop.first %}
	// Client methods
{%- endif %}

	/**
	 *	This method implements the {{ method.name }} client method.
	 */
	virtual void {{ method.name }}(
			{%- for arg in method.args %}
			const {{ arg.1|ctype }} & {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}{% if not loop.last %},{% endif %}
			{%- endfor %} )
	{
		delegate_.call< void >( "{{ method.name }}"
			{%- for arg in method.args %}
			, {% if arg.0 %}{{ arg.0 }}{% else %}arg{{ loop.index0 }}{% endif %}
			{%- endfor %} );
	}
{%- endfor %}


{%- for property in entity.cellToClientProperties %}
{%- if loop.first %}
	// Cell to Client property callbacks (optional)
{%- endif %}

	/**
	 *	This method implements the setter callback for the 
	 * 	{{ property.name }} property.
	 *
	 *	@param oldValue 	The previous property value.
	 */
	virtual void set_{{ property.name }}( 
			const {{ property.type|ctype }} & oldValue )
	{
		delegate_.call< void >( "set_{{ property.name }}", oldValue );
	}
{%- if not property.isConst %}


	/**
	 *	This method implements the nested property setter callback for the 
	 * 	{{ property.name }} property.
	 *
	 *	@param path 		The path to the sub-property.
	 *	@param oldValue 	The previous value of the sub-property.
	 */
	virtual void setNested_{{ property.name }}( 
			const BW::NestedPropertyChange::Path & path, 
			const {{ property.type|ctype }} & oldValue )
	{
		delegate_.call< void >( "setNested_{{ property.name }}", path, oldValue );
	}


	/**
	 *	This method implements the sliced property setter callback for the 
	 * 	{{ property.name }} property.
	 *
	 *	@param path 		The path to the sub-property.
	 *	@param startIndex 	The starting index of the slice.
	 *	@param endIndex 	The end index of the slice.
	 *	@param oldValue 	The previous value of the sub-property.
	 */
	virtual void setSlice_{{ property.name }}( 
			const BW::NestedPropertyChange::Path & path,
			int startIndex, int endIndex, 
			const {{ property.type|ctype }} & oldValue )
	{
		delegate_.call< void >( "setSlice_{{ property.name }}", path, 
			startIndex, endIndex, oldValue );
	}
{%- endif %}
{%- endfor %}

private:
	emscripten::val 		delegate_;
};
{%- endfor %}


{%- for entity in entityDescriptions %}


/**
 *	This method creates the {{entity.name}}Extension for the
 *	{{entity.name}} entity type from the factory delegate.
 *
 *	@param entity 	The {{entity.name}} instance.
 */
{{ entity.name }}Extension * EntityExtensionFactoryJS::createForEntity( 
		const {{ entity.name }} & entity )
{
	emscripten::val extensionDelegate = 
		delegate_.call< emscripten::val >( "createFor{{ entity.name }}", 
			BW::BWEntityPtr( const_cast< {{ entity.name }} * >( &entity ) ) );

	return new {{entity.name}}ExtensionJS( &entity, extensionDelegate );
}


{% endfor %}

EMSCRIPTEN_BINDINGS( EntityExtensionJS )
{
	using namespace emscripten;

{%- for entity in entityDescriptions %}

{%- if entity.hasCellMailBox %}
	class_< CellMB::{{ entity.name }} >( 
			"{{ entity.name }}_Cell" )
{%- 	for method in entity.cellMethods %}
{%- 		if method.isExposed %}
		.function( "{{ method.name }}", &CellMB::{{ entity.name }}::{{ method.name }} )
{%- 		endif %}
{%- 	endfor %}
		;
{% endif %}

{%- if entity.hasBaseMailBox %}
	class_< BaseMB::{{ entity.name }} >( 
			"{{ entity.name }}_Base" )
{%- 	for method in entity.baseMethods %}
{%- 		if method.isExposed %}
		.function( "{{ method.name }}", &BaseMB::{{ entity.name }}::{{ method.name }} )
{%- 		endif %}
{%- 	endfor %}
		;
{% endif %}

	class_< {{ entity.name }}, base< BW::BWEntity > >( "{{ entity.name }}" )
		// No constructor: .constructor() 
{%- if entity.hasCellMailBox %}
		.function( "cell", &{{ entity.name }}::cell )
{%-	endif %}
{%- if entity.hasBaseMailBox %}
		.function( "base", &{{ entity.name }}::base )
{%- endif %}
{%- for property in entity.clientProperties %}
		.function( "{{ property.name }}", &{{ entity.name }}::{{ property.name }} )
{%- endfor %}
		;

{%- endfor %}
}


// EntityExtensionFactoryJS.cpp

