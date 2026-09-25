#include <emscripten/bind.h>

#include "GeneratedTypeBindings.hpp"
#include "GeneratedTypes.hpp"


using namespace emscripten;


namespace emscripten
{
	namespace internal
	{
		// This is required for BW::string conversions in the template usages below.
        template<>
        struct BindingType< BW::string > {
            typedef struct {
                size_t length;
                char data[1]; // trailing data
            }* WireType;

            static WireType toWireType( const BW::string & v ) 
			{
                WireType wt = (WireType)malloc(sizeof(size_t) + v.length());
                wt->length = v.length();
                memcpy( wt->data, v.data(), v.length() );
                return wt;
            }
            static BW::string fromWireType( WireType v ) {
                return BW::string( v->data, v->length );
            }
            static void destroy( WireType v ) {
                free( v );
            }
        };
	}
}

namespace // (anonymous)
{


/**
 *	Helper structure to query a SequenceValueType.
 */
template< typename VECTOR_TYPE >
struct SequenceValueTypeAccess 
{
	typedef typename VECTOR_TYPE::size_type size_type;
	typedef typename VECTOR_TYPE::value_type value_type;

	static size_type size( const VECTOR_TYPE & vector )
	{
		return vector.size();
	}

	static void push_back( VECTOR_TYPE & vector, const value_type & v )
	{
		vector.push_back( v );
	}
	static const value_type & get( const VECTOR_TYPE & vector, size_type i )
	{
		return vector[i];
	}

	static void set( VECTOR_TYPE & vector, size_type i, const value_type & v )
	{
		vector[i] = v;
	}
};


/**
 *	This function is used to register SequenceValueType types.
 */
template< typename T >
class_< BW::SequenceValueType< T > > registerSequenceValueType( 
		const char * name )
{
	typedef BW::SequenceValueType< T > VecType;

	return class_< VecType >( name ).
		template constructor<>().
		function( "push_back", &SequenceValueTypeAccess< VecType >::push_back ).
		function( "size", &SequenceValueTypeAccess< VecType >::size ).
		function( "get", &SequenceValueTypeAccess< VecType >::get ).
		function( "set", &SequenceValueTypeAccess< VecType >::set );
}


/**
 *	This function is used to register BW::map types.
 */
template<typename K, typename V>
class_< BW::map< K, V > > registerBWMap( const char * name )
{
	using namespace emscripten::internal;

	typedef BW::map< K, V > MapType;

	return class_< MapType >( name ).
		template constructor<>().
		function( "size", &MapType::size ).
		function( "get", MapAccess< MapType >::get ).
		function( "set", MapAccess< MapType >::set );
}


template< typename T >
struct ValueOrNoneAccessor
{
	static emscripten::val getValue( const BW::ValueOrNull< T > & valueOrNull )
	{
		if (valueOrNull.isNull())
		{
			return emscripten::val::null();
		}
		return emscripten::val( *(valueOrNull.get()) );
	}
};

EMSCRIPTEN_BINDINGS( GeneratedTypes )
{
	// FIXED_DICT type bindings
{%- for fixedDictType in fixedDictTypes %}

	// {{fixedDictType.className}}
	value_object< {{ fixedDictType.className }} >( "{{ fixedDictType.className }}" )
{%-		for memberName, memberType in fixedDictType.members %}
		.field( "{{ memberName }}", 
			&{{fixedDictType.className}}::{{memberName}} )
{%-		endfor %}
		;
{%- endfor %}

	// Sequence (ARRAY, TUPLE) bindings
{%- for arrayElementCType in arrayElementCTypes %}
	registerSequenceValueType< {{ arrayElementCType }} >( "{{ "Array%03d" % loop.index0 }}" );
{%- endfor %}

{%- for allowNoneType in allowNoneTypes %}

{%- if loop.first %}
	// TODO: Make AllowNone properties and methods be null properly
	// AllowNone types
{%- endif %}

	class_< {{allowNoneType.toCType }} >.( "{{ allowNoneType.wrappedType.toCType() }}OrNull" )
		.function( "setNull", &{{ allowNoneType.toCType() }}::setNull )
		.function( "setValue", &{{ allowNoneType.toCType() }}::setValue )
		.function( "isNull", &{{ allowNoneType.toCType() }}::isNull )
		.function( "value", 
			&ValueOrNoneAccessor< {{ allowNoneType.toCType }} >::getValue )
		;
{%- endfor %}
}


} // end namespace (anonymous)


// GeneratedTypeBindings.cpp

