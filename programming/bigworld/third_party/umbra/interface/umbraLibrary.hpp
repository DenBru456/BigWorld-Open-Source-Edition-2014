#ifndef __UMBRALIBRARY_HPP
#define __UMBRALIBRARY_HPP
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
 * \brief     Library interface
 * 
 */

#if !defined (__UMBRADEFS_HPP)
#   include "umbraDefs.hpp"
#endif

namespace Umbra
{

/*!
 * \brief   Dummy class containing some enumerations and structures
 *          used by Umbra::Library
 */

class LibraryDefs
{
public:

	/*!
	 * \brief   Library version information 
	 */

    enum InfoString
    {
        INFO_VERSION                = 0,        /*!< version string of the library (in format: "1.0.5") */
        INFO_COPYRIGHT              = 1,        /*!< library copyright info string */
        INFO_BUILD_TIME             = 2,        /*!< library build date & time */
    };

	/*!
	 * \brief   Application side matrix format
	 *
	 * \note	Matrices are assumed to be stored in memory as linear arrays and as such, 
	 *			their contents can be interpreted as column-major or row-major.
	 * 
	 * \note	Matrix format can be defined when calling Library::init(). 
	 *
	 * \sa		Library::init()
	 * \sa		Object::setObjectToCellMatrix()
	 * \sa		Camera::setCameraToCellMatrix()
	 */

    enum MatrixFormat
    {
        COLUMN_MAJOR                = 0,        /*!< column-major matrix format */
        ROW_MAJOR                   = 1         /*!< row-major matrix format */
    };

	/*!
	 * \brief   Line types 
	 *
	 * \note	Lines are reported with DRAW_LINE_3D and DRAW_LINE_2D commands
	 * 
	 * \sa		Library::setFlags()
	 * \sa		Library::clearFlags()
	 */

    enum LineType
    {
        LINE_MISC                   = (1<<0),   /*!< miscellaneous */
        LINE_OBJECT_BOUNDS          = (1<<1),   /*!< show cell-space AABBs of objects */
        LINE_VOXELS                 = (1<<2),   /*!< show hierarchy voxels */
        LINE_OBJECT_OBBS            = (1<<3),   /*!< show object obbs which are used in culling */
        LINE_OCCLUSION_QUERIES      = (1<<4),	/*!< show occlusion query shapes */
		LINE_CAMERA_FRUSTUM			= (1<<5)	/*!< show world space camera frustum */
    };

	/*!
	 * \brief   Library flag types
	 *
	 * \sa		Library::setFlags()
	 * \sa		Library::clearFlags()
	 */

	enum FlagType
    {
        LINEDRAW                    = 0         /*!< draw lines */
    };

	/*!
	 * \brief   Library statistics
	 *
	 * \sa		Library::getStatistic()
	 * \sa		Library::clearStatistics()
	 */

    enum Statistic
    {
        STAT_FIRST                      = 0,
        STAT_MEMORYEXTERNALOPERATIONS   = 1,
        STAT_MEMORYOPERATIONS           = 2,
        STAT_TIME                       = 3,
        STAT_MEMORYUSED                 = 4,	/*!< total number of allocated memory in bytes */
        STAT_MEMORYCURRENTALLOCATIONS   = 5,	
        STAT_LIVECAMERAS                = 6,	/*!< total number of cameras */
        STAT_LIVECELLS                  = 7,	/*!< total number of cells */
        STAT_LIVEMODELS                 = 8,	/*!< total number of models	*/
        STAT_LIVEOBJECTS                = 9,	/*!< total number of objects */
        STAT_LIVENODES                  = 10,	/*!< total number of nodes in all cells	*/
        STAT_LIVEINSTANCES              = 11,	/*!< total number of object instances in all nodes */
        STAT_OBJECTMATRIXUPDATES        = 12,	/*!< total number of objectToCell matrix updates */	
        STAT_DATABASENODESINSERTED      = 13,
        STAT_DATABASEOBSREMOVED         = 14,
        STAT_DATABASEINSTANCESREMOVED   = 15,
        STAT_DATABASEINSTANCESINSERTED  = 16,
        STAT_DATABASEINSTANCESMOVED     = 17,
        STAT_DATABASENODESREMOVED       = 18,
        STAT_DATABASEOBSINSERTED        = 19,
        STAT_DATABASEOBSUPDATED         = 20,
        STAT_DATABASENODESPLITS         = 21,
        STAT_DATABASENODEDIRTYUPDATES   = 22,
        STAT_DATABASENODENEWROOTS       = 23,
        STAT_DATABASETRAVERSALS         = 24,
        STAT_DATABASEOBSUPDATEPROCESSED = 25,
        STAT_DATABASEOBSVISIBLE         = 26,	/*!< number of visible objects */
        STAT_OCCLUSIONQUERIESISSUED     = 27,	/*!< number of issued occlusion queries */
        STAT_OCCLUSIONQUERIESHIDDEN     = 28,	/*!< number of issued occlusion queries that were hidden */

        // internal

