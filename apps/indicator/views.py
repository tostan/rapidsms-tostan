#!/usr/bin/env python 
# Create your webui views here.
#from django.shortcuts import render_to_response
from django.http import HttpResponse ,HttpResponseRedirect
from rapidsms.webui.utils import render_to_response
from django.core.urlresolvers import reverse
from apps.indicator.models import *
from django import forms
from .forms import *
from .models import *
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required , permission_required 
from django.http import HttpResponse 
from django.core.exceptions import ValidationError
from datetime import datetime , date 
from django.forms.extras.widgets import SelectDateWidget
from django.core.paginator import Paginator,InvalidPage,EmptyPage
from forms import *
from datetime import datetime
from django.contrib.auth.models import User, check_password
from .config import *
from .utils import AreaForm ,AreaFormForVillage
# The number of indicator displayed into edition  by page 
import codecs
import csv
import cStringIO

import utils
import models
import forms 
from django.db.models import Manager
ITEM_PER_PAGE = 30
def index (req):
    '''Go to indicator dashboard page'''
    return render_to_response (req,"indicator/index.html" , {})

@login_required
def edition_fiche (req):
    '''Go to indicator dashboard page'''
    #return render_to_response (req,"indicator/edition_fiche.html" ,{
    #   "projects":Project.objects.all()})
 
    l  =["GUINEE_CONAKRY" , "GUINEE_BISSAU" , "GAMBIE" , "SENEGAL" , "SOMALIE" , "DJIBOUTI" , "MAURITANIE"]
    context  =list()
    for name in l :
        context.append ((name , Project.objects.filter (pays__name__iexact =  name )))
    return render_to_response (req,"indicator/edition_fiche.html" ,{"projects"  :context})


@login_required
def parametrage(req):
    '''Go to indicator param  dashboard '''
    return render_to_response (req, "indicator/parametrage.html" ,{})
    
@login_required
def parametrage_indicator (req):
    '''Go to indicator param dashboard'''
    return render_to_response (req , "indicator/parametrage_indicator.html" ,{})
    
@login_required
def parametrage_project(req):
    '''Go to indicator project dashboard'''
    return render_to_response (req , "indicator/parametrage_project.html" ,{})
    
@login_required
def parametrage_stat(req):
    '''Go to indicator stats dashboard    '''
    return render_to_response (req , "indicator/parametrage_stat.html",{})
    
@login_required
def parametrage_user(req):
    '''Go to indicator user dashboard'''
    return render_to_response (req , "indicator/parametrage_user.html" , {})

@login_required
def parametrage_export(req):
    '''Go to export dashborad'''
    return render_to_response ( req , "indicator/parametrage_export.html" ,{})
    
def add_pays(req):
    '''Add new contry'''
    msg = list()
    template ="indicator/add_pays.html"
    if req.method=="POST":
        form =PaysForm (req.POST)
        if form.is_valid ():
            form.save ()
            msg.append (_("Element sauvegarde"))
            return render_to_response (req,template ,{
                "form": form ,"pays":Pays.objects.all () ,"msg"  : msg })
        else :
            msg.append (_("Erreur dans le formulaire"))
    else :
        form  = PaysForm ()    
    return render_to_response (req, template ,{
        "form" : form , "pays" : Pays.objects.all () ,"msg": msg })
    
def add_region (req, id):
    '''if senegal , flatten  pays to regions'''
    pays  = get_object_or_404(Pays ,name__icontains = id )
    regions = [pays]
    msg = []
    #as tuple to fill the form choice fields dynamique 
    if id.lower() =="somalie":
        regions   = cast_etat (pays)
    else :
        regions   = [pays]
    parents = regions 
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    form    = AreaForm (**{"parents" : ("pays" , parents)})
    if  req.method =="POST":
        #form = form_class (req.POST)
	form  = AreaForm  (data  =req.POST , **{"parents" :("pays" , parents)})
        if form.is_valid ():
            #form.save ()
            Region.objects.create (
                parent =pays ,
                name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_region.html",{
                "form" : form ,"msg": msg,"regions": Region.objects.all () })
        else :
            msg.append (_("Not OK")) 
    return render_to_response (req,"indicator/add_region.html", {
       "form":form,"msg": msg,"regions": Region.objects.all () })
    
def  edit_pays (req , id ):
    '''Edit the given contry'''
    msg = list ()
    template = "indicator/edit_pays.html"
    contry =  get_object_or_404 (Pays , pk = id)
    form = PaysForm (instance = contry)
    if req.method  == "POST":
            form  = PaysForm (req.POST)
            if form.is_valid ():
                form.save ()
                msg.append (_("Element sauvegarde"))
                return render_to_response (req , template ,
                    {"form" : PaysForm (),"pays" : Pays.objects.all (),"msg" : msg })
            else :
                msg.append (_("Erreur dans le formulaire"))
    return render_to_response (req ,template  , {
        "form": form,"pays" : Pays.objects.all ()})
    
def delete_pays (req, id):
    '''Given an contry , delete it'''
    template = "indicator/confirm_delete.html"    
    contry  = get_object_or_404 (Pays , pk = id )
    if req.method  =="POST":
        try:
            req.POST.get ("confirm_delete")
            contry.delete ()
            return HttpResponseRedirect("/indicator/add_pays")
        except  KeyError , err: 
              return render_to_reponse (req,template , {}) 
    else:
        return render_to_response(req, template , {})
     
def delete_user(req, id):
    '''Given an contry , delete it'''
    template = "indicator/confirm_delete.html"    
    user  = get_object_or_404 (User , pk = id)
    if req.method.lower () =="post":
        try:
            req.POST.get ("confirm_delete")
            user.delete ()
            return HttpResponseRedirect("/indicator/add_user")
        except  KeyError , err: 
              return render_to_reponse (req,template , {}) 
    else:
        return render_to_response(req, template , {})
     

def as_tuple (qs):
    '''Given a list of objets return a tuple'''
    return [("" , "--")] + [ (q.pk , q.__unicode__()) for q in qs]
        
def add_commune (req , pays):
    '''Add new commune'''
    pass


def add_communaute_rurale (req):
    '''Add new rurale community'''
    pass

def   is_filter_commune_arrondissement(post):
	if "departements" in post and post["departements"]:
		return True 
	if "regions" in post and post ["regions"]:
		return True 
	return False
def filter_commune_arrondissement (post):
	rs =[]
	if  "departements" in post and post ["departements"]:
		dep_pk  = post['departements']
		dep     = Departement.objects.get (pk =dep_pk)
		for arron in dep.children.all ():
			rs.append (arron)
		if rs : return rs, None ,None
		else : return rs ,None ,None

        if  "regions" in post and post ["regions"]:
		reg_pk =post["regions"]
		region = Region.objects.get (pk =reg_pk) 
		dep_list   = []
		arron_list = []
		for dep in region.children.all ():
			dep_list.append (dep)
			for arron in dep.children.all ():
				arron_list.append (arron)
		return arron_list, dep_list ,None


