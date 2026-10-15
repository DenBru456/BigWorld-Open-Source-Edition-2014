#ifndef __UMBRACOMMANDER_HPP
#define __UMBRACOMMANDER_HPP
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
 * \brief     Commander interface
 * 
 */

#if !defined (__UMBRALIBRARY_HPP)
#   include "umbraLibrary.hpp"
#endif

namespace Umbra
{

class Camera;
class ImpCommander;

/*!
 *
 * \brief           Class used for Occlusion Booster -> user message passing
 *
 * \note            The Commander interface handles library-to-user communication.
 *                  This approach was taken both to avoid extending the API in
 *                  future releases, and to keep future libraries binary-compatible.
 *
 * \note            The application user should create a new class derived
 *                  from Commander and override the Commander::command() function 
 *                  to provide a valid implementation. See documentation entry 
 *                  for the function for further information.
 *
 * \sa              Commander::command()
 */

class Commander
{
public:

    /*!
     * \brief           Enumeration of different commands that Occlusion Booster
     *                  may send to the Commander::command() function
     *
     *
     * \sa              Commander::command()
     */

    enum Command
    {
        RESOLVE_BEGIN                   = 0x00, /*!< Start of visibility query                      [NONE]      */
        RESOLVE_END                     = 0x01, /*!< End of visibility query                        [NONE]      */
        VIEW_PARAMETERS_CHANGED         = 0x02, /*!< New viewing parameters                         [getViewer()]   */
        OBJECTS_VISIBLE                 = 0x03, /*!< Reports visible objects                        [getObjectData()]    */  
        FLUSH_OCCLUDERS                 = 0x04, /*!< Flush all occluders from OBJECTS_VISIBLE       [NONE] */                      
        ISSUE_OCCLUSION_QUERIES         = 0x05, /*!< Render occlusion query test shapes             [getOcclusionQueryData()] */
        GET_OCCLUSION_QUERY_RESULTS     = 0x06, /*!< Return occlusion query results                 [getOcclusionQueryResultData()] */

        TEXT_MESSAGE                    = 0x07, /*!< Debug function: Text message from the library  [getTextMessage()] */
        DRAW_LINE_2D                    = 0x08, /*!< Debug function: Draw two-dimensional line      [getLine2D()]      */
        DRAW_LINE_3D                    = 0x09, /*!< Debug function: Draw three-dimensional line    [getLine3D()]      */

        COMMAND_MAX                     = 0x7FFFFFFF // force enumerations to be int       
    };

    /*!
     * \brief   Data object for Commander::OBJECTS_VISIBLE.
     */

    class ObjectData
    {
    public:

        UMBRADEC void*   	getUserPointer      (void) const;
        UMBRADEC bool    	isOccluder          (void) const;
        UMBRADEC UINT32  	getTileMask         (void) const; 
    };

    /*!
     * \brief   Data object for Commander::ISSUE_OCCLUSION_QUERIES.
     */

    class OcclusionQueryData
    {
    public:

        UMBRADEC void*				getQueryObject      (void) const; 
        UMBRADEC UINT32				getVertexCount      (void) const; 
		UMBRADEC const Vector3*		getVertices			(void) const; 
        UMBRADEC UINT32				getTriangleCount    (void) const; 
        UMBRADEC const Vector3i*    getTriangles		(void) const; 
    };

    /*!
     * \brief   Data object for Commander::GET_OCCLUSION_QUERY_RESULTS.
     */

	class OcclusionQueryResultData
	{
	public: 

		UMBRADEC void*		getQueryObject		(void) const; 
		UMBRADEC bool		getWaitForResult	(void) const; 
		UMBRADEC void		setResult			(INT64 count); 
	}; 
    
    /*!
     * \brief   A smart object for passing view-related information to 
     *          the user during certain Commander callbacks
     *
     * \note    This class is used by Commander to provide
     *          additional view-specific information during certain
     *          Commander::command() callbacks.
     *
     * \note    The application user cannot construct or destruct Viewers. The
     *          only way to gain access to a Viewer is through the method
     *          Commander::getViewer().
     */

    class Viewer
    {
    public:

        /*!
         * \brief       Enumeration specifying handedness of matrix returned
         *
         * \note        This enumeration is used as a parameter to some Viewer 
         *              member functions to specify the handedness of the matrix
         *              returned.
         *
         * \sa          Commander::Viewer::getProjectionMatrix()
         */

        enum Handedness
        {
            LEFT_HANDED      = 0,    /*!< Matrix is left-handed  */
            RIGHT_HANDED     = 1,    /*!< Matrix is right-handed */
            LEFT_HANDED_D3D  = 2,    /*!< Matrix is left-handed and in D3D projection matrix format  */
            RIGHT_HANDED_D3D = 3     /*!< Matrix is right-handed and in D3D projection matrix format */
        };

        UMBRADEC void   getFrustum              (Frustum&) const;
        UMBRADEC void   getProjectionMatrix     (Matrix4x4&, Handedness) const;    
        UMBRADEC void   getCameraToWorldMatrix  (Matrix4x4&) const; 
        UMBRADEC void   getCellToCameraMatrix   (Matrix4x4&) const;

    private:                                
                        Viewer                  (const Viewer&);    // not allowed
        Viewer&         operator=               (const Viewer&);    // not allowed
                        Viewer                  (void);
                        ~Viewer                 (void);

        friend class ImpCommander;                             
        class ImpCommander* m_imp;                                  // implementation pointer
    };

    UMBRADEC virtual            ~Commander              (void);
    UMBRADEC virtual void       command                 (Command c) = 0;              

    class ImpCommander*         getImplementation       (void) const;		// internal

protected:

    UMBRADEC                                Commander                   (LibraryDefs::GraphicsServices* serv);

    UMBRADEC Library::LineType              getLine2D                   (Vector2& a, Vector2& b, Vector4& color) const;
    UMBRADEC Library::LineType              getLine3D                   (Vector3& a, Vector3& b, Vector4& color) const;
    UMBRADEC const char*                    getTextMessage              (void) const;
    UMBRADEC const Viewer*                  getViewer                   (void) const;

    UMBRADEC int                            getDataCount                (void) const;
	UMBRADEC const OcclusionQueryData*      getOcclusionQueryData       (int index) const;
    UMBRADEC OcclusionQueryResultData*      getOcclusionQueryResultData (int index) const;
    UMBRADEC const ObjectData*              getObjectData               (int index) const;

private:
    friend class ImpCommander;
                                Commander               (const Commander&);     // not allowed
    Commander&                  operator=               (const Commander&);     // not allowed
    ImpCommander*               m_imp;                                          // implementation pointer
};

} // namespace Umbra
                                            
//------------------------------------------------------------------------
#endif // __UMBRACOMMANDER_HPP
