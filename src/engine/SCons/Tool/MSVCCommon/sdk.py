import os

import SCons.Util
from SCons.Tool.MSVCCommon.common import debug, read_reg

# Location of the SDK (checked for 6.1 only)
_SUPPORTED_SDK_VERSIONS = [6.1, 6.0]
_VERSIONED_SDK_HKEY_ROOT = \
        r"Software\Microsoft\Microsoft SDKs\Windows\v%0.1f"
_CURINSTALLED_SDK_HKEY_ROOT = \
        r"Software\Microsoft\Microsoft SDKs\Windows\CurrentInstallFolder"

def get_cur_sdk_dir_from_reg():
    """Try to find the platform sdk directory from the registry.

    Return None if failed or the directory does not exist"""
    if not SCons.Util.can_read_reg:
        debug('SCons cannot read registry')
        return None

    try:
        val = read_reg(_CURINSTALLED_SDK_HKEY_ROOT)
        debug("Found current sdk dir in registry: %s" % val)
    except WindowsError, e:
        debug("Did not find current sdk in registry")
        return None

    if not os.path.exists(val):
        debug("Current sdk dir %s not on fs" % val)
        return None

    return val

def sdir_from_reg(version):
    """Try to find the MS SDK from the registry.

    Return None if failed or the directory does not exist"""
    if not SCons.Util.can_read_reg:
        debug('SCons cannot read registry')
        return None

    sdkbase = _VERSIONED_SDK_HKEY_ROOT % version

    try:
        basedir = read_reg(sdkbase + '\InstallationFolder')
        debug('Found sdk dir in registry: %s' % basedir)
    except WindowsError, e:
        debug('Did not find sdk dir key %s in registry' % \
              (sdkbase + '\InstallationFolder'))
        return None

    if not os.path.exists(basedir):
        debug('%s is not found on the filesystem' % basedir)
        return None

    return basedir