def add_commune_arrondissement(req, pays):
    '''Add new commune '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    parents = departements = regions  = None
    msg = []
    
    if req.method =="POST":
	if is_filter_commune_arrondissement (req.POST):
		parents , departements ,regions  = filter_commune_arrondissement(req.POST)
    if not parents:
	parents     =cast_arrondissement(pays)
    if not departements: 
    	departements=cast_departement(pays)
    if not regions :
	regions     =cast_region(pays)

    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    form    = AreaForm(**{"parents" : ("arrondissements" , parents) ,"parents_rest" : (( "regions" , regions) , ("departements", departements))})
    if  req.method =="POST":
        #form = form_class (req.POST)
	form  = AreaForm (data  = req.POST ,  
	** {"parents": ("arrondissements" ,parents) , "parents_rest": (( "regions", regions ) , ("departements" , departements))})
        if form.is_valid ():
            #form.save ()
            parent = Arrondissement.objects.get (pk =req.POST["arrondissements"])
            CommuneArrondissement.objects.create (
                parent =parent ,
                name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_commune_arrondissement.html",{
                "form" : form, "msg": msg,"regions": CommuneArrondissement.objects.all ()})
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_commune_arrondissement.html", {
        "form" : form ,"msg": msg,"regions": CommuneArrondissement.objects.all ()})



def is_filter_commune (post):
	if "arrondissements" in  post and post ['arrondissements']:
		return True
	if "departements"  in post and post ["departements"]:
		return True
	if "regions" in post and post ["regions"]:
		return True 

def filter_commune (post):
	rs  = list ()
	if "arrondissements" in post and post ["arrondissements"]:
		arr_pk  = post ["arrondissements"]
		arr     = Arrondissement.objects.get (pk = int (arr_pk))
		for com_arr in arr.children.all ():
			rs.append (com_arr)
		return rs ,None ,None,None

	if "departements" in post and post ["departements"]:
		dep_pk  = post ["departements"]
		dep     =Departement.objects.get (pk  = int (dep_pk))
		com_arr_list  = []
		arr_list       =[]
		for arr in dep.children.all ():
			arr_list.append (arr)
			for com_arr in arr.children.all ():
				com_arr_list.append (com_arr)

		return com_arr_list,  arr_list,None ,None
	if "regions" in post and post ["regions"]:
		reg_pk = post ["regions"]
		region =Region.objects.get (pk =int (reg_pk))
		dep_list = []
		arr_list = []
		com_arr_list =[]
		for dep in region.children.all ():
			dep_list.append (dep)
			for arr in dep.children.all ():
				arr_list.append (arr)
				for com_arr in arr.children.all ():
					com_arr_list.append (com_arr)
		return  com_arr_list , arr_list , dep_list, None
	

def add_commune (req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    parents  = arrondissements = departements = regions =None 
    regions =[]
    #regions= cast_commune_arrondissement(pays)    
    msg = []
    if req.method  =="POST":
	if is_filter_commune (req.POST):
		parents ,arrondissements , departements , regions  = filter_commune (req.POST)
    #as tuple to fill the form choice fields dynamique 
    #data =as_tuple (regions)
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    if not parents :
	parents          = cast_commune_arrondissement (pays)
    if not arrondissements :
	arrondissements  = cast_arrondissement (pays)
    if not departements :
	departements     = cast_departement (pays)
    if not regions :
	regions          = cast_region (pays)
    form  = AreaForm (**{"parents"  : ("communearrondissements" , parents) ,"parents_rest" :(("regions" , regions) , ("departements" , departements) , ("arrondissements" , arrondissements))})
    if  req.method  =="POST":
        #form = form_class (req.POST)
	form  = AreaForm (data = req.POST , 
	**{"parents"  : ("communearrondissements" , parents) ,"parents_rest":(("regions" ,regions) , ("departements" ,departements) , ("arrondissements" , arrondissements))})
        if form.is_valid ():
            #form.save ()
            parent = CommuneArrondissement.objects.get (pk =req.POST["communearrondissements"])
            Commune.objects.create (
                parent =parent ,
                name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_commune.html",{
                "form" : form ,"msg": msg,"regions": Commune.objects.all () })
        else :
            msg.append (_("Not OK"))
            
    return render_to_response (req,"indicator/add_commune.html",{
        "form" : form ,"msg": msg,"regions": Commune.objects.all ()})

def  is_filter_arrondissement (post):
	if "regions" in post and post["regions"]:
		return True 
	return False

def filter_arrondissement(post):
	# The user is trying to filter the departement list
	rs  = []
	if "regions" in post and post["regions"]:
		region_pk  = post['regions']
		region = Region.objects.get (pk = region_pk)
		for dep in region.children.all ():
			rs.append(dep)
        if rs: return rs ,None 
	else : return rs ,None 
	                
def add_arrondissement (req, pays):
    '''if senegal , flatten  pays to regions'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    parents= regions  =None
    regions =[]
    if req.method == "POST":
	  if is_filter_arrondissement (req.POST):
		parents, region  = filter_arrondissement (req.POST)
    
    if not parents:
    	parents  = cast_departement (pays)
    if not regions :
	regions  = cast_region(pays)  
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    #data =as_tuple (regions)
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    form    = AreaForm (**{"parents":("dapartements" ,parents) , "parents_rest":(("regions" ,regions),)})
    if  req.method == "POST":
        #form = form_class (req.POST) 
	form  =AreaForm (data  = req.POST , **{"parents" :("departements", parents),"parents_rest": (("regions", regions),)})
        if form.is_valid ():
            #form.save ()
            parent = Departement.objects.get (pk =req.POST["departements"])
            Arrondissement.objects.create (
                parent =parent ,
                name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_arrondissement.html",{
                "form" : form ,"msg": msg,"regions": Arrondissement.objects.all () } )
        else :
            msg.append (_("Not OK"))
    return render_to_response (req,
        "indicator/add_arrondissement.html",{
            "form" : form,"msg": msg,"regions": Arrondissement.objects.all() })

def cast_departement (top):
    '''Get childrens of top , only the departments childrens'''
    deps = []
    regions = cast_region(top)
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =Departement)
            if d and type (d)==Departement:
                deps.append (d)
                
    return deps

def cast_prefecture (top):
    '''Get childrens, only the prefectures types'''
    deps = []
    regions = cast_region(top)
    for region in regions:
        
        for dep in region.children.all():
            
            d = dep._downcast(klass =Prefecture)
            if d and type (d)==Prefecture:
                deps.append (d)
    return deps

def cast_region(top):
    ''' Get the chilrens , only the regions  types'''
    regions =[]
    
    for child in top.children.all ():
        d = child._downcast(klass=Region)
        
        if type (d)==Region:
            regions.append(d)
    return regions

def cast_etat(top):
    '''Get the childrens ,only the etats types'''
    regions =[]
    
    for child in top.children.all ():
        d = child._downcast(klass=Etat)
        if type (d)==Etat:
            regions.append(d)
            
    return regions

def cast_secteur(top):
    '''Get the chilrens , only the secteurs type'''
    
    deps = []
    regions = cast_region(top)
    for region in regions:
        for dep in region.children.all():
            
            d = dep._downcast(klass =Secteur)
            if d and type (d)==Secteur:
                deps.append (d)
    return deps

def cast_district(top):
    '''Cast the childrens ,only the districts types'''
    deps = []
    regions = cast_region(top)
    
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =District)
            if d and type (d)==District:
                deps.append (d)
    return deps


def cast_sub_prefecture (top):
    '''Get the childrens ,only the prefetures types'''
    deps = []
    regions = cast_prefecture(top)
    
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =SubPrefecture)
            if d and type (d)==SubPrefecture:
                deps.append (d)
    return deps

def cast_arrondissement(top):
    '''Get the childrens only the arrondissement types '''
    arrs  = []
    deps = cast_departement(top)
    
    for dep in deps:
        
        for arr in dep.children.all ():
            a = arr._downcast(klass =Arrondissement)
            if a and type(a)==Arrondissement:
                arrs.append (a)
    return arrs

def cast_commune_arrondissement(top):
    '''Get childrens ,only the arrondissements types'''
    coms  = []
    com_arrs= cast_arrondissement(top)
    
    for com_arr in com_arrs:
        for com in com_arr.children.all ():
            c= com._downcast(klass =CommuneArrondissement)
            if c and type(c)==CommuneArrondissement:
                coms.append (c)  
    return coms

def cast_commune(top):
    '''Get childrens ,only the communes types'''
    coms  = []
    com_arrs= cast_commune_arrondissement(top)
    
    for com_arr in com_arrs:
        
        for com in com_arr.children.all ():
            c= com._downcast(klass =Commune)
            if c and type(c)==Commune:
                coms.append (c)                
    return coms


def _get_village_parents_from_pays (contry , contry_name):
    contry_name  =  contry_name.upper ()
    #return   village_parents_dict[contry_name](contry)
    rs  =get_area_of_contry(contry)
    # add as_tuple method
    return rs   

     	
	
def _get_village_parent_from_pays (contry_name , id ):
    try:
        return village_parent_object_dict [contry_name.upper ()].objects.get (pk  = int(id))
    except  Exception , e :
        raise
    return None
        
     
