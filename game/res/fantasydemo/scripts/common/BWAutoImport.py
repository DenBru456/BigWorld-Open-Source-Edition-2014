# This module is automatically imported.

import BigWorld

def testUnicode():
	import unicode_test
	unicode_test.run()

def main():
	if BigWorld.component in ("database", "client"):
		testUnicode()

main()

# BWAutoImport.py
