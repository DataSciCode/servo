from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'servo.views.order.index'),

    url(r'^accounts/', include('servo.urls.account')),

    url(r'^orders/', include('servo.urls.order')),
    url(r'^customers/', include('servo.urls.customer')),
    url(r'^devices/', include('servo.urls.device')),
    url(r'^admin/', include('servo.urls.admin')),
    
    url(r'^notes/', include('servo.urls.note')),
    url(r'^products/', include('servo.urls.product')),
    url(r'^calendars/', include('servo.urls.calendar')),
    url(r'^messages/new/$', 'servo.views.note.edit', {'kind': 'message'}),


    url(r'^document/save$', 'servo.views.documents.save'),
    url(r'^documents/(\d+)/edit/$', 'servo.views.documents.edit'),
    url(r'^documents/(\d+)/view/$', 'servo.views.documents.view'),
    url(r'^documents/(\d+)/remove/$', 'servo.views.documents.remove'),
    url(r'^documents/remove$', 'servo.views.documents.remove'),
    url(r'^document/(\w+)/barcode/$', 'servo.views.documents.barcode'),
    url(r'^documents/new$', 'servo.views.documents.create'),

    url(r'^search/$', 'servo.views.search.spotlight'),
    url(r'^search/gsx/(?P<what>\w+)/$', 'servo.views.search.gsx'),
    url(r'^search/(?P<what>\w+)/$', 'servo.views.search.spotlight'),

    url(r'^orders/(?P<order_id>\d+)/notes/new/$', 'servo.views.note.edit', {'kind': 'note'}),
    url(r'^orders/(?P<order_id>\d+)/issues/new/$', 'servo.views.note.edit', {'kind': 'problem'}),
    url(r'^orders/(?P<order_id>\d+)/messages/new/$', 'servo.views.note.edit', {'kind': 'message'}),
    url(r'^orders/(\d+)/notes/save/$', 'servo.views.note.save'),

)
