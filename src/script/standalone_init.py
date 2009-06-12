#------------------------------------------------------------------------------
# standalone_init.py
#   Initialization script for cx_Freeze based on Console.py which doesn't
# truncate the path. It also sets the attribute sys.frozen so that the Win32
# extensions behave as expected.
#------------------------------------------------------------------------------

import encodings
import os
import sys
import warnings
import zipimport

sys.frozen = True
#sys.path = sys.path[:4]

os.environ["TCL_LIBRARY"] = os.path.join(DIR_NAME, "tcl")
os.environ["TK_LIBRARY"] = os.path.join(DIR_NAME, "tk")

m = __import__("__main__")
importer = zipimport.zipimporter(INITSCRIPT_ZIP_FILE_NAME)
if INITSCRIPT_ZIP_FILE_NAME != SHARED_ZIP_FILE_NAME:
    moduleName = m.__name__
else:
    name, ext = os.path.splitext(os.path.basename(os.path.normcase(FILE_NAME)))
    moduleName = "%s__main__" % name
code = importer.get_code(moduleName)
exec code in m.__dict__

if sys.version_info[:2] >= (2, 5):
    module = sys.modules.get("threading")
    if module is not None:
        module._shutdown()

