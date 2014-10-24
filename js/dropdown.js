jQuery(document).ready(function() {
    // Show and hide drop-down menu
    jQuery('#dropdown').click(function() {
        if (jQuery('.dropdown').css('display') == 'none') {
            jQuery('.dropdown').css('display', 'inline-block');
            jQuery(this).css('border', '1px solid #000000');
        } else {
            jQuery('.dropdown').css('display', 'none');
            jQuery(this).css('border', '0');
        }
    });
});
