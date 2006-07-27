<?
	include "includes/templates.php";

	error_reporting(E_ALL);

	make_top("Donate", "donate");
?>

<div id="bodycontent">
<h2 class="pagetitle"> Donate </h2>

<p> Thank you for considering a donation to support <span
class="sconslogo">SCons</span> </p>

<p> None of us working on <span class="sconslogo">SCons</span> is doing it to
make a fortune, but we have been putting in a lot of time and more than a
little out-of-pocket cash to write and get out the word about a tool that we
hope is helping people build software more easily and effectively.  </p>

<p> If you'd care to make a cash donation to help support the costs of
developing and promoting <span class="sconslogo">SCons</span>, it would be
greatly appreciated.  The following button will take you to a PayPal page where
you can consider making a donation by credit card: </p>

<center>
<form action="https://www.paypal.com/cgi-bin/webscr" method="post">
<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="business" value="donate@scons.org">
<input type="hidden" name="no_note" value="1">
<input type="hidden" name="currency_code" value="USD">
<input type="hidden" name="tax" value="0">
<input type="image" src="https://www.paypal.com/images/x-click-but11.gif" border="0" name="submit" alt="Make a donation with PayPal - it's fast, free and secure!">
</form>
</center>

<p> (Don't worry, nothing will actually happen until you've had a chance check
out the page, satisfy yourself that it's legitimate, and actually submit the
necessary information to make a donation.) </p>

<p> We are also interested in donations of either hardware or software to help
with establishing a test bed that we could use to ensure that <span
class="sconslogo">SCons</span> interoperates with a wide variety of platforms
and tools--even old, outdated ones.  If you have an old, slow system that you
can't find anyone else to take, or an unused copy of an operating system,
compiler or other software tool, consider contacting us at

<a href="mailto:donate@scons.org">donate@scons.org</a> to see if we could use
it.  (If we can use what you have available, and have cash on hand, we'll
likely even pay the shipping costs.) </p>

<p> Note that <span class="sconslogo">SCons</span> is not a 501(c)(3)
charitable organization, so any donations of cash, hardware or software are not
legally tax-deductible in the United States.  If this really starts growing,
we'll likely try to organize in that fashion, but we're just not anywhere near
that big yet...  </p>

<p> Thanks again for consideration a donation.  </p>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>
