"""SCons.Tool.Packaging.rpm

The rpm packager.
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

from packager import BinaryPackager, LocationTagFactory, SimpleTagCompiler
from targz import TarGz

class Rpm(BinaryPackager):
    def create_builder(self, env, kw=None):
        rpmbuilder      = env.get_builder('Rpm')
        env['RPMFLAGS'] = SCons.Util.CLVar('-ta')

        rpmbuilder.push_emitter(self.targz_emitter)
        rpmbuilder.push_emitter(self.specfile_emitter)
        rpmbuilder.push_emitter(self.strip_install_emitter)

        return rpmbuilder

    def add_targets(self, kw):
        """ tries to guess the filenames of the generated RPMS files.
        """
        version           = kw['version']
        projectname       = kw['projectname']
        packageversion    = kw['packageversion']
        # XXX: this shoudl be guessed depending on the env.
        buildarchitecture = 'i386'

        if kw.has_key('architecture'):
            buildarchitecture = kw['architecture']

        srcrpm = '%s-%s-%s.src.rpm' % (projectname, version, packageversion)
        binrpm = srcrpm.replace( 'src', buildarchitecture )

        kw['target'] = [ srcrpm, binrpm ]

        return kw

    def create_specfile_targets(self, env):
        return "%s-%s.spec" % (env['projectname'], env['version'])

    def build_specfile(self, target, source, env):
        """ Builds a RPM specfile from a dictionary with string metadata and
        by analyzing a tree of nodes.
        """
        file = open(target[0].abspath, 'w')
        str  = ""

        try:
            file.write( self.build_specfile_header(env) )
            file.write( self.build_specfile_sections(env) )
            file.write( self.build_specfile_filesection(env, source) )
            file.close()

            # call a user specified function
            if env.has_key('change_specfile'):
                env['change_specfile'](target, source)

        except KeyError, e:
            raise SCons.Errors.UserError( '"%s" package field for RPM is missing.' % e.args[0] )

    def targz_emitter(self, target, source, env):
        """ Puts all source files into a tar.gz file.
        """
        targz   = TarGz()
        builder = targz.create_builder(env)

        # XXX: this might be  inrobust!
        # the rpm tool depends on a source package, until this is chagned
        # this hack needs to be here that tries to pack all sources in.
        # <nastyHack>
        sources = []
        def add_sources(files):
            for f in files:
                if f.sources == [] or f.get_path().find('.spec') != -1:
                    sources.append(f)
                else:
                    add_sources(f.sources)
        add_sources(source)

        sources.append(env.fs.File('SConstruct'))
        from glob import glob
        sources.extend(map(env.fs.File, glob('SConscript')))

        if env.has_key('x_rpm_additional_source_files'):
            sources.extend( env.arg2nodes( env['x_rpm_additional_source_files'], env.fs.Entry ) )
        # </nastyHack>

        # create a special emitter, which does not honor the install_location
        # tag, so we get a real *source* package.
        package_root    = targz.create_package_root(env)
        builder.emitter = targz.package_root_emitter(package_root, honor_install_location=0)

        # as the source contains the url of the source package this rpm package
        # is built from, we extract the target name
        try:
            tarball = env['source_url'].split('/')[-1]
        except KeyError, e:
            raise SCons.Errors.UserError( "Missing PackageTag '%s' for RPM packager" % e.args[0] )

        tarball = builder(env, source=sources, target=tarball)

        return (target, tarball)

    #
    # mandatory and optional package tag section
    #
    def build_specfile_sections(self,spec):
        """ Builds the sections of a rpm specfile.
        """
        str = ""

        mandatory_sections = {
            'description'  : '\n%%description\n%s\n\n', }

        str += SimpleTagCompiler(mandatory_sections).compile( spec )

        optional_sections = {
            'description_'        : '%%description -l %s\n%s\n\n',
            'changelog'           : '%%changelog\n%s\n\n',
            'x_rpm_PreInstall'    : '%%pre\n%s\n\n',
            'x_rpm_PostInstall'   : '%%post\n%s\n\n',
            'x_rpm_PreUninstall'  : '%%preun\n%s\n\n',
            'x_rpm_PostUninstall' : '%%postun\n%s\n\n',
            'x_rpm_Verify'        : '%%verify\n%s\n\n',

            # These are for internal use but could possibly be overriden
            'x_rpm_Prep'          : '%%prep\n%s\n\n',
            'x_rpm_Build'         : '%%build\n%s\n\n',
            'x_rpm_Install'       : '%%install\n%s\n\n',
            'x_rpm_Clean'         : '%%clean\n%s\n\n',
            }

        # Default prep, build, install and clean rules
        if not spec.has_key('x_rpm_Prep'):
            spec['x_rpm_Prep'] = 'rm -rf $RPM_BUILD_ROOT'
            spec['x_rpm_Prep'] += '\n%setup -q'

        if not spec.has_key('x_rpm_Build'):
            spec['x_rpm_Build'] = 'mkdir $RPM_BUILD_ROOT'

        if not spec.has_key('x_rpm_Install'):
            spec['x_rpm_Install'] = 'scons --install-sandbox=$RPM_BUILD_ROOT $RPM_BUILD_ROOT'

        if not spec.has_key('x_rpm_Clean'):
            spec['x_rpm_Clean'] = 'rm -rf $RPM_BUILD_ROOT'

        str += SimpleTagCompiler(optional_sections, mandatory=0).compile( spec )

        return str

    def build_specfile_header(self, spec):
        """ Builds all section but the %file of a rpm specfile
        """
        str = ""

        # first the mandatory sections
        mandatory_header_fields = {
            'projectname'    : '%%define name %s\nName: %%{name}\n',
            'version'        : '%%define version %s\nVersion: %%{version}\n',
            'packageversion' : '%%define release %s\nRelease: %%{release}\n',
            'x_rpm_Group'    : 'Group: %s\n',
            'summary'        : 'Summary: %s\n',
            'license'        : 'License: %s\n', }

        str += SimpleTagCompiler(mandatory_header_fields).compile( spec )

        # now the optional tags
        optional_header_fields = {
            'vendor'              : 'Vendor: %s\n',
            'url'                 : 'Url: %s\n',
            'source_url'          : 'Source: %s\n',
            'summary_'            : 'Summary(%s): %s\n',
            'x_rpm_Distribution'  : 'Distribution: %s\n',
            'x_rpm_Icon'          : 'Icon: %s\n',
            'x_rpm_Packager'      : 'Packager: %s\n',
            'x_rpm_Group_'        : 'Group(%s): %s\n',

            'x_rpm_Requires'      : 'Requires: %s\n',
            'x_rpm_Provides'      : 'Provides: %s\n',
            'x_rpm_Conflicts'     : 'Conflicts: %s\n',
            'x_rpm_BuildRequires' : 'BuildRequires: %s\n',

            'x_rpm_Serial'        : 'Serial: %s\n',
            'x_rpm_Epoch'         : 'Epoch: %s\n',
            'x_rpm_AutoReqProv'   : 'AutoReqProv: %s\n',
            'x_rpm_ExcludeArch'   : 'ExcludeArch: %s\n',
            'x_rpm_ExclusiveArch' : 'ExclusiveArch: %s\n',
            'x_rpm_Prefix'        : 'Prefix: %s\n',
            'x_rpm_Conflicts'     : 'Conflicts: %s\n',

            # internal use
            'x_rpm_BuildRoot'     : 'BuildRoot: %s\n', }

        # fill in default values:
    #    if not s.has_key('x_rpm_BuildRequires'):
    #        s['x_rpm_BuildRequires'] = 'scons'

        if not spec.has_key('x_rpm_BuildRoot'):
            spec['x_rpm_BuildRoot'] = '%{_tmppath}/%{name}-%{version}-%{release}'

        str += SimpleTagCompiler(optional_header_fields, mandatory=0).compile( spec )
        return str

    #
    # mandatory and optional file tags
    #
    def build_specfile_filesection(self, spec, files):
        """ builds the %file section of the specfile
        """
        str  = '%files\n'

        if not spec.has_key('x_rpm_defattr'):
            spec['x_rpm_defattr'] = '(-,root,root)'

        str += '%%defattr %s\n' % spec['x_rpm_defattr']

        supported_tags = {
            'config'           : '%%config %s',
            'config_noreplace' : '%%config(noreplace) %s',
            'doc'              : '%%doc %s',
            'unix_attr'        : '%%attr %s',
            'lang_'            : '%%lang(%s) %s',
            'x_rpm_verify'     : '%%verify %s',
            'x_rpm_dir'        : '%%dir %s',
            'x_rpm_docdir'     : '%%docdir %s',
            'x_rpm_ghost'      : '%%ghost %s', }

        tag_factories = [ LocationTagFactory() ]

        for file in files:
            print "%s %s %s %s"%(file.__hash__(), file.get_path(), file.get_tags(), file.get_stored_info().bsourcesigs)
            tags = file.get_tags( tag_factories )

            str += SimpleTagCompiler(supported_tags, mandatory=0).compile( tags )

            str += ' '
            str += tags['install_location']
            str += '\n\n'

        return str
