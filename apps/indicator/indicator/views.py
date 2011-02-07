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
from .utils import _get_village_form ,  _get_indicator_form ,  _get_submission_form ,_get_search_project_form , _get_area_form
# The number of indicator displayed into edition  by page 
import codecs
import csv
import cStringIO

ITEM_PER_PAGE = 2

def index (req):
    '''Go to indicator dashboard page'''
    return render_to_response (req,"indicator/index.html" , {})

@login_required
def edition_fiche (req):
    '''Go to indicator dashboard page'''
    return render_to_response (req,"indicator/edition_fiche.html" ,\
           { "projects":Project.objects.all()})

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
    if req.method.lower ()=="post":
        form =PaysForm (req.POST)
        if form.is_valid ():
            form.save ()
            msg.append (_("Element sauvegarde"))
            return render_to_response (req,template , {"form": form ,"pays":Pays.objects.all () ,\
                 "msg"  : msg })
        else :
            msg.append (_("Erreur dans le formulaire"))
            #msg.append (form.errors)  
    else :
        form  = PaysForm ()    
    return render_to_response (req, template , {"form" : form , "pays" : Pays.objects.all () , 
            "msg": msg })
    
def add_region (req, id):
    '''if senegal , flatten  pays to regions'''
    pays  = get_object_or_404(Pays ,name__icontains = id )
    regions = [pays]
    msg = []
    #as tuple to fill the form choice fields dynamique 
    if id.lower() =="somalie":
        regions  =cast_etat (pays)
    else :
        regions  =[pays]
    data = as_tuple (regions) 
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            Region.objects.create (parent =pays , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_region.html",{"form" : form ,\
                  "msg": msg,"regions": Region.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_region.html", {"form" : form ,\
          "msg": msg,"regions": Region.objects.all () })
    
def  edit_pays (req , id ):
    '''Edit the given contry'''
    msg = list ()
    template = "indicator/edit_pays.html"
    contry =  get_object_or_404 (Pays , pk = id)
    form = PaysForm (instance = contry)
    if req.method.lower () == "post":
            form  = PaysForm (req.POST)
            if form.is_valid ():
                form.save ()
                msg.append (_("Element sauvegarde"))
                return render_to_response (req , template , {"form" : PaysForm (),\
                    "pays" : Pays.objects.all (),"msg" : msg })
            else :
                msg.append (_("Erreur dans le formulaire"))
    return render_to_response (
            req ,template  , {"form": form,"pays" : Pays.objects.all ()})
    
def delete_pays (req, id):
    '''Given an contry , delete it'''
    template = "indicator/confirm_delete.html"    
    contry  = get_object_or_404 (Pays , pk = id )
    if req.method.lower () =="post":
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
    return [ (q.pk , q.__unicode__()) for q in qs]
        
def add_commune (req , pays):
    '''Add new commune'''
    pass
def add_communaute_rurale (req):
    '''Add new rurale community'''
    pass

def add_commune_arrondissement(req, pays):
    '''Add new commune '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    regions= cast_arrondissement(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Arrondissement.objects.get (pk =req.POST["region"])
            CommuneArrondissement.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_commune_arrondissement.html",
              {"form" : form, "msg": msg,"regions": CommuneArrondissement.objects.all ()})
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_region.html",{"form" : form ,\
          "msg": msg,"regions": CommuneArrondissement.objects.all ()})

def add_commune (req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    regions= cast_commune_arrondissement(pays)    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = CommuneArrondissement.objects.get (pk =req.POST["region"])
            Commune.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_commune.html",{"form" : form ,\
             "msg": msg,"regions": Commune.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_commune.html",{"form" : form ,\
          "msg": msg,"regions": Commune.objects.all ()})

def add_arrondissement (req, pays):
    '''if senegal , flatten  pays to regions'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    regions = cast_departement (pays)    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Departement.objects.get (pk =req.POST["region"])
            Arrondissement.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_arrondissement.html",\
             {"form" : form ,"msg": msg,"regions": Arrondissement.objects.all () } )
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_arrondissement.html",{"form" : form,"msg": msg,\
        "regions": Arrondissement.objects.all() })

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

