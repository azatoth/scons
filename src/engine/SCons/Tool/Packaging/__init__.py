"""SCons.Tool.Packaging

SCons Packaging Tool.
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

import SCons.Errors
import SCons.Environment

import os
import SCons.Defaults

import tarbz2, targz, zip, rpm, msi, ipk

#
# Functions to handle options of the Packager.
#
type = [ 'src_tarbz2' ]

def set_package_type(option, opt, value, parser):
    global type
    type = value

packagers = {
    'src_tarbz2' : tarbz2.TarBz2Packager(),
    'src_targz'  : targz.TarGzPackager(),
    'src_zip'    : zip.ZipPackager(),
    'tarbz2' : tarbz2.BinaryTarBz2Packager(),
    'targz'  : targz.BinaryTarGzPackager(),
    'zip'    : zip.BinaryZipPackager(),
    'rpm'    : rpm.RpmPackager(),
    'msi'    : msi.MsiPackager(),
    'ipk'    : ipk.IpkPackager(),
}

def get_targets(env, kw):
    """ creates the target for the given packager types, completly setup
    with its dependencies.
    """
    global type
    if kw.has_key( 'type' ):
        type = kw['type']
    if SCons.Util.is_String( type ):
        type = [ type ]

    env['SPEC'] = kw

    try:
        selected_packagers = []
        for t in type:
            selected_packagers.append(packagers.get(t))
        targets = []
        for p in selected_packagers:
            builder = p.create_builder(env, kw)
            target  = apply( builder, [env], p.add_targets(kw) )
            targets.extend(target)

        env.Alias( 'package', targets )

    except KeyError:
        raise SCons.Errors.UserError( 'packager %s not available' % t )
