<?
	include "includes/templates.php";

	error_reporting(E_ALL);

	make_top("FAQ", "faq");
?>

<div id="bodycontent">

<h2> FAQ </h2>

<CENTER><H1> SCons FAQ</H1></CENTER>
<CENTER>Version 0.1</CENTER>
<CENTER>2 April 2004</CENTER>
<CENTER>Steven Knight (knight at baldmt dot com)</CENTER>


<H2><A NAME="S_1">Subject: 1. Overview</A></H2>

<H3><A NAME="SS_1_1">1.1. Introduction</A></H3>
<P>
This FAQ contains information about the
SCons software construction tool.
</P>

<H3><A NAME="SS_1_2">1.2. Current Version of This FAQ</A></H3>
<P>
The most recent and up-to-date version of this FAQ
may always be found at:
</P>
<PRE>
 <A HREF="http://www.scons.org/faq/current.html">http://www.scons.org/faq/current.html</A> (HTML)
 <A HREF="http://www.scons.org/faq/current.txt">http://www.scons.org/faq/current.txt</A> (text)
</PRE>
<P>
Please check to make sure your question
hasn't already been answered in the latest version
before submitting a new question
(or an addition or correction to this FAQ).
</P>

<H3><A NAME="SS_1_3">1.3. Copyright</A></H3>
<P>
This document is copyright 2001 by Steven Knight
(knight at baldmt dot com).
</P>
<P>
This document may be freely copied, redistributed or modified for
any purpose and without fee, provided that this copyright notice
is not removed or altered.
</P>
<P>
Individual items from this document may be excerpted and
redistributed without inclusion of the copyright notice.
</P>
<P>
If you incorporate this FAQ in any commercial, salable, or
for-profit collection or product, please be courteous and send a
copy to the copyright holder.
</P>

<H3><A NAME="SS_1_4">1.4. Feedback</A></H3>
<P>
Any and all feedback on this FAQ is welcome:
corrections to existing answers,
suggested new questions,
typographical errors,
better organization of questions,
etc.
Contact the author at knight at baldmt dot com.
</P>


<H2><A NAME="S_2">Subject: 2. Table of Contents</A></H2>
<OL>
<LI VALUE="1"><A HREF="#S_1">Overview</A><BR>
<BR>
1.1. <A HREF="#SS_1_1">Introduction</A><BR>
1.2. <A HREF="#SS_1_2">Current Version of This FAQ</A><BR>
1.3. <A HREF="#SS_1_3">Copyright</A><BR>
1.4. <A HREF="#SS_1_4">Feedback</A><BR>
</LI>
<BR>
<LI VALUE="2"><A HREF="#S_2">Table of Contents</A><BR>
</LI>
<BR>
<LI VALUE="3"><A HREF="#S_3">General Information</A><BR>
<BR>
3.1. <A HREF="#SS_3_1">What is SCons?</A><BR>
3.2. <A HREF="#SS_3_2">Where do I get SCons?</A><BR>
3.3. <A HREF="#SS_3_3">What's the difference between the scons, scons-local and scons-src packages?</A><BR>
3.4. <A HREF="#SS_3_4">What version of Python do I need?</A><BR>
3.5. <A HREF="#SS_3_5">Do I need to know how to program in Python to use SCons?</A><BR>
3.6. <A HREF="#SS_3_6">Why is SCons written for Python version 1.5.2?</A><BR>
3.7. <A HREF="#SS_3_7">Am I restricted to using Python 1.5.2 code in my SConscript files?</A><BR>
3.8. <A HREF="#SS_3_8">Are there any SCons mailing lists or newsgroups?  Are they archived anywhere?</A><BR>
3.9. <A HREF="#SS_3_9">Is SCons released under an Open Source license?</A><BR>
3.10. <A HREF="#SS_3_10">Can I help with SCons development?</A><BR>
</LI>
<BR>
<LI VALUE="4"><A HREF="#S_4">SCons Questions</A><BR>
<BR>
4.1. <A HREF="#SS_4_1">How do I get SCons to find my #include files?</A><BR>
4.2. <A HREF="#SS_4_2">How do I install files?  The Install() method doesn't seem to do anything with them.</A><BR>
4.3. <A HREF="#SS_4_3">Why doesn't SCons find my compiler/linker/etc.?  I can execute it just fine from the command line.</A><BR>
4.4. <A HREF="#SS_4_4">I'm alreadying using ldconfig, pkg-config, gtk-config, etc.  Do I have to rewrite their logic to use SCons?</A><BR>
4.5. <A HREF="#SS_4_5">Linking on Windows gives me an error: LINK: fatal error LNK1104: cannot open file 'TEMPFILE'.  How do I fix this?</A><BR>
</LI>
<BR>
<LI VALUE="5"><A HREF="#S_5">Compatibility with make</A><BR>
<BR>
5.1. <A HREF="#SS_5_1">Is SCons compatible with make?</A><BR>
5.2. <A HREF="#SS_5_2">Is there a Makefile-to-SCons or SCons-to-Makefile converter?</A><BR>
5.3. <A HREF="#SS_5_3">Does SCons support building in parallel, like make's -j option?</A><BR>
5.4. <A HREF="#SS_5_4">Does SCons support something like VPATH in make?</A><BR>
</LI>
<BR>
<LI VALUE="6"><A HREF="#S_6">SCons History and Background</A><BR>
<BR>
6.1. <A HREF="#SS_6_1">Who wrote SCons?</A><BR>
6.2. <A HREF="#SS_6_2">Is SCons the same as Cons?</A><BR>
6.3. <A HREF="#SS_6_3">So what can SCons do that Cons can't?</A><BR>
6.4. <A HREF="#SS_6_4">Should I use Cons or SCons for my project?</A><BR>
6.5. <A HREF="#SS_6_5">Is SCons the same as the ScCons design from the Software Carpentry competition?</A><BR>
</LI>
</OL>


