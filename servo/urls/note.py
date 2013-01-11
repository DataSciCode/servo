from django.conf.urls import patterns, url

urlpatterns = patterns('servo.views.note',
    url(r'^templates/$', 'templates'),
    url(r'^templates/(\d+)/$', 'templates'),
	url(r'^note/(?P<parent>\d+)/reply/$', 'edit'),
    url(r'^note/(?P<note_id>\d+)/edit/$', 'edit', {'kind': 'problem'}),
    url(r'^note/(?P<note_id>\d+)/remove/$', 'remove'),
    url(r'^mailto/(?P<recipient>.+)/$', 'edit'),
    url(r'^smsto/(?P<recipient>\d+)/$', 'edit'),
    url(r'^message/(?P<recipient>.+)/order/(?P<order_id>\d+)/$', 'edit', {'kind': 'message'}),
)
