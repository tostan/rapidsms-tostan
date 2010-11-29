#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
import apps.tostan.views as views
from apps.indicator import views
urlpatterns = patterns('',
    url(r'^indicator/?$',views.index,  name="dashboard"),
    url(r'^indicator/parametrage/?$',views.parametrage,  name="parametrage"),
    url(r'^indicator/add/area/(?P<pays>\w+)/(?P<type>\w+)/?$',views.add_area,  name="add_area"),

)
