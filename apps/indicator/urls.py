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
    url(r'^indicator/add_pays/?$',views.add_pays,  name="add_pays"),
    url(r'^indicator/edit_pays/(?P<id>\d+)/?$',views.edit_pays,  name="edit_pays"),
    url(r'^indicator/delete_pays/(?P<id>\d+)/?$',views.delete_pays,  name="delete_pays"),
    url(r'^indicator/add_region/(?P<pays>\w+)/?$',views.add_region,  name="add_region"),
    url(r'^indicator/add_departement/(?P<pays>\w+)/?$',views.add_departement,  name="add_departement"),
    url(r'^indicator/add_arrondissement/(?P<pays>\w+)/?$',views.add_arrondissement,  name="add_arrondissement"),
    url(r'^indicator/add_commune_arrondissement/(?P<pays>\w+)/?$',views.add_commune_arrondissement,  name="add_commune_arrondissement"),
    url(r'^indicator/add_commune/(?P<pays>\w+)/?$',views.add_commune,  name="add_commune"),
    url(r'^indicator/add_communaute_rurale/(?P<pays>\w+)/?$',views.add_communaute_rurale,  name="add_communaute_rurale"),
    

    # Village is the rural community
    url(r'^indicator/add_village/(?P<pays>\w+)/?$',views.add_village,  name="add_village"),
    
    # Guinee Konkary
    url(r'^indicator/add_prefecture/(?P<pays>\w+)/?$',views.add_prefecture,  name="add_prefecture"),
    url(r'^indicator/add_speciale_zone/(?P<pays>\w+)/?$',views.add_special_zone,  name="add_special_zone"),
    url(r'^indicator/add_commune_hurbaine/(?P<pays>\w+)/?$',views.add_commune_hurbaine,  name="add_commune_hurbaine"),
    url(r'^indicator/add_village_guinee/(?P<pays>\w+)/?$',views.add_village_guinee,  name="add_village_guinee"),
    url(r'^indicator/add_secteur/(?P<pays>\w+)/?$',views.add_secteur,  name="add_secteur"),
    
    # Gambie
    url(r'^indicator/add_district/(?P<pays>\w+)/?$',views.add_secteur,  name="add_district"),
    
    
    # Somalie
    url(r'^indicator/add_etat/(?P<pays>\w+)/?$',views.add_etat,  name="add_etat"),
    
    
    # Indicator 
    url(r'^indicator/parametrage_indicator/?$',views.parametrage_indicator,  name="parametrage_indicator"),
    url(r'^indicator/add_indicator/?$',views.add_indicator,  name="add_indicator"),
    url(r'^indicator/search_indicator/?$',views.search_indicator,  name="search_indicator"),
    url(r'^indicator/export_indicator/?$',views.export_indicator,  name="export_indicator"),
    
    
    #Project peer contry
    
    url(r'^indicator/parametrage_project/?$',views.parametrage_project,  name="parametrage_project"),
    url(r'^indicator/add_project/(?P<pays>\w+)/?$',views.add_project,  name="add_indicator"),
    url(r'^indicator/search_project/(?P<pays>\w+)/?$',views.search_project,  name="search_project"),
    url(r'^indicator/export_project/(?P<pays>\w+)/?$',views.export_project,  name="export_project"),
    
    
)