def cast_village (top , pays_name):
    '''
    Get villages chidrens ,only the village 
    The parent of the village can be :
        *a commune if senegal*
        *a sub prefecture if guinee*
        *a secteur if gambie*
        ...
        ... '''
    coms = []
    #com_arrs=_get_village_parents_from_pays (top ,pays_name)[-1]
    com_arrs =_get_area_of_contry2 (top)[-1][1]
    if not com_arrs or not len (com_arrs):
        return []
    for com_arr in com_arrs:
        for com in com_arr.children.all ():
            c= com._downcast(klass =IndicatorVillage)
            if c and type(c)==IndicatorVillage:
                coms.append (c) 
    return coms

def add_departement (req, pays):
    '''if senegal , flatten  pays to regions'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions = cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    parents = regions
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    form         =AreaForm (**{"parents" :("regions" , parents)})
    if  req.method =="POST":
        #form = form_class (req.POST)
	form  =AreaForm (data =req.POST , ** {"parents" : ("regions" ,parents)})
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["regions"])
            Departement.objects.create (
                parent =parent ,
                name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_departement.html",{
                "form" : form ,"msg": msg, "regions": Departement.objects.all ()})
        else :
            msg.append (_("Not OK"))    
    return render_to_response (req,"indicator/add_departement.html",{
        "form" : form ,"msg": msg,"regions": Departement.objects.all ()})
    
def add_village (req, id):
    '''Add new village'''
    
    pays  = get_object_or_404(Pays ,name__icontains = id )
    #regions  =_get_village_parents_from_pays (pays ,pays.name)
    village_parents_from_dict = _get_village_parents_from_pays (pays , pays.name)
    parents , parents_rest    = village_parents_from_dict [-2] , village_parents_from_dict [:-1]
    #lbl      =_get_village_lbl_parent_from_pays (pays.name)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    #data =as_tuple (regions)
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    #form   = AreaFormForVillage(**{"parents" :(lbl  , data)})
    form    = AreaFormForVillage(**{"parents"  :parents , "parents_rest" : parents_rest})
    if  req.method  =="POST":
        #form  = form_class (req.POST)
        #form  = AreaFormForVillage(data =req.POST , **{"parents" :(lbl , data)})
	form   = AreaFormForVillage (data =req.POST , ** {"parents" :parents  , "parents_rest":parents_rest})
	if form.is_valid():
            #form.save ()
            # parent [0] contain the parent 'of the village name like  district or communearrondissment 
            pk  = req.POST.get(parents[0])
            parent  = _get_village_parent_from_pays (pays.name ,pk )
            IndicatorVillage.objects.create (
                parent    =  parent ,
                name      =  req.POST.get ("name"),
		latitude  =  req.POST.get ('latitude'),
		longitude =  req.POST.get ('longitude'))
            msg.append (_("Merci ,le village a bien ete cree"))
            return render_to_response (req,"indicator/add_village.html",{
                "form" : form ,"msg": msg,"regions": IndicatorVillage.objects.all ()})
        else :
            msg.append (_("Not OK"))
            
    return render_to_response (req,"indicator/add_village.html",{
        "form" : form, "msg": msg,"regions": IndicatorVillage.objects.all ()})
    
def add_prefecture (req, pays):
    '''Add new prefecture '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    # For Guinee Konakry the region  should be casted to precture
    #regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    #data =as_tuple (regions)
    parents  =cast_region (pays)
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    form         = AreaForm ( **{"parents" :("regions" , parents)})
    if  req.method  =="POST":
        #form = form_class (req.POST)
	form  = AreaForm ( data =req.POST , **{"parents" : ("regions" ,parents)})
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["regions"])
            Prefecture.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_prefecture.html",{
                "form" : form ,"msg": msg,"regions": Prefecture.objects.all () })
        
        else :
            msg.append (_("Not OK"))
    return render_to_response (req,"indicator/add_prefecture.html",{
        "form" : form, "msg": msg,"regions": Prefecture.objects.all ()})


def is_filter_sub_prefecture (post): 
	if "regions" in post and post ["regions"]:
		return True
	return False

def filter_sub_prefecture (post):
       	rs  =[]
	if "regions" in post and post ['regions']:
		reg_pk  = post ['regions']
		reg     = Region.objects.get (pk = int(reg_pk))
		for pref in reg.children.all ():
			rs.append (pref)
		return rs ,None 
	
def add_sub_prefecture (req, pays):
    '''Add new commune'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    # For Guinee Konakry , for this moment , special zone should have region as parent
    msg = []
    parents  =regions  =None
    if is_filter_sub_prefecture (req.POST):
		parents , regions  = filter_sub_prefecture (req.POST)
    #as tuple to fill the form choice fields dynamique 
    if not parents:
    	parents =cast_prefecture(pays)
  
    if not regions:
	regions =cast_region (pays)
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    form    =  AreaForm (**{ "parents" : ("prefectures" ,parents)  , "parents_rest"  : (("regions" , regions) , )})
    if  req.method  =="POST":
        #form = form_class (req.POST)
	form  =AreaForm ( data  = req.POST , **{"parents": ("prefectures", parents) , "parents_rest"  : ( ("regions" ,regions),)})
        if form.is_valid ():
            #form.save ()
            parent = Prefecture.objects.get (pk =req.POST["prefectures"])
            SubPrefecture.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_sub_prefecture.html",{
                "form" : form ,"msg": msg,"regions": SubPrefecture.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
           "indicator/add_sub_prefecture.html",{
               "form" : form,"msg": msg,"regions": SubPrefecture.objects.all () })



def add_village_guinee (req, pays):
    '''Add new commune'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]    
    # For Guinee Konakry , for this moment ,Commune hurbaine should have region as parent
    regions= pays
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =regions
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()a
    form  =AreaForm (**{"objs" : data})
    if  req.method  =="POST":
        #form = form_class (req.POST)
	form  = AreaForm ( data =req.POST , ** {"objs" :data})
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            IndicatorVillage.objects.create (
                parent =parent ,
                name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_village.html",{
                "form" : form ,"msg": msg,"regions": IndicatorVillage.objects.all () })
        else :
            msg.append (_("Not OK"))
            
    return render_to_response (req,"indicator/add_village.html",{
        "form" : form, "msg": msg,"regions": IndicatorVillage.objects.all ()})
            
def add_secteur (req, pays):
    '''Add new secteur'''
    
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    # For Guinee Bissau,secteur should have regions as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    parents =regions
    #form_class  =_get_area_form (data,"region")
    #form   = form_class ()
    form         = AreaForm ( ** {"parents" :("regions" , parents)})
    if  req.method  == "POST":
        #form = form_class (req.POST)
	form  = AreaForm (data =req.POST ,** {"parents" : ("regions" , parents)})
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["regions"])
            Secteur.objects.create (
                parent =parent ,
                name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_secteur.html",{
                "form" : form ,"msg": msg,"regions": Secteur.objects.all ()})
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_secteur.html",
         {"form" : form,"msg": msg,"regions": Secteur.objects.all ()})
    
def add_district(req, pays):
    '''Add new district'''
    pays  = get_object_or_404(Pays , name__icontains = pays )
    regions =[]
    # For Guinee Bissau,secteur should have regions as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    parents =regions
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    form  =AreaForm ( **{"parents" : ("regions" , parents)})
    if  req.method  == "POST":
        #form = form_class (req.POST)
	form   =AreaForm (data =req.POST , ** {"parents" : ("regions" , parents)})
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["regions"])
            District.objects.create (
                parent = parent ,
                name   = req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_district.html",
             {"form" : form ,"msg": msg,"regions": District.objects.all () } )
        else :
            msg.append (_("Not OK"))            
    return render_to_response (req,"indicator/add_district.html",{"form" : form, "msg": msg,"regions": District.objects.all () })

    