def cast_village (top , pays_name):
    '''
    Get villages chidrens ,only the village 
    The parent of the village can be :
        *a commune if senegal*
        *a sub prefecture if guinee*
        *a secteur if gambie*
        ...
        ... '''
    coms  = []
    if pays_name  ==conf.senegal:
        com_arrs= cast_commune(top)
    elif pays_name ==conf.konakry:
        com_arrs= cast_sub_prefecture(top)
    elif pays_name == conf.bissau:
        com_arrs= cast_secteur(top)
    elif pays_name == conf.gambie:
        com_arrs= cast_district(top)
    elif pays_name == conf.somalie:
        com_arrs= cast_region(top)
    elif pays_name ==conf.djibouti:
        com_arrs= cast_region(top)
    elif pays_name ==conf.mauritanie:
        com_arrs= cast_departement(top)
    else :
        com_arrs=None
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
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Departement.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_departement.html",{"form" : form ,\
                  "msg": msg, "regions": Departement.objects.all ()})
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_region.html",
             {"form" : form ,"msg": msg,"regions": Departement.objects.all ()})
    
def add_village (req, id):
    '''Add new village'''
    pays  = get_object_or_404(Pays ,name__icontains = id )
    regions =[]
    if id.lower () == conf.senegal:
        regions= cast_commune(pays)
    elif id.lower()==conf.konakry:
        regions =cast_sub_prefecture (pays)
    elif id.lower()==conf.bissau:
        regions = cast_secteur (pays)
    elif id.lower()==conf.gambie:
        regions = cast_district (pays)
    elif id.lower()==conf.somalie:
        regions = cast_region(pays)
    elif id.lower()==conf.djibouti:
        regions = cast_region(pays)
    elif id.lower()==conf.mauritanie:
        regions = cast_departement(pays)
    else :
        regions  =[]
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            if id.lower() ==conf.senegal:
                parent = Commune.objects.get (pk =req.POST["region"])
            elif id.lower()==conf.konakry:
                parent = SubPrefecture.objects.get (pk =req.POST["region"])
            elif id.lower()==conf.bissau:
                parent = Secteur.objects.get (pk =req.POST["region"])
            elif id.lower()==conf.gambie:
                parent = District.objects.get (pk =req.POST["region"])
            elif id.lower()==conf.somalie:
                parent = Region.objects.get (pk =req.POST["region"])
            elif id.lower()==conf.djibouti:
                parent = Region.objects.get (pk =req.POST["region"])
            elif id.lower()==conf.mauritanie:
                parent = Departement.objects.get (pk =req.POST["region"])
            else :
                parent  =None 
            IndicatorVillage.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_village.html",\
             {"form" : form ,"msg": msg,"regions": IndicatorVillage.objects.all ()})
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_village.html",\
         {"form" : form, "msg": msg,"regions": IndicatorVillage.objects.all ()})
    
def add_prefecture (req, pays):
    '''Add new prefecture '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    # For Guinee Konakry the region  should be casted to precture
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Prefecture.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_prefecture.html",\
            {"form" : form ,"msg": msg,"regions": Prefecture.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_prefecture.html",\
          {"form" : form, "msg": msg,"regions": Prefecture.objects.all ()})

def add_sub_prefecture (req, pays):
    '''Add new commune'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    # For Guinee Konakry , for this moment , special zone should have region as parent
    regions= cast_prefecture(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Prefecture.objects.get (pk =req.POST["region"])
            SubPrefecture.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_sub_prefecture.html",{"form" : form ,\
            "msg": msg,"regions": SubPrefecture.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
           "indicator/add_sub_prefecture.html",{"form" : form,"msg": msg,"regions": SubPrefecture.objects.all () })

