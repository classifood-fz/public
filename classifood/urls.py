from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^$', 'classifood.views.index'),
    url(r'^about$', 'classifood.views.about'),
    url(r'^add_additive$', 'classifood.views.add_additive'),
    url(r'^add_allergen$', 'classifood.views.add_allergen'),
    url(r'^add_nutrient$', 'classifood.views.add_nutrient'),
    url(r'^add_ingredient$', 'classifood.views.add_ingredient'),
    url(r'^add_to_pantry$', 'classifood.views.add_to_pantry'),
    url(r'^add_to_shopping_list$', 'classifood.views.add_to_shopping_list'),
    url(r'^authenticate$', 'classifood.views.authenticate'),
    url(r'^contact$', 'classifood.views.contact'),
    url(r'^privacy_policy$', 'classifood.views.privacy_policy'),
    url(r'^remove_additive$', 'classifood.views.remove_additive'),
    url(r'^remove_allergen$', 'classifood.views.remove_allergen'),
    url(r'^remove_nutrient$', 'classifood.views.remove_nutrient'),
    url(r'^remove_ingredient$', 'classifood.views.remove_ingredient'),
    url(r'^remove_from_pantry$', 'classifood.views.remove_from_pantry'),
    url(r'^remove_from_shopping_list$', 'classifood.views.remove_from_shopping_list'),
    url(r'^robots.txt$', 'classifood.views.robots'),
    url(r'^search$', 'classifood.views.search'),
    url(r'^search_ingredients$', 'classifood.views.search_ingredients'),
    url(r'^send_contact_message$', 'classifood.views.send_contact_message'),
    url(r'^signin$', 'classifood.views.signin'),
    url(r'^sitemap$', 'classifood.views.sitemap'),
    url(r'^terms_of_service$', 'classifood.views.terms_of_service'),
    url(r'^user/delete_pantry$', 'classifood.views.delete_pantry'),
    url(r'^user/delete_shopping_list$', 'classifood.views.delete_shopping_list'),
    url(r'^user/pantry$', 'classifood.views.user_pantry'),
    url(r'^user/profile$', 'classifood.views.user_profile'),
    url(r'^user/shopping_list$', 'classifood.views.user_shopping_list')
)

handler404 = 'classifood.views.err404'
handler500 = 'classifood.views.err500'