<H2><A NAME="S_3">Subject: 3. General Information</A></H2>

<H3><A NAME="SS_3_1">3.1. What is SCons?</A></H3>
<P>
SCons is a software construction tool--that is,
a superior alternative to the classic "Make"
build tool that we all know and love.
</P>
<P>
SCons is implemented as a Python script
and set of modules,
and SCons "configuration files"
are actually executed as Python scripts.
This gives SCons many powerful capabilities
not found in other software build tools.
</P>

<H3><A NAME="SS_3_2">3.2. Where do I get SCons?</A></H3>
<P>
The SCons download page is:
</P>
<PRE>
        <A HREF="http://www.scons.org/download.php">http://www.scons.org/download.php</A>
      </PRE>
<P>
If you're interested in the [b]leading edge,
you can take a look at what the developers are up to
in the latest code checked in to the CVS tree.
</P>
<P>
Instructions for Anonymous CVS access are
available at:
</P>
<PRE>
        <A HREF="http://sourceforge.net/cvs/?group_id=30337">http://sourceforge.net/cvs/?group_id=30337</A>
      </PRE>
<P>
Or you can browse the tree on-line at:
</P>
<PRE>
        <A HREF="http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/scons/">http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/scons/</A>
      </PRE>

<H3><A NAME="SS_3_3">3.3. What's the difference between the scons, scons-local and scons-src packages?</A></H3>
<P>
We make SCons available in three distinct packages,
for different purposes.
</P>
<P>
The <tt>scons</tt> package is the basic one
for installing SCons on your system
and using it or experimenting with it.
You don't need any other package
if you just want to try out SCons.
</P>
<P>
The <tt>scons-local</tt> package
is one that you can execute standalone,
out of a local directory.
It's intended to be dropped in to
and shipped with packages of other software
that want to build with SCons,
but which don't want to have to
require that their users install SCons.
</P>
<P>
The <tt>scons-src</tt> package is the complete source tree,
including everything we use to package SCons
and all of the regression tests.
You might want this one if you had concerns
about whether SCons was working correctly
on your operating system and wanted to run the regression tests.
</P>

