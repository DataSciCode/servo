from django.conf.urls import patterns, url

urlpatterns = patterns('calendars.views',
	url(r'^calendars/$', 'index'),
	url(r'^calendars/save$', 'save'),
	url(r'^calendar/save_event$', 'save_event'),
	url(r'^calendar/create$', 'create'),
	url(r'^calendar/edit/(\w+)$', 'edit'),
	url(r'^calendar/remove$', 'remove'),
	url(r'^calendar/remove/(\w+)$', 'remove'),
	url(r'^calendar/events/(\w+)$', 'events'),
	url(r'^calendar/(\w+)/create_event$', 'event'),
)
