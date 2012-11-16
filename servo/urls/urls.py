from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^$', 'orders.views.index'),

    url(r'^orders/', include('orders.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^customers/', include('customers.urls')),

    url(r'^notes/', include('notes.urls')),
    url(r'^products/', include('products.urls')),

    url(r'^messages/new/$', 'notes.views.edit', {'kind': 'message'}),

    url(r'^document/save$', 'servo.views.documents.save'),
    url(r'^documents/(\d+)/edit/$', 'servo.views.documents.edit'),
    url(r'^documents/(\d+)/view/$', 'servo.views.documents.view'),
    url(r'^documents/(\d+)/remove/$', 'servo.views.documents.remove'),
    url(r'^documents/remove$', 'servo.views.documents.remove'),
    url(r'^document/(\w+)/barcode/$', 'servo.views.documents.barcode'),
    url(r'^documents/new$', 'servo.views.documents.create'),

    url(r'^admin/user/save/$', 'servo.views.admin.save_user'),
    url(r'^admin/user/edit/(\w+)$', 'servo.views.admin.edit_user'),

    url(r'^search/$', 'servo.views.search.spotlight'),
    url(r'^search/gsx/(?P<what>\w+)/$', 'servo.views.search.gsx'),
    url(r'^search/(?P<what>\w+)/$', 'servo.views.search.spotlight'),

    url(r'^orders/(?P<order_id>\d+)/notes/new/$', 'notes.views.edit', {'kind': 'note'}),
    url(r'^orders/(?P<order_id>\d+)/issues/new/$', 'notes.views.edit', {'kind': 'problem'}),
    url(r'^orders/(?P<order_id>\d+)/messages/new/$', 'notes.views.edit', {'kind': 'message'}),
    url(r'^orders/(?P<order_id>\d+)/smsto/(?P<smsto>\w+)/$', 'notes.views.edit'),
    url(r'^orders/(?P<order_id>\d+)/mailto/(?P<mailto>.+)/$', 'notes.views.edit'),
    url(r'^orders/(\d+)/notes/save/$', 'notes.views.save'),

    url(r'^api/', include('servo.urls.api')),
    url(r'^admin/', include('servo.urls.admin')),

    url(r'^devices/', include('servo.urls.devices')),

)