<H3><A NAME="SS_3_4">3.4. What version of Python do I need?</A></H3>
<P>
SCons is written to work with Python version 1.5.2
or any later version.
Extensive tests are used to
ensure that SCons works on all
supported versions.
</P>
<P>
In order to install SCons from a source distribution,
the Python Distutils package is required.
Distutils is part of Python version 1.6 and higher.
For Python 1.5.2, you can obtain the Distutils
package from:
</P>
<PRE>
        <A HREF="http://www.python.org/sigs/distutils-sig/">http://www.python.org/sigs/distutils-sig/</A>
      </PRE>

<H3><A NAME="SS_3_5">3.5. Do I need to know how to program in Python to use SCons?</A></H3>
<P>
No, you can use SCons very successfully even if
you don't know how to program in Python.
</P>
<P>
With SCons, you use Python functions to
tell a central build engine about
your input and output files.
You can look at these simply as different commands
that you use to specify
what software (or other files) you want built.
SCons takes care of the rest,
including figuring out most of your dependencies.
</P>
<P>
Of course, if you <i>do</i> know Python,
you can use its scripting capabilities
to do more sophisticated things in your build:
construct lists of files,
manipulate file names dynamically,
handle flow control (loops and conditionals)
in your build process,
etc.
</P>

<H3><A NAME="SS_3_6">3.6. Why is SCons written for Python version 1.5.2?</A></H3>
<P>
Python 1.5.2 is still in widespread use on many systems,
and was the version shipped by Red Hat as late as Red Hat 7.3.
By writing the internal code so that it works on these systems,
we're making it as easy as possible for more sites
to install and work with SCons on as wide a variety of
systems as possible.
</P>
<P>
"Why don't people just upgrade their Python version?"
you may ask.
Yes, Python's packaging and installation make it easy for people
to upgrade versions, but that's not the only barrier.
</P>
<P>
In commercial development environments,
any new operating system or language version must usually
be accompanied by extensive tests to make sure
that the upgrade hasn't introduced subtle
problems or regressions into the code being produced.
Consequently, upgrading is an expensive proposition
that many sites can't undertake just because a new tool
like SCons might require it.
When faced with that sort of choice, it's much less risky
and expensive for them to just walk away from trying the new tool.
</P>

<H3><A NAME="SS_3_7">3.7. Am I restricted to using Python 1.5.2 code in my SConscript files?</A></H3>
<P>
No, you can write Python code in your SConscript file
using any version of Python you have installed.
The SCons internal code will run on Python 1.5.2,
but that does not in any way affect what Python code
it can execute in an SConscript file.
</P>

<H3><A NAME="SS_3_8">3.8. Are there any SCons mailing lists or newsgroups?  Are they archived anywhere?</A></H3>
<P>
There are several SCons mailing lists,
and they are archived.
Information about the lists and archives is available at either:
</P>
<PRE>
        <A HREF="http://www.scons.org/lists.html">http://www.scons.org/lists.html</A>

        <A HREF="http://sourceforge.net/mail/?group_id=30337">http://sourceforge.net/mail/?group_id=30337</A>
      </PRE>
<P>
There is no SCons newsgroup.
</P>

<H3><A NAME="SS_3_9">3.9. Is SCons released under an Open Source license?</A></H3>
<P>
Yes.  SCons is distributed under the MIT license,
an approved Open Source license.
This means you can use it, modify it,
or even redistribute it without charge,
so long as you maintain the license.
</P>

<H3><A NAME="SS_3_10">3.10. Can I help with SCons development?</A></H3>
<P>
Definitely.
We're looking for any help possible:
</P>
<PRE>
        --  Python programmers
        --  documentation writers
        --  web designers and/or administrators
        --  testers (especially if you use a non-usual operating
            system or tool chain)
      </PRE>
<P>
If you have time and/or resources to contribute,
contact the SCons developers at
<A HREF="mailto:dev@scons.tigris.org">dev@scons.tigris.org</A>
and tell us what you're interested in doing.
</P>


<H2><A NAME="S_4">Subject: 4. SCons Questions</A></H2>

<H3><A NAME="SS_4_1">4.1. How do I get SCons to find my #include files?</A></H3>
<TABLE BORDER="0"><TR>
<TD ALIGN="left" VALIGN="top">A:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
<TD ALIGN="left" VALIGN="top" COLSPAN="2">
<P>
If your program has #include files in various directories, SCons
must somehow be told in which directories it should look for
the #include files.  You do this by setting the CPPPATH variable
to the list of directories that contain .h files that you want
to search for:
</P>
<PRE>
          env = Environment(CPPPATH='inc')
          env.Program('foo', 'foo.c')
        </PRE>
