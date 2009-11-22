#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
from contacts.views import edit_contact
import smsforum.views as views

urlpatterns = patterns('',
    url(r'^messages$',                                views.messages),
    url(r'^villages$',                                views.index),
    url(r'^village/(?P<pk>\d+)$',                     views.village),
    url(r'^village/add$',                             views.add_village),
    url(r'^village/delete/(?P<pk>\d+)$',              views.delete_village),
    url(r'^village/(?P<pk>\d+)/history$',             views.village_history),
    url(r'^village/(?P<pk>\d+)/history/csv$',         views.export_village_history, name='export_village_history'),
    url(r'^village/(?P<pk>\d+)/membership/csv$',      views.export_village_membership, name='export_village_membership'),
    url(r'^member/(?P<pk>\d+)$',                      views.member),
    url(r'^village/(?P<village_id>\d+)/member/add$',  views.add_member),
    url(r'^village/(?P<village_id>\d+)/member/add/(?P<member_id>\d+)$',  views.add_member),
    url(r'^member/edit/(?P<pk>\d+)$',                 views.edit_member),
    url(r'^i18n/',                                    include('django.conf.urls.i18n')),
    #url(r'^community/add$',                          views.add_community),
)