def add_commune_hurbaine (req, pays):
    '''Add new commune  hurbaine'''
    pays  = get_object_or_404(Pays , name__icontains = pays )
    regions =[]
    # For Guinee Konakry , for this moment ,Commune hurbaine should have region as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            CommuneHurbaine.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_commune_hurbaine.html",
             {"form" : form ,"msg": msg,"regions": CommuneHurbaine.objects.all () } )
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_commune_hurbaine.html",
         {"form" : form, "msg": msg,"regions": CommuneHurbaine.objects.all ()})

def add_village_guinee (req, pays):
    '''Add new commune'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]    
    # For Guinee Konakry , for this moment ,Commune hurbaine should have region as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            IndicatorVillage.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_village.html",\
             {"form" : form ,"msg": msg,"regions": IndicatorVillage.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_village.html",\
         {"form" : form, "msg": msg,"regions": IndicatorVillage.objects.all ()})
            
def add_secteur (req, pays):
    '''Add new secteur'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    # For Guinee Bissau,secteur should have regions as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  =_get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Secteur.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_secteur.html",\
             {"form" : form ,"msg": msg,"regions": Secteur.objects.all ()})
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
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            District.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_district.html",\
             {"form" : form ,"msg": msg,"regions": District.objects.all () } )
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_district.html",{"form" : form, 
          "msg": msg,"regions": District.objects.all () })
    
def add_etat(req, pays):
    '''Add new etat'''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    # For Guinee Bissau,secteur should have regions as parent
    #regions= cast_region(pays)
    regions  = [pays]
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = _get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Pays.objects.get (pk =req.POST["region"])
            Etat.objects.create (parent =parent ,name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,"indicator/add_etat.html",
             {"form" : form ,"msg": msg,"regions": Etat.objects.all ()} )
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,"indicator/add_etat.html",
         {"form" : form, "msg": msg,"regions": Etat.objects.all ()})
    
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
            
def get_pays_form (pays):
    '''
    Pour chaque pays nous devons lui permettre de selectionner 
    les villages , ou secteurs , ou  regions a ajouter au projet
    '''
    def get_konakry_form():
        return {"regions": cast_region (pays),
            "prefectures": cast_prefecture (pays),
         "subprefectures": cast_sub_prefecture (pays),
               "villages": cast_village(pays , "guinee_conakry")}
    
    def get_bissau_form ():
        return {"regions":cast_region(pays) ,
               "secteurs":cast_secteur(pays),
               "villages":cast_village(pays , "guinee_bissau")}
    
    def get_gambie_form ():
        return {"regions":cast_region(pays),
              "districts":cast_district (pays),
               "villages":cast_village(pays , "gambie")}
        
    def get_senegal_form ():
        return {"regions": cast_region (pays),
        "arrondissements": cast_arrondissement (pays),
           "departements": cast_departement (pays),
"commune_arrondissements": cast_arrondissement (pays),
                #The last element list to be asspciated to the project
              "villages" :cast_village (pays , "senegal")}
    
    def get_somalie_form ():
        '''Des regions qui sont regroupes en etats'''
        return  {"etats" :cast_etat (pays),
        # The last element to be associated to the projects
              "regions"  :cast_region (pays),
              "villages" :cast_village (pays , "somalie")}
        
    def get_djibouti_form ():
        ''' Des regions '''
        # The last element list to be associated to the projet 
        return {"regions":cast_region (pays),
               "villages":cast_village (pays , "djibouti")}
    
    def get_mauritanie_form ():
        ''' Regions qui sont partages en departements '''
        return {"regions":cast_region (pays),
                # The elelements list to be associated to the projects
           "departements":cast_departement (pays),
               "villages":cast_village (pays ,"mauritanie")}
    
    name  = pays.name.lower ()
    if name  ==conf.konakry:
        return get_konakry_form () 
    elif name == conf.bissau:
        return get_bissau_form ()
    elif name == conf.gambie :
        return get_gambie_form ()
    elif name == conf.senegal:
        return get_senegal_form ()
    elif name ==conf.somalie:
        return get_somalie_form ()
    elif name == conf.djibouti:
        return get_djibouti_form ()
    elif name ==conf.mauritanie:
        return get_mauritanie_form ()
    else :
        return []
      