<P>
SCons will add to the compilation command line(s)
the right -I options, or whatever similar options
are appropriate for the C or C++ compiler you're using.
This makes your SCons-based build configuration portable.
</P>
<P>
Note specifically that you should <emphasis>not</emphasis>
set the include directories directly in the CFFLAGS variable,
as you might initially expect:
</P>
<PRE>
          env = Environment(CCFLAGS='-Iinc')    # THIS IS INCORRECT!
          env.Program('foo', 'foo.c')
        </PRE>
<P>
This will make the program compile correctly,
but SCons will not find the dependencies in the "inc" subdirectory
and the program will <emphasis>not</emphasis> be rebuilt
if any of those #include files change.
</P>
</TD>
</TR></TABLE>

<H3><A NAME="SS_4_2">4.2. How do I install files?  The Install() method doesn't seem to do anything with them.</A></H3>
<TABLE BORDER="0"><TR>
<TD ALIGN="left" VALIGN="top">A:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
<TD ALIGN="left" VALIGN="top" COLSPAN="2">
<P>
By default, SCons only builds what you tell it to, and anything
that these files depend on.  If you want SCons to install all your
targets, you have to tell it to do so somehow.  There are two ways
you might do this:
</P>
<P>
1. Use Default().  Any argument you pass to Default() will
be built when the user just runs "scons" without explicitly
specifying any targets to build.  So, you'd say something like:
</P>
<PRE>
        Default(env.Install(directory='my_install_dir', source='foo'))
      </PRE>
<P>
2. Use Alias().  Alias allows you to attach a "pseudo target" to
one or more files.  Say you want a user to type "scons install"
in order to install all your targets, just like a user might type
"make install" for traditional make.  Here is how you do that:
</P>
<PRE>
        env.Alias(target="install", source=env.Install(dir="install_dir", source="foo"))
      </PRE>
<P>
Note that you can call Alias() with a target of "install" as many
times as you want with different source files, and SCons will
build all of them when the user types "scons install".
</P>

[Charles Crain, 14 August 2003]
</TD>
</TR></TABLE>

<H3><A NAME="SS_4_3">4.3. Why doesn't SCons find my compiler/linker/etc.?  I can execute it just fine from the command line.</A></H3>
<TABLE BORDER="0"><TR>
<TD ALIGN="left" VALIGN="top">A:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
<TD ALIGN="left" VALIGN="top" COLSPAN="2">
<P>
A common problem for new users is that SCons
can't seem to find a compiler, linker or other utility
that they can run just fine from the command line.
This is almost always because, by default, SCons does not use the same
PATH environment variable that you use from the command line,
so it can't find a program that has been installed in a
"non-standard" location unless you tell it how.
Here is the explanation from the SCons man page:
</P>
<P>
<blockquote>
scons does not automatically propagate the external environment
used to execute scons to the commands used to build target
files.  This is so that builds will be guaranteed repeatable
regardless of the environment variables set at the time scons is
invoked.  This also means that if the compiler or other commands
that you want to use to build your target files are not in
standard system locations, scons will not find them unless you
explicitly set the PATH to include those locations.
</blockquote>
</P>
<P>
Fortunately, it's easy to propagate the PATH value
from your external environment by initializing
the ENV construction variable as follows:
</P>
<PRE>
        import os
        env = Environment(ENV = {'PATH' : os.environ['PATH']})
      </PRE>
<P>
Alternatively, you might want to propagate your entire
external environment to the build commands as follows:
</P>
<PRE>
        import os
        env = Environment(ENV = os.environ)
      </PRE>
<P>
Of course, by propagating external environment variables
into your build, you're running the risk that a change
in the external environment will affect the build,
possibly in unintended ways.
The way to guarantee that the build is repeatable
is to explicitly initialize the PATH
</P>
<PRE>
        path = ['/bin', '/usr/bin', '/path/to/other/compiler/bin']
        env = Environment(ENV = {'PATH' : path})
      </PRE>
