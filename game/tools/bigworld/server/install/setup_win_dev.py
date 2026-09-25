#!/usr/bin/env python

import os
import stat
import sys
import pwd
import tempfile
import getpass
import shutil
import optparse

import bwsetup; bwsetup.addPath( ".." )
from pycommon import util
util.setUpBasicCleanLogging()

import logging
log = logging.getLogger( __name__ )


SUDO_USAGE = """
Please check the following before continuing:

1) Your sysadmin has entered you in the sudoers file on this box (with `visudo`)
2) You know where your home directory ($HOME) is on this machine
3) You have shared the MF directory on your Windows machine
4) You have allowed full control for everyone on your Windows share
""".lstrip()

USAGE = """
NOTE: If you are immediately prompted for a password, enter your *own*
      password not that of the root user.\n""".lstrip()

BW_BINARY_PATH = "bigworld/bin"

# Alias this common function call
prompt = util.prompt

# This function writes a file 'fname' with contents 'text', using sudo to
# write with appropriate permissions.
def sudo_fwrite( text, fname ):
	fd, tmpname = tempfile.mkstemp()
	done = os.write( fd, text )
	if done != len( text ):
		log.error( "Only %d/%d bytes written to %s" % (done, len( text ), tmpname) )
		return False

	if os.system( "sudo cp %s %s" % (tmpname, fname) ):
		log.error( "Couldn't `sudo cp` %s -> %s" % (tmpname, fname) )
		return False

	return True


def promptUntilNotNull( question ):
	answer = None
	while not answer or not len( answer.strip() ):
		answer = prompt( question )

	return answer