def indicators_list():
    #The indicator list to be associated to the project
    return {"indicators":Indicator.objects.all ()}

def  edit_project (req , id):
     msg= []
     project  = get_object_or_404(Project , pk= id)
     form  = ProjectForm (instance = project)
     if req.method  =='POST':
          #return HttpResponse ( ''.join ( [ '%s:%s \n'%(k, v)  for(k ,v) in req.POST.items ()] ))
          if 'delete' in req.POST:
               #delete request was sent
               project.delete()
               msg.append (_('Suppression reussie'))
               #Ok redirect to param project
               return HttpResponseRedirect(reverse('parametrage_project'))
          form  = ProjectForm (req.POST)
          if form.is_valid ():
               form.save()
               msg.append (_('Sauvegarde reussie'))
          else:
               msg.append (_('Formulaire invalide'))
     template  = 'indicator/edit_project.html'
     return  render_to_response (req ,  template , { 'form':form})
     
          
def add_project(req , pays):
    '''
    Each pays should have it own layout 
    Chaque pays doit avoir la liste de ces regions village , etc afin que dans 
    l'edition d'un project qu'on puisse filter et ajouter un village'''
    template = 'indicator/add_project.html'
    pays= get_object_or_404(Pays , name__icontains = pays.lower ())
    #Get the village filter form
    vil_form_data         =get_pays_form (pays)
    ind_form_data         =indicators_list()
    #Go to create dynamically a project from based on the vil_from_filter and the indicator_form
    form_village_class   =_get_village_form (vil_form_data)
    form_village         =form_village_class ()
    form_indicator_class =_get_indicator_form (ind_form_data)
    form_indicator       =form_indicator_class ()
    msg  =[]
    if req.method.lower () == "post":
        form_village   = form_village_class(req.POST)
        form_indicator = form_indicator_class (req.POST)
        if form_village.is_valid  ()  and form_indicator.is_valid ():
                try:
                   villages, indicators =[], []
                   for vil_pk in  req.POST.getlist("villages"):
                       villages.append(IndicatorVillage.objects.get (pk =vil_pk)) 
                   for ind_pk in req.POST.getlist ('indicators'):
                       indicators.append(Indicator.objects.get (pk =ind_pk))
                   dt = date = datetime.now().date ()
                   try:
                         year, month ,day  = req.POST.get( 'edited_date' ,None)
                         dt = datetime(year, month, day).date ()
                   except:
                        pass
                   # get the projet remained args from post data
                   #  bailleur , decsription  ,date creattion
                   d   =dict ()
                   args  = ['bailleur' , 'titre',
                      'description' ]
                   for key in req.POST.iterkeys ():
                             if key in  args:
                                    d[str(key)] = req.POST [key]
                   Project.create_project (villages , indicators ,**d)
                   msg.append (_("Le projet a bien ete sauvegarde"))          
                except (KeyError, Exception):
                   #print  '--*POOF*--'
                   #raise 
                   msg.append(_("Vous devez choisir le dernier element dans le filtre"))
        else:
                msg.append (_("Le formulaire est invalide ,verifiez que tous\
                    les champs obligatoires sont bien renseignes"))
    return render_to_response (req , template ,{ "form_village" : form_village ,
           "form_indicator": form_indicator , "projects" :Project.objects.all (), "msg" :msg })

def search_project (req,pays):
    '''Search a new projet'''
    form_class  =_get_search_project_form()
    form  = form_class ()
    projects  = Project.objects.all ()
    if req.POST :
        form  = form_class (req.POST)
        if form.is_valid ():
            try:
                    def _project_search_args():
                    #Help fonction , return a  dict or args to find projet
                         return  {
                         "indicators__in": [Indicator.objects.get (id =int (id))\
                                    for id in  form.cleaned_data["indicators"]],
                         "villages__in"  :[IndicatorVillage.objects.get (id =int (pk))\
                                    for pk in form.cleaned_data["villages"] ],
                         "name" : form.cleaned_data ["name"]
                    }
                    project_search_args  =_project_search_args ()
                    projects =Project.objects.filter (**project_search_args).all ()            
            except Exception  ,e :
                     #raise 
                     projects  = Project.objects.all ()
                     
    template ='indicator/search_project.html'
    return render_to_response (req , template , 
        {"projects" : projects ,"form" : form})

