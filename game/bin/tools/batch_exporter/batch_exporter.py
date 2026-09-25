
from Tkinter import *
from tkFileDialog import askdirectory
from tkFileDialog import askopenfilename
import tkMessageBox
import os
import shutil
from time import gmtime, strftime, localtime
from datetime import datetime

g_lf = None #log file and full path

#Classes Capitalize first and all
class App( Frame ):
    def __init__( self, master = None ):
        Frame.__init__( self, master )
        frame = Frame( master )
        frame.pack()

        #Parent frame for Source folder picker and text field
        frameSourcePicker = Frame( master=frame )
        frameSourcePicker.pack()
        
        self.sourceButton = Button( master=frameSourcePicker, text = "Choose Source directory", command=self.chooseSourceDir )
        self.sourceButton.pack( side = LEFT, pady = 2, padx = 2 )

        self.sourceTextField = Entry( master=frameSourcePicker, width = 30 )
        self.sourceTextField.pack( side = RIGHT, pady = 2, padx = 2 )

        #Parent frame for Dest folder picker and text field
        frameDestPicker = Frame( master=frame )
        frameDestPicker.pack()
        
        self.destButton = Button( master=frameDestPicker, text = "Choose Export directory", command=self.chooseExpDir )
        self.destButton.pack( side = LEFT, pady = 2, padx = 2 )

        self.destTextField = Entry( master=frameDestPicker, width = 30 )
        self.destTextField.pack( side = RIGHT, pady = 2, padx = 2 )

        #Parent frame for options
        frameOptions = Frame( master=frame, padx=5, pady=5)
        frameOptions.pack()

        self.copyMaps = IntVar()
        copyMapsCb = Checkbutton( master=frameOptions, text = "Copy bitmaps and materials (.bmp, .tga, .dds, .mfm) to destination", variable=self.copyMaps )
        copyMapsCb.pack( anchor=W )

        self.copyVisualSettings = IntVar()
        copyVisualSettingsCb = Checkbutton( master=frameOptions, text = "Copy (.animationsettings, .visualsettings) to source directory", variable=self.copyVisualSettings )
        copyVisualSettingsCb.pack( anchor=W )

        ## Parent frame for Versions
        frameVersions = Frame( master=frameOptions, padx=5, pady=5)
        frameVersions.pack( anchor=W )

        ### Parent frame for MaxVersions
        frameMaxVersions = LabelFrame( master=frameVersions, padx=5, pady=5)
        frameMaxVersions.pack( side=LEFT, anchor=N )

        ####
        self.var3dsMax = IntVar()
        maxCb = Checkbutton( master=frameMaxVersions, text = "Export 3dsMax (.max) Files", variable=self.var3dsMax, command=self.changeMaxRadButtonState )
        maxCb.pack( anchor=W )
        
        #### Parent frame for 3dsMax versions
        frame3dsMaxVersion = LabelFrame( master=frameMaxVersions, text="Choose 3dsMax Version", borderwidth=1, padx=5, pady=5 )
        frame3dsMaxVersion.pack( anchor=W )

        #### Create Max version radiobuttons
        self.maxVersion = IntVar()
        self.maxRadButtons = [
            Radiobutton( master=frame3dsMaxVersion, text="3dsMax 2011x32bit", variable=self.maxVersion, value=0, state='disabled' ),            
            Radiobutton( master=frame3dsMaxVersion, text="3dsMax 2011x64bit", variable=self.maxVersion, value=1, state='disabled' ),
            Radiobutton( master=frame3dsMaxVersion, text="3dsMax 2012x32bit", variable=self.maxVersion, value=2, state='disabled' ),
            Radiobutton( master=frame3dsMaxVersion, text="3dsMax 2012x64bit", variable=self.maxVersion, value=3, state='disabled' ),
            Radiobutton( master=frame3dsMaxVersion, text="3dsMax 2013x32bit", variable=self.maxVersion, value=4, state='disabled' ),
            Radiobutton( master=frame3dsMaxVersion, text="3dsMax 2013x64bit", variable=self.maxVersion, value=5, state='disabled' ),
            Radiobutton( master=frame3dsMaxVersion, text="3dsMax 2014x32bit", variable=self.maxVersion, value=6, state='disabled' ),
            Radiobutton( master=frame3dsMaxVersion, text="3dsMax 2014x64bit", variable=self.maxVersion, value=7, state='disabled' ),
        ]
        for item in self.maxRadButtons:
            item.pack( anchor=W )


        ### Parent frame for MayaVersions
        frameMayaVersions = LabelFrame( master=frameVersions, padx=5, pady=5)
        frameMayaVersions.pack( side=RIGHT, anchor=N )

        ####
        self.varMaya = IntVar()
        mayaMbCb = Checkbutton( master=frameMayaVersions, text = "Export Maya Binary (.mb) Files", variable=self.varMaya )
        mayaMbCb.pack( anchor=W )

        self.varMayaMa = IntVar()
        mayaMaCb = Checkbutton( master=frameMayaVersions, text = "Export Maya ASCII (.ma) Files", variable=self.varMayaMa )
        mayaMaCb.pack( anchor=W )


        ##### Parent frame for Maya exe picker and text field
        frameMayaPicker = Frame( master=frameMayaVersions )
        frameMayaPicker.pack()

        self.instructionText2 = Label( master=frameMayaPicker, text="Select location of Maya executable.\n" +
                                    "If unselected, the exporter will use \n" +
                                    "system paths to launch maya\n", justify=LEFT )
        self.instructionText2.pack()
        
        self.mayaButton = Button( master=frameMayaPicker, text = "Choose Maya executable", command=self.chooseMayaLocation )
        self.mayaButton.pack()

        self.mayaTextField = Entry( master=frameMayaPicker, width = 30 )
        self.mayaTextField.pack( pady = 2, padx = 2 )

        ## Frame Options        
        self.varOverwriteFiles = IntVar()
        overwriteCb = Checkbutton( master=frameOptions, text = "Overwrite files", variable=self.varOverwriteFiles )
        overwriteCb.pack( anchor = W )

        #Parent frame for OK or Quit
        frameOkQuit = Frame( master=frame )
        frameOkQuit.pack()

        self.exportButton = Button( master=frameOkQuit, text = "Begin export", command=self.beginExport )
        self.exportButton.pack( side = LEFT, ipadx = 50, pady = 2, padx = 2 )

        self.quitButton = Button( master=frameOkQuit, text = "Quit", fg = "red", command=frame.quit )
        self.quitButton.pack( side = RIGHT )

    def chooseMayaLocation( self ):
        # Locate the Maya Exectuable
        self.mayaLocation = askopenfilename(filetypes=[("executables", "*.exe")], title = "Select Maya.exe" )
        self.mayaTextField.delete(0, END)
        self.mayaTextField.insert( 0, self.mayaLocation )

    def changeMaxRadButtonState( self ):
        # Turns the max radio buttons on/off
        for item in self.maxRadButtons:
            if self.var3dsMax.get() == 1:
                item.config( state='normal' )
            if self.var3dsMax.get() == 0:
                item.config( state='disabled' )

    def chooseSourceDir( self ):        
        self.rootDir = askdirectory( title = "Select Source directory", mustexist=1 )
        self.sourceTextField.delete(0, END)
        self.sourceTextField.insert( 0, self.rootDir )

    def chooseExpDir( self ):
        self.expDir = askdirectory( title = "Select Export directory", mustexist=1 )
        self.destTextField.delete(0, END)
        self.destTextField.insert( 0, self.expDir )

    def beginExport( self ):        
        sourceName = self.sourceTextField.get().strip()
        destName = self.destTextField.get().strip()
        overWrite = self.varOverwriteFiles.get()
        copyMaps = self.copyMaps.get()
        copyVisualSettings = self.copyVisualSettings.get()
        
        if sourceName == "" and destName == "":
            tkMessageBox.showwarning( "Error", "Souce and destination directories not defined.\nPlease choose a source and destination folder" )
        elif sourceName == "" and destName != "":
            tkMessageBox.showwarning( "Error", "Souce directory not defined.\nPlease choose a source folder" )
        elif sourceName != "" and destName == "":
            tkMessageBox.showwarning( "Error", "Destination directory not defined.\nPlease choose a destination folder" )
        else:
            if not os.path.exists( sourceName ):
                tkMessageBox.showwarning( "Error", "Source directory is invalid." )
            elif not os.path.exists( destName ):
                #Source exists but dest doesnt
                if tkMessageBox.askyesno( "Error", "Destination directory does not exist.\n Create directory?" ):
                    try: #make destination directory
                        os.makedirs( destName )
                    except os.error:
                        tkMessageBox.showwarning( "Error", "Failed to create destination directory" )
            else:
                # Create the source directory structure at destination
                exportDir ( sourceName, destName, overWrite, copyMaps, copyVisualSettings )

