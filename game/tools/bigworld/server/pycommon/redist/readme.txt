Using Python libraries
===============================================================================

Here's an two ways of using the libraries in this directory. We assume we're
currently in a directory below mf/bigworld/tools/server/.

--------------------------------------------------------------------------------
METHOD 1 - Using an undocumented feature of pkg_resources. This is the
recommended way to do things (for the eason, see Method 2 description).
--------------------------------------------------------------------------------

__requires__ = [
	"TurboGears>=1.0.0",
	"SQLObject==0.8.1",
	"flashticle",
	]
import sys
sys.path.insert( 0, "../pycommon/redist" )
import pkg_resources

# Somewhere later in the program, perhaps in another module
import turbogears
import sqlobject
import flashticle

--------------------------------------------------------------------------------
METHOD 2 - Using the documented way to use pkg_resources.

This has a fairly high chance of raising VersionConflict errors - this occurs
if there are already active .egg distributions in the site-packages directory
which don't meet any requirements set by the user.

e.g. if there's an active TurboGears 0.9 egg in the site-packages directory, 
and we try to use TurboGears 1.0.1 from this directory, this will cause a
VersionConflict exception. The above method doesn't have this problem (in 
fact, I think it was created to avoid this problem).

Because the likelihood of this happening can be quite high, I can't recommend
this method.
--------------------------------------------------------------------------------

import sys
sys.path.insert( 0, "../pycommon/redist" )
from pkg_resources import require
require( "TurboGears>=1.0.0" )
require( "SQLObject==0.8.1" )
require( "flashticle" )

# Somewhere later in the program, perhaps in another module
import turbogears
import sqlobject
import flashticle


Use with Python 2.5
===============================================================================

They seem to be tied to the Python version - you'll noticed they all contain
"2.4" in their names. This means that when moving to Python 2.5, pkg_resources
will not consider any of these eggs to be suitable.

The best thing to do is to acquire new eggs using easy_install, which will
pull the appropriate eggs from the Python Cheeseshop. 

I suspect it may be possible to simply rename these eggs, but no guarantees
there. I also suspect .eggs containing C extensions (those which contain a CPU
architecture in their name, such as "PyProtocols-1.0a0-py2.4-linux-i686.egg")
will also need recompiling from the source to link with the newer Python
library.

Pulling latest or new eggs
===============================================================================

Get the latest copy of easy_install from
http://peak.telecommunity.com/DevCenter/EasyInstall, then for each package
that needs to be retrieved, run:

easy_install -zmaxd . <package-name>

See documentation for easy_install for more details on specifying version
rules for the packages to download. Some examples are below:

easy_install -zmaxd . TurboGears>=1.0.0
easy_install -zmaxd . MySQL-python>=1.2.2
easy_install -zmaxd . SQLObject==0.8.1

For packages with multiple dependencies, this will also download the depended
eggs as well, so there is no need to individually get every single package.

Other tricks
===============================================================================

Egg packages can be either zip compressed files or directories. So if you
need to do some debugging with some of these packages, you can replace the
zipped .egg with the unzipped version. This is usually a three stage process:

1) Unzip the compressed .egg to an intermediate directory
2) Rename, move or delete the compressed .egg file.
3) Rename the intermediate directory to the same name as the original .egg.
