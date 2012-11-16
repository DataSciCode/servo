from django.conf.urls import patterns, url

urlpatterns = patterns('servo.views.devices',
    url(r'^$', 'index'),
    url(r'^search$', 'search'),
    url(r'^search/(?P<query>\w+)$', 'index'),
    url(r'^tag/(?P<tag>\d+)/$', 'index'),
    url(r'^(\d+)/edit/$', 'edit'),
    url(r'^(\d+)/view/$', 'view'),
    url(r'^new/$', 'create'),
    url(r'^remove/$', 'remove'),
    url(r'^(\d+)/remove/$', 'remove'),
    url(r'^(\w+)/save/$', 'save'),
)