</TD>
</TR></TABLE>

<H3><A NAME="SS_4_4">4.4. I'm alreadying using ldconfig, pkg-config, gtk-config, etc.  Do I have to rewrite their logic to use SCons?</A></H3>
<TABLE BORDER="0"><TR>
<TD ALIGN="left" VALIGN="top">A:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
<TD ALIGN="left" VALIGN="top" COLSPAN="2">
<P>
SCons provides explicit support for getting information
from programs like ldconfig and pkg-config.
The relevant method is ParseConfig(),
which executes a *-config command,
parses the returned flags,
and puts them in the environment
through which the ParseConfig() method is called:
</P>
<PRE>
        env.ParseConfig('pkg-config --cflags --libs libxml')
      </PRE>
<P>
If you need to provide some special-purpose processing,
you can supply a function
to process the flags and apply them to the environment
in any way you want.
</P>
</TD>
</TR></TABLE>

<H3><A NAME="SS_4_5">4.5. Linking on Windows gives me an error: LINK: fatal error LNK1104: cannot open file 'TEMPFILE'.  How do I fix this?</A></H3>
<TABLE BORDER="0"><TR>
<TD ALIGN="left" VALIGN="top">A:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
<TD ALIGN="left" VALIGN="top" COLSPAN="2">
<P>
The Microsoft linker requires that the environment variable TMP is set.
I do the following in my SConstruct file.
</P>
<PRE>
        env['ENV']['TMP'] = os.environ['TMP']
      </PRE>
<P>
There are potential pitfalls for copying user environement variables
into the build environment, but that is well documented. If you don't
want to import from your external environment,
set it to some directory explicitly.
</P>

[Rich Hoesly, 18 November 2003]
</TD>
</TR></TABLE>


<H2><A NAME="S_5">Subject: 5. Compatibility with make</A></H2>

<H3><A NAME="SS_5_1">5.1. Is SCons compatible with make?</A></H3>
<P>
No.  The SCons input files are Python scripts,
with function calls to specify what you want built,
</P>

<H3><A NAME="SS_5_2">5.2. Is there a Makefile-to-SCons or SCons-to-Makefile converter?</A></H3>
<P>
There are no current plans for a converter.
The SCons architecture, however, leaves open
the future possibility of wrapping a Makefile interpreter
around the SCons internal build engine,
to provide an alternate Make-like interface.
Contact the SCons developers if this is something
you're interested in helping build.
</P>
<P>
Note that a proof-of-concept for parsing Makefiles in a scripting
language exists in the Perl-based implementation for
Gary Holt's Make++ tool, which has its home page at:
</P>
<PRE>
        <A HREF="http://lnc.usc.edu/~holt/makepp/">http://lnc.usc.edu/~holt/makepp/</A>
      </PRE>

<H3><A NAME="SS_5_3">5.3. Does SCons support building in parallel, like make's -j option?</A></H3>
<P>
Yes, SCons is designed from the ground up to support a -j option
for parallel builds.
</P>

<H3><A NAME="SS_5_4">5.4. Does SCons support something like VPATH in make?</A></H3>
<P>
Yes.  SCons supports a Repository feature and -Y option that
provide very similar functionality to VPATH, although without
some inconsistencies that make VPATH somewhat difficult to use.
These features are directly modeled on (read: stolen from)
the corresponding features in the Cons tool.
</P>


<H2><A NAME="S_6">Subject: 6. SCons History and Background</A></H2>

<H3><A NAME="SS_6_1">6.1. Who wrote SCons?</A></H3>
<P>
SCons was written by Steven Knight
and the original band of developers:
Chad Austin, Charles Crain, Steve Leblanc, and Anthony Roach.
</P>

<H3><A NAME="SS_6_2">6.2. Is SCons the same as Cons?</A></H3>
<P>
No, SCons and Cons are not the same program,
although their architectures are very closely related.
The most obvious difference is that SCons is
implemented in Python and uses Python scripts as its
configuration files, while Cons is implemented in Perl
and uses Perl scripts...
</P>
<P>
SCons is essentially a re-design of the Cons architecture
(by one of the principal Cons implementors)
to take advantage of Python's ease of use,
and to add a number of improvements and enhancements
to the architecture
based on several years of experience working with Cons.
</P>
<P>
Information about the classic Cons tool is available at:
</P>
<PRE>
        <A HREF="http://www.dsmit.com/cons/">http://www.dsmit.com/cons/</A>
      </PRE>