        STAT_COMMANDERWAITTIME,
        STAT_TIMER_RESETTRAVERSEDFLAGS,
        STAT_TIMER_WT_WORK,
        STAT_TIMER_FASTDATA_SET_GETUINT32,
        STAT_TIMER_FASTDATA_SET_PUTDATA,
        STAT_DMAACCESSTIME_GETUINT32,
        STAT_DMAACCESSTIME_GETDATAALIGNED,
        STAT_DMAACCESSTIME_GETDATAUNALIGNED,
        STAT_DMAACCESSTIME_GETDATA,
        STAT_DMAACCESSTIME_PUTDATAALIGNED,
        STAT_DMAACCESSTIME_PUTDATAUNALIGNED,
        STAT_DMAACCESSTIME_PUTDATA,
        STAT_TIMER_DMA_WAIT_GET,
        STAT_TIMER_DMA_WAIT_PUT,
        STAT_TIMER_DATASTREAMWRITER,
        STAT_TIMER_DATASTREAMREADER,
        STAT_TIMER_DATASTREAMWRITER_WAIT,
        STAT_TIMER_DATASTREAMREADER_WAIT,
        STAT_TIMER_GET_OBJECT_DATA,
        STAT_TRAVERSE_TIME,
        STAT_TIMER_ALLOCATE_VERTEX_BUFFER,
        STAT_TIMER_PROCESS_QUERY,
        STAT_TIMER_WORKER_WAIT_FOR_QUERY,
        STAT_TIMER_PROCESS_OBJECT,
        STAT_TIMER_PROCESS_NODE,
        STAT_TIMER_PROCESS_VISIBLE_NODE,
        STAT_TIMER_PROCESS_NODE_GETINSTANCE,
        STAT_TIMER_PROCESS_NODE_TRAVERSEOBJECT,
        STAT_TIMER_PROCESS_NODE_SETNODEPROCESSED,
        STAT_TIMER_PROCESS_NODE_TRAVERSE_CHILDREN,
        STAT_TIMER_PROCESS_NODE_OBJECTS,
        STAT_TIMER_PROCESS_NODE_MISC_GETS,
        STAT_TIMER_PROCESS_NODE_GETINSTANCECOUNT,
        STAT_TIMER_GETRESULTS,
        STAT_TIMER_COMMANDER,
        STAT_TIMER_COMMAND,
        STAT_TIMER_ISSUE_PENDING_QUERIES,
        STAT_TIMER_ISSUE_BUDGET_QUERIES,
        STAT_TIMER_ISSUE_QUERY,
        STAT_TIMER_PROXY_FLUSH,
        STAT_TIMER_PROXY_SYNC,
        STAT_TIMER_PROXY_INIT,
		STAT_TIMER_SHADOW_AABB, 
        STAT_TIMER_OCCLUSION_QUERY_ISSUE_ARRAY,
        STAT_TIMER_MAX,

        STAT_MAX                                // end of list
    };

    enum
    {
        STAT_TIMER_FIRST = STAT_COMMANDERWAITTIME,
        STAT_TIMER_COUNT = STAT_TIMER_MAX - STAT_TIMER_FIRST
    };

    /*!
     * \brief   SystemServices interface for custom memory allocation etc.
     *
     * \note    These are callback functions that have default implementations
     *          but can be overridden by the application.
     */

    class SystemServices
    {
    public:
        UMBRADEC                SystemServices      (void);
        UMBRADEC virtual        ~SystemServices     (void);

        UMBRADEC virtual void   error               (const char* message);
        UMBRADEC virtual void*  allocateMemory      (size_t bytes);         
        UMBRADEC virtual void   releaseMemory       (void*);                
        UMBRADEC virtual void   namedCounter        (float t, char* str);
	    UMBRADEC virtual void   beginNamedEvent     (int id, const char* str);
	    UMBRADEC virtual void   endNamedEvent       (int id);
    private:
                                SystemServices      (const SystemServices&);
        SystemServices&         operator=           (const SystemServices&);
    };

    /*!
     * \brief   GraphicsServices interface for creating rendering related
     *          resources
     *
     * \note	Umbra Occlusion Booster does not access the rendering API directly, 
     *			instead it uses this interface to gain access to the necessary 
     *			graphics resources.
     *
     * \note    This interface is separate from SystemServices interface since
     *          it can be called from a different thread.
     */

    class GraphicsServices
    {
    public:
        UMBRADEC                GraphicsServices    (void);
        UMBRADEC virtual        ~GraphicsServices   (void);

        UMBRADEC virtual void*  allocateQueryObject (void)			= 0;            
		UMBRADEC virtual void   releaseQueryObject  (void* object)	= 0;            
    private:
                                GraphicsServices    (const GraphicsServices&);
        GraphicsServices&       operator=           (const GraphicsServices&);
    };
};

/*!
 * \brief   Umbra Occlusion Booster global functions
 *
 * \note    This class contains functions for initializing and
 *          shutting down the library, for querying performance
 *          statistics and other debug information.
 */

class Library : public LibraryDefs
{
public:
    
    static UMBRADEC void            UMBRACALL clearFlags              (FlagType,unsigned int);
    static UMBRADEC void            UMBRACALL exit                    (void);
    static UMBRADEC int             UMBRACALL getEventCount           (void);
    static UMBRADEC unsigned int    UMBRACALL getFlags                (FlagType);
    static UMBRADEC const char*     UMBRACALL getInfoString           (InfoString);
    static UMBRADEC float           UMBRACALL getStatistic            (Statistic);
    static UMBRADEC const char*     UMBRACALL getStatisticName        (Statistic);
    static UMBRADEC void            UMBRACALL init                    (MatrixFormat mf, SystemServices* s = 0);
    static UMBRADEC void            UMBRACALL initThreads             (void* context, int numCores, int* coreIDs, int priority);
    static UMBRADEC void            UMBRACALL resetStatistics         (void);
    static UMBRADEC void            UMBRACALL setEvaluationKey        (const char* evaluationKey);
    static UMBRADEC void            UMBRACALL setFlags                (FlagType,unsigned int);
    static UMBRADEC int             UMBRACALL textCommand             (class Commander*, const char*);     // external debugging

private:                                            
                                    Library                 (void);             // no constructor exists
                                    Library                 (const Library&);   // no constructor exists
    static class ImpLibrary*        s_implementation;                           // implementation pointer
};

} // namespace Umbra

//------------------------------------------------------------------------
#endif //__UMBRALIBRARY_HPP
