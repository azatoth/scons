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
import SCons.Tool.Packaging.targz

import os

def create_default_target(kw):
    """ tries to guess the filenames of the generated RPMS files.
    """
    version        = kw['version']
    projectname    = kw['projectname']
    packageversion = kw['packageversion']
    # XXX: this should be guessed by inspecting compilerflags?!?! how to get
    # them?
    buildarchitecture = 'i386'

    srcrpm = '%s-%s-%s.src.rpm' % (projectname, version, packageversion)
    binrpm = srcrpm.replace( 'src', buildarchitecture )

    return [ srcrpm, binrpm ]

def create_builder(env, keywords=None):
    rpmbuilder = env.get_builder('Rpm')
    rpmbuilder.push_emitter(rpm_emitter)

    env['RPMSPEC'] = keywords

    return rpmbuilder

def rpm_emitter(target, source, env):
    """This emitter adds a source package to the list of sources. The source
    list is split into three parts, seperated by their location:
     * those that go into the source package (these are the nodes which have
       no tags set). They are removed from the source argument list.
     * those that go into the rpm package (these are the nodes which have at
       least a 'install_location' tag ). They are removed from the source
       argument list and are given to the specfile builder as putting files
       into the rpm file really means putting an entry into the spec file.
     * those that do not fall into one of the above categories. These will
       generate a Exception as they would otherwise be ignored.

    The source list of this source packager will also include a specfile
    with an attached specfile builder.
    """

    # categorize files
    tag_factories = [ SCons.Tool.Packaging.LocationTagFactory() ]

    def belongs_into_source_pkg(file):
        return len( file.get_tags(factories=tag_factories) ) == 0

    def belongs_into_rpm_pkg(file):
        tags = file.get_tags(factories=tag_factories)
        return tags.has_key('install_location')

    def belongs_to_no_category(file):
        return not belongs_into_source_pkg(file) and\
               not belongs_into_rpm_pkg(file)

    uncategorized = filter( belongs_to_no_category, source )
    rpm_files     = filter( belongs_into_rpm_pkg, source )
    src_files     = filter( belongs_into_source_pkg, source )

    # spit out warning and errors.
    if len( uncategorized ) != 0:
        # XXX: better error message?
        raise SCons.Errors.UserError( 'There are files which tags but are missing a install_location tag and are therefore not packageable.' )

    if len(rpm_files) == 0:
        raise SCons.Errors.UserError( 'No file to put into the RPM package? Only files with are returned by Install() or InstallAs() will be put into the RPM Package!.')

    # build the specfile.
    p, v        = env['RPMSPEC']['projectname'], env['RPMSPEC']['version']
    spec_target = '%s-%s' % ( p, v )

    specfilebuilder = SCons.Builder.Builder( action = specfile_action,
                                             suffix = '.spec' )
    specfile = apply( specfilebuilder, [env], {
                      'target' : spec_target,
                      'source' : rpm_files } )

    # build a source package with three properties:
    #  * contains a SConstruct with an install target with a prefix argument.
    #  * contains a generated specfile.
    #  * contains all source files.
    srcbuilder = SCons.Tool.Packaging.targz.create_builder(env, env['RPMSPEC'])
    suffix     = srcbuilder.get_suffix(env)
    srcnode    = apply( srcbuilder, [env], {
                        'source' : src_files + specfile,
                        'target' : target[0].abspath + suffix } )

    # set the source target in the rpmspec file
    env['RPMSPEC']['x_rpm_Source'] = os.path.basename(srcnode[0].get_path())

    return (target, srcnode)

def string_specfile(target, source, env):
    return "building RPM specfile %s"%( target[0].path )

def build_specfile(target, source, env):
    """ Builds a RPM specfile from a dictionary with string metadata and
    by analyzing a tree of nodes.
    """
    spec = env['RPMSPEC']
    file = open(target[0].abspath, 'w')

    try:
        file.write( build_specfile_header(spec) )
        file.write( build_specfile_sections(spec) )
        file.write( build_specfile_filesection(source) )

    except KeyError, e:
        raise SCons.Errors.UserError( '"%s" package field for RPM is missing.' % e.args[0] )


def compile( tags, values, mandatory=1 ):
    """ takes a list of given tags and fills in there values.

    tags is a dict of the form { 'tag' : 'str with %s replacement markers' }
    values is a dict of the form { 'tag'  : 'value',
                                   'tag_xx' : 'international value' }
    """
    str = ""

    if mandatory:
        available_values = [ (k, v) for k,v in tags.items() if not k.endswith('_') ]
        international    = [ (k, v) for k,v in tags.items() if k.endswith('_') ]

        for (key, replacement) in available_values:
            str += replacement % values[key]
            str += '\n\n'

        for (key, replacement) in international:
            for (value_key, value_value) in [ (k, v) for k,v in values.items() if k.startswith(key) ]:
                land_mark = value_key[rfind('_')+1:]
                str += replacement % (land_mark, value_key)
                str += '\n\n'
    else:
        available_values = [ (k, v) for k,v in tags.items() if values.has_key(k) and not k.endswith('_') ]
        # international replacement tags look like x_rpm_Group_,
        # while the value tag looks like           x_rpm_Group_de
        international    = [ (k, v) for k,v in values.items() if k[len(k)-3]=='_' and tags.has_key(k[:len(k)-2]) ]

        for (key, replacement) in available_values:
            str += replacement % values[key]
            str += '\n\n'

        for (key, value) in international:
            land_code             = key[key.rfind('_')+1:]
            key_without_land_code = key[:key.rfind('_')+1]
            replacement           = tags[key_without_land_code]
            str += replacement % (land_code, value)
            str += '\n\n'

    return str

