from django.conf.urls import patterns, url

urlpatterns = patterns('notes.views',
	url(r'^(?P<parent>\d+)/reply/$', 'edit'),
    url(r'^templates/(\d+)/view/$', 'template'),
    url(r'^(?P<id>\d+)/edit/$', 'edit', {'kind': 'problem'}),
    url(r'^(?P<id>\d+)/remove/$', 'remove'),
    url(r'^save/$', 'save'),
)
