from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext as _

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

   url(r'^user/save$', 'admin.views.save_user'),
   url(r'^user/edit/(\w+)$', 'admin.views.edit_user'),
   
    url(r'^customer/index', 'customers.views.index'),
    url(r'^customer/edit/(\w+)$', 'customers.views.edit'),
    
    url(r'^customer/create$', 'customers.views.create'),
    url(r'^customer/create/(\w+)$', 'customers.views.create'),
    url(r'^customer/create/order/(?P<order>\w+)$', 'customers.views.create'),
    
    url(r'^customer/remove$', 'customers.views.remove'),
    url(r'^customer/remove/(\w+)$', 'customers.views.remove'),
    url(r'^customer/save$', 'customers.views.save'),
    url(r'^customer/view/(\w+)$', 'customers.views.view'),
    url(r'^customer/move$', 'customers.views.move'),
    url(r'^customer/move/(\w+)$', 'customers.views.move'),
    
    url(r'^$', 'orders.views.index'),
    url(r'^orders/$', 'orders.views.index'),
    url(r'^orders/index/(\w+)/(\w+)/$', 'orders.views.index'),
    
    url(r'^orders/edit/(\w+)$', 'orders.views.edit'),
    url(r'^orders/remove/(\w+)$', 'orders.views.remove'),
    url(r'^orders/remove$', 'orders.views.remove'),
    url(r'^orders/create$', 'orders.views.create'),
    url(r'^orders/follow/(\w+)$', 'orders.views.follow'),
    url(r'^orders/tags/(\w+)$', 'orders.views.tags'),
     
    url(r'^message/$', 'messages.views.index'),
    url(r'^message/save$', 'messages.views.save'),
    url(r'^message/view/(\w+)$', 'messages.views.view'),
    url(r'^message/remove$', 'messages.views.remove'),
    url(r'^message/remove/(\w+)$', 'messages.views.remove'),
    url(r'^message/create/order/(\w+)$', 'messages.views.form'),
    
    url(r'^admin/files$', 'documents.views.index'),
    url(r'^admin/status/$', 'admin.views.status'),
    url(r'^status/save$', 'admin.views.save_status'),
    url(r'^status/edit/(\w+)$', 'admin.views.status_form'),
    url(r'^admin/queues/$', 'queues.views.index'),
    url(r'^admin/status/create$', 'admin.views.status_form'),
    url(r'^admin/fields/$', 'admin.views.fields'),
    url(r'^admin/fields/edit/$', 'admin.views.edit_field'),
    url(r'^admin/settings$', 'admin.views.settings'),
    url(r'^admin/users$', 'admin.views.users'),
    url(r'^admin/user/create$', 'admin.views.edit_user'),
    url(r'^admin/locations$', 'admin.views.locations'),
    url(r'^admin/location/create$', 'admin.views.edit_location'),
    
    url(r'^fields/edit/(\w+)$', 'admin.views.edit_field'),
    url(r'^fields/remove/$', 'admin.views.remove_field'),
    url(r'^fields/remove/(\w+)$', 'admin.views.remove_field'),
    url(r'^admin/fields/save/$', 'admin.views.save_field'),
    url(r'^admin/templates/$', 'admin.views.templates'),
    url(r'^template/create$', 'admin.views.create_template'),
    url(r'^template/save$', 'admin.views.save_template'),
    url(r'^template/view/(\w+)$', 'admin.views.view_template'),
    
    url(r'^gsx/accounts$', 'admin.views.gsx_accounts'),
    url(r'^gsx/create_account$', 'admin.views.gsx_form'),
    url(r'^gsx/edit_account$', 'admin.views.gsx_form'),
    url(r'^gsx/remove_account$', 'admin.views.gsx_remove'),
    url(r'^gsx/save_account$', 'admin.views.gsx_save'),
    
    url(r'^queue/create$', 'queues.views.edit'),
    url(r'^queue/save$', 'queues.views.save'),
    url(r'^queue/edit/(\w+)$', 'queues.views.edit'),
    url(r'^queue/remove$', 'queues.views.remove'),
    url(r'^queue/remove/(\w+)$', 'queues.views.remove'),
    
    url(r'^products/create/order/(\w+)$', 'products.views.create'),
    
    url(r'^issue/create/order/(\w+)$', 'issues.views.create'),
    url(r'^issue/edit/(\w+)$', 'issues.views.edit'),
    url(r'^issue/save$', 'issues.views.save'),
    url(r'^issue/remove$', 'issues.views.remove'),
    url(r'^issue/remove/(\w+)$', 'issues.views.remove'),
    
    url(r'^tag/create/(\w+)$', 'tags.views.create'),
    url(r'^tag/index$', 'tags.views.index'),
    
    url(r'^location/save$', 'admin.views.save_location'),
    # url(r'^servo3/', include('servo3.foo.urls')),
)
