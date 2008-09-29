import sys

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re)

if sys.platform != 'win32':
    msg = "Skipping Visual C/C++ test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

#####
# Test the basics

test.write('SConstruct',"""
from SCons.Tool.MSVCCommon import FindMSVSBatFile, ParseBatFile, MergeMSVSBatFile, query_versions
#env = Environment(tools = ['mingw'])
DefaultEnvironment(tools = [])
#for v in [9, 8, 7.1, 7]:
#    print " ==== Testing for version %s ==== " % str(v)
#    bat = FindMSVSBatFile(v)
#    print bat
#    if bat:
#        d = ParseBatFile(bat)
#        for k, v in d.items():
#            print k, v
#MergeMSVSBatFile(env, 9.0)
#print env['ENV']['PATH']
print query_versions()
""")

test.run(stderr = None)
test.pass_test()
