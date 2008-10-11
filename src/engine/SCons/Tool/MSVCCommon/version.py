import SCons.Util

from SCons.Tool.MSVCCommon.findloc import find_bat

# Default value of VS to use
DEFVERSIONSTR = "9.0"
DEFVERSION = float(DEFVERSIONSTR)

_SUPPORTED_VERSIONS = [9.0, 8.0, 7.1, 7.0, 6.0]
_SUPPORTED_VERSIONSSTR = [str(i) for i in _SUPPORTED_VERSIONS]

_VSCOMNTOOL_VARNAME = dict([(v, 'VS%dCOMNTOOLS' % round(v * 10))
                            for v in _SUPPORTED_VERSIONS])

def query_versions():
    """Query the system to get available versions of VS. A version is
    considered when a batfile is found."""
    versions = []
    # We put in decreasing order: versions itself should be in drecreasing
    # order
    for v in _SUPPORTED_VERSIONS:
        bat = find_bat(v)
        if bat is not None:
            versions.append(v)

    return versions

def get_default_version(env):
    """Return the default version to use for MSVS

    if no version was requested by the user through the MSVS environment
    variable, query all the available the visual studios through
    query_versions, and take the highest one.

    Return
    ------
    version: str
        the default version."""
    versions = [DEFVERSIONSTR]

    if not env.has_key('MSVS') or not SCons.Util.is_Dict(env['MSVS']):
        v = [str(i) for i in query_versions()]
        if v:
            versions = v
        env['MSVS'] = {'VERSIONS' : versions}
    else:
        versions = env['MSVS'].get('VERSIONS', versions)

    if not env.has_key('MSVS_VERSION'):
        env['MSVS_VERSION'] = versions[0] #use highest version by default

    env['MSVS']['VERSION'] = env['MSVS_VERSION']

    return env['MSVS_VERSION']

def detect_msvs():
    version = query_versions()
    if len(version) > 0:
        return 1
    else:
        return 0