<H3><A NAME="SS_6_3">6.3. So what can SCons do that Cons can't?</A></H3>
<P>
Although SCons was not started to be the anti-Cons,
there are a number of features designed into SCons that
are not present in the Cons architecture:
</P>
<P>
SCons is easier to extend for new file types.  In Cons, these
methods are hard-coded inside the script, and to create a
new Builder or Scanner, you need to write some Perl for an
undocumented internal interface.  In SCons, there are factory
methods that you call to create new Builders and Scanners.
</P>
<P>
SCons is more modular.  Cons is pretty monolithic.  SCons is
designed from the ground up in separate modules that can be
imported or not depending on your needs.
</P>
<P>
The SCons build engine (dependency management) is separate from
the wrapper "scons" script.  Consequently, you can use the build
engine in any other piece of Python software.  For exmple, you
could even theoretically wrap it in another interface that would
read up Makefiles (a la Gary Holt's make++ Perl script).
</P>
<P>
SCons dependencies can be between arbitrary objects, not just
files.  Dependencies are actually managed in an abstract "Node"
base class, and specific subclasses (can) exist for files,
database fields, lines within a file, etc.  So you will be able to
use SCons to update a file because a certain web page changed, or
a value changed in a database, for example.
</P>
<P>
SCons has good parallel build (-j) support.  Cons' recursive
dependency descent makes it difficult to restructure for good
parallel build support.  SCons was designed from the ground up
with a multithreaded tasking engine (courtesy Anthony Roach)
that will keep N jobs going simultaneously, modulo waiting for
dependent files to finish building.
</P>

<H3><A NAME="SS_6_4">6.4. Should I use Cons or SCons for my project?</A></H3>
<P>
Well, this <i>is</i> the SCons FAQ, so of course we'll recommend
that you use SCons.  That having been said...
</P>
<P>
Unfortunately, Cons classic is essentially a dead project at this
point.  The last release was more than two years ago (May 2001)
and no one is actively working on it.  This is really too bad,
because Cons is still a very useful tool, and could continue to
help people solve build problems if it got some more development.
</P>
<P>
In contrast, SCons has a thriving development and user community,
and we're releasing new functionality and fixes approximately
once a month.  SCons also has a virtual superset of Cons classic
functionality, the only things really missing are some minor
debugging capabilities that don't affect basic software builds.
</P>
<P>
So at this point, probably the only reason to prefer Cons over
SCons is if you're a die-hard Perl fan who <i>really</i> can't
stomach using Python for your software build configuration
scripts, and the functionality you need from Cons works well
enough that you don't need new features or bug fixes, or you can
get by with fixing your own bugs.  If that's your situation and
Cons is a better fit for you, then more power to you.  Maybe
you could even help get Cons kick-started again...
</P>

<H3><A NAME="SS_6_5">6.5. Is SCons the same as the ScCons design from the Software Carpentry competition?</A></H3>
<P>
Yes.  Same design, same developer, same goals,
essentially the same tool.
</P>
<P>
SCons, however, is an independent project,
and no longer directly associated with Software Carpentry.
Hence, we dropped the middle 'c' to differentiate it slightly,
and to make it a tiny bit easier to type.
</P>
<P>
Even though SCons is being developed independently,
the goal is for SCons to be a flexible enough tool
that it would fit in with any future tools that
the Software Carpentry project may produce.
</P>
<P>
Note that, at last report,
the Software Carpentry project renamed their tools
with the prefix "qm"--the build tool being "qmbuild"--so
there shouldn't be any confusion
between SCons and any indepent build tool that
Software Carpentry may eventually produce.
</P>
<P>
Information about Software Carpentry is available at:
</P>
<PRE>
	<A HREF="http://software-carpentry.codesourcery.com/">http://software-carpentry.codesourcery.com/</A>
      </PRE>


</div> <!-- End bodycontent -->
<?
	make_bottom();
?>