def list_project(req , pays):
    '''Go to list projects'''
    return render_to_response (req,"indicator/list_project.html" ,\
           { "projects":Project.objects.all()})

def project_indicators (req , id):
     project = get_object_or_404 (Project , pk  = id)
     return   render_to_response (req , 'indicator/project_indicators.html' , {'indicators':project.indicators.all()}) 
     
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
            for k , val in form.cleaned_data.items ():
                pk_indicator = k.split ("_")[-1]
                indicator = Indicator.objects.get (pk =pk_indicator)
                if type (val)==list :
                    for v in val:
                        indicator_value = get_object_or_404( IndicatorValue , id =int (v))
                        submission.indicatorvalues.add(indicator_value)
                else:
                    submission.indicatorvalues.get_or_create(indicator = indicator, value =val)
            msg.append ("Les elements precedents sont bien sauvegarde")
    template ="indicator/edit_submission.html"
    return render_to_response (req, template  , 
        {"form": form  , "submission": submission , "msg": msg , "submissions": Submission.objects.all ()})

def  delete_submission(req , id):
    submission = get_object_or_404 (Submission,pk =id)
    template = "indicator/confirm_delete.html"
    if req.POST:
        try:
            req.POST.get ("confirm_delete")
            submission.delete ()
            return HttpResponseRedirect (reverse('parametrage_project'))
        except KeyError , err:
            pass 
    return render_to_response(req, 
         template , {})
                
def add_submission (req , fiche_id , submission_id):
    '''Get a request '''
    msg  = []
    fiche = get_object_or_404 (Fiche , pk =fiche_id)
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
    if req.method =='POST':
        form  = form_class (req.POST)
        if form.is_valid ():
            if "submission_id" in req.POST:
                 if req.POST.get('submission_id').isdigit():
                     submission    = get_object_or_404 (Submission , pk =req.POST.get('submission_id'))
            if not submission:
                submission    = Submission.objects.create(fiche= fiche)
                submission_id = submission.pk
            indicator_input_values =[]
            for k , val in form.cleaned_data.items ():
                pk_indicator = k.split ("_")[-1]
                indicator = Indicator.objects.get (pk =pk_indicator)
                if type (val)==list :
                    # This is a indicator list 
                    for v in val:
                        indicator_value = get_object_or_404( IndicatorValue , id =int (v))
                        submission.indicatorvalues.add(indicator_value)
                else:
                    submission.indicatorvalues.get_or_create(indicator = indicator, value =val)
            msg.append ("Les elements precedents sont bien sauvegarde")
          
                
    template = 'indicator/add_submission.html'
    return render_to_response ( req ,template , {"indicators":indicators ,"submissions": Submission.objects.all () ,
               "form": form  ,"fiche": fiche,"msg" : msg  , "submission_id" :submission_id})          

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
    if req.method.lower ()=="post":
        form = IndicatorForm (req.POST)
        form_value =IndicatorValueForm(req.POST) 
        if form.is_valid ():
            indicator =form.save ()
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
                              #create init values
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
            req, template , {"form":form , "form_value": form_value ,\
             "msg": msg,"indicators" : Indicator.objects.all ()})

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
     return render_to_response(req,template,{ 'form' :form ,
          'msg': msg , 'form_value' :form_value,'indicators':Indicator.objects.all()}) 

def search_indicator (req):
    template ="indicator/search_indicator.html"
    form = SearchIndicatorForm()
    msg =[]
    indicators  = Indicator.objects.all ()
    if req.method.lower ()=="post":
        form =SearchIndicatorForm (req.POST)
        if form.is_valid ():
            ind = form.cleaned_data ["name"]
            indicators  = Indicator.objects.filter (name__icontains =str(ind))
            if not len(indicators):
                msg.append (_("La recherche n'a rien donnee"))
                indicators = Indicator.objects.all ()
            else :
                msg.append (_("La recherche a touve ces indicateurs"))
    return  render_to_response(req,template , {"msg": msg , "indicators": indicators  ,\
            "form": form})

