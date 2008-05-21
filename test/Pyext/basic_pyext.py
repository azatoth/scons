# This just tests that the Python* builders actually run on the tested
# platform. This tests whether the tools is building working python
# extensions.
import TestSCons

from test_common import can_real_pytests

test_pyext = TestSCons.TestSCons()

can_real_pytests(test_pyext)

test_pyext.write('SConstruct', """\
env = Environment()
t = Tool('pyext')
t(env)
env.PythonExtension('hello.c')
""")

hello = """
#include <Python.h>

static PyObject *
spam_system(PyObject *self, PyObject *args)
{
    printf("Hello from C python");
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef SpamMethods[] = {
    {"hello",  spam_system, METH_VARARGS, "Execute a shell command."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
inithello(void)
{
    (void) Py_InitModule("hello", SpamMethods);
}
"""

test_pyext.write('hello.c', hello)

test_pyext.write('test_hello.py', """
import hello
hello.hello()
""")

test_pyext.run() 
test_pyext.run(program = ['python', 'test_hello.py'], stdout = "Hello from C python")

test_pyext.pass_test()

