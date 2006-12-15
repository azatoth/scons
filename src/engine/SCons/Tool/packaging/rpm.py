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

from SCons.Tool.packaging import stripinstall_emitter, packageroot_emitter, src_targz

def package(env, target, source, packageroot, projectname, version,
            packageversion, description, summary, x_rpm_Group, license,
            **kw):
    # initialize the rpm tool
    SCons.Tool.Tool('rpm').generate(env)

    print map(str, source)

    # create the neccesary builder
    bld = env['BUILDERS']['Rpm']
    env['RPMFLAGS'] = SCons.Util.CLVar('-ta')

    bld.push_emitter(targz_emitter)
    bld.push_emitter(specfile_emitter)
    bld.push_emitter(stripinstall_emitter())

    # override the default target, with the rpm specific ones.
    if str(target[0])=="%s-%s"%(projectname, version):
        # This should be overridable from the construction environment,
        # which it is by using architecture=.
        # Guessing based on what os.uname() returns at least allows it
        # to work for both i386 and x86_64 Linux systems.
        archmap = {
            'i686'  : 'i386',
            'i586'  : 'i386',
            'i486'  : 'i386',
        }

        buildarchitecture = os.uname()[4]
        buildarchitecture = archmap.get(buildarchitecture, buildarchitecture)

        if kw.has_key('architecture'):
            buildarchitecture = kw['architecture']

        srcrpm = '%s-%s-%s.src.rpm' % (projectname, version, packageversion)
        binrpm = srcrpm.replace( 'src', buildarchitecture )

        target = [ srcrpm, binrpm ]

    # now call the rpm builder to actually build the packet.
    loc=locals()
    del loc['kw']
    kw.update(loc)
    del kw['source']
    del kw['target']
    del kw['env']

    # if no "source_url" tag is given add a default one.
    if not kw.has_key('source_url'):
        kw['source_url']=(str(target[0])+".tar.gz").replace('.rpm', '')

    return apply(bld, [env, target, source], kw)


def targz_emitter(target, source, env):
    """ Puts all source files into a tar.gz file. """
    # the rpm tool depends on a source package, until this is chagned
    # this hack needs to be here that tries to pack all sources in.
    sources = env.FindSourceFiles()

    # filter out the target we are building the source list for.
    sources = [s for s in sources if not (s in target)]

    # find the .spec file for rpm and add it
    sources.extend( [s for s in source if str(s).rfind('.spec')!=-1] )

    # as the source contains the url of the source package this rpm package
    # is built from, we extract the target name
    try:
        tarball = env['source_url'].split('/')[-1]
    except KeyError, e:
        raise SCons.Errors.UserError( "Missing PackageTag '%s' for RPM packager" % e.args[0] )

    tarball = src_targz.package(env, source=sources, target=tarball,
                                packageroot=env['packageroot'], )

    return (target, tarball)

def specfile_emitter(target, source, env):
    specfile = "%s-%s" % (env['projectname'], env['version'])

    bld = SCons.Builder.Builder(action         = build_specfile,
                                suffix         = '.spec',
                                target_factory = SCons.Node.FS.File)

    source.extend(bld(env, specfile, source))

    return (target,source)

def build_specfile(target, source, env):
    """ Builds a RPM specfile from a dictionary with string metadata and
    by analyzing a tree of nodes.
    """
    file = open(target[0].abspath, 'w')
    str  = ""

    try:
        file.write( build_specfile_header(env) )
        file.write( build_specfile_sections(env) )
        file.write( build_specfile_filesection(env, source) )
        file.close()

        # call a user specified function
        if env.has_key('change_specfile'):
            env['change_specfile'](target, source)

    except KeyError, e:
        raise SCons.Errors.UserError( '"%s" package field for RPM is missing.' % e.args[0] )


#
# mandatory and optional package tag section
#
def build_specfile_sections(spec):
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

def build_specfile_header(spec):
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
def build_specfile_filesection(spec, files):
    """ builds the %file section of the specfile
    """
    str  = '%files\n'

    if not spec.has_key('x_rpm_defattr'):
        spec['x_rpm_defattr'] = '(-,root,root)'

    str += '%%defattr %s\n' % spec['x_rpm_defattr']

    supported_tags = {
        'packaging_config'           : '%%config %s',
        'packaging_config_noreplace' : '%%config(noreplace) %s',
        'packaging_doc'              : '%%doc %s',
        'packaging_unix_attr'        : '%%attr %s',
        'packaging_lang_'            : '%%lang(%s) %s',
        'packaging_x_rpm_verify'     : '%%verify %s',
        'packaging_x_rpm_dir'        : '%%dir %s',
        'packaging_x_rpm_docdir'     : '%%docdir %s',
        'packaging_x_rpm_ghost'      : '%%ghost %s', }

    for file in files:
        # build the tagset
        tags = {}
        for k in supported_tags:
            try:
                tags[k]=getattr(file, k)
            except AttributeError:
                pass

        # compile the tagset
        str += SimpleTagCompiler(supported_tags, mandatory=0).compile( tags )

        str += ' '
        str += file.packaging_install_location
        str += '\n\n'

    return str

class SimpleTagCompiler:
    """ This class is a simple string substition utility:
    the replacement specfication is stored in the tagset dictionary, something
    like:
     { "abc"  : "cdef %s ",
       "abc_" : "cdef %s %s" }

    the compile function gets a value dictionary, which may look like:
    { "abc"    : "ghij",
      "abc_gh" : "ij" }

    The resulting string will be:
     "cdef ghij cdef gh ij"
    """
    def __init__(self, tagset, mandatory=1):
        self.tagset    = tagset
        self.mandatory = mandatory

    def compile(self, values):
        """ compiles the tagset and returns a str containing the result
        """
        def is_international(tag):
            return tag.endswith('_')

        def get_country_code(tag):
            return tag[-2:]

        def strip_country_code(tag):
            return tag[:-2]

        replacements = self.tagset.items()

        str = ""
        for key, replacement in [ (k,v) for k,v in replacements if not is_international(k) ]:
            try:
                str += replacement % values[key]
            except KeyError, e:
                if self.mandatory:
                    raise e

        for key, replacement in [ (k,v) for k,v in replacements if is_international(k) ]:
            try:
                int_values_for_key = [ (get_country_code(k),v) for k,v in values.items() if strip_country_code(k) == key ]
                for v in int_values_for_key:
                    str += replacement % v
            except KeyError, e:
                if self.mandatory:
                    raise e

        return str

