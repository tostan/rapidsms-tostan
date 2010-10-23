#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
from contacts.views import edit_contact
import rapidsuivi.views as views
urlpatterns = patterns('',
    url(r'^calendar', views.calendar , name ="calendar"),
    url(r'^map', views.map , name ="map"),
    url(r'^update_message_status/(?P<message_pk>\d+)/(?P<from_template>\w+)$' ,views.update_message_status ,name ="update_message"),
    )

