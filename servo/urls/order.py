from django.conf.urls import patterns, url

urlpatterns = patterns('servo.views.order',
	url(r'^$', 'index'),
	url(r'^create/$', 'create'),
	url(r'^order/(\d+)/$', 'edit'),
	url(r'^order/(\d+)/remove/$', 'remove'),
	url(r'^order/(\d+)/remove/$', 'remove'),
	url(r'^order/(\d+)/follow/$', 'follow'),
	url(r'^order/(\d+)/events/$', 'events'),
	url(r'^order/(\d+)/parts/(\d+)/$', 'parts'),
	url(r'^order/(\d+)/add_device/(\d+)/$', 'add_device'),
	url(r'^order/(\d+)/remove_device/(\d+)/$', 'remove_device'),
	url(r'^order/(?P<order_id>\d+)/add_device/(?P<sn>\w+)/$', 'add_device'),
	url(r'^order/(\d+)/products/$', 'products'),
	url(r'^order/(\d+)/close/$', 'close'),
	url(r'^order/(\d+)/tags/(\d+)/toggle/$', 'toggle_tag'),
	url(r'^order/(\d+)/update/$', 'update'),
	url(r'^order/(\d+)/dispatch/$', 'dispatch'),
	url(r'^order/(\d+)/gsx_repair/$', 'create_gsx_repair'),
	url(r'^order/(\d+)/products/reserve/$', 'reserve_products'),
	url(r'^create/product/(?P<product_id>\d+)/$', 'create'),
	url(r'^create/note/(?P<note_id>\d+)/$', 'create'),
	url(r'^create/sn/(?P<sn>\w+)/$', 'create'),
	url(r'^state/(?P<state>\d+)/$', 'index'),
	url(r'^color/(?P<color>\w+)/$', 'index'),
	url(r'^queue/(?P<queue>\d+)/$', 'index'),
	url(r'^tag/(?P<tag>\d+)/$', 'index'),
	url(r'^user/(?P<user>\d+)/$', 'index'),
	url(r'^spec/(?P<spec>\d+)/$', 'index'),
	url(r'^status/(?P<status>\w+)/$', 'index'),
	url(r'^date/(?P<date>[\d\-]+)/$', 'index'),
	url(r'^customer/(?P<customer>\d+)/$', 'index'),
	url(r'^device/(?P<device>\d+)/$', 'index'),
	url(r'^order/(?P<order_id>\d+)/print/?(?P<kind>\w+)?/$', 'put_on_paper'),
	url(r'^order/(?P<order_id>\d+)/products/(?P<item_id>\d+)/(?P<action>\w+)/$', 'products'),
)