def add_etat(req, pays):
    '''Add new etat'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    # For Guinee Bissau,secteur should have regions as parent
    #regions= cast_region(pays)
    regions  = [pays]
    msg = []
    #as tuple to fill the form choice fields dynamique 
    parents =regions
    #form_class  = _get_area_form (data,"region")
    #form   = form_class ()
    form    = AreaForm ( **{"parents" : ("regions"  , parents)})
    if  req.method   =="POST":
        #form = form_class (req.POST)
	form =AreaForm  (data =req.POST, ** {"parents" : ("regions" , parents)})
        if form.is_valid ():
            #form.save ()
            parent = Pays.objects.get (pk =req.POST["regions"])
            Etat.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_etat.html", {"form" : form ,"msg": msg,"regions": Etat.objects.all ()} )
        else :
            msg.append (_("Not OK"))   
    return render_to_response (req,"indicator/add_etat.html", {"form" : form, "msg": msg,"regions": Etat.objects.all ()})
    
def get_village (pays , id):
    ''' Selon le  decoupage , le dernier maillon de la chaine peut etre 
    le village  ex senegal , secteur  ex gambie  , region ex somalie '''
     
    def get_konakry_village (id):
        IndicatorVillage.objects.get (pk =id)
    def get_senegal_village (id):
        IndicatorVillage.objects.get (pk =id)
    def get_bissau_village (id):
        Secteur.objects.get (pk =id)
    def get_gambie_village (id):
        District.objects.get (pk =id)
    def get_somalie_village (id):
        Region.objects.get (pk =id)
    def get_djibouti_village (id):
        Region.objects.get (pk =id)
    def get_mauritanie_village (id):
        Deparetement.objects.get (pk =id)

def indicators_list():
    #The indicator list to be associated to the project
    return Indicator.objects.all ()

def  edit_project (req , id):
     msg=[]
     project  = get_object_or_404(Project , pk= id)
     form  = ProjectForm (instance = project)
     if req.method  =='POST':
          # User  need  to delete data
          if 'delete' in req.POST:
               #delete request was sent
               project.delete()
               msg.append (_('Suppression reussie'))
               #Ok redirect to param project
               return HttpResponseRedirect(reverse('parametrage_project'))
          form  = ProjectForm (req.POST , instance = project)
          if form.is_valid ():
               form.save()
               msg.append (_('Sauvegarde reussie'))
          else:
               msg.append (_('Formulaire invalide'))
     template  = 'indicator/edit_project.html'
     return  render_to_response (req ,  template , { 'form':form  ,'msg' :msg })
          
def add_project(req , pays):
    '''
    Each pays should have it own layout 
    Chaque pays doit avoir la liste de ces regions village , etc afin que dans 
    l'edition d'un project qu'on puisse filter et ajouter un village'''
    template = 'indicator/add_project.html'
    pays= get_object_or_404(Pays , name__icontains = pays.lower ())
    #Get the village filter form
    #vil_form_data         = get_pays_form (pays)
    ind_form_data         = indicators_list()
    #Go to create dynamically a project from based on the vil_from_filter and the indicator_form
    #form_village_class    = _get_village_form (vil_form_data)
    #form_village          = form_village_class ()
    form_village           = utils.VillageForm (**{"area_of_contry": get_area_of_contry(pays)})
    #form_indicator_class  = _get_indicator_form (ind_form_data)
    #form_indicator        = form_indicator_class ()
    form_indicator         = utils.IndicatorForm (**{"indicators" :ind_form_data})
    msg  =[]
    if req.method == "POST":
        #form_village       = utils.VillageForm(data  =req.POST , **{"area_of_contry": get_area_of_contry (pays)})
        #return HttpResponse ("%s=%s<br>"% (i,j) for (i,j) in req.POST.items())
        #return  HttpResponse (filter_area(pays, req.POST))
        data  = filter_area(pays, req.POST) or  get_area_of_contry (pays)
        form_village       = utils.VillageForm(data  =req.POST , **{"area_of_contry": data})
    if req.method =='POST' and "filtre" not in req.POST:
        form_indicator     = utils.IndicatorForm (data  = req.POST , ** {"indicators" : ind_form_data})
    	if form_village.is_valid  ()  and form_indicator.is_valid ():
    		        #return  HttpResponse ( "</br>".join ( [  "%s= %s" %(k,v) for (k, v) in form_village.cleaned_data.items  ()]))
                    try:
                       villages, indicators =[], []
                       #Get list of the   projet's villages 
                       for vil_pk in  req.POST.getlist("villages"):
                           villages.append(IndicatorVillage.objects.get (pk =vil_pk)) 
                       #  Get the list of the projet 's indicators 
                       for ind_pk in req.POST.getlist ('indicators'):
                           indicators.append(Indicator.objects.get (pk =ind_pk))
                       dt = date = datetime.now().date ()
                       # get the projet remained args from post data
                       #  bailleur , decsription  ,date creattion
                       #  Set  other  value  needed  when creatin  new projet  ,
                       #  The  user provide thde   bailleur , the  titre   and   the description of the
                       #  projet   we will  fill  aother   value later
                       d      = {}
                       args   = ['bailleur' , 'titre','description']
                       dict   = req.POST
                       for key in  dict.iterkeys ()  :
                            if key in  args:d[str(key)] = dict [key]
                            else : pass
                       # Now  we  can  create  the   projet
                       # Add the contry of the projet
                       d ["pays"] = pays
                       Project.create_project (villages , indicators ,**d)
                       msg.append (_("Le projet a bien ete sauvegarde"))          
                    except (KeyError, Exception):
                       #print  '--*POOF*--'
                       raise 
                       msg.append(_("Vous devez choisir le dernier element dans le filtre"))
        else:
                    msg.append (_("Le formulaire est invalide ,verifiez que tous les champs obligatoires sont bien renseignes"))
    return render_to_response (req , template ,{ "form_village" : form_village ,
           "form_indicator": form_indicator , "projects" :Project.objects.all (), "msg" :msg })

def search_project (req,pays):
    '''Search a new projet'''
    form  = utils.SearchProjectForm ()
    projects  = Project.objects.all ()
    if req.POST  == 'POST':
        form  = utils.SearchProjectForm (data = req.POST)
        if form.is_valid ():
            try:

                    #  create  a dict  neeed  
                    dict  = {
                         "indicators__in": [Indicator.objects.get (id =int (id))
                                            for id in  form.cleaned_data["indicators"]],
                         "villages__in"  : [IndicatorVillage.objects.get (id =int (pk))
                                            for pk in form.cleaned_data["villages"] ],
                         "name" : form.cleaned_data ["name"]}
                    project_search_args  =_project_search_args ()
                    projects =Project.objects.filter (**dict).all ()            
            except Exception  ,e :
                #raise 
                projects  = Project.objects.all ()                
    template ='indicator/search_project.html'
    return render_to_response (req , template , {"projects" : projects ,"form" : form})

def list_project(req , pays):
    '''Go to list projects'''
    return render_to_response (req,"indicator/list_project.html" ,{ "projects":Project.objects.all()})



def project_indicators (req , id):
     project = get_object_or_404 (Project , pk  = id)
     return   render_to_response (req , 'indicator/project_indicators.html' ,{'indicators':project.indicators.all()}) 


def edit_submission (req , submission_pk):
    '''Edit Submission '''
    dict =[]
    msg  =[]
    submission = get_object_or_404 (Submission , pk =submission_pk)
    fiche  = submission.fiche
    indicatorvalues  = submission.indicatorvalues.all ()
    form_class  =fiche.form_edit(submission ,indicatorvalues)
    form = form_class ()
    if req.method =="POST":
        form =  form_class(req.POST)
        if form.is_valid ():
            #Tous les indicateurs    
            for k , val in form.cleaned_data.items ():
                pk_indicator = k.split ("_")[-1]
                indicator = Indicator.objects.get (pk =pk_indicator)
                # si le type est un type list  alors  on cree les indicateurs values
                # correspondants
                # sinon on cree l'indicateur  value correspondant              
                if type (val)==list :
                    for v in val:     
                        indicator_value = get_object_or_404(IndicatorValue , id =int (v))
                        submissi.indicatorvalues.add(indicator_value)           
                else:
                    submission.indicatorvalues.get_or_create(indicator = indicator, value =val)
            msg.append ("Les elements precedents sont bien sauvegarde")

    template ="indicator/edit_submission.html"
    
    return render_to_response (req, template  , {"form": form  , "submission": submission , "msg": msg , "submissions": Submission.objects.all ()})


def  delete_submission(req , id):
    submission = get_object_or_404 (Submission,pk =id)
    template = "indicator/confirm_delete.html"
    if req.POST == 'POST':
        try:
            req.POST.get ("confirm_delete")
            submission.delete ()
            return HttpResponseRedirect (reverse('parametrage_project'))  
        except KeyError , err:
            pass
        
    return render_to_response(req, 
         template , {})

                
