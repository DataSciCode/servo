from django.conf.urls import patterns, url

urlpatterns = patterns('servo.views.device',
    url(r'^$', 'index'),
    url(r'^new/$', 'edit'),
    url(r'^search$', 'search'),
    url(r'^search/(?P<query>\w+)$', 'index'),
    url(r'^tag/(?P<tag>\d+)/$', 'index'),
    url(r'^(\d+)/edit/$', 'edit'),
    url(r'^(\d+)/view/$', 'view'),
    url(r'^remove/$', 'remove'),
    url(r'^(\d+)/remove/$', 'remove'),
    url(r'^(\d+)?/save/$', 'save'),
    url(r'^(\d+)/parts/$', 'parts'),
)
