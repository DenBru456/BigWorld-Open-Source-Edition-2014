#ifndef __UMBRAOBJECT_HPP
#define __UMBRAOBJECT_HPP
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
 * \brief     Object interface
 *
 */

#if !defined (__UMBRAREFERENCECOUNT_HPP)
#   include "umbraReferenceCount.hpp"
#endif

namespace Umbra
{
class Cell;
class Model;

/*!
 * \brief   Physical instance of a Umbra::Model
 *
 * \note    Objects are used to place models into the world.
 * 
 */

class Object : public ReferenceCount
{
public:

    /*!
     * \brief   Object properties
     */

    enum Property
    {
        ENABLED         = 0,        /*!< is the object active (enabled by default) */
        UNBOUNDED       = 1,        /*!< object model bounds ignored, object regarded to be of infinite size and reported as always visible (disabled by default) */
        OCCLUDER        = 2			/*!< is the object an occluder (enabled by default) */
    };

    /*!
     * \brief   Object render cost 
     */

	enum RenderCost
	{
		CHEAP			= 0,		/*!< disable non-hierarchical occlusion tests */
		NORMAL			= 1,		/*!< normal render cost (enabled by default) */ 
		EXPENSIVE		= 2			/*!< test visibility every frame */
	}; 

	static UMBRADEC Object* UMBRACALL create        (Model* testModel);

    UMBRADEC void           set                     (Property, bool);
	UMBRADEC void			setRenderCost			(RenderCost); 
    UMBRADEC void           setCell                 (Cell*);
    UMBRADEC void           setObjectToCellMatrix   (const Matrix4x4&);
    UMBRADEC void           setModel				(Model*);
    UMBRADEC void           setCullDistance         (float near, float far);
    UMBRADEC void		    setBitmask				(UINT32 mask); 
    UMBRADEC void           setPVSID                (UINT32 PVSID);

protected:
                            Object                  (class ImpReferenceCount*);
    virtual void            destruct                (void) const;
private:
                            Object                  (const Object&);            // not allowed
    Object&                 operator=               (const Object&);            // not allowed

    friend class APIWorker;														// internal
};

} // namespace Umbra

//------------------------------------------------------------------------
#endif // __UMBRAOBJECT_HPP
