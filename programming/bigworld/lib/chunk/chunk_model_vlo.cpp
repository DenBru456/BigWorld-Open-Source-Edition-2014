#include "pch.hpp"
#include "chunk_model_vlo.hpp"

#include "cstdmf/guard.hpp"

#include "chunk.hpp"
#include "chunk_obstacle.hpp"
#include "chunk/chunk_manager.hpp"
#include "chunk/chunk_vlo_obstacle.hpp"

#ifdef MF_SERVER
#include "server_super_model.hpp"
#else // MF_SERVER
#include "model/super_model.hpp"
#include "moo/render_context.hpp"
#include "moo/line_helper.hpp"
#endif // MF_SERVER


BW_BEGIN_NAMESPACE

int ChunkModelVLO_token;

// -----------------------------------------------------------------------------
// Section: ChunkModelVLO
// -----------------------------------------------------------------------------


/**
 *	Constructor.
 */
ChunkModelVLO::ChunkModelVLO( const BW::string & uid )
	: VeryLargeObject( uid, ChunkModelVLO::getLargeObjectType() )
#ifdef MF_SERVER
	, proxiedModel_( new ServerChunkModel() )
#else // MF_SERVER
	, proxiedModel_( new ChunkModel() )
	, drawnChunk_( NULL )
	, shadowDrawnChunk_( NULL )
	, shadowVPKey_( 0 )
#endif // MF_SERVER
{
}


/**
 *	Destructor.
 */
ChunkModelVLO::~ChunkModelVLO()
{
}


/**
 *	Load method
 */
bool ChunkModelVLO::load( DataSectionPtr pSection, Chunk * pChunk )
{
	BW_GUARD;
	if (pChunk==NULL)
	{
		return false;
	}

	DataSectionPtr modelSection =
#ifdef MF_SERVER
		pSection->openSection( ServerChunkModel::getSectionName() );
#else // MF_SERVER
		pSection->openSection( ChunkModel::getSectionName() );
#endif // MF_SERVER

	bool isModelLoaded =
#ifdef MF_SERVER
		proxiedModel_->load( modelSection );
#else // MF_SERVER
		proxiedModel_->load( modelSection, pChunk );
#endif // MF_SERVER

	if (!isModelLoaded)
	{
		return false;
	}

	Matrix storedTransform = modelSection->readMatrix34(
		getWorldTransformAttrName(), Matrix::identity );
	updateLocalVars( storedTransform );

	return true;
}


/**
 *
 * Returns VLO transform relative to chunk
 *
 */
const Matrix & ChunkModelVLO::localTransform( Chunk * pChunk )
{
	static Matrix s_chunkLocalTransform;
	s_chunkLocalTransform = worldTransform_;
	s_chunkLocalTransform.postMultiply( pChunk->transformInverse() );
	return s_chunkLocalTransform;
}


/**
 *
 * Returns VLO chunk BB relative to chunk
 * Used by UMBRA
 *
 */
BoundingBox ChunkModelVLO::chunkBB( Chunk* pChunk )
{
	BW_GUARD;

	BoundingBox wbb( proxiedModel_->localBB() );

	Matrix world( worldTransform() );
	world.postMultiply( pChunk->transformInverse() );
	wbb.transformBy( world );
	return wbb;
}

/*virtual*/void ChunkModelVLO::syncInit( ChunkVLO* pVLO )
{
	if (proxiedModel_)
	{
		proxiedModel_->syncInit();
	}
}


#ifndef MF_SERVER
/*virtual */void ChunkModelVLO::tick( float dTime )
{
	drawnChunk_ = NULL;
#ifndef MF_SERVER
	// All shadow atlas splits render within one frame; the per-split latch
	// is keyed on the viewport and must reset only per frame, like
	// drawnChunk_.
	shadowDrawnChunk_ = NULL;
	shadowVPKey_ = 0;
#endif // !MF_SERVER
}


