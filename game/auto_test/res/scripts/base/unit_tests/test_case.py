import BigWorld
import traceback
import time
import math

g_testCaseClasses = []

class TestMetaClass( type ):
	def __init__( cls, name, bases, dct ):
		super( TestMetaClass, cls ).__init__( name, bases, dct )
		if hasattr( cls, "run" ) and not cls.__dict__.get( "EXCLUDE_TEST" ):
			g_testCaseClasses.append( cls )


def fail_on_exception( f ):
	def wrapper( self, *args, **kwargs ):
		try:
			f( self, *args, **kwargs )
		except:
			self.onException()

	return wrapper


class TestCase( object ):
	# The metaclass is responsible for adding the test into the collection of
	# all tests.
	__metaclass__ = TestMetaClass

	def __init__( self ):
		self._hasFinished = False
		self.successful = True

	def name( self ):
		return self.__class__.__name__

	def start( self, testCases ):
		print "Starting test %s" % self.name()
		self._testCases = testCases
		self._startTime = time.time()
		try:
			self.run()
		except:
			self.onException()

	def runningTime( self ):
		try:
			return time.time() - self._startTime
		except AttribruteError:
			return 0.0

	def onException( self ):
		print "Exception caught while running test", self.name()
		traceback.print_exc()
		self.fail( None, False )
		self.finishTest()

	def hasStarted( self ):
		return hasattr( self, "_testCases" )

	def status( self ):
		if not self.hasStarted():
			return "PENDING"

		if not self._hasFinished:
			if self.successful:
				return "RUNNING"
			else:
				return "RUNNING (HAS FAILED)"

		return "PASSED" if self.successful else "FAILED"


	# This should be implemented by derived classes
	# def run( self ):
	#	self.finishTest()

	def assertTrue( self, expr, msg = None ):
		assert( not self._hasFinished )

		if not expr:
			self.fail( msg or "%r" % expr )

	def assertEqual( self, val1, val2, msg = None ):
		assert( not self._hasFinished )

		if val1 != val2:
			self.fail( msg or "%r != %r" % (val1, val2) )

	def assertAlmostEqual( self, val1, val2, epsilon = 0.0004, msg = None ):
		assert( not self._hasFinished )

		if math.fabs( val1 - val2 ) > epsilon:
			self.fail( msg or "%r != %r" % (val1, val2) )

	def assertNotEqual( self, val1, val2, msg = None ):
		assert( not self._hasFinished )

		if val1 == val2:
			self.fail( msg or "%r == %r" % (val1, val2) )

	def fail( self, msg = None, printStack = True ):
		if msg:
			print "Test %s failed assertion: %s" % (self.name(), msg )

		if printStack:
			# TODO: Make this nicer
			traceback.print_stack()

		self.successful = False

	def finishTest( self ):
		if not self._hasFinished:
			self._hasFinished = True
			self._testCases.finishTest( self )


class TestCases( object ):
	def __init__( self, classes, prefix = "default" ):
		# Make the tests in reverse order
		self._tests = [klass() for klass in classes[::-1]]
		self._numPassed = 0
		self._numFailed = 0
		self._currentTest = None

		self._watcherPrefix = "unitTests/%s/" % prefix

		self.addWatcher( "currentTest", self.currentTest )
		self.addWatcher( "numRemaining", self.numRemaining )
		self.addWatcher( "numPassed", self.numPassed )
		self.addWatcher( "numFailed", self.numFailed )

		for i, test in enumerate( self._tests[::-1] ):
			self.addWatcher( "result/%03d %s" % (i, test.name()), test.status )

	def addWatcher( self, name, func ):
		BigWorld.addWatcher( self._watcherPrefix + name, func )

	def numRemaining( self ):
		return len( self._tests )

	def numPassed( self ):
		return self._numPassed

	def numFailed( self ):
		return self._numFailed

	def currentTest( self ):
		if self._currentTest:
			return self._currentTest.name()
		else:
			return ""

	def run( self ):
		self.startNext()

	def finishTest( self, test ):
		assert self._currentTest == test

		resultStr = "PASSED" if self._currentTest.successful else "FAILED"
		testName = self._currentTest.name()

		print "Finished test %s: %s (%.2f seconds)" % \
			(testName, resultStr, self._currentTest.runningTime())

		if test.successful:
			self._numPassed += 1
		else:
			self._numFailed += 1

		self.startNext()

	def startNext( self ):
		self._currentTest = None

		if self._tests:
			self._currentTest = self._tests.pop()
			self._currentTest.start( self )
		else:
			print "All tests finished. Passed = %d. Failed = %d" % \
				(self._numPassed, self._numFailed)


def runAll( prefix = "default" ):
	testCases = TestCases( g_testCaseClasses, prefix )
	testCases.run()

# test_case.py
