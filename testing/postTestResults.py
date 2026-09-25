#! /usr/bin/env python

import sys
import inspect
import glob
from xml.dom import minidom
from datetime import date
from optparse import OptionParser

sys.path.append( "lib" )
import testrail
from bwtest import loader


def loadCurrentSuite( options ):
	sections = tr.get( "get_sections/%s&suite_id=%s" % ( options.project, options.suite) )
	for s in sections:
		s['cases'] = tr.get( "get_cases/%s&suite_id=%s&section_id=%s"
							% ( options.project, options.suite, s['id'] ) )
	return sections


def getSectionId( name, current ):
	for s in current:
		if s['name'] == name:
			return s['id']
	return None

def getCaseId( name, current ):
	for s in current:
		for case in s['cases']:
			if case['title'] == "%s (Automated)" % name:
				return case['id']
	return None


def clearTestCases( options ):
	sections = tr.get( "get_sections/%s&suite_id=%s" % \
							( options.project, options.suite ) )
	for s in sections:
		try:
			tr.post( "delete_section/%s" % s["id"], "" )
		except:
			pass
	
def populateTestCases( suite, current, options, parent_id = None ):
	
	sectionId = getSectionId(suite.name, current)
	
	if not sectionId:
		print "Adding section %s" % suite.name
		section = tr.post( "add_section/%s" % options.project,
						{"suite_id": options.suite, 
						"parent_id": parent_id, 
						"name": suite.name})
		sectionId = section["id"]
	
	for subSuite in suite.testsuites:
		populateTestCases( subSuite, current, options, sectionId )

	for case in suite.testcases:
		caseId = getCaseId( case.name, current )
		if not caseId:
			print "Adding case %s" % case.name
			url = "add_case/%s" % sectionId
		else:
			print "Updating case %s" % case.name
			url = "update_case/%s" % caseId
		notes = case.description.strip()
		classDir = "/".join(inspect.getmodule(case).__name__.split( "." )[0:-1])
		runString = "./runtests -v %s -c %s" % ( classDir,
												case.__class__.__name__)
		
		test_type = "Automated"
		if hasattr(case, "tags") and \
					( "MANUAL" in case.tags or "STAGED" in case.tags ):
			test_type = "Semi-Automated"
		data =  {"title": "%s (%s)" % (case.name, test_type),
				 "type_id": 1,
				 "priority_id": 4,
				 "custom_notes": notes,
				 "custom_procedure_and_results": runString
				 }

		tr.post( url, data )


def parseXMLResults( suite, current, outfolder, results ):
	
	for subSuite in suite.testsuites:
		parseXMLResults( subSuite, current, 'output', results)
	
	for case in suite.testcases:
		fullClassName = case.__module__+"."+case.__class__.__name__
		files = sorted( glob.glob( "%s/TEST-%s-*.xml" 
									% (outfolder, fullClassName ) ) )
		if not files:
			continue
		xmldoc = minidom.parse( files[-1] )
		caseId = getCaseId( case.name, current )
		suiteElement = xmldoc.getElementsByTagName( "testsuite" )[0]
		errors = int( suiteElement.getAttribute( 'errors' ) )
		failures = int( suiteElement.getAttribute( 'failures' ) )
		elapsed = suiteElement.getAttribute( 'time' )
		
		#Testrail cries if elapsed time ends in .000
		if elapsed.endswith( "0.000" ):
			elapsed = elapsed.refplace( "0.000", "0.001" )
		
		elapsed += "s"
		status = 1
		comment = ""
		
		if errors > 0:
			status = 4
			comment += "Error: \n"
			comment += suiteElement.getElementsByTagName( 
											"error" )[0].firstChild.wholeText
		elif failures > 0:
			status = 4
			comment += "Failure: \n"
			comment += suiteElement.getElementsByTagName( 
											"failure" )[0].firstChild.wholeText
		results[caseId] = {"status_id": status,
							"comment": comment,
							"elapsed": elapsed}


tr = testrail.TestRail( "http://testrail.bigworldtech.com", 
						"build", "build")
SUITE_ID=29
PROJECT_ID=3
VERSION = "Server 2.9"

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option( "-p", "--project", dest="project",
                  help="TestRail project id to report to", default=PROJECT_ID )
	parser.add_option("-s", "--suite", dest="suite",
                  help="TestRail suite id to report to", default=SUITE_ID )
	parser.add_option("-v", "--version",
                  help="Version to report the results as", default=VERSION )

	(options, args) = parser.parse_args()
	topSuite = loader.discover( "tests", [], ["WIP"], [] )
	current = {}
	
	#Clear test cases if there are no existing active test runs
	runs = tr.get( "get_runs/%s" % options.project )
	hasActiveRuns = False
	for run in runs:
		if run['suite_id'] == options.suite and not run['is_completed']:
			hasActiveRuns = True
			break
	if not hasActiveRuns:
		clearTestCases( options )
	
	for suite in topSuite.testsuites:
		populateTestCases( suite, current, options )
	
	#Reloading test cases after populating
	current = loadCurrentSuite( options )
	results = {}
	
	for suite in topSuite.testsuites:
		parseXMLResults( suite, current, 'output', results)
	
	#Add run
	runData = {'suite_id': options.suite,
				'name': "%s Automated Test Run - %s" % \
						( options.version, date.today().isoformat() ),
				'description': "",
				'include_all': True}
	runID = tr.post( 'add_run/%s' % options.project, runData )['id']
	
	#Get test IDs and post results
	tests = tr.get( 'get_tests/%s' % runID )
	for test in tests:
		if test['case_id'] in results:
			tr.post( 'add_result/%s' % test['id'], results[test['case_id']] )