from django.conf.urls import patterns, url

urlpatterns = patterns('admin.views',
    url(r'^$', 'settings'),
    url(r'^files/$', 'documents'),
    url(r'^statuses/$', 'statuses'),
    url(r'^statuses/(\d+)/save/$', 'save_status'),
    url(r'^statuses/(\d+)/edit/$', 'status_form'),
    url(r'^queues/$', 'queues'),
    url(r'^status/new/$', 'status_form'),
    url(r'^settings/$', 'settings'),

    url(r'^users/$', 'users'),
    url(r'^users/new/$', 'edit_user'),
    url(r'^users/(\d+)/edit/$', 'edit_user'),

    url(r'^groups/$', 'groups'),
    url(r'^groups/new/$', 'edit_group'),
    url(r'^groups/(\d+)/edit/$', 'edit_group'),

    url(r'^tags/$', 'tags'),
    url(r'^tags/new/$', 'edit_tag'),
    url(r'^tags/(\w+)/save/$', 'edit_tag'),

    url(r'^fields/$', 'fields'),
    url(r'^fields/(?P<field_id>\w+)/save/$', 'edit_field'),
    url(r'^fields/(?P<field_id>\w+)/$', 'edit_field'),
    url(r'^fields/(\d+)/remove/$', 'remove_field'),
    
    url(r'^templates/$', 'templates'),
    url(r'^templates/new/$', 'edit_template'),
    url(r'^template/save/$', 'edit_template'),
    url(r'^templates/(\d+)/edit/$', 'edit_template'),
    url(r'^templates/(\d+)/delete/$', 'remove_template'),

    url(r'^queues/new/$', 'edit_queue'),
    url(r'^queue/save/$', 'save_queue'),
    url(r'^queue/remove$', 'remove_queue'),
    url(r'^queues/(\d+)/edit/$', 'edit_queue'),
    url(r'^queue/(\d+)/remove/$', 'remove_queue'),

    url(r'^gsx/accounts/$', 'gsx_accounts'),
    url(r'^gsx/accounts/new/$', 'gsx_form'),
    url(r'^gsx/accounts/(\d+)/$', 'gsx_form'),
    url(r'^gsx/accounts/(\d+)?/delete/$', 'gsx_remove'),
    url(r'^gsx/accounts/(\d+)/save/$', 'gsx_save'),

    url(r'^locations/$', 'locations'),
    url(r'^locations/new/$', 'edit_location'),
    url(r'^locations/(\d+)/edit/$', 'edit_location'),
    url(r'^location/save$', 'edit_location'),

    url(r'^products/groups/$', 'product_groups'),
    url(r'^products/groups/new/$', 'edit_product_group'),
    url(r'^products/groups/(\d+)/$', 'edit_product_group'),
    url(r'^products/groups/(\d+)/save/$', 'edit_product_group'),
)
