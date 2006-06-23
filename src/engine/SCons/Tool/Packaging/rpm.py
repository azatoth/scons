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

def create_builder(env, keywords=None):
    rpmbuilder = env.get_builder('Rpm')
    rpmbuilder.push_emitter(rpm_emitter)

    env['RPMSPEC'] = keywords

    return rpmbuilder

def build_specfile(target, source, env):
    """ Builds a RPM specfile from a dictionary with string metadata and
    by analyzing a tree of nodes.
    """
    spec = env['RPMSPEC']
    file = open(target[0].abspath, 'w')

    try:
        file.write( build_specfile_header(spec) )
        file.write( build_specfile_sections(spec, source) )
    except KeyError, e:
        raise SCons.Errors.UserError( '"%s" package field for RPM is missing.' % e.args[0] )

def compile( tags, values, mandatory=1 ):
    """ takes a list of given tags and fills in there values.

    tags is a dict of the form { 'tag' : 'str with %s replacement markers' }
    values is a dict of the form { 'tag'  : 'value',
                                   'tag_' : 'international value' }
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
        international    = [ (k, v) for k,v in tags.items() if values.has_key(k) and k.endswith('_') ]

        for (key, replacement) in available_values:
            str += replacement % values[key]
            str += '\n\n'

        for (key, replacement) in international:
            for (value_key, value_value) in [ (k, v) for k,v in values.items() if k.startswith(key) ]:
              land_mark = value_key[rfind('_')+1:]
              str += replacement % (land_mark, value_key)
              str += '\n\n'

    return str

def build_specfile_sections(spec, files):
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
        spec['x_rpm_Prep'] = '%setup -q'

#    if not spec.has_key('x_rpm_Build'):
#        spec['x_rpm_Build'] = 'scons'

    if not spec.has_key('x_rpm_Install'):
        spec['x_rpm_Install'] = 'scons install'

    if not spec.has_key('x_rpm_Clean'):
        spec['x_rpm_Clean'] = 'rm -rf $RPM_BUILD_ROOT'

    str += compile( optional_sections, spec, mandatory = 0 )

    str += '\n%files\n'
    for file in files:
        str += '/'+file.get_path().replace(spec['subdir'], '')
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
        'x_rpm_Source'        : 'Source: %s'}

    # fill in default values:
#    if not s.has_key('x_rpm_BuildRequires'):
#        s['x_rpm_BuildRequires'] = 'scons'

    # XXX: assumed the name of the src package!
    if not s.has_key('x_rpm_Source'):
        s['x_rpm_Source'] = '%{name}-%{version}.rpm.tar.gz'

    str += compile( optional_header_fields, s, mandatory=0 )

    return str

def string_specfile(target, source, env):
    return "building RPM specfile %s"%( target[0].path )

specfile_action = SCons.Action.Action( build_specfile,
                                       string_specfile,
                                       varlist=[ 'RPMSPEC' ] )

def rpm_emitter(target, source, env):
    """This emitter adds a source package to the list of sources.

    The source list of this source packager also includes a specfile, which an
    attached specfile builder.
    """
    specfilebuilder = SCons.Builder.Builder( action = specfile_action,
                                             suffix = '.spec' )
    spec_target = env['RPMSPEC']['projectname']
    specfile = apply( specfilebuilder, [env], { 'source' : source,
                                                'target' : spec_target })

    # XXX: might use the create_builder function of Packaging
    srcbuilder = SCons.Tool.Packaging.targz.create_builder(env)
    suffix  = srcbuilder.get_suffix(env)
    srcnode = apply( srcbuilder, [env], { 'source' : source + specfile,
                                          'target' : target[0].abspath + suffix } )

    return (target, srcnode)
