import sys

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re)

if sys.platform != 'win32':
    msg = "Skipping Visual C/C++ test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

#####
# Test the basics

test.write('SConstruct',"""
import os
env = Environment(tools = ['MSVCCommon'])
""")

test.run(stderr = None)
test.pass_test()