def add_submission (req , fiche_id, pays_id):
    '''Get a request '''
    pays   = get_object_or_404(Pays , pk =pays_id)
    msg    = []
    fiche  = get_object_or_404(Fiche , pk=fiche_id)
    indicators  = fiche.indicators.all ()
    p = Paginator (indicators , ITEM_PER_PAGE)
    submission =None
    try:
            page = int (req.GET.get ("page")) 
    except Exception :
            page = 1
    try:
            indicators = p.page (page)
            form_class = fiche.form_save (indicators.object_list)
            form = form_class ()
    except EmptyPage :
            form =None
            pass
    submission_id =None
    try:
        submission_id = req.GET.get('submission_id')
    except :
        pass
    form_header =None 
    if page ==1 :
        # Add  form to allow user choice the suprvisor's name  ,
        # The date of submission  and the village  from data
        #form_header =HeaderSubmissionForm ()
        #form_header  =utils.VillageFormForSubmission (**{"area_of_contry": get_area_of_contry(pays)})
        data          = filter_area(pays ,req.POST ) or  get_area_of_contry(pays)
        form_header   = utils.VillageFormForSubmission (**{"area_of_contry": data})
    if req.method =='POST' and "filtre" not in req.POST:
        form  = form_class (req.POST)
        if form.is_valid ():
            try:
                    # Si une premiere partie du form a deja ete  valide  , donc
                    # si il existe deja une  submission
                    # Sinon , nous  somme a la premiere etate de la saisie 
                    if "submission_id" in req.POST:
                         if req.POST.get('submission_id').isdigit():
                             submission    = get_object_or_404 (Submission , pk =req.POST.get('submission_id'))
                    if not submission:
                        #  Recuperer la submission deja existante
                        submission    = Submission.objects.create(fiche= fiche)
                        submission_id = submission.pk  
                    # Add header informations to the submission like
                    # The village  , date edition
        
                    # Mettre  l'entete s'il   y'a lieu
        
                    # A cet  instant on commence  la submssion donc a l'ecran un
                    # Dans l'entete  , nous avons le nom du village  , la date  date la saisie
                    # enfin si necessaire le superviseur de la fiche qu'on saisie
                    #form_header  = HeaderSubmissionForm(req.POST)
                    data         = filter_area(pays ,req.POST ) or  get_area_of_contry(pays)
                    form_header  = utils.VillageFormForSubmission (req.POST, **{"area_of_contry": data})
                    if form_header.is_valid ():
                        data  = form_header.cleaned_data 
                        # Le village 
                        #return HttpResponse ([ "%s:%s</br>" % (i , j)  for (i,j) in data.items()])
                        #get only one village peer submission ,beacause each edtion is reated to one village
                        submission.village   =  IndicatorVillage.objects.get (pk = int( data ['villages'][0]))
                        # La date 
                        submission.date      =  data ['date']
                    submission.save ()
                    indicator_input_values   =[]
                    for k , val in form.cleaned_data.items ():
                        pk_indicator = k.split ("_")[-1]
                        indicator = Indicator.objects.get (pk =pk_indicator)
                        # Si l'indicateur est de  type list  dans ce cas  plusieurs  valeurs
                        # sont crees autant d'element de  la   list
                        if type (val)==list :
                            # This is a indicator list 
                            edited_value_for_type_list  =[]
                            for v in val:
                                indicator_value= get_object_or_404(IndicatorValue , id =int (v))
                                #submission.indicatorvalues.add(indicator_value)
                                edited_value_for_type_list.append (indicator_value.value)
                            submission.indicatorvalues.get_or_create(indicator =indicator, value = ":".join (edited_value_for_type_list))
                        else:
                            # Si non un seul element est cree nous somme en  presence d'un numeric  , text ou double
                            submission.indicatorvalues.get_or_create(indicator = indicator, value =val)
                    # Now we can save the  submission
                    submission.save ()
                    msg.append ("Les elements precedents sont bien sauvegarde")
            except:
              msg.append ("Erreur dans la saisie, verifier que tous les champs sont saisies")
    template = 'indicator/add_submission.html'
    return render_to_response ( req ,template , {"indicators":indicators ,"submissions": Submission.objects.all () ,
        "form": form  ,"fiche": fiche,"msg" : msg  , "submission_id" :submission_id , 'form_header' : form_header})          

def _init_indicator_value_from_indicator (values  , indicator):
     ''' create a list fo indicateur values , initialise it  '''
     for value in values:
          IndicatorValue.objects.create (value =  value  , indicator = indicator)
     
def add_indicator(req):
    '''Here we are going to define  our indicator , by adding a basic indicator form and a list .
    Creation des indicateurs ici , en specifiant le type et les valeurs si 'indicateur est de type list
    [FR.]
    Pour un indicateur , trois type de valeur sont disponible  , text , date , numeric
    Si un indicateur est de  type text ou numeric , on cree un  indicateur value ,avec submission null
    et avec value = text ou value  = numeric .
    Si l'indicateur est de type list alors nous creeons un indicateurvalue avec une submission vide
    et avec value  =list des valeurs saisies par l'administateur.'''
    form =IndicatorForm ()
    form_value =IndicatorValueForm ()
    template = "indicator/add_indicator.html"
    msg  = []
    if req.method   ==  "POST":
        form = IndicatorForm (req.POST)
        form_value =IndicatorValueForm(req.POST) 
        if form.is_valid ():
            # Nous enregistrons l'indicateur  sans  ses valeurs 
            indicator =form.save ()
            try:

                        value =form_value.save(commit =False)
                        values  =  list ()
                        # value doit etre remplit que lorsque  l'indicateur est  de type list
                        #si ce n'est pas le cas donc  value  ne doit pas  etre  rempli
                        # L'indicateur  n'est pas de type list   et  value n'est pas vide probleme
                        if value.value.strip()!=""  and indicator.type !=Indicator.TYPE_LIST:
                            raise forms.ValidationError("La liste des valeurs doit etre saisie si l'indicateur est de type list")
                        # L'indicateur est de type list donc  value est vide donct probleme
                        # si l'indicateur est de type list donc  value  doit etre automatiquement  remplit 
                        if value.value.strip()==""  and indicator.type ==Indicator.TYPE_LIST:
                            raise forms.ValidationError("La liste des valeurs est obligatoire si l'indicateur est de type list") 
                        # L'indicateur est de type text 
                        if indicator.type ==Indicator.TYPE_TEXT:
                             values =  ['text']
                        # L'indicateur est de type date 
                        elif indicator.type ==Indicator.TYPE_DATE:
                             values  =['date']
                        # l'indicateur est de type numeric
                        elif indicator.type ==Indicator.TYPE_NUMERIC:
                             values = ['numeric']
                        # L'indicateur est de type list   alors  split sur les indicateurs  et cree les
                        # indicateurs  values  correspondants
                        elif indicator.type ==Indicator.TYPE_LIST:
                            values  = [v for  v  in value.value.split ('\r\n')  if v.strip() !='' ]
                        else :
                              pass
                        if len (values)>0:
                              # Si il y'a lieu  de creer  les indicateur  values
                              _init_indicator_value_from_indicator (values , indicator)
                        msg.append (_("OK"))
            except forms.ValidationError as err:
                indicator.delete()
                #return HttpResponse (str(err))
                msg.append (str(err))
        else :
            msg.append(form.errors)
            msg.append (form_value.errors)
            #return HttpResponse (form.errors)
    return render_to_response (
            req, template , {"form":form , "form_value": form_value ,"msg": msg,"indicators" : Indicator.objects.all ()})

