/*
  This files contains 6 functions for adding and removing nutrients, allergens,
  and additives via AJAX.
*/

function add_nutrient(nutrient, dom_id) {
    nutrient = jQuery.trim(nutrient);

    // If input is not empty, call ajax
    if (nutrient == '') {
        jQuery('#add_nutrient_message').text('Please enter a nutrient.').show();
    }
    else {
        jQuery('#new_nutrient').hide();
        jQuery('#add_nutrient').hide();
        jQuery('#add_nutrient_message').html('<span style="color:#000000;">Please wait...</span>').show();
        jQuery.ajax({
	    type: 'POST',
            url: '/add_nutrient',
            dataType: 'json',
            headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
            data: { 'nutrient': nutrient }
        }).done(function(returned_json, status, jqxhr) {
            // If ajax was successful, check returned json for result
            // Make necessary effects on the page
            jQuery('#new_nutrient').show();
            jQuery('#add_nutrient').show();

            if (returned_json['result'] == 'success') {
                jQuery('#nutrients').append('<div id="%s" class="list_item">%s<a onclick="remove_nutrient(\'%s\', \'%s\');"> <span class="subtract"></span></a></div>'.replace2('%s', [dom_id, nutrient, nutrient, dom_id]));
                jQuery('#new_nutrient').val('');
                jQuery('#add_nutrient_message').hide();
                jQuery('#no_nutrients').hide();
                nutrient_count++;
            }
            else if (returned_json['result'] == 'not found') {
                jQuery('#add_nutrient_message').text('This is not on our list of nutrients.').show();
            }
            else if (returned_json['result'] == 'exists') {
                jQuery('#add_nutrient_message').text('This nutrient is on your list.').show();
            }
            else {
                jQuery('#add_nutrient_message').text('An error occurred. Please try again later.').show();
            }
        }).fail(function(jqxhr, status, error) {
            // If ajax failed, show error message
            jQuery('#add_nutrient_message').text('An error occurred. Please try again later.').show();
        });
    }
}

function remove_nutrient(nutrient, dom_id) {
    nutrient = jQuery.trim(nutrient);

    // If input is not empty, call ajax
    if (nutrient == '') {
        jQuery('#add_nutrient_message').text('Please enter a nutrient.').show();
    }
    else {
        jQuery('#new_nutrient').hide();
        jQuery('#add_nutrient').hide();
        jQuery('#add_nutrient_message').html('<span style="color:#000000;">Please wait...</span>').show();
        jQuery.ajax({
	    type: 'POST',
            url: '/remove_nutrient',
            dataType: 'json',
            headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
            data: { 'nutrient': nutrient }
        }).done(function(returned_json, status, jqxhr) {
            // If ajax was successful, check returned json for result
            // Make necessary effects on the page
            jQuery('#new_nutrient').show();
            jQuery('#add_nutrient').show();

            if (returned_json['result'] == 'success') {
                jQuery('#'+dom_id).hide();
                jQuery('#add_nutrient_message').hide();
            }
            else {
                jQuery('#add_nutrient_message').text('An error occurred. Please try again later.').show();
            }
        }).fail(function(jqxhr, status, error) {
            // If ajax failed, show error message
            jQuery('#add_nutrient_message').text('An error occurred. Please try again later.').show();
        });
    }
}

function add_allergen(allergen, dom_id) {
    allergen = jQuery.trim(allergen);

    // If input is not empty, call ajax
    if (allergen == '') {
        jQuery('#add_allergen_message').text('Please enter an allergen.').show();
    }
    else {
        jQuery('#new_allergen').hide();
        jQuery('#add_allergen').hide();
        jQuery('#add_allergen_message').html('<span style="color:#000000;">Please wait...</span>').show();
        jQuery.ajax({
	    type: 'POST',
            url: '/add_allergen',
            dataType: 'json',
            headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
            data: { 'allergen': allergen }
        }).done(function(returned_json, status, jqxhr) {
            // If ajax was successful, check returned json for result
            // Make necessary effects on the page
            jQuery('#new_allergen').show();
            jQuery('#add_allergen').show();

            if (returned_json['result'] == 'success') {
                jQuery('#allergens').append('<div id="%s" class="list_item">%s<a onclick="remove_allergen(\'%s\', \'%s\');"> <span class="subtract"></span></a></div>'.replace2('%s', [dom_id, allergen, allergen, dom_id]));
                jQuery('#new_allergen').val('');
                jQuery('#add_allergen_message').hide();
                jQuery('#no_allergens').hide();
                allergen_count++;
            }
            else if (returned_json['result'] == 'not found') {
                jQuery('#add_allergen_message').text('This is not on our list of allergens.').show();
            }
            else if (returned_json['result'] == 'exists') {
                jQuery('#add_allergen_message').text('This allergen is on your list.').show();
            }
            else {
                jQuery('#add_allergen_message').text('An error occurred. Please try again later.').show();
            }
        }).fail(function(jqxhr, status, error) {
            // If ajax failed, show error message
            jQuery('#add_allergen_message').text('An error occurred. Please try again later.').show();
        });
    }
}

