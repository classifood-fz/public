function ajax(url, barcode, success_callback) {
    jQuery.ajax({
        type: 'POST',
        url: url,
        dataType: 'json',
        headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
        data: { 'barcode': barcode },
        success: function(returned_json, status, jqxhr) {
            success_callback(returned_json);
        }
    });
}

function add_to_shopping_list(barcode, success_callback) {
    ajax('/add_to_shopping_list', barcode, success_callback);
}

function remove_from_shopping_list(barcode, success_callback) {
    ajax('/remove_from_shopping_list', barcode, success_callback);
}

function add_to_pantry(barcode, success_callback) {
    ajax('/add_to_pantry', barcode, success_callback);
}

function remove_from_pantry(barcode, success_callback) {
    ajax('/remove_from_pantry', barcode, success_callback);
}
