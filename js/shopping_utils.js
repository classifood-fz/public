function add_to_shopping_list(barcode, callback) {
    jQuery.ajax({
        type: 'POST',
        url: '/add_to_shopping_list',
        dataType: 'json',
        headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
        data: { 'barcode': barcode },
        success: function(returned_json, status, jqxhr) {
            if ((returned_json['result'] == 'success' || returned_json['result'] == 'found') && typeof callback === 'function')
	        callback();
        }
    }).done();
}

function remove_from_shopping_list(barcode, callback) {
    jQuery.ajax({
        type: 'POST',
        url: '/remove_from_shopping_list',
        dataType: 'json',
        headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
        data: { 'barcode': barcode },
        success: function(returned_json, status, jqxhr) {
            if (returned_json['result'] == 'success' && typeof callback === 'function')
                callback();
        }
    });
}

function add_to_pantry(barcode, callback) {
    jQuery.ajax({
        type: 'POST',
        url: '/add_to_pantry',
        dataType: 'json',
        headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
        data: { 'barcode': barcode },
        success: function(returned_json, status, jqxhr) {
            if ((returned_json['result'] == 'success' || returned_json['result'] == 'found') && typeof callback === 'function')
	        callback();
        }
    });
}

function remove_from_pantry(barcode, callback) {
    jQuery.ajax({
        type: 'POST',
        url: '/remove_from_pantry',
        dataType: 'json',
        headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
        data: { 'barcode': barcode },
        success: function(returned_json, status, jqxhr) {
            if (returned_json['result'] == 'success' && typeof callback === 'function')
	        callback();
        }
    });
}
