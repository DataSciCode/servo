from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext as _

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
  
    url(r'^customer/index', 'customers.views.index'),
    url(r'^customer/edit$', 'customers.views.edit'),
    url(r'^customer/create$', 'customers.views.edit'),
    url(r'^customer/remove$', 'customers.views.remove'),
    url(r'^customer/save$', 'customers.views.save'),
    
    url(r'^$', 'orders.views.index'),
    url(r'^orders/$', 'orders.views.index'),
    url(r'^orders/index/(\w+)/(\w+)/$', 'orders.views.index'),
    
    url(r'^orders/edit/(\w+)$', 'orders.views.edit'),
    
    url(r'^orders/create$', 'orders.views.create'),
    url(r'^issue/create/order/(\w+)$', 'orders.views.issue_create'),
    
    url(r'^message/$', 'orders.views.messages'),
    url(r'^message/save$', 'orders.views.message_save'),
    url(r'^message/view/id/(\w+)$', 'orders.views.message_view'),
    url(r'^message/create/order/(\w+)$', 'orders.views.message_form'),
    
    url(r'^admin/status/$', 'admin.views.status'),
    url(r'^admin/queues/$', 'admin.views.queues'),
    url(r'^admin/status/create$', 'admin.views.status_form'),
    url(r'^admin/queue/create$', 'admin.views.queue_form'),
    url(r'^admin/fields/$', 'admin.views.fields'),
    url(r'^admin/fields/edit/$', 'admin.views.edit_field'),
    url(r'^fields/edit/(\w+)$', 'admin.views.edit_field'),
    url(r'^fields/remove/$', 'admin.views.remove_field'),
    url(r'^fields/remove/(\w+)$', 'admin.views.remove_field'),
    url(r'^admin/fields/save/$', 'admin.views.save_field'),
    
    url(r'^gsx/accounts$', 'admin.views.gsx_accounts'),
    url(r'^gsx/create_account$', 'admin.views.gsx_form'),
    url(r'^gsx/edit_account$', 'admin.views.gsx_form'),
    url(r'^gsx/remove_account$', 'admin.views.gsx_remove'),
    
    url(r'^products/create/order/(\w+)$', 'products.views.create'),
    
    # url(r'^servo3/', include('servo3.foo.urls')),
)
