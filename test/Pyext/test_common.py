def can_real_pytests(test):
    try:
        from distutils import sysconfig
        from os.path import join, exists
        pypath = sysconfig.get_python_inc()
        if not exists(join(pypath, 'Python.h')):
            test.skip_test('Could not find Python header; skipping test.\n')
            return 0
    except ImportError:
        test.skip_test('Could not import distutils; skipping test.\n')
        return 0

    return 1

