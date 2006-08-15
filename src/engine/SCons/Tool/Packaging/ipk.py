"""SCons.Tool.Packaging.ipk
"""

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

import SCons.Builder
import os

from packager import SourcePackager, BinaryPackager, LocationTagFactory, SimpleTagCompiler

class IpkPackager(BinaryPackager, SourcePackager):
    def create_builder(self, env, kw=None):
        SCons.Tool.Tool( 'ipkg' ).generate(env)
        ipkbuilder = env['BUILDERS']['Ipkg']
        env['IPKGUSER']  = os.popen('id -un').read().strip()
        env['IPKGGROUP'] = os.popen('id -gn').read().strip()
        env['IPKGFLAGS'] = SCons.Util.CLVar('-o $IPKGUSER -g $IPKGGROUP')
        env['IPKGCOM']   = '$IPKG $IPKGFLAGS ${SOURCE.get_path().replace("/CONTROL/control","")}'
        ipkbuilder.push_emitter(self.specfile_emitter)

        self.pkg_root    = "%s-%s" % ( kw['projectname'], kw['version'] )
        pkg_root_emitter = SourcePackager.package_root_emitter(self, self.pkg_root)
        ipkbuilder.push_emitter( pkg_root_emitter )

        return ipkbuilder

    def add_targets(self, kw):
        """ tries to guess the filenames of the generated IPKG files.
        """
        version      = kw['version']
        projectname  = kw['projectname']
        architecture = kw['x_ipk_architecture']

        kw['target'] = [ "%s_%s_%s.ipk" % (projectname, version, architecture) ]

        return kw

    def create_specfile_targets(self, env):
        """ returns the specfile target names.
        """
        targets  = []
        pkg_root = env.Dir( self.pkg_root )
        #targets.append( pkg_root )
        control  = pkg_root.Dir( 'CONTROL' )
        targets.append( control.File( 'control' ) )
        targets.append( control.File( 'conffiles' ) )
        targets.append( control.File( 'postrm' ) )
        targets.append( control.File( 'prerm' ) )
        targets.append( control.File( 'postinst' ) )
        targets.append( control.File( 'preinst' ) )
        return targets

    def build_specfile(self, target, source, env):
        """ Builds the CONTROL/control file from the target list by finding the
        PackageMetaData in the env dictionary.

        Afterwards the list of files is copied in.
        """
        control_target   = filter( lambda x: x.get_path().rfind('control') != -1, target )[0]
        control_file     = open(control_target.abspath, 'w')

        try:
            # XXX: portability
            if not env.has_key('x_ipk_description'):
                env['x_ipk_description'] = "%s\n %s" % ( env['summary'],
                                                        env['description'].replace( '\n', '\n ' ) )

            # assert that the mandatory field are there.
            env['projectname']
            env['version']
            env['x_ipk_priority']
            env['x_ipk_section']
            env['x_ipk_source']
            env['x_ipk_architecture']
            env['x_ipk_maintainer']
            env['x_ipk_depends']
            env['x_ipk_description']

            content = """
Package: $projectname
Version: $version
Priority: $x_ipk_priority
Section: $x_ipk_section
Source: $x_ipk_source
Architecture: $x_ipk_architecture
Maintainer: $x_ipk_maintainer
Depends: $x_ipk_depends
Description: $x_ipk_description
"""
            control_file.write( env.subst(content) )
            control_file.close()
            self.handle_other_control_files(target, source, env)
        except KeyError, e:
            raise SCons.Errors.UserError( '"%s" package field for IPK is missing.' % e.args[0] )

    def handle_other_control_files(self, target, source, env):
        """ this function cares for CONTROL/conffiles, CONTROL/post*, CONTROL/pre*
        files.
        """
        output_files = {}
        def get_file( file ):
            target_file = filter( lambda x: x.get_path().rfind(file) != -1, target )[0]
            if not output_files.has_key(file):
                output_files[file] = open(target_file.abspath, 'w')

            return output_files[file]

        for f in source:
            tags = f.get_tags()
            if tags.has_key( 'conf' ):
                get_file( 'conffiles' ).write( tags['install_location'][0].get_path() )
                get_file( 'conffiles' ).write( '\n' )

        for str in 'postrm prerm postinst preinst'.split():
            if env.has_key( "x_ipk_%s" % str ):
                get_file( str ).write( env[str] )

        for f in output_files.values():
            f.close()