# Gets all directories and subdirectores of root
def recursiveDirGen( mydir ):
    for root, dirs, files in os.walk( mydir ):
        for dir in dirs:
            yield os.path.join( root, dir )

# Gets all files in directories and subdirectores of root
def recursiveFileGen( mydir ):
    for root, dirs, files in os.walk( mydir ):
        for file in files:
            yield os.path.join( root, file )

def createListOfExportFiles( logDir, fileName ): #logDir is root
    listOfExportFiles = os.path.join( logDir, fileName )
    return listOfExportFiles

def appendListFile ( data, list_file ): #Append function for both max and maya list
    list_file.write( data )
    list_file.write( "\n" )

def createLogFile(logDir): #logDir is root
    global g_lf
    logFile_url = os.path.join (logDir, 'export_log.txt')
    g_lf = open( logFile_url, 'a' )
    g_lf.write( "\n *** Export process started at " )
    t = strftime( "%a, %d %b %Y %H:%M:%S +0000", localtime())            
    g_lf.write( t )
    g_lf.write( "\n\n" )
    return logFile_url # need the string to pass to max, cant find files url from file object

def appendToLog ( data, logFile ):
    logFile.write( data )

def closeLogFile( logDir ):
    global g_lf
    logFile_url = os.path.join (logDir, 'export_log.txt')
    g_lf = open( logFile_url, 'a' ) # has to be re-openned as we closed this for maxscript/mel
    appendToLog( "*** Export process finished at ", g_lf )
    t = strftime( "%a, %d %b %Y %H:%M:%S +0000 ", gmtime() )            
    appendToLog( t, g_lf )
    appendToLog( "\n", g_lf )
    g_lf.close()

