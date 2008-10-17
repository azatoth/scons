"""Set of tools to extract env variables from bat file executed in a "sandbox"."""
import copy
import os
import subprocess
import re

from SCons.Tool.MSVCCommon.common import debug

def normalize_env(env, keys):
    """Given a dictionary representing a shell environment, add the variables
    from os.environ needed for the processing of .bat files; the keys are
    controlled by the keys argument.

    It also makes sure the environment values are correctly encoded.

    Note: the environment is copied"""
    normenv = {}
    if env:
        for k in env.keys():
            normenv[k] = copy.deepcopy(env[k]).encode('mbcs')

        for k in keys:
            if os.environ.has_key(k):
                normenv[k] = os.environ[k].encode('mbcs')

    return normenv

def get_output(vcbat, args = None, env = None):
    """Parse the output of given bat file, with given args."""
    if args:
        debug("Calling '%s %s'" % (vcbat, args))
        popen = subprocess.Popen('"%s" %s & set' % (vcbat, args),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=env)
    else:
        debug("Calling '%s'" % vcbat)
        popen = subprocess.Popen('"%s" & set' % vcbat,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=env)

    stdout, stderr = popen.communicate()
    if popen.wait() != 0:
        raise IOError(stderr.decode("mbcs"))

    output = stdout.decode("mbcs")
    return output

# You gotta love this: they had to set Path instead of PATH...
# (also below we search case-insensitively because VC9 uses uppercase PATH)
_ENV_TO_T = {"INCLUDE": "INCLUDE", "PATH": "PATH",
             "LIB": "LIB", "LIBPATH": "LIBPATH"}

def parse_output(output, keep = ("INCLUDE", "LIB", "LIBPATH", "PATH")):
    # dkeep is a dict associating key: path_list, where key is one item from
    # keep, and pat_list the associated list of paths

    # TODO(1.5):  replace with the following list comprehension:
    #dkeep = dict([(i, []) for i in keep])
    dkeep = dict(map(lambda i: (i, []), keep))

    # rdk will  keep the regex to match the .bat file output line starts
    rdk = {}
    for i in keep:
        # XXX: the _ENV_TO_T indirection may not be necessary anymore. Check
        # this
        if _ENV_TO_T.has_key(i):
            rdk[i] = re.compile('%s=(.*)' % _ENV_TO_T[i], re.I)
        else:
            rdk[i] = re.compile('%s=(.*)' % i, re.I)

    def add_env(rmatch, key):
        plist = rmatch.group(1).split(os.pathsep)
        for p in plist:
            # Do not add empty paths (when a var ends with ;)
            if p:
                dkeep[key].append(p)

    for line in output.splitlines():
        for k,v in rdk.items():
            m = v.match(line)
            if m:
                add_env(m, k)

    return dkeep

def output_to_dict(output):
    """Given an output string, parse it to find env variables.

    Return a dict where keys are variables names, and values their content"""
    envlinem = re.compile(r'^([a-zA-z0-9]+)=([\S\s]*)$')
    parsedenv = {}
    for line in output.splitlines():
        m = envlinem.match(line)
        if m:
            parsedenv[m.group(1)] = m.group(2)
    return parsedenv

def get_new(l1, l2):
    """Given two list l1 and l2, return the items in l2 which are not in l1.
    Order is maintained."""

    # We don't try to be smart: lists are small, and this is not the bottleneck
    # is any case
    new = []
    for i in l2:
        if i not in l1:
            new.append(i)

    return new

