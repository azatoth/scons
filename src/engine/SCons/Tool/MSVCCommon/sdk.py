import os

import SCons.Util
from SCons.Tool.MSVCCommon.common import debug, read_reg

# SDK Checks. This is of course a mess as everything else on MS platforms. Here
# is what we do to detect the SDK:
#
# For Windows SDK >= 6.0: just look into the registry entries:
#	HKLM\Software\Microsoft\Microsoft SDKs\Windows
# All the keys in there are the available versions.
#
# For Platform SDK before (2003 server R1 and R2, etc...), there does not seem
# to have any sane registry key, so the precise location is hardcoded (yeah).

# Location of the SDK (checked for 6.1 only)
_SUPPORTED_SDK_VERSIONS_STR = ["6.1", "6.0A", "6.0"]
_VERSIONED_SDK_HKEY_ROOT = \
        r"Software\Microsoft\Microsoft SDKs\Windows\v%s"
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

def sdir_from_reg(versionstr):
    """Try to find the MS SDK from the registry.

    Return None if failed or the directory does not exist"""
    if not SCons.Util.can_read_reg:
        debug('SCons cannot read registry')
        return None

    sdkbase = _VERSIONED_SDK_HKEY_ROOT % versionstr

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

def parse_version(versionstr):
    import re
    r = re.compile("([0-9\.]*)([\s\S]*)")
    m = r.match(versionstr)
    if not m:
        raise ValueError("Could not parse version string %s" % versiontr)

    return float(m.group(1)), m.group(2)

def query_versions():
    versions = []
    for v in _SUPPORTED_SDK_VERSIONS_STR:
        if sdir_from_reg(v):
            versions.append(v)

    return versions