def fileExportFromList( tbemaxf_url, tbemayaf_url, overw, logFileString ):
    MAX_SYSTEM_VARS = ("3DSMAX_2011_PATH", "3DSMAX_2011x64_PATH", "ADSK_3DSMAX_x32_2012", "ADSK_3DSMAX_x64_2012", "ADSK_3DSMAX_x86_2013",
                          "ADSK_3DSMAX_x64_2013", "ADSK_3DSMAX_x86_2014", "ADSK_3DSMAX_x64_2014")
    os.path.normpath(tbemaxf_url)
    # replacing \ with / in maxFilesTxtList for cmd prompt
    tbemaxf_url.replace( "\\", "/" )
    os.path.normpath(tbemayaf_url)
    tbemayaf_url = tbemayaf_url.replace( "\\", "/" )
    logFileString = logFileString.replace( "\\", "/" )

    # If multiple versions of max/maya are going to be called modifications are required here

    #------Max------ Open Max and call a batch export function that is preloaded on max startup.
    if app.var3dsMax.get(): #If checkbox "export 3dsMax" is pressed.
        a = app.maxVersion.get()
        if not os.environ.has_key(MAX_SYSTEM_VARS[a]):
            tkMessageBox.showwarning( "Error", "3dsMax Environment Variable does not exist" )
            print "Environment Variable does not exist"
        basePath = os.environ[MAX_SYSTEM_VARS[a]]
        
        maxCmdString = '3dsmax\"'
        maxCmdOptions = ' -mxs \"BigWorld_Batch_Export \\\"' + tbemaxf_url + '\\\" ' + str(overw) + ' \\\"' + logFileString + '\\\"\"' #Python - dos - maxscript string literals
        varPathMaxCmdString = '\"\"' + basePath + maxCmdString
        varPathMaxCmdStringOptions = varPathMaxCmdString + maxCmdOptions
        os.system( varPathMaxCmdStringOptions )

    #-----MAYA------- Open Maya and call a batch export procedure that is already loaded by its userSetup.mel script
    if app.varMaya.get() or app.varMayaMa.get(): # Either .mb and .ma files selected
        if app.mayaTextField.get() != "": # Using user defined maya.exe path
            mayaExePath = app.mayaTextField.get()
            mayaCmdString = ("\"\"" + mayaExePath + "\"" + " -command 'BigWorld_Batch_Export(\"" + tbemayaf_url + "\", \"" + str(overw) + "\", \"" + logFileString + "\");\'" + "\"") #Python - dos - mel string literals
            os.system( mayaCmdString )            
        else: # Using System Path to locate maya.exe            
            mayaCmdString = ("maya -command 'BigWorld_Batch_Export(\"" + tbemayaf_url + "\", \"" + str(overw) + "\", \"" + logFileString + "\");\'") #Python - dos - mel string literals
            os.system( mayaCmdString )
        
    tkMessageBox.showwarning( "Complete", "Export complete, Log file created." )    
    