def edit_indicator(req , id):
     indicator = get_object_or_404(Indicator , pk =id)
     form  = IndicatorForm(instance = indicator)
     form_value = IndicatorValueForm (initial = {'value': indicator.expected_values})
     msg  = []
     if req.method  =='POST':
          form =IndicatorForm (data = req.POST , instance=indicator)
          form_value =IndicatorValueForm(req.POST) 
          if form.is_valid ():
               indicator = form.save ()
               try:
                      value =form_value.save(commit =False)
                      values  =  list ()
                      if value.value.strip()!=""  and indicator.type !=Indicator.TYPE_LIST:
                         raise forms.ValidationError("La liste des valeurs doit etre saisie si l'indicateur est de type list")
                      if value.value.strip()==""  and indicator.type ==Indicator.TYPE_LIST:
                              raise forms.ValidationError("La liste des valeurs est obligatoire si l'indicateur est de type list") 
                      if indicator.type ==Indicator.TYPE_TEXT:
                              values =  ['text']
                      elif indicator.type ==Indicator.TYPE_DATE:
                              values  =['date']        
                      elif indicator.type ==Indicator.TYPE_NUMERIC:
                              values = ['numeric']    
                      elif indicator.type ==Indicator.TYPE_LIST:
                              values  = [v for  v  in value.value.split ('\r\n')  if v.strip() !='' ]
                      else :
                              pass
                      if len (values)>0:
                              # Delete the old incator value init , we are sur that it  exit
                              # I dont think that we need to try catch an exception
                              # because the indicator have a value init , I am sure  , ;) not sure
                              try:
                                   indicator.values.filter (submission__isnull =True).delete()
                              except Exception as e :
                                        pass
                              #create init values
                              _init_indicator_value_from_indicator (values , indicator)
                      msg.append (_("OK"))
                      
               except forms.ValidationError as err:
                     #return HttpResponse (str(err))
                     msg.append (str(err))
          else :
            msg.append(form.errors)
     template  = 'indicator/add_indicator.html'
     return render_to_response(req,template,
        { 'form' :form ,'msg': msg , 'form_value' :form_value,'indicators':Indicator.objects.all()}) 


def search_indicator (req):
    template ="indicator/search_indicator.html"
    form = SearchIndicatorForm()
    msg =[]
    indicators  = Indicator.objects.all ()
    if req.method  =="POST":
        form =SearchIndicatorForm (req.POST)
        if form.is_valid ():
            ind = form.cleaned_data ["name"]
            indicators  = Indicator.objects.filter (name__icontains =str(ind))
            if not len(indicators):
                msg.append (_("La recherche n'a rien donnee"))
                indicators = Indicator.objects.all ()
            else :
                msg.append (_("La recherche a touve ces indicateurs"))
    return  render_to_response(req,template , {"msg": msg , "indicators": indicators  ,"form": form})

def  delete_indicator(req , id):
    indicator = get_object_or_404 (Indicator,pk =id)
    template = "indicator/confirm_delete.html"
    if req.method  == "POST":
        try:
            req.POST.get ("confirm_delete")
            indicator.delete ()
            return HttpResponseRedirect (reverse("add_indicator"))
        except KeyError , err:
            pass 
    return render_to_response(req, 
         template , {})
    
    
def delete_region (req , id ,name):
    """
    Delete area  , region, departement , village
    district .....
    """    
    # GEt the  model class to delete
    model  = getattr (models , name.capitalize())
    # Get the class'name 
    cls_name     = model.__name__
    # Get class 's instance
    region  = get_object_or_404 (model  , pk  =id)
    # Delete the instance
    region.delete ()
    return render_to_response (req, "indicator/parametrage.html" , {"msg" :["La %s a ete  supprimee"%cls_name]})    

def edit_region (req , id , name):
    """
    Delete area ,region , departement , village
    """
    model_form_dict ={"region" : "RegionForm_" , 
    "arrondissement": "ArrondissementForm" ,
    "communearrondissement": "CommuneArrondissementForm" ,
    "commune":"CommuneForm" ,
    "departement":"DepartementForm",
    "district" :"DistrictForm" ,
    "etat" : "EtatForm" ,
    "secteur": "SecteurForm" ,
    "prefecture" :"PrefectureForm" ,
    "subprefecture":"SubPrefectureForm" ,
    "indicatorvillage":"IndicatorVillageForm" 
    }
    form  = getattr (forms , model_form_dict.get (name))
    model = getattr (models , name.capitalize())
    region= get_object_or_404 (model , pk  =id)
    form_instance  =form(instance  = region)
    if req.method  == "POST":
        form_instance  = form (req.POST , instance  =region)
        if form_instance.is_valid():
                form_instance.save ()
    return render_to_response (req, "indicator/edit_region.html" , 
    {"msg" :["La %s a ete  supprimee"]  , "form" :form_instance})    


def list_indicator (req):
    ''' list all indicator '''
    '''Go to list projects'''
    return render_to_response (req,"indicator/list_indicator.html" ,{ "indicators":Indicator.objects.all()})


def  delete_project(req , id):
    project= get_object_or_404 (Project,pk =id)
    template = "indicator/confirm_delete.html"
    if req.method == 'POST':
        try:
            req.POST.get ("confirm_delete")
            project.delete ()
            return HttpResponseRedirect (reverse("parametrage_project"))
        except KeyError , err:
            pass 
    return render_to_response(req, 
         template , {} )


def search_user (req):
    '''
    Get form to search new user
    '''
    form = UserSearchForm()
    msg  = []
    users  = User.objects.filter (groups__name="indicator_edit")
    if req.method  =='POST':
        form  = UserSearchForm(req.POST)
        if form.is_valid ():
           data  = form.cleaned_data
           users  =User.objects.filter (
                    Q(username__icontains=data['first_name'])| Q(username__icontains=data['last_name']))
    template ="indicator/add_user.html"
    return render_to_response (req , template ,
    {"form": form ,"users" : users,"msg" : msg})


        
def project_exports(req):
    '''Provide a list of projets  and  let us the user to choice one projet for export
    IF no indicator are selected , all will be exported ,'''
    form =ProjectExportForm ()
    if req.method =="POST":
#        form  = ProjectExportForm(req.POST)
#        if form.is_valid (): 
#            data = form.cleaned_data
#            projects= data ["projects"]
#            if len (projects):
#                 return  export(projects)
#            else :
#                 return  export(Project.objects.all ())
             return  export(Project.objects.all ())
    template = "indicator/project_exports.html"
    return render_to_response (req,template , {"form": form})
         
def indicator_exports (req):
    '''Let the user choice one indicator and the list of projects linked , if no project
    is selected all project are considered'''
    form =IndicatorExportForm ()
    if req.method=="POST":
        form =IndicatorExportForm (req.POST)
        if form.is_valid ():
#            data = form.cleaned_data
#            indicators= data ["indicators"]
#            if len(indicators):
#               return  export (indicators)
            return  export(Indicator.objects.all() , 
            ["name" ,"type", "period"  , "modified" , "created","description" ,"values"])
    template = "indicator/indicator_exports.html"
    return render_to_response (req, template , {"form": form})
 
def data_export (req):
    form  = DataExportForm()
    if req.method=="POST":
        form =DataExportForm(req.POST)
        if form.is_valid ():
            return export (Submission.objects.all () ,
        ["date" , "fiche", "village" ,"project" ,"date" ,"indicatorvalues"])
    template ='indicator/data_export.html'
    return render_to_response (req,template , {'form': form})
              
def user_exports (req):
    '''Export the users_list'''
    form = UserExportForm()
    msg  = []
    if req.method =="POST":
        form  = UserExportForm(req.POST)
        if form.is_valid ():
            users   = form.cleaned_data ['users']
            if len (users):
                return export(users)
            return  export (User.objects.filter (groups__name__in = ['indicator_edit', 'indicator_admin']))
    template = "indicator/user_exports.html"
    return render_to_response (req,template ,{"form": form})
   
def village_exports(req):
    '''Export  village list'''
    form = VillageExportForm()
    if req.method =="POST":
        form  = VillageExportForm(req.POST)
        if form.is_valid ():
               villages   = form.cleaned_data ['villages']
               if len(villages):
                   return export(villages)
               return  export (IndicatorVillage.objects.all ())
    template = "indicator/village_exports.html"
    return render_to_response (req,template ,{"form": form})

def stats (req):
    template ="indicator/index_stats.html"
    return render_to_response (req, template  , {})