# This class is a convenient mechanism for passing around all the information
# required for connecting to and interacting with the Windows host containing
# the BigWorld data.
class WinShareMountAssistant( object ):

	def __init__( self, passwordEntry ):
		# Windows credentials and locations.
		self.username = None
		self.password = None
		self.sharePath = None
		self.shouldAutoMount = False
		self.isAlreadyMounted = False


		# Linux machine credentials and locations.
		self.systemUid = passwordEntry.pw_uid
		self.systemGid = passwordEntry.pw_gid
		self.systemUsername = passwordEntry.pw_name
		self.homeDir = passwordEntry.pw_dir
		self.credentialsFile = "%s/.bw_share_credentials" % self.homeDir
		self.destinationPath = None

		self.originalFstab = None


	# This function queries the user for the desired destination for the
	# mounted file system to be linked into.
	# If the directory exists we should ensure that:
	# - something else isn't already linked in there
	# - we can create the directory if required
	def setupBigWorldRootDirectory( self, bw_root = None ):

		print "* Setting up destination location for Windows resources"

		if bw_root == None:
			bw_root = "%s/bigworld_windows_share" % self.homeDir

		self.destinationPath = bw_root

		return util.softMkDir( bw_root )


	# This method queries the user for the information required to locate and
	# mount the BigWorld resouces on a Windows machine.
	def discoverWindowsShareLocation( self ):

		print "* Querying location of remote resources\n"

		# enter the hostname to use
		hostname = promptUntilNotNull( "Enter the hostname of your Windows "
										"machine" )

		# enter the directory
		share = promptUntilNotNull( "Enter the share name of the shared "
										"BigWorld directory" )

		# User credentials
		print
		print( "We now need the username and password required to connect to "
				"the Windows share" )
		username = prompt( "Username", self.systemUsername )
		password = confPasswd = None

		while not password or password != confPasswd:
			if confPasswd != None:
				print( "Passwords don't match, try again." )

			password = getpass.getpass( "Password: " )
			confPasswd = getpass.getpass( "Confirm password: " )

		self.username = username
		self.password = password
		self.sharePath = "//%s/%s" % (hostname, share)
		
		print
		print( "Using remote location: '%s'" % self.sharePath )
		print


	def discoverAutoMount( self ):
		print
		# Ask the user if they want to automount on every boot
		self.shouldAutoMount = util.promptYesNo(
			"Do you want to automount your Windows share each time this "
			"Linux box boots?\n"
			"This will place a file in your home directory containing a "
			"clear-text copy\nof your password that is only readable by "
			"your user." )

		print


	# This method writes the username and password into the home directory
	# of the user running the script.
	def writeCredentials( self ):
		fp = open( self.credentialsFile, "w" )
		fp.write( "username=%s\n" % self.username )
		fp.write( "password=%s\n" % self.password )
		fp.close()

		# Make the file only read/writeable by the owner to protect the
		# password.
		os.chmod( self.credentialsFile, stat.S_IRUSR | stat.S_IWUSR )


	def updateFSTab( self ):

		# Patch /etc/fstab if necessary
		self.originalFstab = open( "/etc/fstab", "r" ).read().rstrip()

		fstablines = self.originalFstab.split( "\n" )

		# Work on a copy of fstablines as we want to modify it, removing any
		# exiting entries for the mount points we are dealing with.
		for line in list( fstablines ):
			if self.sharePath in line or self.destinationPath in line:
				fstablines.remove( line )

		if self.shouldAutoMount:
			credentials = "credentials=%s" % self.credentialsFile
		else:
			credentials = "user=%s,noauto" % self.username

		# Now add our mount point to the fstab collection
		fstablines.append( "%s\t%s\tcifs\tuid=%d,gid=%d,"
						   "file_mode=0755,dir_mode=0755,%s\t0 0\n" % \
						   (self.sharePath, self.destinationPath,
							self.systemUid, self.systemGid, credentials) )

		# Try to write patched table back to /etc/fstab
		if sudo_fwrite( "\n".join( fstablines ), "/etc/fstab" ):
			print( "Patched /etc/fstab successfully" )

		else:
			log.error( "Unable to patch /etc/fstab with desired details" )
			sys.exit( 1 )



	def checkMountPoints( self ):
		isOkay = True

		# Check if it is already correctly mounted
		commandStr = "mount | grep '%s on %s'" % \
						(self.sharePath, self.destinationPath)
		grepout = os.popen( commandStr ).read().strip()
		if grepout:
			print( "It appears that '%s' has been mounted already:\n\t%s" %
						(self.sharePath, grepout) )

			if util.promptYesNo( "Is this correct?" ):
				self.isAlreadyMounted = True
				return isOkay

		# Check if something else is mounted at the mount point
		commandStr = "mount | grep 'on %s'" % self.destinationPath
		grepout = os.popen( commandStr ).read().strip()
		if grepout:
			print( "Unmounting existing mount at %s" % self.destinationPath)
			os.system( "sudo umount %s" % self.destinationPath )

		if os.path.isdir( self.destinationPath ) and \
			os.listdir( self.destinationPath ):

			log.error( "%s already exists and is not empty",
							self.destinationPath )
			isOkay = False

		if os.path.exists( self.destinationPath ) and \
			not os.path.isdir( self.destinationPath ):

			log.error( "%s already exists and is not a directory",
							self.destinationPath )
			isOkay = False

		return isOkay



	# This method configures the /etc/fstab file and the mounts the share
	# after verifying that the mount points are not already in use.
	def mountShare( self ):

		if not self.checkMountPoints():
			sys.exit( 1 )

		self.discoverAutoMount()

		if self.shouldAutoMount:
			self.writeCredentials()

		self.updateFSTab()

		# Attempt to mount the windows MF dir
		if self.isAlreadyMounted or \
			os.system( "sudo mount %s" % self.destinationPath ) == 0:

			print( "%s is mounted at %s" % 
						(self.sharePath, self.destinationPath) )

		else:
			log.error( "Couldn't mount shared Windows directory, "
						"restoring original fstab" )
			sudo_fwrite( self.originalFstab, "/etc/fstab" )
			log.error( "Aborting due to previous errors" )
			sys.exit( 1 )


def main( mountDir = None ):

	print USAGE

	print "* Validating user has 'sudo' privileges"
	# Verify we are in the sudoers file
	if os.system( "sudo ls > /dev/null" ):
		log.error( "You must be in the sudoers list for this machine" )
		print
		print SUDO_USAGE
		return 1

	# Who are we configuring for
	ent = pwd.getpwuid( os.getuid() )

	if not os.path.exists( ent.pw_dir ):
		log.error( "No $HOME directory exists for the current user." )
		return 1

	winAssist = WinShareMountAssistant( ent )

	if not winAssist.setupBigWorldRootDirectory( mountDir ):
		raise RuntimeError( "Unable to create destination for Windows share." )

	winAssist.discoverWindowsShareLocation()
	winAssist.mountShare()

	print( "* Windows directory successfully mounted" )


def parseOptions():
	opt = optparse.OptionParser( usage = USAGE )

	opt.add_option( "-m", "--mount-dir",
		dest = "bigworld_root",
		default = None,
		help = "The directory where the Windows share will be mounted" )

	options, args = opt.parse_args()

	mountDir = options.bigworld_root
	if mountDir != None:
		mountDir = os.path.abspath( mountDir )

	return mountDir


if __name__ == "__main__":
	try:
		mountDir = parseOptions()
		sys.exit( main( mountDir ) )
	except KeyboardInterrupt:
		print "\n[terminated]"
	except RuntimeError, e:
		print e
