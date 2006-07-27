<?
	include "includes/templates.php";

	error_reporting(E_ALL);

	make_top("News", "news");
?>

<div id="bodycontent">
<h2 class="pagetitle"> News </h2>

<?

include "news-raw.xhtml";

?>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>