def project_stats (req):
    '''Dashorboard project stat '''
    form =ProjectStatForm ()
    dict ={}
    data  ='[1000 ,500]'
    if req.method  =='POST' :
        form  = ProjectStatForm(req.POST)
        if form.is_valid (): 
            d  =form.cleaned_data
            village , indicator , project , date1 ,date2  = d ["village"] , d["indicator"] ,d["project"] ,d["date1"] ,d["date2"]
            try:
                submission1  = Submission.objects.filter (village =village , fiche__project = project , date__month =date1.month)[0]
                submission2  = Submission.objects.filter (village =village , fiche__project = project , date__month =date2.month)[0]
                data      ='[%s,%s]'%( int (submission1.indicatorvalues.filter (indicator = indicator)[0].value),
                                int(submission2.indicatorvalues.filter (indicator = indicator)[0].value))
            except :
                pass 
    template = "indicator/project_stats.html"
    return render_to_response (req,template , {"form": form  , "data"  : data })

def user_stats (req):
     ''' Nothing  to display here we will see later what-to-do '''
     return HttpResponseRedirect (reverse ('indicator_dashboard'))

def add_user (req):
    '''Add new user'''
    form = UserForm()
    msg  = []
    if req.method  == 'POST':
        form  = UserForm(req.POST)
        if form.is_valid ():
             try:
                 form.save ()
                 msg.append (_("Element sauvegarge"))
             except Exception , err:
                 msg.append (str(err))
    template ="indicator/add_user.html"
    return render_to_response (req , template ,
    {"form": form ,"users" : User.objects.filter (groups__name__in = ['indicator_edit', 'indicator_admin']),"msg" : msg})

def edit_user (req , id):
    '''Edit new user'''
    user  = get_object_or_404(User ,pk =id)
    form  = UserForm(initial ={
        'first_name' : user.first_name  ,
        'last_name' : user.last_name ,
        'username': user.username ,
        'password' :''})
    msg  = []
    if req.method == 'POST':
      form  = UserForm(req.POST)
      if form.is_valid ():
            form.save()
            msg.append (_("Modification a ete  effectue"))
    template ="indicator/add_user.html"
    return render_to_response (req , template ,
    {"form": form ,'users':User.objects.filter (groups__name__in = ['indicator_edit', 'indicator_admin']),"msg" : msg})

          
def export(qs , header =None):
    #return HttpResponse (map (lambda f :f.name, qs[0]._meta.fields))
    if not qs or not len (qs):
        response = HttpResponse (mimetype ="text/csv")
        response ["Content-Disposition"]="attachment; filename =export.xls"
        return response
    fields =qs[0]._meta.fields
    if not header:
        header = map (lambda f :f.name , fields)
    response = HttpResponse (mimetype ="text/csv")
    response ["Content-Disposition"]="attachment; filename =export.xls"
    w= UnicodeWriter(response)
    w.writerow(header)
    for q in qs:
        row =[]
        for h in header:
            val =getattr (q, h)
            if isinstance (val , Manager):
                 val  =val.all()
                 val  =u",".join ([unicode(v) for v in val])
            else:
                if callable (val):
                    val =val ()
                elif hasattr (q , "get_"+ h + "_display"):
                    val = getattr (q , "get_" + h + "_display")()
                elif isinstance (val ,datetime):
                    val =u"%s-%s-%s"%(val.year , val.month , val.day)
                else :
                    val = u"%s"%val
            row.append (val.encode("latin"))
        w.writerow (row)
    return response
        
        
class UnicodeWriter(object):
        """ 
    A unicode Writer helper that allow us to write
        any given encoding , default is utf-8
        """
        def __init__ (self,stream , dialect ="excel-tab" , encoding= "utf-8",**kw):   
          self.queue = cStringIO.StringIO()
          self.writer = csv.writer (self.queue ,dialect =dialect)
          self.encoder = codecs.getincrementalencoder (encoding)()
          self.stream =stream

        def writerow(self, row):
           self.writer.writerow([unicode (s , "latin").encode('utf-8')  for s in row])
           # Get data from queue
           data = self.queue.getvalue ()
           # Decode to unicode
           data = data.decode ("utf-8")
           # Reencode from given encoding
           self.encoder.encode (data)
           # write into stram
           self.stream.write (data)
           self.queue.truncate (0)





#def get_pays_form (pays):
def  get_area_of_contry (pays):
    '''
    Pour chaque pays nous devons lui permettre de selectionner 
    les villages , ou secteurs , ou  regions a ajouter au projet
    '''
    name  =  pays.name.upper()
    if name  == 'GUINEE_CONAKRY': 
       return  (("regions", cast_region (pays)),
                ("prefectures", cast_prefecture (pays)),
        ("subprefectures", cast_sub_prefecture (pays)),
        ("villages",   cast_village(pays , "GUINEE_CONAKRY")))
    elif name  == 'GUINEE_BISSAU':
        return (("regions" , cast_region(pays)) ,
                ("secteurs" ,  cast_secteur(pays)),
                ( "villages" ,  cast_village(pays , "GUINEE_BISSAU")))
    elif name  == 'GAMBIE' :
       return  (("regions",  cast_region(pays)),
                ("districts" ,  cast_district (pays)),("villages" , (pays , "GAMBIE")),)
    elif name  == 'SENEGAL' :
        return (( "regions" , cast_region (pays)) ,  ( "departements" ,  cast_departement (pays)),
                ("arrondissements" , cast_arrondissement (pays)),
                ("commune_arrondissements" ,  cast_commune_arrondissement (pays)),
                 ("communes",cast_commune (pays)) ,( "villages"  ,   cast_village (pays , "SENEGAL")))
    elif name  == 'SOMALIE' :
        return  (("etats" ,      cast_etat (pays)),
                 ("regions"  ,  cast_region (pays)),("villages" ,   cast_village (pays , "SOMALIE")))
    elif name  == 'DJIBOUTI':
        return  (("regions",  cast_region (pays)),
                  ("villages", cast_village (pays , "DJIBOUTI")))
    elif name  == 'MAURITANIE':
       return (("regions", cast_region (pays)),
               ( "departements", cast_departement (pays)),
               ( "villages", cast_village (pays ,"MAURITANIE")))
    else :
        return []
   
village_parent_object_dict  = {'SENEGAL' :Commune   ,'GUINEE_CONAKRY' : SubPrefecture ,'GUINEE_BISSAU' : Secteur  ,
    'GAMBIE' :District ,'SOMALIE' :Region ,'DJIBOUTI' : Region  ,'MAURITANIE': Departement}
 
def _get_area_of_contry2(pays):
    '''
    Pour chaque pays nous devons lui permettre de selectionner 
    les villages , ou secteurs , ou  regions a ajouter au projet
    '''
    name  =  pays.name.upper()
    if name  == 'GUINEE_CONAKRY': 
       return  (("regions", cast_region (pays)),
                ("prefectures", cast_prefecture (pays)),
                ("subprefectures", cast_sub_prefecture (pays)))
    elif name  == 'GUINEE_BISSAU':
        return (("regions" , cast_region(pays)) ,
                ("secteurs" ,  cast_secteur (pays)))
    elif name  == 'GAMBIE' :
       return  (("regions",  cast_region(pays)),
                ("districts" ,  cast_district (pays)))
    elif name  == 'SENEGAL' :
       return (( "regions" , cast_region (pays)) ,
               ("departements" ,  cast_departement (pays)),
               ("arrondissements" , cast_arrondissement (pays)),
               ("commune_arrondissements" ,  cast_commune_arrondissement (pays)) ,
               ("communes" ,  cast_commune(pays)) ,
               )
    elif name  == 'SOMALIE' :
        return  (("etats" ,      cast_etat (pays)),
                 ("regions"  ,  cast_region (pays)))
    elif name  == 'DJIBOUTI':
        return  (("regions",  cast_region (pays)),)
    elif name  == 'MAURITANIE':
       return (("regions", cast_region (pays)),
               ( "departements", cast_departement (pays)))
    else :
        return []  
    

