#ifndef __UMBRAREFERENCECOUNT_HPP
#define __UMBRAREFERENCECOUNT_HPP
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
 * \brief     Reference counting mechanism used by most Umbra public classes
 * 
 */

#if !defined (__UMBRADEFS_HPP)
#   include "umbraDefs.hpp"
#endif

namespace Umbra
{

/*!
 *
 * \brief           Reference counting base class
 *
 * \note            Classes in the library that use reference counting are
 *                  all derived from this class. Instances of reference
 *                  counted classes cannot be destructed by calling
 *                  'delete', instead the member function release() should
 *                  be used.
 *
 *                  Note that only Occlusion Booster classes can inherit the
 *                  ReferenceCount class.
 *
 *                  Note that the user cannot inherit from Umbra classes.
 *
 * \sa              ReferenceCount::release()
 *
 */

class ReferenceCount
{
public:

    UMBRADEC void           addReference        (void);         
    UMBRADEC void           release             (void) const;   
    UMBRADEC void           setUserPointer      (void*);

    // internal

    void                    addReferenceInternal(void);
    void                    releaseInternal     (void);
    INT32                   getReserved         (void);

protected:
                            ReferenceCount      (class ImpReferenceCount*);         
    virtual                 ~ReferenceCount     (void);   
    virtual void            destruct            (void) const;
    INT32                   m_reserved0;                    // reserved for internal use

private: 

    mutable INT32			m_referenceCount;				// reference count of the object

    friend class APIWorker;
};

} // namespace Umbra

//------------------------------------------------------------------------
#endif //__UMBRAREFERENCECOUNT_HPP