def build_specfile_sections(spec):
    """ Builds the %files and other sections of a rpm specfile.
    """
    str = ""

    mandatory_sections = {
        'description'  : '%%description\n%s', }

    str += compile( mandatory_sections, spec )

    optional_sections = {
        'description_'        : '%%description -l %s\n%s',
        'changelog'           : '%%changelog\n%s',
        'x_rpm_PreInstall'    : '%%pre\n%s',
        'x_rpm_PostInstall'   : '%%post\n%s',
        'x_rpm_PreUninstall'  : '%%preun\n%s',
        'x_rpm_PostUninstall' : '%%postun\n%s',
        'x_rpm_Verify'        : '%%verify\n%s',

        # These are for internal use but could possibly be overriden
        'x_rpm_Prep'          : '%%prep\n%s',
        'x_rpm_Build'         : '%%build\n%s',
        'x_rpm_Install'       : '%%install\n%s',
        'x_rpm_Clean'         : '%%clean\n%s',
        }

    # Default prep, build, install and clean rules
    if not spec.has_key('x_rpm_Prep'):
        spec['x_rpm_Prep']  = 'rm -rf $RPM_BUILD_ROOT\n'
        spec['x_rpm_Prep'] += '%setup -q'

    if not spec.has_key('x_rpm_Build'):
        spec['x_rpm_Build'] = 'mkdir $RPM_BUILD_ROOT'

    if not spec.has_key('x_rpm_Install'):
        spec['x_rpm_Install'] = 'scons prefix=$RPM_BUILD_ROOT install'

    if not spec.has_key('x_rpm_Clean'):
        spec['x_rpm_Clean'] = 'rm -rf $RPM_BUILD_ROOT'

    str += compile( optional_sections, spec, mandatory = 0 )

    return str

def build_specfile_filesection(files):
    """ builds the %file section of the specfile
    """
    str  = '%files\n'

    tag_factories = [ SCons.Tool.Packaging.LocationTagFactory() ]

    for file in files:
        tags = file.get_tags( tag_factories )
        # compile() file-tags
        

        str += tags['install_location'][0].get_path()
        str += '\n'

    return str

def build_specfile_header(specs):
    """ Builds all section but the %file of a rpm specfile
    """
    s = specs.copy()
    str = ""

    # first the mandatory sections
    mandatory_header_fields = {
        'projectname'    : '%%define name %s\nName: %%{name}',
        'version'        : '%%define version %s\nVersion: %%{version}',
        'packageversion' : '%%define release %s\nRelease: %%{release}',
        'x_rpm_Group'    : 'Group: %s',
        'summary'        : 'Summary: %s',
        'license'        : 'License: %s', }

    str += compile( mandatory_header_fields, s )

    # now the optional tags
    optional_header_fields = {
        'vendor'              : 'Vendor: %s',
        'url'                 : 'Url: %s', 
        'summary_'            : 'Summary(%s): %s',
        'x_rpm_Distribution'  : 'Distribution: %s',
        'x_rpm_Icon'          : 'Icon: %s',
        'x_rpm_Packager'      : 'Packager: %s',
        'x_rpm_Group_'        : 'Group(%s): %s',

        'x_rpm_Requires'      : 'Requires: %s',
        'x_rpm_Provides'      : 'Provides: %s',
        'x_rpm_Conflicts'     : 'Conflicts: %s',
        'x_rpm_BuildRequires' : 'BuildRequires: %s',

        'x_rpm_Serial'        : 'Serial: %s',
        'x_rpm_Epoch'         : 'Epoch: %s',
        'x_rpm_AutoReqProv'   : 'AutoReqProv: %s',
        'x_rpm_ExcludeArch'   : 'ExcludeArch: %s',
        'x_rpm_ExclusiveArch' : 'ExclusiveArch: %s',
        'x_rpm_Prefix'        : 'Prefix: %s',
        'x_rpm_Conflicts'     : 'Conflicts: %s',

        # internal use
        'x_rpm_Source'        : 'Source: %s',
        'x_rpm_BuildRoot'      : 'BuildRoot: %s', }

    # fill in default values:
#    if not s.has_key('x_rpm_BuildRequires'):
#        s['x_rpm_BuildRequires'] = 'scons'

    if not s.has_key('x_rpm_BuildRoot'):
        s['x_rpm_BuildRoot'] = '%{_tmppath}/%{name}-%{version}-%{release}'

    str += compile( optional_header_fields, s, mandatory=0 )
    return str

specfile_action = SCons.Action.Action( build_specfile,
                                       string_specfile,
                                       varlist=[ 'RPMSPEC' ] )
