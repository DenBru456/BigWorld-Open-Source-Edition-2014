import os

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
cmd = 'python -m unittest discover ' + WORKING_DIR + ' --pattern=*_unit_test.py'
os.system(cmd)
