#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
import apps.tostan.views as views

urlpatterns = patterns('',
    url(r'^$',         login_required(direct_to_template), 
                       {'template':"tostan/dashboard.html"}, name="dashboard"),
    url(r'^help$',     login_required(direct_to_template), 
                       {'template':"tostan/smscommands.html"}, name="help"),
    url(r'^export$',   views.export, name="export"),
    url(r'^404$',      login_required(direct_to_template), 
                       {'template':"tostan/404.html"}, name="404"),
)
