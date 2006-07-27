<?
	include "includes/templates.php";

	error_reporting(E_ALL);

	make_top("Download", "download");

	$currentrelease = "0.96.1";
	$downloadpage = "http://prdownloads.sourceforge.net/scons";
	$listpage = "http://scons.tigris.org/servlets/SummarizeList";
?>

<div id="bodycontent">
<h2 class="pagetitle"> Download </h2>

<p>
<strong>NOTE:</strong>
A 0.96.92 testing pre-release is available from our
<a href="http://sourceforge.net/project/showfiles.php?group_id=30337">download page</a>
at SourceForge.
This is intended as the last testing pre-release before
the .sconsign file changes significantly
to (among other things)
handle builds consistently
when only a subset of a tree's
dependency graph is used,
as well as
supporting more flexible detection of file changes.
This pre-release
also makes available more features and bug fixes
that have accumulated since 0.96.91.
</p>

<p>
<strong>The current official release</strong> of <span class="sconslogo">SCons</span> is
<strong><?echo $currentrelease;?></strong> [<a href="CHANGES.txt">ChangeLog</a>]. This is a beta release, which means that
we might still tweak corners of the interface before release 1.0, so you could,
conceivably, have to change a configuration file on a successive release. 
</p>

<p>
We make <span class="sconslogo">SCons</span> available in three distinct packages, for different purposes.
</p>

<h3> scons Packages </h3>
<p>
The <span class="sconslogo">scons</span> packages are the basic packages for installing <span
class="sconslogo">SCons</span> on your system and using it or experimenting
with it. You only need one of the following packages if you just want to try
out <span class="sconslogo">SCons</span>:
</p>

<a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>.tar.gz">scons-<?echo $currentrelease;?>.tar.gz</a>
<div class="downloaddescription">
Gzipped tar file,
installable using
the Python
<code>setup.py</code> script.<br>
</div>

<a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>.zip">scons-<?echo $currentrelease;?>.zip</a> 
<div class="downloaddescription">
Zip file,
installable using
the Python
<code>setup.py</code> script.
</div>
<a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>-1.noarch.rpm">scons-<?echo $currentrelease;?>-1.noarch.rpm</a> 
<div class="downloaddescription"> Redhat RPM </div>
<a href="<?echo $downloadpage;?>/scons_<?echo $currentrelease;?>-0.1_all.deb">scons_<?echo $currentrelease;?>-0.1_all.deb</a> 
<div class="downloaddescription"> Debian package </div>
<a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>.win32.exe">scons-<?echo $currentrelease;?>.win32.exe</a>
<div class="downloaddescription"> Windows installer </div>
<a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>-1.src.rpm">scons-<?echo $currentrelease;?>-1.src.rpm</a> 
<div class="downloaddescription">
Source RPM,
containing the <code>.tar.gz</code> and <code>.spec</code>
files for building your own RPM.
</div>


<h3> scons-local Packages </h3>
<p>
The <span class="sconslogo">scons-local</span> packages contain versions of <span class="sconslogo">SCons</span>that you can execute standalone, out of a local directory. They are intended to be dropped in to and shipped with packages of other software that you want to build with <span class="sconslogo">SCons</span>, but for which you don't want to have to require that your users install <span class="sconslogo">SCons</span>:
</p>

<a href="<?echo $downloadpage;?>/scons-local-<?echo $currentrelease;?>.tar.gz">scons-local-<?echo $currentrelease;?>.tar.gz</a> 
<div class="downloaddescription">
Tarball of a locally-executable package, suitable for dropping in and shipping with other software. 
</div>
<a href="<?echo $downloadpage;?>/scons-local-<?echo $currentrelease;?>.zip">scons-local-<?echo $currentrelease;?>.zip</a> 
<div class="downloaddescription">
Zip of a locally-executable package, suitable for dropping in and shipping with other software.
</div>

<h3> scons-src Packages </h3>
<p>
The <span class="sconslogo">scons-src</span> packages contain the complete source tree, including everything we use to package <span class="sconslogo">SCons</span> and all of the regression tests. You might want one of these packages if you have concerns about whether <span class="sconslogo">SCons</span> is working correctly on your operating system and wanted to run the regression tests, or if you want to contribute to <span class="sconslogo">SCons</span> development:
</p>

<a href="<?echo $downloadpage;?>/scons-src-<?echo $currentrelease;?>.tar.gz">scons-src-<?echo $currentrelease;?>.tar.gz</a>
<div class="downloaddescription">
Tarball of the checked-in source tree, including all of the regression tests.
</div>
<a href="<?echo $downloadpage;?>/scons-src-<?echo $currentrelease;?>.zip">scons-src-<?echo $currentrelease;?>.zip</a>
<div class="downloaddescription">
Zip of the checked-in source tree, including all of the regression
tests.</div>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>
