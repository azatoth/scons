#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Test the ability to handle internationalized package and file meta-data.

These are x-rpm-Group, description, summary and the lang_xx file tag.
"""

import os
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

rpm = test.Environment().WhereIs('rpm')

if rpm:
    #
    # test INTERNATIONAL PACKAGE META-DATA
    #
    test.write( [ 'main.c' ], r"""
int main( int argc, char* argv[] )
{
  return 0;
}
""")

    test.write('SConstruct', """
import os

prog_install = Install( os.path.join( ARGUMENTS.get('prefix', '/'), 'bin'), Program( 'main.c' ) )

Package( projectname    = 'foo',
         version        = '1.2.3',
         type           = 'rpm',
         license        = 'gpl',
         summary        = 'hello',
         summary_de     = 'hallo',
         summary_fr     = 'bonjour',
         packageversion = 0,
         x_rpm_Group    = 'Application/office',
         x_rpm_Group_de = 'Applikation/büro',
         x_rpm_Group_fr = 'Application/bureau',
         description    = 'this should be really long',
         description_de = 'das sollte wirklich lang sein',
         description_fr = 'ceci devrait être vraiment long',
         source         = [ 'main.c', 'SConstruct', prog_install ],
        )

Alias ( 'install', prog_install )
""")

    test.run(arguments='', stderr = None)

    test.fail_test( not os.path.exists( 'foo-1.2.3-0.src.rpm' ) )
    test.fail_test( not os.path.exists( 'foo-1.2.3-0.i386.rpm' ) )
    cmd = 'LANGUAGE=%s && rpm -qp --queryformat \'%%{GROUP}-%%{SUMMARY}-%%{DESCRIPTION}\' %s'
    out = os.popen( cmd % ('de', test.workpath('foo-1.2.3-0.i386.rpm') ) ).read()
    test.fail_test( not out == 'Applikation/büro-hallo-das sollte wirklich lang sein' )
    out = os.popen( cmd % ('fr', test.workpath('foo-1.2.3-0.i386.rpm') )).read()
    test.fail_test( not out == 'Application/bureau-bonjour-ceci devrait être vraiment long' )
    out = os.popen( cmd % ('en', test.workpath('foo-1.2.3-0.i386.rpm') ) ).read()
    test.fail_test( not out == 'Application/office-hello-this should be really long' )
    out = os.popen( cmd % ('ae', test.workpath('foo-1.2.3-0.i386.rpm') ) ).read()
    test.fail_test( not out == 'Application/office-hello-this should be really long' )

#   DEACTIVATED until the problems with Installer <-> Packager collaboration are solved.
#
#    #
#    # test INTERNATIONAL PACKAGE TAGS
#    #
#
#    test.write( [ 'main.c' ], r"""
#int main( int argc, char* argv[] )
#{
#  return 0;
#}
#""")
#
#    test.write( ['man.de'], '' )
#    test.write( ['man.en'], '' )
#    test.write( ['man.fr'], '' )
#
#    test.write('SConstruct', """
#import os
#
#install_dir = os.path.join( ARGUMENTS.get('prefix', '.') )
#
#prog = Install( os.path.join( install_dir, 'bin' ), Program( 'main.c' ) )
#
#man_pages = Flatten( [
#  Install( os.path.join( install_dir, 'usr/share/man/de'), 'man.de' ),
#  Install( os.path.join( install_dir, 'usr/share/man/en'), 'man.en' ),
#  Install( os.path.join( install_dir, 'usr/share/man/fr'), 'man.fr' )
#] )
#
#Tag( man_pages, 'lang_de', 'doc', 'source' )
#
#Package( projectname    = 'foo',
#         version        = '1.2.3',
#         type           = 'rpm',
#         license        = 'gpl',
#         summary        = 'hello',
#         summary_de     = 'hallo',
#         summary_fr     = 'bonjour',
#         packageversion = 0,
#         x_rpm_Group    = 'Application/office',
#         x_rpm_Group_de = 'Applikation/büro',
#         x_rpm_Group_fr = 'Application/bureau',
#         description    = 'this should be really long',
#         description_de = 'das sollte wirklich lang sein',
#         description_fr = 'ceci devrait être vraiment long',
#         source         = [ 'main.c', 'SConstruct', prog, man_pages ],
#        )
#
#Alias ( 'install', install_dir )
#""")
#
#
#    test.run(arguments='--debug=stree prefix=blubb install', stderr = None)
#
#    test.fail_test( not os.path.exists( 'foo-1.2.3-0.src.rpm' ) )
#    test.fail_test( not os.path.exists( 'foo-1.2.3-0.i386.rpm' ) )

test.pass_test()
