/*
  This files contains functions for adding and removing nutrients, allergens,
  and additives via AJAX.
*/

function ajax(url, data, success_callback, error_callback) {
    jQuery.ajax({
        type: 'POST',
        url: url,
        dataType: 'json',
        headers: { 'X-CSRFToken': jQuery('input[name="csrfmiddlewaretoken"]').val() },
        data: data,
        success: function(returned_json, status, jqxhr) {
            success_callback(returned_json);
        },
        error: function(jqxhr, status, error) {
            error_callback();
        }
    });
}

function add_nutrient(nutrient, success_callback, error_callback) {
    ajax('/add_nutrient', {'nutrient': nutrient}, success_callback, error_callback);
}

function remove_nutrient(nutrient, success_callback, error_callback) {
    ajax('/remove_nutrient', {'nutrient': nutrient}, success_callback, error_callback);
}

function add_allergen(allergen, success_callback, error_callback) {
    ajax('/add_allergen', {'allergen': allergen}, success_callback, error_callback);
}

function remove_allergen(allergen, success_callback, error_callback) {
    ajax('/remove_allergen', {'allergen': allergen}, success_callback, error_callback);
}

function add_additive(additive, success_callback, error_callback) {
    ajax('/add_additive', {'additive': additive}, success_callback, error_callback);
}

function remove_additive(additive, success_callback, error_callback) {
    ajax('/remove_additive', {'additive': additive}, success_callback, error_callback);
}

function add_ingredient(ingredient_id, ingredient_name, success_callback, error_callback) {
    ajax('/add_ingredient', {'ingredient_id': ingredient_id, 'ingredient_name': ingredient_name}, success_callback, error_callback);
}

function remove_ingredient(ingredient_id, ingredient_name, success_callback, error_callback) {
    ajax('/remove_ingredient', {'ingredient_id': ingredient_id, 'ingredient_name': ingredient_name}, success_callback, error_callback);
}

function search_ingredients(ingredient, start, success_callback, error_callback) {
    jQuery.ajax({
        type: 'GET',
        url: '/search_ingredients',
        dataType: 'json',
        data: {'ingredient': ingredient, 'start': start},
        success: function(returned_json, status, jqxhr) {
            success_callback(returned_json);
        },
        error: function(jqxhr, status, error) {
            error_callback();
        }
    });
}
