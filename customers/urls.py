from django.conf.urls import patterns, url

urlpatterns = patterns('customers.views',
    url(r'^$', 'index'),
    url(r'^(\d+)/$', 'view'),
    url(r'^new/$', 'edit'),
    url(r'^(\w+)/save/$', 'save'),
    url(r'^(?P<customer_id>\d+)/edit/$', 'edit'),
    url(r'^(?P<parent_id>\d+)/new/$', 'edit'),
    url(r'^(\d+)/delete/$', 'delete'),
    url(r'^(\d+)/view/$', 'view'),
    url(r'^(\d+)/move/$', 'move'),
    url(r'^(\d+)/move/(\d+)/$', 'move'),
    url(r'^index/tag/(?P<tag>\d+)/$', 'index'),
    url(r'^(\d+)/orders/new/$', 'create_order'),
    url(r'^(\d+)/orders/(\d+)/$', 'add_order'),
    url(r'^(?P<customer_id>\d+)/notes/new/$', 'notes'),
    url(r'^search/$', 'search'),
)