def exportDir( root, dest, overw, copyMaps, copyVisualSettings ):
    VISUAL_EXT = ".visual"
    ANIM_EXT = ".animation"
    EXTENSIONS = (".tga", ".jpg", ".dds", ".bmp", ".mfm")
    VIS_ANIM_SETTINGS = (".animationsettings", ".visualsettings")
    ANIM_SETTINGS = ".animationsettings"    
    
    #Create a log file, and a list of max and maya files to be exported
    tbemaxf_url = createListOfExportFiles( root, 'ListOfMaxFiles.txt' )
    tbemaxf = open( tbemaxf_url, 'w' )
    tbemayaf_url = createListOfExportFiles( root, 'ListOfMayaFiles.txt' )
    tbemayaf = open( tbemayaf_url, 'w' )
    
    logFileString = createLogFile( root )
    
    dirArray = list( recursiveDirGen( root )) #gets all folders + sub, full path in form ['C:\\tmp\\1', 'C:\\tmp\\2', 'etc']
    fileArray = list( recursiveFileGen( root )) #gets all files + sub, full path, note this will get other file types too.
    
    #Create a mirror of the root directory folders in dest
    for d in dirArray:
        try:
            #make directories
            os.makedirs( dest + d.lstrip( root ))
        except os.error:
            pass

    # Root directory added to the array of directories to export 
    dirArray.append( root )

    # Copy any texture maps    
    if copyMaps==True:
        for sf in fileArray:
            #check for file extension.
            ( fname, extension ) = os.path.splitext( sf )
            if extension in EXTENSIONS:
                sfdir = os.path.dirname( sf )
                relative_folders = str( sfdir.lstrip( root ))
                sf_with_ext = os.path.basename( sf )
                finalDest = dest+relative_folders
                shutil.copy( sf, finalDest )

    # Copy .visualsettings and .animationsettings file
    # This will be used by the max function to determine if both a .animation and .visual are require and it will preset any options
    if copyVisualSettings==True:
        for sf in fileArray:
            #check for file extension.
            ( fname, extension ) = os.path.splitext( sf )
            if extension in VIS_ANIM_SETTINGS:
                sfdir = os.path.dirname( sf )
                relative_folders = str( sfdir.lstrip( root ))
                sf_with_ext = os.path.basename( sf )
                finalDest = dest+relative_folders
                shutil.copy( sf, finalDest )            
    
    # Generate a list of max files and maya files from fileArray
    for sf in fileArray:
        #Get the source and dest
        sfdir = os.path.dirname( sf )
        relative_folders = str( sfdir.lstrip( root ))
        sf_with_ext = os.path.basename( sf )
        ( fname, extension ) = os.path.splitext( sf_with_ext )
        # The Maxsxcript BigWorld_Startup.ms function BigWorld_Load_Export_WriteLog will switch export type (.animation or .visual) depending on extension
        expf = dest + relative_folders + os.path.sep + fname

        # Write out the exportfile.txt 
        if extension == ".max":
            # This assumes that you will always want the .visual exported. May be problematic when only a .animation is required.
            appendListFile( sf + "\n" + expf + VISUAL_EXT, tbemaxf )
            animSetFileString = sfdir + "\\" + fname + ANIM_SETTINGS
            if animSetFileString in fileArray:
                appendListFile( sf + "\n" + expf + ANIM_EXT, tbemaxf )            
        elif extension == ".ma" and app.varMayaMa.get():  #Tests for .animationsettings will eventually be required here
            mixedSlash_url = ( sf + "\n" + expf )
            fixedSlash_url = mixedSlash_url.replace( "\\", "/" )
            appendListFile( fixedSlash_url, tbemayaf )
        elif extension == ".mb" and app.varMaya.get():
            mixedSlash_url = ( sf + "\n" + expf )
            fixedSlash_url = mixedSlash_url.replace( "\\", "/" )
            appendListFile( fixedSlash_url, tbemayaf )
    
    tbemaxf.close()
    tbemayaf.close()
    g_lf.close() #temporarily close log file so mel and max can edit it.
    
    fileExportFromList( tbemaxf_url, tbemayaf_url, overw, logFileString )
    closeLogFile( root )

root=Tk()
app = App( root )
app.master.title( "BigWorld Batch Exporter" )
root.mainloop()
root.destroy()


