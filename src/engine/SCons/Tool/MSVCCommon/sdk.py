"""Module to detect the Platform/Windows SDK (starting with PSDK 2003 R1)."""

import os

import SCons.Util
from SCons.Tool.MSVCCommon.common import debug, read_reg

# SDK Checks. This is of course a mess as everything else on MS platforms. Here
# is what we do to detect the SDK:
#
# For Windows SDK >= 6.0: just look into the registry entries:
#   HKLM\Software\Microsoft\Microsoft SDKs\Windows
# All the keys in there are the available versions.
#
# For Platform SDK before (2003 server R1 and R2, etc...), there does not seem
# to have any sane registry key, so the precise location is hardcoded (yeah).
#
# For versions below 2003R1, it seems the PSDK is included with Visual Studio ?


# 2003* sdk:
_SDK2003_HKEY_ROOT = r"Software\Microsoft\MicrosoftSDK\InstalledSDKS"
_SDK2003_UUID = {"2003R2": "D2FF9F89-8AA2-4373-8A31-C838BF4DBBE1",
                 "2003R1": "8F9E5EF3-A9A5-491B-A889-C58EFFECE8B3"}

# Location of the SDK (checked for 6.1 only)
_SUPPORTED_SDK_VERSIONS_STR = ["6.1", "6.0A", "6.0", "2003R2", "2003R1"]
_VERSIONED_SDK_HKEY_ROOT = \
        r"Software\Microsoft\Microsoft SDKs\Windows\v%s"
_CURINSTALLED_SDK_HKEY_ROOT = \
        r"Software\Microsoft\Microsoft SDKs\Windows\CurrentInstallFolder"

# For the given version string, we check that the given file does exist
# relatively to the mssdk path, to be sure we don't deal with a stale entry in
# the registry.
_SANITY_CHECK_FILE = {"6.0" : r"bin\gacutil.exe",
    "6.0A" : r"include\windows.h",
    "6.1" : r"include\windows.h",
    "2003R2" : r"SetEnv.Cmd",
    "2003R1" : r"SetEnv.Cmd"}

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

def find_mssdk_2003(versionstr):
    debug("Looking for %s sdk" % versionstr)
    sdkbase = _SDK2003_HKEY_ROOT

    if not _SDK2003_UUID.has_key(versionstr):
        debug("UUID for %s not known" % versionstr)
        return None
    else:
        key = sdkbase + r'\\' + _SDK2003_UUID[versionstr] + r'\Install Dir'
        try:
            mssdk = read_reg(key)
            debug("Found registry key %s" % key)
        except WindowsError:
            debug("Could not find registry key %s" % key)
            return None

    if not os.path.exists(mssdk):
        debug("path %s not found" % mssdk)
        return None

    return mssdk

def find_mssdk(versionstr):
    """Return the MSSSDK given the version string."""
    if versionstr.startswith('2003'):
        mssdk = find_mssdk_2003(versionstr)
    else:
        mssdk = sdir_from_reg(versionstr)

    if mssdk is not None:
        ftc = os.path.join(mssdk, _SANITY_CHECK_FILE[versionstr])
        if not os.path.exists(ftc):
            debug("File %s used for sanity check not found" % ftc)
            return None
    else:
        return None

    return mssdk

def query_versions():
    versions = []
    for v in _SUPPORTED_SDK_VERSIONS_STR:
        if find_mssdk(v):
            versions.append(v)

    return versions

def detect_mssdk():
    versions = query_versions()
    if len(versions) > 0:
        return 1
    else:
        return 0

def set_sdk(env, mssdk):
    """Set the Platform sdk given the MS SDK path."""
    env.PrependENVPath("INCLUDE", os.path.join(mssdk, "include"))
    env.PrependENVPath("LIB", os.path.join(mssdk, "lib"))
    env.PrependENVPath("LIBPATH", os.path.join(mssdk, "lib"))

def set_default_sdk(env, msver):
    """Set up the default Platform/Windows SDK."""
    # For MSVS < 8, use integrated windows sdk by default
    if msver >= 8:
        versstr = query_versions()
        if len(versstr) > 0:
            mssdk = find_mssdk(versstr[0])
            if mssdk:
                set_sdk(env, mssdk)
