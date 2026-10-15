#ifndef __UMBRADEFS_HPP
#define __UMBRADEFS_HPP
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
 * \brief     Common type definitions for all classes of Umbra
 * 
 */

#ifndef __cplusplus
#   error "C++ compiler required"
#endif

#include <stddef.h>                                             // required for size_t on some platforms

//------------------------------------------------------------------------
// Define some internal macros affecting how the library is compiled
//------------------------------------------------------------------------

#if defined (UMBRA_DLL)                         // Dynamic Link Library
#   if defined (UMBRA_BUILD_LIBRARY)
#       define UMBRADEC __declspec(dllexport)
#   else
#       define UMBRADEC __declspec(dllimport)
#   endif
#else
#   define UMBRADEC                             // Static Library
#endif

#if defined(WIN32) || defined(_WIN64)
#   define UMBRACALL __cdecl
#else
#   define UMBRACALL 
#endif

namespace Umbra
{

//------------------------------------------------------------------------
// Portable definition of a 32-bit integer. Most of the Umbra API
// uses 'ints' that can be 32 or 64 bits depending on the target
// platform. However, some large structures must always use 32-bit
// integers. Note that these definitions are inside the Umbra namespace
// so they should not conflict with the user's code.
//------------------------------------------------------------------------

typedef unsigned char       UINT8;            // 8-bit unsigned integer

typedef short int           INT16;            // 16-bit signed integer
typedef unsigned short int  UINT16;           // 16-bit unsigned integer

typedef int                 INT32;            // 32-bit signed integer
typedef unsigned int        UINT32;           // 32-bit unsigned integer

typedef long long           INT64;            // 64-bit signed integer
typedef unsigned long long  UINT64;           // 64-bit unsigned integer

/*!
 * \brief   Frustum class used for passing view-frustum information to several
 *          API functions.
 */

struct Frustum                                          
{
    /*!
	 * \brief       Frustum constructor
	 * \note        Initializes all components to zero.
	 *
	 */

	Frustum (void) : 
		left	(0.0f), 
		right	(0.0f), 
		top		(0.0f), 
		bottom	(0.0f), 
		zNear	(0.0f), 
		zFar	(0.0f),
		type	(Frustum::PERSPECTIVE)
	{
		// nada here 
	}

    /*!
	 * \brief       Projection type defined by the frustum
	 *
	 */

    enum Type
    {
        PERSPECTIVE     = 0,        /*!< the frustum describes a perspective projection */
        ORTHOGRAPHIC    = 1         /*!< the frustum describes an orthographic projection */
    };

    float left;        /*!< frustum left value */
    float right;       /*!< frustum right value */
    float top;         /*!< frustum top value */
    float bottom;      /*!< frustum bottom value */
    float zNear;       /*!< frustum near value in range ]0,zFar[ */
    float zFar;        /*!< frustum far value in range ]zNear,infinity] */
    Type  type;        /*!< PERSPECTIVE (default) or ORTHOGRAPHIC */
};

/*!
 * \brief       Tile defines a screen-space rectangle. 
 * 
 * \note        Tiles are used for tiled rendering together with
 *				Camera::setTilingScenario()
 *
 * \sa			Camera::setTilingScenario()
 */

struct Tile
{
    /*!
     * \brief       Tile constructor
	 * 
     * \note        Initializes all components to zero.
     */

    Tile (void) :
        left	(0),
        top		(0),
        right	(0),
        bottom	(0)
    {
    }

    /*!
     * \brief       Tile constructor
     */

	Tile(int l, int t, int r, int b) : 
        left	(l), 
        top		(t), 
        right	(r), 
        bottom	(b) 
    {
    }

    INT32 left;
    INT32 top;
    INT32 right;
    INT32 bottom;
};

//------------------------------------------------------------------------
// If UMBRA_OVERRIDE_VECTOR_TYPES macro has been defined, the vector and
// matrix classes are not defined here - the user must provide his own 
// implementation of the classes below. The data layout of the vectors and
// matrices must be bit-exact with the following definitions.
//------------------------------------------------------------------------

#if !defined (UMBRA_OVERRIDE_VECTOR_TYPES) 

class Vector2    { public: float v[2];          };
class Vector3    { public: float v[3];          };
class Vector3i   { public: INT32 i,j,k;         };
class Vector4    { public: float v[4];          };
class Matrix4x4  { public: float m[4][4];       };

#endif // !UMBRA_OVERRIDE_VECTOR_TYPES

} // namespace Umbra

//------------------------------------------------------------------------
#endif // __UMBRADEFS_HPP
