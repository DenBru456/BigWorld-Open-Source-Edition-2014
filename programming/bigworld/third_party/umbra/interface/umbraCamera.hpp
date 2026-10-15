#ifndef __UMBRACAMERA_HPP
#define __UMBRACAMERA_HPP
/*!
 *
 * Umbra Occlusion Booster
 * -----------------------------------------
 *
 * (C) 2009-2010 Umbra Software Ltd. 
 * All Rights Reserved.
 *
 * This file consists of unpublished, proprietary source code of
 * Umbra Software Ltd., and is considered Confidential Information for
 * purposes of non-disclosure agreement. Disclosure outside the terms
 * outlined in signed agreement may result in irrepairable harm to
 * Umbra Software Ltd. and legal action against the party in breach.
 *
 * \file
 * \brief     Camera interface
 * 
 */

#if !defined (__UMBRAREFERENCECOUNT_HPP)
#   include "umbraReferenceCount.hpp"
#endif

namespace Umbra
{

class Commander;

/*!
 *
 * \brief           Class for representing a virtual viewer
 *
 * \note            The Camera class is used for determining visible 
 *                  objects in a scene. The camera defines the 
 *                  position and orientation of the viewer and the shape of the
 *                  view frustum. The camera interface is also used to
 *                  select culling methods used by the visibility query.
 *
 * \note            Because the class is derived from ReferenceCount, 
 *                  it does not have a public destructor. Use the function 
 *                  ReferenceCount::release() to release instances of the class. 
 *
 */

class Camera : public ReferenceCount
{
public:

    /*!
     * \brief       Enumeration of culling methods used by visibility queries
     *
     * \note        These enumerations are used when constructing the
     *              property mask for Umbra::Camera::setProperties()
     */

    enum Property
    {
        VIEWFRUSTUM_CULLING     			= (1<<0),       /*!< enable view frustum culling */
        OCCLUSION_CULLING       			= (1<<1),       /*!< enable occlusion culling (note that VIEWFRUSTUM_CULLING is automatically enabled if this is set) */
        LATENT_QUERIES          			= (1<<2),       /*!< can improve performance at the cost of potentially introducing rendering artifacts */
        DISTANCE_CULLING					= (1<<3), 		/*!< enable distance culling */
        PVS_CULLING                         = (1<<4),       /*!< enable using pre-computed data for culling */
		BENCHMARK							= (1<<5),		/*!< benchmark mode to get the optimal from-point visibility (note that OCCLUSION_CULLING is automatically enabled */
		FREEZE_OCCLUSION					= (1<<6)		/*!< freeze occlusion */
    };

    enum Space
	{
		CAMERA_SPACE, 
		CELL_SPACE
	}; 

    enum
    {
        MAX_TILES               = 16,            /*!< maximum number of tiles supported by Camera::setTilingScenario() */
        MAX_PLANES              = 32             /*!< maximum number of planes supported by Camera::setCullPlanes() */
    };

    static UMBRADEC Camera* UMBRACALL create            (void);

    UMBRADEC void           resolveVisibility           (void) const;
    UMBRADEC void           processVisibility           (Commander*);	// pairs with Camera::resolveVisibility()

    UMBRADEC void           setCameraToCellMatrix       (const Matrix4x4&);
    UMBRADEC void           setCell                     (class Cell*);

    UMBRADEC void           setFrustum                  (const Frustum&);  
    UMBRADEC void           setFrustumAndCullPlanes     (const Frustum&, const Vector4* planes, int numPlanes, Space space);	// combines planes, supports occlusion
	UMBRADEC void			setCullPlanes				(const Vector4* planes, int numPlanes, Space space);				

    UMBRADEC void           setProperties               (unsigned int propertyMask);
	UMBRADEC void			setBitmask					(UINT32 mask); 
    UMBRADEC void           setTilingScenario           (const Tile* tiles, int numTiles);

    class ImpCamera*        getImplementation           (void) const;       // internal
protected:                                          
                            Camera                      (class ImpCamera*);
    UMBRADEC virtual        ~Camera                     (void);
private:                                                    
                            Camera                      (const Camera&);    // not allowed
    Camera&                 operator=                   (const Camera&);    // not allowed
    class ImpCamera*        m_imp;                                          // opaque pointer

    friend class APIWorker;													// internal
};
} // namespace Umbra

//------------------------------------------------------------------------
#endif // __UMBRACAMERA_HPP
