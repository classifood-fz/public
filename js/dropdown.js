jQuery(document).ready(function() {
    // Show and hide drop-down menu on hover
    jQuery('#dropdown').hover(
        function() {
            jQuery('.dropdown').css('display', 'inline-block');
        },
        function() {
            jQuery('.dropdown').css('display', 'none');
        }
    );
});
