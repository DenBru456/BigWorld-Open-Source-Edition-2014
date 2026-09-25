#!/usr/bin/python
import sys
import md5
import os
import cPickle


def printUsage():
    print "USAGE:"
    print "\t Generate Hash:\t-hash <folder name> <hash file name>"
    print "\t Generate Diff:\t-diff <folder name> <hash file name> <diff file name> <bin file name>"
    print "\t Merge Folder:\t-merge <hash folder name> <hash file name> <diff file name> <bin file name> <merge folder name>"


def md5File( fileName ):
    hash = ''
    f = open( fileName, "rb" )

    try:
        m = md5.new()

        while True:
            x = f.read( 102400 )

            if len(x):
                m.update( x )
            else:
                break

        hash = m.hexdigest()
    finally:
        f.close()

    return hash


def getAllFiles( folder ):
    result = []
    folderLength = len( folder )
    dirs = os.walk( folder )
    for dir in dirs:
        for file in dir[2]:
            relPath = ( dir[0] + os.path.sep + file )[folderLength:]
            result.append( relPath )
    return result


# the format of hash file is
# hash => relative file name
def generateFolderHash( folder, hashFile ):
    if folder[-1] != os.path.sep:
        folder = folder + os.path.sep

    files = getAllFiles( folder )
    fileDict = {}
    for x in files:
        try:
            hash = md5File( folder + x )
            if not fileDict.has_key( hash ):
                fileDict[hash] = x
        except IOError, e:
            print e

    f = open( hashFile, "wb" )
    cPickle.dump( fileDict, f )
    f.close()


# the format of diff file is
# relative file name => tuple
#   tuple => ( content included: boolean, ... )
#   if content included:
#       tuple[1:] => creation time, modification time, content offset, content length
#   else:
#       tuple[1:] => creation time, modification time, reference file name
def generateFolderDiff( folder, hashFile, diffFile, binFile ):
    if folder[-1] != os.path.sep:
        folder = folder + os.path.sep
    fileDict = {}
    f = open( hashFile, "rb" )
    fileDict = cPickle.load( f )
    f.close()

    files = getAllFiles( folder )
    diff = {}

    f = open( binFile, "wb" )
    try:
        for fileName in files:
            try:
                pathName = folder + fileName
                ctime = os.path.getctime( pathName )
                mtime = os.path.getmtime( pathName )
                hash = md5File( pathName )
                if fileDict.has_key( hash ):
                    diff[ fileName ] = ( False, ctime, mtime, fileDict[ hash ] )
                else:
                    offset = f.tell();
                    source = open( pathName, "rb" )
                    while True:
                        x = source.read( 102400 )

                        if len(x):
                            f.write( x )
                        else:
                            break
                    source.close()
                            
                    diff[ fileName ] = ( True, ctime, mtime, offset, os.path.getsize( pathName ) )
            except IOError, e:
                print e
    finally:
        f.close()

    f = open( diffFile, "wb" ) 
    cPickle.dump( diff, f )
    f.close()


def copyContentWithHandle( target, source, sourceOffset, sourceLength ):
    if sourceOffset == 0 and sourceLength == -1:
        source.seek( 0, 2 )
        sourceLength = source.tell()
    source.seek( sourceOffset )
    while True:
        if sourceLength > 1024 * 1024:
            readSize = 1024 * 1024
        else:
            readSize = sourceLength
        x = source.read( readSize )
        sourceLength = sourceLength - readSize
        if len( x ):
            target.write( x )
        else:
            break


def copyContent( targetFileName, sourceFile, sourceOffset = 0, sourceLength = -1 ):
    directory = os.path.dirname( targetFileName )
    if not os.path.exists( directory ):
        os.makedirs( directory )

    target = open( targetFileName, "wb" )
    try:
        if sourceOffset == 0 and sourceLength == -1:
            src = open( sourceFile, "rb" )
            copyContentWithHandle( target, src, sourceOffset, sourceLength )
            src.close()
        else:
            copyContentWithHandle( target, sourceFile, sourceOffset, sourceLength )
    finally:
        target.close()


def mergeFolderDiff( folder, hashFile, diffFile, binFile, destFolder ):
    if folder[-1] != os.path.sep:
        folder = folder + os.path.sep
    if destFolder[-1] != os.path.sep:
        destFolder = destFolder + os.path.sep

    fileDict = {}
    f = open( hashFile, "rb" )
    fileDict = cPickle.load( f )
    f.close()

    diff = {}
    f = open( diffFile, "rb" )
    diff = cPickle.load( f )
    f.close()

    f = open( binFile, "rb" )
    try:
        for fileName in diff:
            try:
                pathName = folder + fileName
                record = diff[ fileName ]
                if record[0]:
                    copyContent( destFolder + fileName, f, record[3], record[4] )
                else:
                    copyContent( destFolder + fileName, folder + record[3] )

            except IOError, e:
                print e
    finally:
        f.close()


def processCommandLine():
    if len( sys.argv ) == 4 and sys.argv[1] == '-hash':
        generateFolderHash( sys.argv[2], sys.argv[3] )
    elif len( sys.argv ) == 6 and sys.argv[1] == '-diff':
        generateFolderDiff( sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] )
    elif len( sys.argv ) == 7 and sys.argv[1] == '-merge':
        mergeFolderDiff( sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6] )
    else:
        printUsage()


if __name__ == "__main__":
    processCommandLine()
