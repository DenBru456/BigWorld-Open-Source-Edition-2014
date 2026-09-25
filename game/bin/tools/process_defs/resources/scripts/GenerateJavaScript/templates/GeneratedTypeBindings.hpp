#ifndef ENTITY_EXTENSION_FACTORY_JS_HPP
#define ENTITY_EXTENSION_FACTORY_JS_HPP

// This header file is only to be included from bindings.cpp, as it is meant to
// be compiled using C++11.

#include <emscripten/val.h>

#include "EntityExtensionFactory.hpp"


/**
 *	This concrete subclass of EntityExtensionFactory is used to delegate calls
 *	to create extensions to a JavaScript object.
 */
class EntityExtensionFactoryJS : public EntityExtensionFactory
{
public:
	EntityExtensionFactoryJS( emscripten::val delegate ) : 
			delegate_( delegate ) 
	{}

	virtual ~EntityExtensionFactoryJS() {}

	void delegate( emscripten::val delegate ) 	{ delegate_ = delegate; }
	emscripten::val delegate() const 			{ return delegate_; }

{%- for entity in entityDescriptions %}
	virtual {{ entity.name }}Extension * createForEntity( const {{ entity.name }} & entity );
{%- endfor %}

private:
	emscripten::val delegate_;
};


#endif // ENTITY_EXTENSION_FACTORY_JS_HPP