/**
 *	Update animations
 */
/*virtual */void ChunkModelVLO::updateAnimations()
{
	if (proxiedModel_ && proxiedModel_->wantsUpdate())
	{
		proxiedModel_->updateAnimations();
	}
}


/**
 *	Draw
 */
/*virtual */void ChunkModelVLO::drawInChunk( Moo::DrawContext& drawContext, Chunk * pChunk )
{
	BW_GUARD;

#ifndef MF_SERVER
	if (drawContext.renderingPassType() == Moo::RENDERING_PASS_SHADOWS)
	{
		// All atlas splits render within the same frame through the same
		// shadow DrawContext, each split with its own atlas viewport
		// (dynamic_shadow.cpp: X = mapSize * splitIndex). A per-frame
		// latch would let only the first split draw the model and leave
		// the other split tiles empty, slicing the shadow at split
		// boundaries. De-duplicate refs per split instead, keyed on the
		// current viewport.
		DX::Viewport vp;
		Moo::rc().getViewport( &vp );
		const unsigned int vpKey = (vp.X << 16) ^ vp.Y;
		if (shadowVPKey_ == vpKey)
		{
			if (shadowDrawnChunk_ != NULL &&
				shadowDrawnChunk_ != pChunk)
			{
				return;
			}
		}
		shadowVPKey_ = vpKey;
		shadowDrawnChunk_ = pChunk;
	}
	else
#endif // !MF_SERVER
	{
		if (drawnChunk_ != NULL &&
			drawnChunk_ != pChunk)
		{
			return;
		}
		bool chunkUpdated = drawnChunk_ == pChunk;
		drawnChunk_ = pChunk;
	}

	if (proxiedModel_)
	{
		proxiedModel_->chunk( pChunk );
		proxiedModel_->transform( localTransform( pChunk ) );
		proxiedModel_->syncInit();
		proxiedModel_->draw( drawContext );
	}
}
#endif // !MF_SERVER


/*virtual */void ChunkModelVLO::addCollision( ChunkItemPtr item )
{
	SuperModel * superModel =  proxiedModel_->getSuperModel();

	Matrix world( this->worldTransform() );

	Chunk & itemChunk = *item->chunk();
	for (int i = 0; i < superModel->nModels(); i++)
	{
		ChunkVLOObstacle::instance( itemChunk ).addModel(
			superModel->topModel( i ), world, item );
	}
}


bool ChunkModelVLO::create(
	Chunk * pChunk, DataSectionPtr pSection, const BW::string & uid )
{
	BW_GUARD;

	// VeryLargeObject stores itself into the VLO map, no need to store
	// this returned reference anywhere.
	SmartPointer<ChunkModelVLO> pItem = new ChunkModelVLO( uid );
	if (!pItem->load( pSection, pChunk ))
	{
		return false;
	}

	return true;
}


/**
 *	This method updates our local vars from the transform
 */
void ChunkModelVLO::updateLocalVars( const Matrix & m )
{
	BW_GUARD;
	worldTransform_ = m;
}


/*static */const BW::string & ChunkModelVLO::getLargeObjectType()
{
	static const BW::string LARGE_OBJECT_TYPE( "proxy" );
	return LARGE_OBJECT_TYPE;
}


/*static */const BW::string & ChunkModelVLO::getSectionName()
{
	static const BW::string SECT_NAME( "proxy" );
	return SECT_NAME;
}


/*static */const BW::string & ChunkModelVLO::getWorldTransformAttrName()
{
	static const BW::string WORLD_TRANSFORM_ATTR_NAME( "worldTransform" );
	return WORLD_TRANSFORM_ATTR_NAME;
}


// Static factory initialiser
VLOFactory ChunkModelVLO::factory_(
	ChunkModelVLO::getSectionName(), 0, ChunkModelVLO::create );

BW_END_NAMESPACE

// chunk_model_vlo.cpp
