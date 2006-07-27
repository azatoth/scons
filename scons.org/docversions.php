<?
	include "includes/templates.php";
	include "includes/versions.php";

	error_reporting(E_ALL);

	make_top("Version-Specific SCons Documentation", "docs");

	$downloadpage = "http://prdownloads.sourceforge.net/scons";
	$listpage = "http://scons.tigris.org/servlets/SummarizeList";
?>

<div id="bodycontent">
<h2 class="pagetitle">Version-Specific SCons Documentation</h2>

<p>
The <span class="sconslogo">SCons</span> man page and
User's Guide are available in different formats for
most recent releases.
The current stable release of
<span class="sconslogo">SCons</span>
is <?echo $currentrelease;?>.
</p>

<h3> SCons man page </h3>
<p>
In general,
the man page is updated
whenever new functionality is added or something changes.
The man pages for various recent releases are
available in the following formats:
</p>

<div id="sconsdocversiontable">
<sconsversiontable>
  <sconsversionrow>
    <docformat>&nbsp;</docformat>
    <docformat>Single-<br>page<br>HTML</docformat>
    <docformat>PostScript</docformat>
    <docformat>Plain text</docformat>
  </sconsversionrow>
<?
    foreach ( $docversions as $inx => $ver) {
      echo "  <sconsversionrow>\n";
      echo "    <sconsversion>$ver</sconsversion>\n";
      echo "    <docversion><a href=\"doc/$ver/HTML/scons-man.html\">.html</a></docversion>\n";
      echo "    <docversion><a href=\"doc/$ver/PS/scons-man.ps\">.ps</a></docversion>\n";
      echo "    <docversion><a href=\"doc/$ver/TEXT/scons-man.txt\">.txt</a></docversion>\n";
      echo "  </sconsversionrow>\n";
    }
?>
</sconsversiontable>
</div>

<h3> SCons User's Guide </h3>

<p>
Unlike the man page,
the User's Guide is not updated in lock-step with the code,
so it tends to lag in its discussion of newer features.
Copies of the User's Guide for various recent releases are
available in the following formats:
</p>

<div id="sconsdocversiontable">
<sconsversiontable>
  <sconsversionrow>
    <docformat>&nbsp;</docformat>
    <docformat>Single-<br>page<br>HTML</docformat>
    <docformat>Multi-<br>page<br>HTML</docformat>
    <docformat>PDF</docformat>
    <docformat>PostScript</docformat>
    <docformat>Plain text</docformat>
  </sconsversionrow>
<?
    foreach ( $docversions as $inx => $ver) {
      echo "  <sconsversionrow>\n";
      echo "    <sconsversion>$ver</sconsversion>\n";
      echo "    <docversion><a href=\"doc/$ver/HTML/scons-user.html\">.html</a></docversion>\n";
      echo "    <docversion><a href=\"doc/$ver/HTML/scons-user/book1.html\">.html</a></docversion>\n";
      echo "    <docversion><a href=\"doc/$ver/PDF/scons-user.pdf\">.pdf</a></docversion>\n";
      echo "    <docversion><a href=\"doc/$ver/PS/scons-user.ps\">.ps</a></docversion>\n";
      echo "    <docversion><a href=\"doc/$ver/TEXT/scons-user.txt\">.txt</a></docversion>\n";
      echo "  </sconsversionrow>\n";
    }
?>
</sconsversiontable>
</div>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>
