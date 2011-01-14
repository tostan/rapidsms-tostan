#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
from contacts.views import edit_contact
import rapidsuivi.views as views
urlpatterns = patterns('',
    url(r'^calendar', views.calendar , name ="calendar"),
    url(r'^map', views.map , name ="map"),
    url(r'^rapidsuivi/update_message_status/(?P<from_page>\w+)/(?P<type>\w+)/(?P<message_pk>\d+)$' ,views.update_message_status ,name ="update_message_status"),
    url(r'^rapidsuivi/update_message/(?P<from_page>\w+)/(?P<type>\w+)/(?P<message_pk>\d+)?$' , views.update_message , name ="update_message"),   
    # Instead of accepting along  int for village_pk, we are going to accept a string  we will able  to handle a  None for radio 
    url(r'^rapidsuivi/export_village_message/(?P<village_pk>.+)$' , views.export_message , name ='export_village')
)

