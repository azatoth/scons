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

from SCons.Tool.packaging import stripinstall_emitter, packageroot_emitter

def package(env, target, source, packageroot, projectname, version, description,
            architecture, summary, x_ipk_priority, x_ipk_section, source_url,
            x_ipk_maintainer, x_ipk_depends, **kw):
    """ this function prepares the packageroot directory for packaging with the
    ipkg builder.
    """
    SCons.Tool.Tool('ipkg').generate(env)

    bld = env['BUILDERS']['Ipkg']
    env['IPKGUSER']  = os.popen('id -un').read().strip()
    env['IPKGGROUP'] = os.popen('id -gn').read().strip()
    env['IPKGFLAGS'] = SCons.Util.CLVar('-o $IPKGUSER -g $IPKGGROUP')
    env['IPKGCOM']   = '$IPKG $IPKGFLAGS ${SOURCE.get_path().replace("/CONTROL/control","")}'

    bld.push_emitter(gen_ipk_specfiles)
    bld.push_emitter(packageroot_emitter(packageroot))
    bld.push_emitter(stripinstall_emitter())

    # override the default target.
    if str(target[0])=="%s-%s"%(projectname, version):
        target=[ "%s_%s_%s.ipk"%(projectname, version, architecture) ]

    # now call the ipk builder to actually build the packet.
    loc=locals()
    del loc['kw']
    kw.update(loc)
    del kw['source']
    del kw['target']
    del kw['env']
    return apply(bld, [env, target, source], kw)

def gen_ipk_specfiles(target, source, env):
    # create the specfile builder
    s_bld=SCons.Builder.Builder(action=build_specfiles)

    # create the specfile targets
    spec_target=[]
    proot=env.fs.Dir(env['packageroot'])
    control=proot.Dir('CONTROL')
    spec_target.append(control.File('control'))
    spec_target.append(control.File('conffiles'))
    spec_target.append(control.File('postrm'))
    spec_target.append(control.File('prerm'))
    spec_target.append(control.File('postinst'))
    spec_target.append(control.File('preinst'))

    # apply the builder to the specfile targets
    n_source=s_bld(env, target=spec_target, source=source)
    n_source.extend(source)
    source=n_source

    return (target, source)

def build_specfiles(source, target, env):
    """ filter the targets for the needed files and use the variables in env
    to create the specfile.
    """
    #
    # At first we care for the CONTROL/control file, which is the main file for ipk.
    #
    # For this we need to open multiple files in random order, so we store into
    # a dict so they can be easily accessed.
    #
    #
    opened_files={}
    def open_file(needle, haystack):
        try:
            return opened_files[needle]
        except KeyError:
            file=filter(lambda x: x.get_path().rfind(needle)!=-1, haystack)[0]
            opened_files[needle]=open(file.abspath, 'w')
            return opened_files[needle]

    control_file=open_file('control', target)

    if not env.has_key('x_ipk_description'):
        env['x_ipk_description']="%s\n %s"%(env['summary'],
                                            env['description'].replace('\n', '\n '))


    content = """
Package: $projectname
Version: $version
Priority: $x_ipk_priority
Section: $x_ipk_section
Source: $source_url
Architecture: $architecture
Maintainer: $x_ipk_maintainer
Depends: $x_ipk_depends
Description: $x_ipk_description
"""

    control_file.write(env.subst(content))

    #
    # now handle the various other files, which purpose it is to set post-, 
    # pre-scripts and mark files as config files.
    #
    # We do so by filtering the source files for files which are marked with
    # the "config" tag and afterwards we do the same for x_ipk_postrm,
    # x_ipk_prerm, x_ipk_postinst and x_ipk_preinst tags.
    #
    # The first one will write the name of the file into the file
    # CONTROL/configfiles, the latter add the content of the x_ipk_* variable
    # into the same named file.
    #
    for f in [x for x in source if 'packaging_config' in dir(x)]:
        config=open_file('conffiles')
        config.write(f.packaging_install_location)
        config.write('\n')

    for str in 'postrm prerm postinst preinst'.split():
        name="packaging_x_ipk_%s"%str
        for f in [x for x in source if name in dir(x)]:
            file=open_file(name)
            file.write(env[str])

    #
    # close all opened files
    for f in opened_files.values():
        f.close()

    # call a user specified function
    if env.has_key('change_specfile'):
        content += env['change_specfile'](target)

    return 0