def  delete_indicator(req , id):
    indicator = get_object_or_404 (Indicator,pk =id)
    template = "indicator/confirm_delete.html"
    if req.POST:
        try:
            req.POST.get ("confirm_delete")
            indicator.delete ()
            return HttpResponseRedirect (reverse("add_indicator"))
        except KeyError , err:
            pass 
    return render_to_response(req, 
         template , {})
def list_indicator (req):
    ''' list all indicator '''
    '''Go to list projects'''
    return render_to_response (req,"indicator/list_indicator.html" ,\
           { "indicators":Indicator.objects.all()})

def  delete_project(req , id):
    project= get_object_or_404 (Project,pk =id)
    template = "indicator/confirm_delete.html"
    if req.POST:
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
    if req.POST:
        form  = UserSearchForm(req.POST)
        if form.is_valid ():
           data  = form.cleaned_data
           users  =User.objects.filter (
                    Q(username__icontains=data['first_name'])| Q(username__icontains=data['last_name']))
    template ="indicator/add_user.html"
    return render_to_response (req , template ,
    {"form": form ,
      "users" : users,
     "msg" : msg})


        
def project_exports(req):
    '''Provide a list of projets  and  let us the user to choice one projet for export
    IF no indicator are selected , all will be exported ,'''
    form =ProjectExportForm ()
    if req.method =="POST":
        form  = ProjectExportForm(req.POST)
        if form.is_valid (): 
            data = form.cleaned_data
            projects= data ["projects"]
            if len (projects):
                 return  export(projects)
            else :
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
            data = form.cleaned_data
            indicators= data ["indicators"]
            if len(indicators):
               return  export (indicators)
            return  export(Indicator.objects.all())
    template = "indicator/indicator_exports.html"
    return render_to_response (req, template , {"form": form})

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

def indicator_stats (req):
    '''
    Dashboard stats indicator
    '''
    form =IndicatorStatForm ()
    stat_data ={}
    if req.POST :
        if form.is_valid ():
            data = form.cleaned_data
            project = data ["indicator"]
            stat_data = _get_stat_data_for_indicator (project)  
    template = "indicator/indicator_stats.html"
    return render_to_response (req,
        template ,{"form": form  , "stat_data"  : stat_data})
    
def project_stats (req):
    '''Dashorboard project stat '''
    form =ProjectStatForm ()
    stat_data ={}
    if req.POST :
        form  = ProjectStatForm(req.POST)
        if form.is_valid (): 
            data = form.cleaned_data
            project = data ["project"]
            stat_data['indicator_count'] = project.indicators.count()
            stat_data['village_count']   = project.villages.count ()
            stat_data =_get_stat_data_for_project (project)
    template = "indicator/project_stats.html"
    return render_to_response (req,
        template ,
        {"form": form  , "stat_data"  : stat_data})

def village_stats (req):
    '''Dashorboard village  stat'''
    form =VillageStatForm ()
    stat_data ={}
    if req.POST :
        form  = VillageStatForm(req.POST)
        if form.is_valid (): 
            data = form.cleaned_data
            village = data ["village"]
            stat_data = _get_stat_data_for_village (village)
    template = "indicator/village_stats.html"
    return render_to_response (req,
        template ,
        {"form": form  , "stat_data"  : stat_data})

def user_stats (req):
     ''' Nothing  to display here we will see later what-to-do '''
     return HttpResponseRedirect (reverse ('indicator_dashboard'))

def _get_stat_data_for_project (project) :
      return  project.indicatorvalues
           
def _get_stat_data_for_indicator(indicator) :
          return  {}
def _get_stat_data_for_village(village) :
          return  {}
     
