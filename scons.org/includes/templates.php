<?
// We always want this.
error_reporting(E_ALL);

function make_top($title, $page)
{
	$currentrelease = "0.96.1";
	$downloadpage = "http://prdownloads.sourceforge.net/scons";
	$currentpage = ' id="currentpage"';
	$listpage = "http://scons.tigris.org/servlets/SummarizeList";
	?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" >
<head>
	<meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />
	<meta name="robots" content="all" />
	<title>SCons: <?echo $title?></title>

	<!-- fixes Flash of Unstyled Content. http://www.bluerobot.com/web/css/fouc.asp -->
	<script type="text/javascript"></script>
	
	<style type="text/css" title="currentStyle">
		@import "css/scons.css";
	</style>
	<link rel="Shortcut Icon" type="image/x-icon" href="favicon.ico" />
</head>

<body>

<div id="main">

<div id="banner">

&nbsp;
&nbsp;
&nbsp;
&nbsp;
&nbsp;

</div> 

<div id="menu">
<ul class="menuitems">
<li><a href="."<?if(!strcmp($page,"home"))echo $currentpage;?>>Home</a></li>
<li><a href="/wiki/index.html">Wiki</a></li>
<li><a href="download.php"<?if(!strcmp($page,"download"))echo $currentpage;?>>Download</a><br />
	<ul class="submenuitems">
	<li> <a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>.tar.gz">Tarball</a> </li>
	<li> <a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>.zip">Zip</a> </li>
	<li> <a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>.win32.exe">Windows</a> </li>
	<li> <a href="<?echo $downloadpage;?>/scons-<?echo $currentrelease;?>-1.noarch.rpm">Redhat</a> </li>
	<li> <a href="<?echo $downloadpage;?>/scons_<?echo $currentrelease;?>-0.1_all.deb">Debian</a> </li>
	<li> <a href="<?echo $downloadpage;?>/scons-src-<?echo $currentrelease;?>.tar.gz">Source</a> </li>
	</ul>
</li>
<li> <a href="documentation.php"<?if(!strcmp($page,"docs"))echo $currentpage;?>>Documentation</a><br />
	<ul class="submenuitems">
	<li><a href="/doc/HTML/scons-user/book1.html">User's Guide (<?echo $currentrelease;?>)</a></li>
	<li><a href="/doc/HTML/scons-man.html">Man page (<?echo $currentrelease;?>)</a></li>
	<li><a href="/docversions.php">Other releases</a></li>
	</ul>
</li>
<li><a href="faq.php"<?if(!strcmp($page,"faq"))echo $currentpage;?>>FAQ</a></li>
<li><a href="dev.php"<?if(!strcmp($page,"dev"))echo $currentpage;?>>Development</a></li>
<li><a href="lists.php"<?if(!strcmp($page,"lists"))echo $currentpage;?>>Mailing Lists</a><br />
	<small>Archives:</small>
	<ul class="submenuitems">
	<li><a href="<?echo $listpage;?>?listName=announce">announce</a></li>
	<li><a href="<?echo $listpage;?>?listName=dev">dev</a></li>
	<li><a href="<?echo $listpage;?>?listName=users">users</a></li>
	</ul>

</li>
<li><a href="http://scons.tigris.org/">Tigris.org</a><br />
	<ul class="submenuitems">
	<li><a href="http://scons.tigris.org/bug-submission.html">Report bugs</a></li>
	<li><a href="http://scons.tigris.org/patch-submission.html">Submit patches</a></li>
	<li><a href="http://scons.tigris.org/feature-request.html">Feature requests</a></li>
	</ul>
	</li>
<li><a href="links.php"<?if(!strcmp($page,"links"))echo $currentpage;?>>Links</a></li>
<li><a href="contact.php"<?if(!strcmp($page,"contact"))echo $currentpage;?>>Contact</a></li>
<li><a href="refer.php"<?if(!strcmp($page,"references"))echo $currentpage;?>>References</a></li>
<li><a href="donate.php"<?if(!strcmp($page,"donate"))echo $currentpage;?>>Donate</a></li>
</ul>

<div id="osrating">
<form method="post" action="http://osdir.com/modules.php?op=modload&amp;name=Downloads&amp;file=index">
	Rate SCons on <a href="http://osdir.com/">OSDir.com</a><br />
	<select name="rating">
		<option selected> </option><br>
		<option value="10">10</option><br>
		<option value="9">9</option><br>
		<option value="8">8</option><br>
		<option value="7">7</option><br>
		<option value="6">6</option><br>
		<option value="5">5</option><br>
		<option value="4">4</option><br>
		<option value="3">3</option><br>
		<option value="2">2</option><br>
		<option value="1">1</option><br>
	</select>
	<input type="hidden" name="ratinglid" value="327" />
	<input type="hidden" name="ratinguser" value="outside" />
	<input type="hidden" name="req" value="addrating" />
	<input type="submit" value="Vote!" />
</form>
</div>

<div id="menu">
<ul class="menuitems">
<li>Hosting provided by:  <a href="http://www.pair.com/">pair.com</a></li>
</ul>
</div>

</div> <!-- menu -->
<?

} // End make_top

function make_bottom()
{
	?>
<div id="footer">
&copy; 2004 <a href="http://www.scons.org">The SCons Foundation</a>
</div>
</div> <!-- End main -->
</body>
</html>
	<?
}
?>
