"""SCons.Tool.Packaging.msi

The msi packager.
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

from xml.dom.minidom import *

filename_set = []

def create_default_target(kw):
    """ tries to guess the filenames of the generated msi file.
    """
    version        = kw['version']
    projectname    = kw['projectname']
    packageversion = kw['packageversion']

    msi = '%s-%s-%s.msi' % (projectname, version, packageversion)

    return [ msi ]

def create_builder(env, keywords=None):
    # the wxs_builder is kind of hacked, calling the object_builder and 
    # linker_builder with the correct files.
    def attach_wix_process(source, target, env):
        # categorize files
        tag_factories = [ SCons.Tool.Packaging.LocationTagFactory() ]

        def belongs_into_msi_pkg(file):
            tags = file.get_tags(factories=tag_factories)
            return tags.has_key('install_location')

        msi_files = filter( belongs_into_msi_pkg, source )

        # spit out warnings and errors.
        if len(msi_files) == 0:
            raise SCons.Errors.UserError( 'No file to put into the MSI package? Only files with are returned by Install() or InstallAs() can be put into the MSI Package!.')

        spec = env['MSISPEC']

        # build the specfile.
        p, v, pv   = env['MSISPEC']['projectname'], env['MSISPEC']['version'], env['MSISPEC']['packageversion']
        wxs_target = '%s-%s.%s.wxs' % ( p, v, pv )
        wxi_target = '%s-%s.%s.wxiobj' % ( p, v, pv )

        wxs_builder = SCons.Builder.Builder(
            action  = wxsfile_action,
            suffix  = '.wxs',)

        wxi_builder = SCons.Builder.Builder(
            action = '$WIXCANDLECOM',
            src_suffix  = '.wxs',)

        wxs_file = apply( wxs_builder, [env], { 'source' : msi_files,
                                                'target' : wxs_target, } )[0]
        wxi_file = apply( wxi_builder, [env], { 'source' : wxs_file,
                                                'target' : wxi_target, } )[0]

        return (target, wxi_file)

    linker_builder = SCons.Builder.Builder(
        action = '$WIXLIGHTCOM',
        emitter = attach_wix_process,
        src_suffix  = '.wxiobj')

    env['MSISPEC'] = keywords

    return linker_builder

def string_wxsfile(target, source, env):
    return "building WiX file %s"%( target[0].path )

def build_wxsfile(target, source, env):
    """ Builds a WiX file from a dictionary with string metadata and
    by analyzing a tree of nodes.

    As with RPM there is an abstract compile() function, the build_ function
    define the dict to wxsfile-content mapping. In this case this is a XML
    Attribute, so we have a tuple consisting of XML tag- and attributename.
    """
    file = open(target[0].abspath, 'w')
    spec = env['MSISPEC']

    try:
        # Create a document with the Wix root tag
        doc  = Document()
        root = doc.createElement( 'Wix' )
        root.attributes['xmlns']='http://schemas.microsoft.com/wix/2003/01/wi'
        doc.appendChild( root )

        # Create the content
        build_wxsfile_header_section(root, spec)
        build_wxsfile_file_section(root, spec, source)
        generate_guids(root)
        build_wxsfile_features_section(root)
    #    build_wxsfile_default_gui(root)

        # write the xml to a file
        file.write( doc.toprettyxml() )

    except KeyError, e:
        raise SCons.Errors.UserError( '"%s" package field for MSI is missing.' % e.args[0] )

def generate_guids( root ):
    """ generates globally unique identifiers for parts of the xml which need 
    them.

    Component tags have a special requirement. Their UUID is only allowed to
    change if the list of their contained resources has changed.

    To handle this requirement, the uuid is generated with an md5 hashing the
    whole subtree of a xml node.
    """
    from md5 import md5

    # specify which tags need a guid and in which attribute this should be stored.
    needs_id = { 'Product'   : 'Id',
                 'Package'   : 'Id',
                 'Component' : 'Guid',
               }

    # find all XMl nodes matching the key, retrieve their attribute, hash their 
    # subtree, convert hash to string and add as a attribute to the xml node.
    for (key,value) in needs_id.items():
        node_list = root.getElementsByTagName(key)
        attribute = value
        for node in node_list:
            hash = md5(node.toxml()).hexdigest()
            hash_str = '%s-%s-%s-%s-%s' % ( hash[:8], hash[8:12], hash[12:16], hash[16:20], hash[20:] )
            node.attributes[attribute] = hash_str

def create_default_directory_layout(root, spec):
    """ Create the wix default target directory layout and return the innermost
    directory.

    We assume that the XML tree delivered in the root argument already contains
    the Product tag.
    """
    doc = Document()
    d1  = doc.createElement( 'Directory' )
    d1.attributes['Id']   = 'TARGETDIR'
    d1.attributes['Name'] = 'SourceDir'

    d2  = doc.createElement( 'Directory' )
    d2.attributes['Id']   = 'ProgramFilesFolder'
    d2.attributes['Name'] = 'PFiles'

    d3  = doc.createElement( 'Directory' )
    d3.attributes['Id']   = 'default_folder'
    d3.attributes['Name'] = "%s-%s.%s" % (spec['projectname'], spec['version'], spec['packageversion'])

    d1.childNodes.append( d2 )
    d2.childNodes.append( d3 )

    root.getElementsByTagName('Product')[0].childNodes.append( d1 )

    return d3

def build_wxsfile_file_section(root, spec, files):
    """ builds the Component sections of the wxs file with their included files.
    """
    # Helper function for convering a long filename to a DOS 8.3 one.
    def is_dos_short_file_name(file):
        fname, ext = os.path.splitext(file)

        return len(fname) <= 8 and len(ext) <= 3 and file.isupper()

    def gen_dos_short_file_name(file):
        """ see http://support.microsoft.com/default.aspx?scid=kb;en-us;Q142982
        XXX: this conversion is incomplete.
        """
        if is_dos_short_file_name(file):
            return file

        fname, ext = os.path.splitext(file)

        # first try if it suffices to convert to upper
        file = file.upper()
        if is_dos_short_file_name(file):
            return file

        for x in [ '.', '"', '/', '[', ']', ':', ';', '=', ',', ' ' ]:
            fname.replace(x, '')

        # check if we already generated a filename with the same number:
        # Thisis~1.txt, Thisis~2.txt etc.
        duplicate, num = not None, 1
        while duplicate:
            shortname = "%s~%s" % (fname[:7-len(str(num))].upper(),\
                                   str(num))
            if len(ext) > 0:
                shortname = "%s.%s" % (shortname, ext[:3].upper())

            duplicate = shortname in filename_set
            num += 1

        assert( is_dos_short_file_name(shortname) )
        filename_set.append(shortname)
        return shortname

    # create a default layout and a <Component> tag.
    Component = Document().createElement('Component')
    Component.attributes['DiskId'] = '1'
    Component.attributes['Id']     = 'default'

    Directory = create_default_directory_layout(root, spec)
    Directory.childNodes.append(Component)

    tag_factories = [ SCons.Tool.Packaging.LocationTagFactory() ]

    for file in files:
        tags = file.get_tags( tag_factories )
        filename = os.path.basename( file.get_path() )

        if not tags.has_key('x_msi_vital'):
            tags['x_msi_vital'] = 'yes'

        if not tags.has_key('x_msi_fileid'):
            tags['x_msi_fileid'] = filename

        if not tags.has_key('x_msi_longname'):
            tags['x_msi_longname'] = filename

        if not tags.has_key('x_msi_shortname'):
            tags['x_msi_shortname'] = gen_dos_short_file_name( filename )

        if not tags.has_key('x_msi_source'):
            tags['x_msi_source'] = filename

        File = Document().createElement( 'File' )
        File.attributes['LongName'] = tags['x_msi_longname']
        File.attributes['Name']     = tags['x_msi_shortname']
        File.attributes['Source']   = tags['x_msi_source']
        File.attributes['Id']       = tags['x_msi_fileid']
        File.attributes['Vital']    = tags['x_msi_vital']

        Component.childNodes.append(File)

def build_wxsfile_features_section(root):
    """ This function creates the <features> tag based on the supplied xml tree.

    This is achieved by finding all <component>s and adding them to a default target.

    It should be called after the tree has been built completly.  We assume
    that a TARGETDIR Property is defined in the wxs file tree.
    """
    factory = Document()
    Feature = factory.createElement('Feature')
    Feature.attributes['Id']                    = 'complete'
    Feature.attributes['ConfigurableDirectory'] = 'TARGETDIR'
    Feature.attributes['Level']                 = '1'

    for node in root.getElementsByTagName('Component'):
        ComponentRef = factory.createElement('ComponentRef')
        ComponentRef.attributes['Id'] = node.attributes['Id']
        Feature.childNodes.append(ComponentRef)

    root.getElementsByTagName('Product')[0].childNodes.append(Feature)

def build_wxsfile_header_section(root, spec):
    """ Adds the xml file node which define the package meta-data.
    """
    # Create the needed DOM nodes and add them at the correct position in the tree.
    factory = Document()
    Product = factory.createElement( 'Product' )
    Package = factory.createElement( 'Package' )

    root.childNodes.append( Product )
    Product.childNodes.append( Package )

    # set "mandatory" default values
    if not spec.has_key('x_msi_language'):
        spec['x_msi_language'] = '1033' # select english

    # mandatory sections, will throw a KeyError if the tag is not available
    Product.attributes['Name']         = spec['projectname']
    Product.attributes['Version']      = "%s.%s" % (spec['version'], spec['packageversion'])
    Product.attributes['Manufacturer'] = spec['vendor']
    Product.attributes['Language']     = spec['x_msi_language']

    Package.attributes['Description']  = spec['summary']

    # now the optional tags, for which we avoid the KeyErrror exception
    if spec.has_key( 'description' ):
        Package.attributes['Comments'] = spec['description']

    # We hardcode the media tag as our current model cannot handle it.
    Media = factory.createElement('Media')
    Media.attributes['Id']       = '1'
    Media.attributes['Cabinet']  = 'default.cab'
    Media.attributes['EmbedCab'] = 'yes'
    root.getElementsByTagName('Product')[0].childNodes.append(Media)

def build_wxsfile_default_gui(root):
    """ this function adds a default GUI to the wxs file
    """
    factory = Document()
    Product = root.getElementsByTagName('Product')[0]

    UIRef   = factory.createElement('UIRef')
    UIRef.attributes['Id'] = 'WixUI_Mondo'

    Product.childNodes.append(UIRef)

wxsfile_action = SCons.Action.Action( build_wxsfile,
                                      string_wxsfile,
                                      varlist=[ 'MSISPEC' ] )
