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
import os

from packager import BinaryPackager, LocationTagFactory

from xml.dom.minidom import *
from xml.sax.saxutils import escape

class Msi(BinaryPackager):
    def __init__(self):
        BinaryPackager.__init__(self)
        self.filename_set = []
        self.id_set = {}

        self.specfile_suffix = '.wxs'

    def create_builder(self, env, kw=None):
        # the wxs_builder is kind of hacked, calling the object_builder and 
        # linker_builder with the correct files.

        def attach_candle(source, target, env):
            ''' This emitter attaches the candle.exe to the call chain.
            '''
            build_dir = target[0].get_dir()

            p, v          = env['SPEC']['projectname'], env['SPEC']['version']
            wxiobj_target = build_dir.File( '%s-%s.wxiobj' % ( p, v ) )

            wxs_builder = SCons.Builder.Builder(
                action  = '$WIXCANDLECOM',
                emitter = [ self.strip_install_emitter, self.specfile_emitter ],
                src_suffix = '.wxs' )

            wxs_file = apply( wxs_builder, [env], { 'source' : source,
                                                    'target' : wxiobj_target, } )

            return (target, wxs_file)

        def blubb():
            raise Exception

        linker_builder = SCons.Builder.Builder(
            action      = '$WIXLIGHTCOM',
            emitter     = attach_candle,
            suffix      = '.msi',
            src_suffix  = '.wxiobj')

        env['SPEC'] = kw

        return linker_builder

    def string_wxsfile(self, target, source, env):
        return "building WiX file %s"%( target[0].path )

    def build_specfile(self, target, source, env):
        """ Builds a WiX file from a dictionary with string metadata and
        by analyzing a tree of nodes.
        """
        file = open(target[0].abspath, 'w')

        try:
            # Create a document with the Wix root tag
            doc  = Document()
            root = doc.createElement( 'Wix' )
            root.attributes['xmlns']='http://schemas.microsoft.com/wix/2003/01/wi'
            doc.appendChild( root )

            # Create the content
            self.build_wxsfile_header_section(root, env)
            self.build_wxsfile_file_section(root, env, source)
            self.generate_guids(root)
            self.build_wxsfile_features_section(root, env, source)
            self.build_wxsfile_default_gui(root)
            self.build_license_file(target[0].get_dir(), env)

            # write the xml to a file
            file.write( doc.toprettyxml() )

            # call a user specified function
            if env.has_key('change_specfile'):
                env['change_specfile'](target, source)

        except KeyError, e:
            raise SCons.Errors.UserError( '"%s" package field for MSI is missing.' % e.args[0] )

    #
    # Utility functions
    #
    def is_dos_short_file_name(self, file):
        fname, ext = os.path.splitext(file)

        return len(fname) <= 8 and ((2 <= len(ext) <= 4) or (len(ext) ==0)) and file.isupper()

    def gen_dos_short_file_name(self, file):
        """ see http://support.microsoft.com/default.aspx?scid=kb;en-us;Q142982
        """
        if self.is_dos_short_file_name(file):
            return file

        fname, ext = os.path.splitext(file)

        # first try if it suffices to convert to upper
        file = file.upper()
        if self.is_dos_short_file_name(file):
            return file

        for x in [ '.', '"', '/', '[', ']', ':', ';', '=', ',', ' ' ]:
            fname=fname.replace(x, '')

        # check if we already generated a filename with the same number:
        # Thisis~1.txt, Thisis~2.txt etc.
        duplicate, num = not None, 1
        while duplicate:
            shortname = "%s%s" % (fname[:8-len(str(num))].upper(),\
                                  str(num))
            if len( ext ) >= 2:
                shortname = "%s%s" % (shortname, ext[:4].upper())

            duplicate = shortname in self.filename_set
            num += 1

        assert( self.is_dos_short_file_name(shortname) ), 'shortname is %s, longname is %s' % (shortname, file)
        self.filename_set.append(shortname)
        return shortname

    def create_feature_dict(self, files):
        """ creates a dictioniary which maps from the x_msi_feature and doc FileTag
        to the included files.
        """
        dict = {}

        def add_to_dict( feature, file ):
            if not SCons.Util.is_List( feature ):
                feature = [ feature ]

            for f in feature:
                if not dict.has_key( f ):
                    dict[ f ] = [ file ]
                else:
                    dict[ f ].append( file )

        for file in files:
            tags = file.get_tags()
            if tags.has_key( 'x_msi_feature' ):
                add_to_dict( tags['x_msi_feature'], file ) 
            elif tags.has_key( 'doc' ):
                add_to_dict( 'doc', file )
            else:
                add_to_dict( 'default', file )

        return dict

    def convert_to_id(self, _str):
        """ converts a long str to a valid Id. This means a str which consists only
        of A-Z and a-z characters is returned. 

        Furthermore cares for duplicate ids.
        """
        try:
            return self.id_set[_str]
        except KeyError:
            n_id = filter( lambda c: 'A' <= c <= 'Z' or 'a' <= c <= 'z', _str )
            def conv_num_to_str( num ):
                alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                str  = 'a' * (num/len(alphabet))
                return str + alphabet[num % len(alphabet)]

            num  = 0
            while "%s_%s" % (n_id, conv_num_to_str(num)) in self.id_set.values():
                num += 1

            name = "%s_%s" % (n_id, conv_num_to_str(num))
            self.id_set[_str] = name

            return name

    def generate_guids(self, root):
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

    #
    # setup function
    #
    def create_default_directory_layout(self, root, spec):
        """ Create the wix default target directory layout and return the innermost
        directory.

        We assume that the XML tree delivered in the root argument already contains
        the Product tag.

        Everything is put under the PFiles directory property defined by WiX.
        After that a directory  with the optional 'vendor' tag is placed and then
        a directory with the name of the project and its version. This leads to the
        following TARGET Directory Layout:
        C:\<PFiles>\<Vendor>\<Projectname-Version>\ , where vendor is optional. 
        Example: C:\Programme\Company\Product-1.2\
        """
        doc = Document()
        d1  = doc.createElement( 'Directory' )
        d1.attributes['Id']   = 'TARGETDIR'
        d1.attributes['Name'] = 'SourceDir'

        d2  = doc.createElement( 'Directory' )
        d2.attributes['Id']   = 'ProgramFilesFolder'
        d2.attributes['Name'] = 'PFiles'

        d3 = doc.createElement( 'Directory' )
        d3.attributes['Id']       = 'vendor_folder'
        d3.attributes['Name']     = escape( self.gen_dos_short_file_name( spec['vendor'] ) )
        d3.attributes['LongName'] = escape( spec['vendor'] )

        d4 = doc.createElement( 'Directory' )
        project_folder            = "%s-%s" % (spec['projectname'], spec['version'])
        d4.attributes['Id']       = 'MY_DEFAULT_FOLDER'
        d4.attributes['Name']     = escape( self.gen_dos_short_file_name( project_folder ) )
        d4.attributes['LongName'] = escape( project_folder )

        d1.childNodes.append( d2 )
        d2.childNodes.append( d3 )
        d3.childNodes.append( d4 )

        root.getElementsByTagName('Product')[0].childNodes.append( d1 )

        return d4

    #
    # mandatory and optional file tags
    #
    def build_wxsfile_file_section(self, root, spec, files):
        """ builds the Component sections of the wxs file with their included files.

        As the files need to specified in 8.3 Filename format and long filename, we needed
        to write a function that converts long filename to 8.3 filenames.

        Features are specficied with the 'x_msi_feature' or 'doc' FileTag.
        """
        root       = self.create_default_directory_layout(root, spec)
        components = self.create_feature_dict( files )
        factory    = Document()

        def get_directory( node, dir ):
            """ returns the node under the given node representing the directory.

            Returns the component node if dir is None or empty.
            """
            if dir == '' or not dir:
                return node

            Directory = node
            dir_parts = dir.split(os.path.sep)

            # to make sure that our directory id are unique, the parent folder are 
            # consecutively added to upper_dir
            upper_dir = ''

            # walk down the xml tree finding parts of the directory
            dir_parts = filter( lambda d: d != '', dir_parts )
            for d in dir_parts[:]:
                already_created = filter( lambda c: c.nodeName == 'Directory' and c.attributes['LongName'].value == escape(d), Directory.childNodes ) 

                if already_created != []:
                    Directory = already_created[0]
                    dir_parts.remove(d)
                    upper_dir += d
                else:
                    break

            for d in dir_parts:
                nDirectory = factory.createElement( 'Directory' )
                nDirectory.attributes['LongName'] = escape( d )
                nDirectory.attributes['Name']     = escape( self.gen_dos_short_file_name( d ) )
                upper_dir += d
                nDirectory.attributes['Id']       = self.convert_to_id( upper_dir )

                Directory.childNodes.append( nDirectory )
                Directory = nDirectory

            return Directory

        tag_factories = [ LocationTagFactory() ]

        for file in files:
            tags = file.get_tags( tag_factories )
            drive, path = os.path.splitdrive( tags['install_location'] )
            filename = os.path.basename( path )
            dirname  = os.path.dirname( path )

            if not tags.has_key('x_msi_vital'):
                tags['x_msi_vital'] = 'yes'

            if not tags.has_key('x_msi_fileid'):
                # TODO convert_to_id does not care for uniqueness
                tags['x_msi_fileid'] = self.convert_to_id( filename )

            if not tags.has_key('x_msi_longname'):
                tags['x_msi_longname'] = filename

            if not tags.has_key('x_msi_shortname'):
                tags['x_msi_shortname'] = self.gen_dos_short_file_name( filename )

            if not tags.has_key('x_msi_source'):
                tags['x_msi_source'] = file.get_path()

            File = factory.createElement( 'File' )
            File.attributes['LongName'] = escape( tags['x_msi_longname'] )
            File.attributes['Name']     = escape( tags['x_msi_shortname'] )
            File.attributes['Source']   = escape( tags['x_msi_source'] )
            File.attributes['Id']       = escape( tags['x_msi_fileid'] )
            File.attributes['Vital']    = escape( tags['x_msi_vital'] )

            # create the <Component> Tag under which this file should appear
            Component = factory.createElement('Component')
            Component.attributes['DiskId'] = '1'
            Component.attributes['Id']     = self.convert_to_id( filename )

            # hang the component node under the root node and the file node
            # under the component node.
            Directory = get_directory( root, dirname )
            Directory.childNodes.append( Component )
            Component.childNodes.append( File )

    #
    # additional functions
    #
    def build_wxsfile_features_section(self, root, spec, files):
        """ This function creates the <features> tag based on the supplied xml tree.

        This is achieved by finding all <component>s and adding them to a default target.

        It should be called after the tree has been built completly.  We assume
        that a MY_DEFAULT_FOLDER Property is defined in the wxs file tree.

        Furthermore a top-level with the name and version of the software will be created.
        """
        factory = Document()
        Feature = factory.createElement('Feature')
        Feature.attributes['Id']                    = 'complete'
        Feature.attributes['ConfigurableDirectory'] = 'MY_DEFAULT_FOLDER'
        Feature.attributes['Level']                 = '1'
        Feature.attributes['Title']                 = escape( '%s %s' % (spec['projectname'], spec['version']) )
        Feature.attributes['Description']           = escape( spec['summary'] )
        Feature.attributes['Display']               = 'expand'

        for (feature, files) in self.create_feature_dict(files).items():
            SubFeature   = factory.createElement('Feature')
            SubFeature.attributes['Id']    = self.convert_to_id( feature )
            SubFeature.attributes['Title'] = ('Main Part',feature)[feature!='default']
            SubFeature.attributes['Level'] = '1'

            f = files
            if SCons.Util.is_List( files ):
                f = files[0]

            tags = f.get_tags()
            if tags.has_key( 'x_msi_feature' ):
                SubFeature.attributes['Description'] = tags['x_msi_feature']
            elif tags.has_key( 'doc' ):
                SubFeature.attributes['Description'] = 'Documentation'
                SubFeature.attributes['Title']       = 'Documentation'

            # build the componentrefs. As one of the design decision is that every
            # file is also a component we walk the list of files and create a
            # reference.
            for f in files:
                ComponentRef = factory.createElement('ComponentRef')
                ComponentRef.attributes['Id'] = self.convert_to_id( os.path.basename(f.get_path()) )
                SubFeature.childNodes.append(ComponentRef)

            Feature.childNodes.append(SubFeature)

        root.getElementsByTagName('Product')[0].childNodes.append(Feature)

    def build_wxsfile_default_gui(self, root):
        """ this function adds a default GUI to the wxs file
        """
        factory = Document()
        Product = root.getElementsByTagName('Product')[0]

        UIRef   = factory.createElement('UIRef')
        UIRef.attributes['Id'] = 'WixUI_Mondo'
        Product.childNodes.append(UIRef)

        UIRef   = factory.createElement('UIRef')
        UIRef.attributes['Id'] = 'WixUI_ErrorProgressText'
        Product.childNodes.append(UIRef)

    def build_license_file(self, directory, spec):
        """ creates a License.rtf file with the content of "x_msi_license_text" 
        in the given directory. """
        name, text = '', ''

        try:
            name = spec['license']
            text = spec['license_text']
        except KeyError:
            pass # ignore this as x_msi_license_text is optional

        if name!='' or text!='':
            file = open( os.path.join(directory.get_path(), 'License.rtf'), 'w' )
            file.write('{\\rtf')
            if text!='':
                 file.write(text.replace('\n', '\\par '))
            else:
                 file.write(name+'\\par\\par')
            file.write('}')
            file.close()

    #
    # mandatory and optional package tags
    #
    def build_wxsfile_header_section(self, root, spec):
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
        Product.attributes['Name']         = escape( spec['projectname'] )
        Product.attributes['Version']      = escape( spec['version'] )
        Product.attributes['Manufacturer'] = escape( spec['vendor'] )
        Product.attributes['Language']     = escape( spec['x_msi_language'] )

        Package.attributes['Description']  = escape( spec['summary'] )

        # now the optional tags, for which we avoid the KeyErrror exception
        if spec.has_key( 'description' ):
            Package.attributes['Comments'] = escape( spec['description'] )

        if spec.has_key( 'x_msi_upgrade_code' ):
            Package.attributes['x_msi_upgrade_code'] = escape( spec['x_msi_upgrade_code'] ) 

        # We hardcode the media tag as our current model cannot handle it.
        Media = factory.createElement('Media')
        Media.attributes['Id']       = '1'
        Media.attributes['Cabinet']  = 'default.cab'
        Media.attributes['EmbedCab'] = 'yes'
        root.getElementsByTagName('Product')[0].childNodes.append(Media)
