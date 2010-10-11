#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
from contacts.views import edit_contact
import rapidsuivi.views as views
urlpatterns = patterns('',
    url(r'^calendar', views.calendar , name ="calendar"),
    url(r'^map', views.map , name ="map"),
    url(r'^message_read/(?P<pk>\d+)', views.message_read ,name="message_read")
    )

