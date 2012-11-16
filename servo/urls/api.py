from django.conf.urls import patterns, url

urlpatterns = patterns('servo.views.api',
    url(r'^orders/$', 'orders'),
    url(r'^notes/$', 'notes'),
    url(r'^login/$', 'login'),
)