def add_user (req):
    '''Add new user'''
    form = UserForm()
    msg  = []
    if req.POST:
        form  = UserForm(req.POST)
        if form.is_valid ():
             try:
                 form.save ()
                 msg.append (_("Element sauvegarge"))
             except Exception , err:
                 msg.append (str(err))
    template ="indicator/add_user.html"
    return render_to_response (req , template ,
    {"form": form ,
      # Get teh list of users that have  a profil to edit  from Web UI of the indicators app
      "users" : User.objects.filter (groups__name__in = ['indicator_edit', 'indicator_admin']),"msg" : msg})

def edit_user (req , id):
    '''Edit new user'''
    user  = get_object_or_404(User ,pk =id)
    form  = UserForm(initial = {'first_name' : user.first_name  , 'last_name' : user.last_name ,
          'username': user.username , 'password' :''})
    msg  = []
    if req.POST:
        form  = UserForm(req.POST)
        if form.is_valid ():
             try:
                 # delete the exiting user before save change to avoid key duplicate
                 # If the  password is empty skip
                 # The user cahange the password 
                 if form.cleaned_data ['password'] !='':
                      user.delete()
                      form.save ()
                      msg.append (_("Element sauvegarge"))
                 # return to the add_user to avoid user hit dabase   for deleted user :)
                 return HttpResponseRedirect(reverse ('add_user'))
             except Exception , err:
                 msg.append (str(err))
    template ="indicator/add_user.html"
    return render_to_response (req , template ,
    {"form": form ,'users':User.objects.filter (groups__name__in = ['indicator_edit', 'indicator_admin']),"msg" : msg})


                
def data_export (req):
    form  = DataExportForm()
    if req.method=="POST":
        form =DataExportForm(req.POST)
        if form.is_valid ():
            data  = form.cleaned_data
            #return HttpResponse ("<br/>".join ( "%s :%s "%(k,v) for (k,v) in data.items ()))
            villages =data['villages']
            project =data['project']
            if not len(villages):
                villages = project.villages.all () 
            date_edit=  data['date_edit']
            response = HttpResponse (mimetype ="text/csv")
            response ["Content-Disposition"]="attachment; filename =%s_%s_%s.xls"%(project.name,
                    villages[0].name ,date_edit)
            writer  = UnicodeWriter (response)
            projet= ["Projet" , "Village" , "Indicator" , "Valeur"]
            for village in villages:
                for fiche in  project.fiches.all ():
                        for submission  in fiche.submissions.filter (village =village ,
                             date__month =date_edit.month , date__year=date_edit.year):
                                indicator =map(lambda v: v.indicator.name , submission.indicatorvalues.all ())
                                value     =map(lambda v: v.indicator.value , submission.indicatorvalues.all ())
                                writer.writerow([projet.name , village.name ,indicator,value])
            return response
    template ='indicator/data_export.html'
    return render_to_response (req,template , {'form': form})
        
            
def export(qs):
    #return HttpResponse (map (lambda f :f.name, qs[0]._meta.fields))
    fields =qs[0]._meta.fields
    header = map (lambda f :f.name , fields)
    response = HttpResponse (mimetype ="text/csv")
    response ["Content-Disposition"]="attachment; filename =export.xls"
    w= UnicodeWriter(response)
    w.writerow(header)
    for q in qs:
        row =[]
        for h in header:
            val =getattr (q, h)
            row.append (val)
        w.writerow (row)
    return response
        
        
class UnicodeWriter(object):
        """ 
    A unicode Writer helper that allow us to write
        any given encoding , default is utf-8
        """
        def __init__ (self,stream , dialect ="excel-tab" , encoding= "Utf-8",**kw):   
          self.queue = cStringIO.StringIO()
          self.writer = csv.writer (self.queue ,dialect =dialect)
          self.encoder = codecs.getincrementalencoder (encoding)()
          self.stream =stream

        def writerow(self, row):
           self.writer.writerow([unicode (s).encode('utf-8') for s in row])
           # Get data from queue
           data = self.queue.getvalue ()
           # Decode to unicode
           data = data.decode ("Utf-8")
           # Reencode from given encoding
           self.encoder.encode (data)
           # write into stram
           self.stream.write (data)
           self.queue.truncate (0)
