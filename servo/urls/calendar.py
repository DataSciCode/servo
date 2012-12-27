from django.conf.urls import patterns, url

urlpatterns = patterns('servo.views.calendar',
	url(r'^$', 'index'),
	url(r'^save$', 'save'),
	url(r'^calendar/save_event$', 'save_event'),
	url(r'^create$', 'create'),
	url(r'^(\d+)/edit/$', 'edit'),
	url(r'^(\d+)/remove/$', 'remove'),
	url(r'^(\d+)events/$', 'events'),
	url(r'^(\d+)/create_event$', 'event'),
)
