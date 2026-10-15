#ifndef __UMBRAMODEL_HPP
#define __UMBRAMODEL_HPP
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
 * \brief     Model interfaces
 *
 */

#if !defined (__UMBRAREFERENCECOUNT_HPP)
#   include "umbraReferenceCount.hpp"
#endif

namespace Umbra
{

/*!
 *
 * \brief   Base class for all models in Occlusion Booster
 *
 * \note    Models are used to describe shapes of objects. They don't
 *          "exist" by themselves - in order to physically place a model
 *          into a world, an Umbra::Object must be created to provide
 *          the location and orientation information. Models can
 *          be shared by multiple objects.
 *
 * \sa      OBBModel
 *
 */

class Model : public ReferenceCount
{
protected:
                        Model               (class ImpReferenceCount*); // internal
    virtual void        destruct            (void) const;
private:
                        Model               (const Model&);				// not permitted
    Model&              operator=           (const Model&);				// not permitted
};

/*!
 *
 * \brief   A model type describing an oriented bounding box. This
 *          class is also used to describe an axis-aligned bounding
 *          box (there's no separate AABBModel class).
 *
 */

class OBBModel : public Model
{
public:

    static UMBRADEC OBBModel*	UMBRACALL create	(const Matrix4x4& obb);
    static UMBRADEC OBBModel*   UMBRACALL create	(const Vector3* vertices, int numVertices);
    static UMBRADEC OBBModel*   UMBRACALL create	(const Vector3& mn, const Vector3& mx);

protected:
                                OBBModel			(class ImpReferenceCount*);     // internal
private:                                    
                                OBBModel            (const OBBModel&);				// not permitted
    OBBModel&                   operator=           (const OBBModel&);				// not permitted

    friend class APIWorker;														    // internal
};

} // namespace Umbra

//------------------------------------------------------------------------
#endif //__UMBRAMODEL_HPP
