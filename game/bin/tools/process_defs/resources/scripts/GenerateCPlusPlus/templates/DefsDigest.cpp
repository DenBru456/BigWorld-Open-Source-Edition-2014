#include "DefsDigest.hpp"

#include "connection/entity_def_constants.hpp"

namespace DefsDigest
{

BW::EntityDefConstants g_entityDefConstants(
		BW::MD5::Digest( "{{ constants.digest }}" ),
		{{ constants.maxExposedClientMethodCount }}, // numClientMethods
		{{ constants.maxExposedBaseMethodCount }}, // numBaseMethods
		{{ constants.maxExposedCellMethodCount }} ); // numCellMethods

const BW::EntityDefConstants & constants()
{
	return g_entityDefConstants;
}

} // namespace DefsDigest


// DefsDigest.cpp


