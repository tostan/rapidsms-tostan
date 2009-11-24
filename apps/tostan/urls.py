#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
import apps.tostan.views as views

urlpatterns = patterns('django.views.generic.simple',
    url(r'^$',    'direct_to_template', {'template':"tostan/dashboard.html"}),
    url(r'^help$',    'direct_to_template', {'template':"tostan/smscommands.html"}, name="help"),
    url(r'^export$',   views.export, name="export"),
    url(r'^404$',       'direct_to_template', {'template':"tostan/404.html"}, name="404"),
)