function remove_allergen(allergen, dom_id) {
    allergen = jQuery.trim(allergen);

    // If input is not empty, call ajax
    if (allergen == '') {
        jQuery('#add_allergen_message').text('Please enter an allergen.').show();
    }
    else {
        jQuery('#new_allergen').hide();
        jQuery('#add_allergen').hide();
        jQuery('#add_allergen_message').html('<span style="color:#000000;">Please wait...</span>').show();
        jQuery.ajax({
            type: 'POST',
            url: '/remove_allergen',
            dataType: 'json',
            headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
            data: { 'allergen': allergen }
        }).done(function(returned_json, status, jqxhr) {
            // If ajax was successful, check returned json for result
            // Make necessary effects on the page
            jQuery('#new_allergen').show();
            jQuery('#add_allergen').show();

            if (returned_json['result'] == 'success') {
                jQuery('#'+dom_id).hide();
                jQuery('#add_allergen_message').hide();
            }
            else {
                jQuery('#add_allergen_message').text('An error occurred. Please try again later.').show();
            }
        }).fail(function(jqxhr, status, error) {
            // If ajax failed, show error message
            jQuery('#add_allergen_message').text('An error occurred. Please try again later.').show();
        });
    }
}

function add_additive(additive, dom_id) {
    additive = jQuery.trim(additive);

    // If input is not empty, call ajax
    if (additive == '') {
        jQuery('#add_additive_message').text('Please enter an additive.').show();
    }
    else {
        jQuery('#new_additive').hide();
        jQuery('#add_additive').hide();
        jQuery('#add_additive_message').html('<span style="color:#000000;">Please wait...</span>').show();
        jQuery.ajax({
	    type: 'POST',
            url: '/add_additive',
            dataType: 'json',
            headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
            data: { 'additive': additive }
        }).done(function(returned_json, status, jqxhr) {
            // If ajax was successful, check returned json for result
            // Make necessary effects on the page
            jQuery('#new_additive').show();
            jQuery('#add_additive').show();

            if (returned_json['result'] == 'success') {
                jQuery('#additives').append('<div id="%s" class="list_item">%s<a onclick="remove_additive(\'%s\', \'%s\');"> <span class="subtract"></span></a></div>'.replace2('%s', [dom_id, additive, additive, dom_id]));
                jQuery('#new_additive').val('');
                jQuery('#add_additive_message').hide();
                jQuery('#no_additives').hide();
                additive_count++;
            }
            else if (returned_json['result'] == 'not found') {
                jQuery('#add_additive_message').text('This is not on our list of additives.').show();
            }
            else if (returned_json['result'] == 'exists') {
                jQuery('#add_additive_message').text('This additive is on your list.').show();
            }
            else {
                jQuery('#add_additive_message').text('An error occurred. Please try again later.').show();
            }
        }).fail(function(jqxhr, status, error) {
            // If ajax failed, show error message
            jQuery('#add_additive_message').text('An error occurred. Please try again later.').show();
        });
    }
}

function remove_additive(additive, dom_id) {
    additive = jQuery.trim(additive);

    // If input is not empty, call ajax
    if (additive == '') {
        jQuery('#add_additive_message').text('Please enter an additive.').show();
    }
    else {
        jQuery('#new_additive').hide();
        jQuery('#add_additive').hide();
        jQuery('#add_additive_message').html('<span style="color:#000000;">Please wait...</span>').show();
        jQuery.ajax({
	    type: 'POST',
            url: '/remove_additive',
            dataType: 'json',
            headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
            data: { 'additive': additive }
        }).done(function(returned_json, status, jqxhr) {
            // If ajax was successful, check returned json for result
            // Make necessary effects on the page
            jQuery('#new_additive').show();
            jQuery('#add_additive').show();

            if (returned_json['result'] == 'success') {
                jQuery('#'+dom_id).hide();
                jQuery('#add_additive_message').hide();
            }
            else {
                jQuery('#add_additive_message').text('An error occurred. Please try again later.').show();
            }
        }).fail(function(jqxhr, status, error) {
            // If ajax failed, show error message
            jQuery('#add_additive_message').text('An error occurred. Please try again later.').show();
        });
    }
}