def filter_area (pays ,post_data):
     if pays.name.upper()  == "GUINEE_CONAKRY":
         if "subprefectures" in post_data and post_data ["subprefectures"] :
                subprefecture =Subprefecture.objects.get (pk =post_data ["subprefectures"])
                villages =[]
                for vil in subprefecture.children.all ():
                    villages.append(vil)
                return (("regions", cast_region (pays)),
                ("prefectures", cast_prefecture (pays)),
                ("subprefectures", cast_sub_prefecture (pays)),
                ("villages",   villages))
         if "prefectures" in post_data and post_data ["prefectures"] :
                prefecture =Prefecture.objects.get (pk =post_data ["prefectures"])
                villages =[]
                subprefectures =[]
                for subprefecture in prefecture.children.all ():
                        subprefectures.append (subprefecture)
                        for vil in subprefecture.children.all ():
                                villages.append(vil)
                return (("regions", cast_region (pays)),
                ("prefectures", cast_prefecture (pays)),
                ("subprefectures", subprefectures),
                ("villages",   villages))
         if "regions" in post_data and post_data ["regions"] :
                region =Region.objects.get (pk =post_data ["regions"])
                villages =[]
                subprefectures =[]
                prefectures    =[]
                for prefecture in region.children.all ():
                    prefectures.append (prefecture)
                    for subprefecture in prefecture.children.all ():
                            subprefectures.append(subprefecture)
                            for vil in subprefecture.children.all ():
                                    villages.append(vil)
                return (("regions", cast_region (pays)),
                ("prefectures", prefectures ),
                ("subprefectures", subprefectures),
                ("villages",   villages))
     if pays.name.upper() == "GUINEE_BISSAU":
         if "secteurs" in post_data and post_data ["secteurs"] :
                secteur =Secteur.objects.get (pk =post_data ["secteurs"])
                villages =[]
                for vil in secteur.children.all ():
                    villages.append(vil)
                return (("regions", cast_region (pays)),
                ("secteurs", cast_secteur (pays)),
                ("villages",   villages))
         if "regions" in post_data and post_data ["regions"]:
                region =Region.objects.get (pk =post_data ["regions"])
                villages =[]
                secteurs =[]
                for secteur in region.chidlren.all ():
                    secteurs.append(secteur)
                    for vil in secteur.children.all ():
                        villages.append(vil)
                return (("regions", cast_region (pays)),
                ("secteurs", secteurs),
                ("villages",   villages))
     if pays.name.upper() == "GAMBIE":
         if "disticts" in post_data and post_data ["disticts"]:
                district =Distict.objects.get (pk =post_data ["disticts"])
                villages =[]
                for vil in district.children.all ():
                    villages.append(vil)
                return (("regions", cast_region (pays)),
                ("districts", cast_district(pays)),
                ("villages",   villages))
         if "regions" in post_data and post_data ["regions"]:
                region =Region.objects.get (pk =post_data ["regions"])
                villages =[]
                disticts =[]
                for district in region.chidlren.all ():
                    districts.append(secteur)
                    for vil in district.children.all ():
                        villages.append(vil)
                return (("regions", cast_region (pays)),
                ("districts", districts),
                ("villages",   villages))
                
     if pays.name.upper() == "SENEGAL":
         if "communes" in post_data and post_data ["communes"]:
                commune =Commune.objects.get (pk =post_data ["communes"])
                villages =[]
                for vil in commune.children.all ():
                    villages.append(vil)
                return(("regions", cast_region (pays)),
                ("departements" ,  cast_departement (pays)),
               ("arrondissements" , cast_arrondissement (pays)),
               ("commune_arrondissements" ,  cast_commune_arrondissement (pays)) ,
                ("communes", cast_commune(pays)),
                ("villages",   villages))
                
         if "commune_arrondissements" in post_data  and post_data ["commune_arrondissements"]:
                commune_arrondissement =CommuneArrondissement.objects.get (pk =post_data ["commune_arrondissements"])
                villages =[]
                communes =[]
                for commune in commune_arrondissement.children.all ():
                    communes.append(commune)
                    for vil in commune.children.all ():
                        villages.append(vil)
                return(("regions", cast_region (pays)),
                ("departements" ,  cast_departement (pays)),
               ("arrondissements" , cast_arrondissement (pays)),
               ("commune_arrondissements" ,  cast_commune_arrondissement (pays)) ,
                ("communes", communes),
                ("villages",   villages))
                
         if "arrondissements" in post_data and post_data ["arrondissements"]:
                arrondissement =Arrondissement.objects.get (pk =post_data ["arrondissements"])
                villages =[]
                communes =[]
                commune_arrondissements =[]
                for commune_arrondissement in arrondissement.children.all ():
                    commune_arrondissements.append(commune_arrondissement)
                    for commune in commune_arrondissement.children.all ():
                        communes.append (commune)
                        for vil in commune.children.all ():
                            villages.append(vil)
                return(("regions", cast_region (pays)),
                ("departements" ,  cast_departement (pays)),
               ("arrondissements" , cast_arrondissement (pays)),
               ("commune_arrondissements" , commune_arrondissements) ,
                ("communes", communes),
                ("villages",   villages))
                
         if "departements" in post_data and post_data ["departements"]:
                departement =Departement.objects.get (pk =post_data ["departements"])
                villages =[]
                communes =[]
                commune_arrondissements =[]
                arrondissements  =[]
                for arrondissement in departement.children.all ():
                    arrondissements.append(arrondissement)
                    for commune_arrondissement in arrondissement.children.all ():
                        commune_arrondissements.append (commune_arrondissement)
                        for commune in commune_arrondissement.children.all ():
                            communes.append(commune)
                            for vil in commune.children.all ():
                                villages.append(vil)
                return(("regions", cast_region (pays)),
                ("departements" ,  cast_departement (pays)),
               ("arrondissements" , arrondissements),
               ("commune_arrondissements" , commune_arrondissements) ,
                ("communes", communes),
                ("villages",   villages))
                
         if "regions" in post_data and post_data ["regions"]:
                region =Region.objects.get (pk =post_data ["regions"])
                villages =[]
                communes =[]
                commune_arrondissements =[]
                arrondissements  =[]
                departements  =[]
                for departement in region.children.all ():
                        departements.append(departement)
                        for arrondissement in departement.children.all ():
                            arrondissements.append (arrondissement)
                            for commune_arrondissement in arrondissement.children.all ():
                                commune_arrondissements.append(commune_arrondissement)
                                for commune in commune_arrondissement.children.all ():
                                    communes.append(commune)
                                    for vil in commune.children.all ():
                                        villages.append(vil)
                return(("regions", cast_region (pays)),
                ("departements" ,  departements),
               ("arrondissements" , arrondissements),
               ("commune_arrondissements" , commune_arrondissements) ,
                ("communes", communes),
                ("villages",   villages))
     if pays.name.upper() == "SOMALIE":
         if "regions" in post_data and post_data["regions"]:
                region =Region.objects.get (pk =post_data ["regions"])
                villages =[]
                for vil in region.children.all ():
                    villages.append(vil)
                return  (("etats" , cast_etat (pays)),
                 ("regions"  ,  cast_region (pays)) ,
                 ("villages" , villages))
                
         if "etats" in post_data and post_data["etats"] :
                etat =Etat.objects.get (pk =post_data ["etats"])
                villages =[]
                regions  =[]
                for region in etat.children.all ():
                    regions.append(region)
                    for vil in region.children.all ():
                        villages.append(vil)
                return  (("etats" ,  cast_etat (pays)),
                 ("regions"  , regions) ,
                 ("villages" , villages))
                
     if pays.name.upper()  == "SOMALIE":
         if "regions" in post_data and post_data["regions"] :
                region =Region.objects.get (pk =post_data ["regions"])
                villages =[]
                for vil in region.children.all ():
                    villages.append(vil)
                return  (("regions",  cast_region (pays)),
                         ("villages" , villages))          
     if pays.name.upper()  == "MAURITANIE":
         if "departements" in post_data and post_data["departements"]:
                departement =Departement.objects.get (pk =post_data ["departements"])
                villages =[]
                for vil in departement.children.all ():
                        villages.append(vil)
                return (("regions", cast_region (pays)),
               ( "departements", cast_departement (pays)),
               ("villages" , villages))
         if "regions" in post_data:
                region =Region.objects.get (pk =post_data ["regions"])
                villages =[]
                departements =[]
                for departement in region.children.all ():
                    departements.append(departements)
                    for vil in departement.children.all ():
                            villages.append(vil)
                return (("regions", cast_region (pays)),
               ( "departements", departements),
               ("villages" , villages))
     return None 
         
         
   
 
         
                    
               
       
