"""
This is a perforce helper tool that operates on a perforce workspace directory recursively.
It detects and removes *outstanding* files (i.e. any files that aren't tracked/versioned in perforce).

**NOTE**: This is NOT the same as a perforce (delete + sync) or reconcile! This script:
 - Does NOT handle restoring missing files (tracked files that have been deleted).
 - Does NOT handle restoring modified files back to their original state.
 - (BUG) Does NOT respect files that have been marked for add (added but not committed).
		 These files will get deleted! careful! One way to protect them is to shelve added
		 files prior to running this script and then unshelve them afterwards.

So, you should only use it to remove "extra" files that are not tracked in perforce. This 
script was created to help speed up test cycles of asset pipeline's generated assets.

You can run this script prior to a perforce force-sync to have a potentially faster "clean"
operation than doing a reconcile (dont need to compare/hash all files). 

There is a simple whitelist below for protecting certain filepaths and extensions.

Relies on "p4" command to be available. If you get errors running this command complaining 
about bad port or client, make sure you set the relevant p4 environment variables using the
"p4 set " command.

e.g:

	p4 set P4PORT=perforce:1666
	p4 set P4CLIENT=<workspace_name>

	where <workspace_name> is the workspace you use in p4v (e.g. bob_windows)
	... or through any of the other documented equivalent mechanisms

"""

import os
import re
import subprocess
import time
import platform

# This white list does not support regex or glob syntax
# it only matches a given "xyz" for paths that end with "xyz" exactly.
whitelist = [
	# protect this script file!
	"p4_remove_unversioned.py",		

	"asset_rules.xml",	# custom asset rules
	".exe",				# executables
	".pdb",				# debug symbols
	".dll",				# dynamic link libraries (some debug variants aren't tracked)
	".ilk",				# MSVC incremental link status file	(build box artifact)
]

class PerforceException(Exception):
	pass

def ascii_line(c="-", n=80):
	return c*n

def sanitize_path(absolute_path):
	"""
	if on windows, case is insensitive.
	so make drive letter (assumed first char for abs path) lowercase for
	comparison purposes.
	this is needed if certain tools/env change capitalisation:
		- p4 clientspec mapping having lowercase,
		- running in MSYS/git bash/cygwin environment
	since python path libraries return uppercase drive letter.
	"""
	return os.path.normcase(absolute_path)

def get_p4_have_set(base_dir="."):
	"""
	:rtype : set
	"""
	perforce_command = "p4"
	args = [perforce_command, 'have', os.path.join(base_dir, '...')]
	try:
		p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(stdoutdata, stderrdata) = p.communicate()
		p.wait()
		success = (p.returncode == 0)
	except WindowsError, we:
		raise PerforceException("Error calling perforce command '%s', please make sure it is installed." % perforce_command)
	if stderrdata:
		perforce_exc = PerforceException(stderrdata)
		raise perforce_exc

	# TODO: should use -G flag and unmarshal stdout data
	# which would properly handle the case where a file name 
	# actually has a "#2 - " or similar pattern.
	out_have_set = set()
	if success:
		rgx = re.compile(r".+(#\d+ - )(.*$)")
		for line in stdoutdata.splitlines():
			m = rgx.search(line)
			if m:
				if len(m.groups()) == 2:
					local_abs_path = sanitize_path(m.groups()[1])
					out_have_set.add(local_abs_path)
	return out_have_set

def delete_filepaths(paths, verbose=True):
	if isinstance(paths, basestring):
		paths = [paths]
	total = len(paths)
	deleted = 0
	failures = []
	for i, p in enumerate(paths):
		if verbose:
			print "deleting [%d/%d] %s" % (i+1, total, p)
		try:
			os.remove(p)
			deleted += 1
		except OSError, ose:
			failures.append(ose)
	return deleted, failures

def main(user_confirmation=True, show_files_on_confirm=True, pause_on_exit=True):
	start_dir = "."
	print "retrieving have list..."
	try:
		have = get_p4_have_set(base_dir=start_dir)
	except PerforceException, perforce_exc:
		# TODO: probably should print error to stderr
		print ascii_line()
		print perforce_exc
		print "exiting..."
		return

	print "tracking %d files in this directory" % len(have)
	print "scanning %s recursively..." % (os.path.abspath(start_dir))
	found = []
	failures = []
	subdir_count = 0
	prev_report_time = time.time()
	for r, ds, fs in os.walk(start_dir):
		root_path = os.path.abspath(r)
		found.extend([sanitize_path(os.path.join(root_path, f)) for f in fs if not any((f.endswith(wi) for wi in whitelist))])
		subdir_count += 1
		if time.time() - prev_report_time > 5.0:
			print "scanned %d dirs, found %d files..." % (subdir_count, len(found))
			prev_report_time = time.time()

	print "-"*60
	print "found %d local files" % ( len(found) )
	print "resolving outstanding files for deletion..."
	to_delete = sorted(list(set(found).difference(have)))
	found = None
	have = None

	do_delete = True
	if len(to_delete) == 0:
		do_delete = False
	elif user_confirmation:
		if show_files_on_confirm:
			for p in to_delete:
				print p
		if raw_input("found %d items for deletion. delete? [y\N]: " % len(to_delete)).lower() != "y":
			return

	deleted = 0
	if do_delete:
		delete_count, delete_failures = delete_filepaths(to_delete)
		deleted += delete_count
		failures.extend(delete_failures)
	elif not deleted:
		print "no items found!"

	if failures:
		print
		print "failures:"
		print ascii_line()
		for exc in failures:
			print exc
		print ascii_line()
		print

	if deleted:
		print "deleted %d of %d items, with %d failures" % (deleted, len(to_delete), len(failures))

	if pause_on_exit:
		raw_input("press any key to continue...")

if __name__ == "__main__":
	main()
