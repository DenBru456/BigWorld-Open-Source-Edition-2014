import BigWorld
import srvtest

@srvtest.testSnippet
def selfTestSnippetInModule():
	srvtest.finish( ( True, "test", 123 ) )


@srvtest.testSnippet
def selfTestSnippetInModuleWithFailure():
	selfTestSnippetInModuleWithFailure_1()


@srvtest.testStep
def selfTestSnippetInModuleWithFailure_1():
	raise Exception()

