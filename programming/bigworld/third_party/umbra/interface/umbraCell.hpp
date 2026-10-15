#ifndef __UMBRACELL_HPP
#define __UMBRACELL_HPP
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
 * \brief     Cell interface
 * 
 */

#if !defined (__UMBRAREFERENCECOUNT_HPP)
#   include "umbraReferenceCount.hpp"
#endif
    
namespace Umbra
{

/*!
 *
 * \brief			Cell holds a collection of objects and cameras. 
 *					
 * \note            Every object and camera in the world must belong to some
 *                  cell in order to be used in a visibility query.
 *
 * \note			Cells are typically associated with scenes, worlds and 
 *					levels on the application side. 
 *
 * \note            Because the class is derived from ReferenceCount, 
 *                  it does not have a public destructor. Use the function 
 *                  ReferenceCount::release() to release instances of the class. 
 *
 */

class Cell : public ReferenceCount
{
public:

    static UMBRADEC Cell* UMBRACALL create          (void);
    

    UMBRADEC void           setPVS                  (const UINT8*);

protected:
                            Cell                    (class ImpReferenceCount*);
    virtual void            destruct                (void) const;
private:                                        
                            Cell                    (const Cell&);              // not allowed
    Cell&                   operator=               (const Cell&);              // not allowed

    friend class APIWorker;														// internal
};

} // namespace Umbra

//------------------------------------------------------------------------
#endif // __UMBRACELL_HPP
