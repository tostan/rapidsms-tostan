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
from utilities.export import export
from forms import *

ITEM_PER_PAGE = 10

def index (req):
    '''
     Go to indicator dashboard page
    '''
    return render_to_response (
            req,"indicator/index.html" , 
            {})
@login_required
def parametrage(req):
    '''
    Go to indicator param  dashboard 
    '''
    return render_to_response (
     req, "indicator/parametrage.html" ,
     {})
    
@login_required
def parametrage_indicator (req):
    '''
    Go to indicator param dashboard
    '''
    return render_to_response (
    req , "indicator/parametrage_indicator.html" ,
    {})
    
@login_required
def parametrage_project(req):
    '''
    Go to indicator project dashboard
    '''
    return render_to_response (
    req , "indicator/parametrage_project.html" ,
    {})
    
@login_required
def parametrage_stat(req):
    '''
    Go to indicator stats dashboard    '''
    return render_to_response (
    req , "indicator/parametrage_stat.html",
    {})
    
@login_required
def parametrage_user(req):
    '''
    Go to indicator user dashboard
    '''
    return render_to_response (
    req , "indicator/parametrage_user.html" , 
    {})

@login_required
def parametrage_export(req):
    '''
    Go to export dashborad
    '''
    return render_to_response (
    req , "indicator/parametrage_export.html" ,
    {})

def make_village_form (form_data):
    '''
    Create a form to filter contry , regions ,departements , village 
    districts 
    Should go later into the form  module 
    >>> form  = make_village_form ({})
    >>> form.as_table ()
    '''
    fields  = {}
    #Get village data  without villages , the region , departements , etc
    village_list  = form_data.pop("villages")
    for item , qs  in form_data.iteritems () :
            fields [str (item)] = forms.ChoiceField(label =_(str(item)),
            choices  = as_tuple (qs))
    fields["villages"] = forms.MultipleChoiceField (
            label =_("Villages du projet") ,
            choices = as_tuple (village_list))
    
    def clean (self):
          return self.cleaned_data 
    return type ("FormArea" , (forms.BaseForm , ) , {"base_fields": fields , "clean": clean})
    
def make_indicator_form (ind_dict):
    '''
    Create a indicator form to let user choices the indicators when it 
    create a new project.Should go into the form module 
    >>> form = make_indicator_form 
    >>> form.as_table ()
    '''
    fields  = {}
    fields  ["titre"]  =forms.CharField (
                label    =_("Titre"),
                widget   = forms.TextInput (attrs  = {"size": "50"}))
    fields  ["bailleur"] =forms.CharField (
                label  =_("Bailleur") ,
                widget  =forms.TextInput (attrs  ={"size" : "50"}))
    fields  ["description"] =forms.CharField (
                label  =_("Description du Projet") ,
                widget = forms.Textarea (attrs  ={"size" : "50"}))
    fields  ["started"]  = forms.DateField (
                label =_("Date de demarrage"),
                widget  = SelectDateWidget ,
                required =False , 
                initial =date.today)
    # Get the indicator list of elements
    indicator_list=ind_dict.pop ("indicators")  
    #fields ['indicators'] =forms.MultipleChoiceField(label =_("Indicateurs du projet"), choices = as_tuple (indicator_list))
    fields ['indicators'] =forms.MultipleChoiceField(
                label =_("Indicateurs du projet"),
                widget =forms.CheckboxSelectMultiple , 
                choices = as_tuple (indicator_list))
    
    def clean (self):
          return self.cleaned_data 
    return type ("FormArea" , (forms.BaseForm , ) , 
                 {"base_fields": fields , "clean": clean})
    

def make_submission_form (submission):
    ''' Create a dynamique submission form
        It create dymamically a form to handle a list of indicators (max_per_page= 100)
        Each submission form is linked to a *fiche* of project ,and it allow us to submit
        values of given indicators .
        Should go  into the form module later
        >>> form  = make_submission_form (submission)
            form.as_table ()
    '''
    fields  ={}
    indicatorsubmissions = submission.indicatorsubmissions.all ()
    for indicator_submission in  indicatorsubmissions:
            fields ["%s_%s"%(indicator.name,indicator.pk)] =forms.CharField ()
    
def add_pays(req):
    '''
    Add new contry 
    '''
    msg = list()
    template ="indicator/add_pays.html"
    if req.method.lower ()=="post":
        form =PaysForm (req.POST)
        if form.is_valid ():
            form.save ()
            msg.append (_("Element sauvegarde"))
            return render_to_response (req,template ,
                {"form": form ,
                 "pays":Pays.objects.all () , 
                 "msg"  : msg })
        else :
            msg.append (_("Erreur dans le formulaire"))
            #msg.append (form.errors)  
    else :
        form  = PaysForm ()    
    return render_to_response (req, template , 
                {"form" : form , 
                 "pays" : Pays.objects.all () , 
                 "msg": msg })
    
def add_region (req, id):
    '''
    if senegal , flatten  pays to regions
    '''
    pays  = get_object_or_404(Pays ,name__icontains = id )
    regions = [pays]
    msg = []
    #as tuple to fill the form choice fields dynamique 
    if id.lower() =="somalie":
        regions  =cast_etat (pays)
    else :
        regions  =[pays]
    data = as_tuple (regions) 
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            Region.objects.create (parent =pays , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_region.html",
         {"form" : form ,
          "msg": msg,
          "regions": Region.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_region.html",
         {"form" : form ,
          "msg": msg,
          "regions": Region.objects.all () })
    
def  edit_pays (req , id ):
    '''
    Edit the given contry
    '''
    msg = list ()
    template = "indicator/edit_pays.html"
    contry =  get_object_or_404 (Pays , pk = id)
    form = PaysForm (instance = contry)
    if req.method.lower () == "post":
            form  = PaysForm (req.POST)
            if form.is_valid ():
                form.save ()
                msg.append (_("Element sauvegarde"))
                return render_to_response (
                    req , template , 
                    {
                     "form" : PaysForm (),
                     "pays" : Pays.objects.all (),
                     "msg" : msg 
                    }
                )
            else :
                msg.append (_("Erreur dans le formulaire"))
    return render_to_response (
            req ,template  , 
            {"form": form,
             "pays" : Pays.objects.all ()})
    
def delete_pays (req, id):
    '''
    Given an contry , delete it
    '''
    template = "indicator/confirm_delete.html"    
    contry  = get_object_or_404 (Pays , pk = id )
    if req.method.lower () =="post":
        try:
            req.POST.get ("confirm_delete")
            contry.delete ()
            return HttpResponseRedirect("/indicator/add_pays")
        
        except  KeyError , err: 
              return render_to_reponse (
              req, 
              template , {}) 
    else:
        return render_to_response(req, 
              template , {}
        )
def as_tuple (qs):
    '''
    Given a list of objets return a tuple
    '''
    return [ (q.pk , q.__unicode__()) for q in qs]
        
def add_commune (req , pays):
    '''
    Add new commune
    '''
    pass
def add_communaute_rurale (req):
    '''
    Add new rurale community
    '''
    pass

def add_commune_arrondissement(req, pays):
    '''
    Add new commune 
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    regions= cast_arrondissement(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Arrondissement.objects.get (pk =req.POST["region"])
            CommuneArrondissement.objects.create (
                                        parent =parent ,
                                        name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_commune_arrondissement.html",
         {"form" : form, 
          "msg": msg,
          "regions": CommuneArrondissement.objects.all ()})
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_region.html",
         {"form" : form ,
          "msg": msg,
          "regions": CommuneArrondissement.objects.all ()})

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
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = CommuneArrondissement.objects.get (pk =req.POST["region"])
            Commune.objects.create (parent =parent ,
                                    name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_commune.html",
         {"form" : form ,
          "msg": msg,
          "regions": Commune.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_commune.html",
         {"form" : form ,
          "msg": msg,
          "regions": Commune.objects.all ()})

def add_arrondissement (req, pays):
    '''
    if senegal , flatten  pays to regions
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    regions = cast_departement (pays)    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Departement.objects.get (pk =req.POST["region"])
            Arrondissement.objects.create (
                                           parent =parent , 
                                           name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
            "indicator/add_arrondissement.html",
             {"form" : form ,
              "msg": msg,
              "regions": Arrondissement.objects.all () } )
        
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_arrondissement.html",
         {"form" : form,
          "msg": msg,
          "regions": Arrondissement.objects.all() })

def cast_departement (top):
    '''
    Get childrens of top , only the departments childrens
    '''
    deps = []
    regions = cast_region(top)
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =Departement)
            if d and type (d)==Departement:
                deps.append (d)
    return deps

def cast_prefecture (top):
    '''
    Get childrens, only the prefectures types
    '''
    deps = []
    regions = cast_region(top)
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =Prefecture)
            if d and type (d)==Prefecture:
                deps.append (d)
    return deps

def cast_region(top):
    '''
    Get the chilrens , only the regions  types
    '''
    regions =[]
    for child in top.children.all ():
        d = child._downcast(klass=Region)
        if type (d)==Region:
            regions.append(d)
    return regions

def cast_etat(top):
    '''
    Get the childrens ,only the etats types
    '''
    regions =[]
    for child in top.children.all ():
        d = child._downcast(klass=Etat)
        if type (d)==Etat:
            regions.append(d)
    return regions

def cast_secteur(top):
    '''
    Get the chilrens , only the secteurs type
    '''
    deps = []
    regions = cast_region(top)
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =Secteur)
            if d and type (d)==Secteur:
                deps.append (d)
    return deps

def cast_district(top):
    '''
    Cast the childrens ,only the districts types
    '''
    deps = []
    regions = cast_region(top)
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =District)
            if d and type (d)==District:
                deps.append (d)
    return deps


def cast_sub_prefecture (top):
    '''
    Get the childrens ,only the prefetures types
    '''
    deps = []
    regions = cast_prefecture(top)
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =SubPrefecture)
            if d and type (d)==SubPrefecture:
                deps.append (d)
    return deps

def cast_arrondissement(top):
    '''
    Get the childrens only the arrondissement types
    '''
    arrs  = []
    deps = cast_departement(top)
    for dep in deps:
        for arr in dep.children.all ():
            a = arr._downcast(klass =Arrondissement)
            if a and type(a)==Arrondissement:
                arrs.append (a)
    return arrs

def cast_commune_arrondissement(top):
    '''
    Get childrens ,only the arrondissements types
    '''
    coms  = []
    com_arrs= cast_arrondissement(top)
    for com_arr in com_arrs:
        for com in com_arr.children.all ():
            c= com._downcast(klass =CommuneArrondissement)
            if c and type(c)==CommuneArrondissement:
                coms.append (c)  
    return coms

def cast_commune(top):
    '''
    Get childrens ,only the communes types
    '''
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
        ...
    '''
    coms  = []
    if pays_name  =="senegal":
        com_arrs= cast_commune(top)
    elif pays_name =="guinee_konakry":
        com_arrs= cast_sub_prefecture(top)
    elif pays_name =="guinee_bissau":
        com_arrs= cast_secteur(top)
    elif pays_name =="gambie":
        com_arrs= cast_district(top)
    elif pays_name =="somalie":
        com_arrs= cast_region(top)
    elif pays_name =="djibouti":
        com_arrs= cast_region(top)
    elif pays_name =="mauritanie":
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
    '''
    if senegal , flatten  pays to regions
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions = cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Departement.objects.create (
                                parent =parent , 
                                name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_departement.html",
         {"form" : form ,
          "msg": msg,
          "regions": Departement.objects.all ()})
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_region.html",
         {"form" : form ,
          "msg": msg,
          "regions": Departement.objects.all ()})
    
def add_village (req, id):
    '''
    Add new village
    '''
    pays  = get_object_or_404(Pays ,name__icontains = id )
    regions =[]
    if id.lower () == "senegal":
        regions= cast_commune(pays)
    elif id.lower()=="guinee_konakry":
        regions =cast_sub_prefecture (pays)
    elif id.lower()=="guinee_bissau":
        regions = cast_secteur (pays)
    elif id.lower()=="gambie":
        regions = cast_district (pays)
    elif id.lower()=="somalie":
        regions = cast_region(pays)
    elif id.lower()=="djibouti":
        regions = cast_region(pays)
    elif id.lower()=="mauritanie":
        regions = cast_departement(pays)
    else :
        regions  =[]
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            if id.lower() =="senegal":
                parent = Commune.objects.get (pk =req.POST["region"])
            elif id.lower()=="guinee_konakry":
                parent = SubPrefecture.objects.get (pk =req.POST["region"])
            elif id.lower()=="guinee_bissau":
                parent = Secteur.objects.get (pk =req.POST["region"])
            elif id.lower()=="gambie":
                parent = District.objects.get (pk =req.POST["region"])
            elif id.lower()=="somalie":
                parent = Region.objects.get (pk =req.POST["region"])
            elif id.lower()=="djibouti":
                parent = Region.objects.get (pk =req.POST["region"])
            elif id.lower()=="mauritanie":
                parent = Departement.objects.get (pk =req.POST["region"])
            else :
                parent  =None 
            IndicatorVillage.objects.create (parent =parent ,
                                             name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
            "indicator/add_village.html",
             {"form" : form ,
              "msg": msg,
              "regions": IndicatorVillage.objects.all ()})
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_village.html",
         {"form" : form, 
          "msg": msg,
          "regions": IndicatorVillage.objects.all ()})
    
def add_prefecture (req, pays):
    '''
    Add new prefecture 
    '''
    pays  = get_object_or_404(Pays ,
                              name__icontains = pays )
    regions =[]
    
    # For Guinee Konakry the region  should be casted to precture
    regions= cast_region(pays)
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Prefecture.objects.create (parent =parent , 
                                       name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_prefecture.html",
         {"form" : form ,
          "msg": msg,
          "regions": Prefecture.objects.all () })
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_prefecture.html",
         {"form" : form, 
          "msg": msg,
          "regions": Prefecture.objects.all ()})

def add_sub_prefecture (req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    
    # For Guinee Konakry , for this moment , special zone should have region as parent
    regions= cast_prefecture(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Prefecture.objects.get (pk =req.POST["region"])
            SubPrefecture.objects.create (parent =parent , 
                                          name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
            "indicator/add_sub_prefecture.html",
             {"form" : form ,
              "msg": msg,
              "regions": SubPrefecture.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_sub_prefecture.html",
         {"form" : form, 
          "msg": msg,
          "regions": SubPrefecture.objects.all () })

def add_commune_hurbaine (req, pays):
    '''
    Add new commune  hurbaine
    '''
    pays  = get_object_or_404(Pays ,
                              name__icontains = pays )
    regions =[]
    # For Guinee Konakry , for this moment ,Commune hurbaine should have region as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            CommuneHurbaine.objects.create (parent =parent ,
                                            name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
            "indicator/add_commune_hurbaine.html",
             {"form" : form ,
              "msg": msg,
              "regions": CommuneHurbaine.objects.all () } )
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_commune_hurbaine.html",
         {"form" : form, 
          "msg": msg,
          "regions": CommuneHurbaine.objects.all ()})

def add_village_guinee (req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]    
    # For Guinee Konakry , for this moment ,Commune hurbaine should have region as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            IndicatorVillage.objects.create (parent =parent , 
                                             name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
            "indicator/add_village.html",
             {"form" : form ,
              "msg": msg,
              "regions": IndicatorVillage.objects.all () })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_village.html",
         {"form" : form, 
          "msg": msg,
          "regions": IndicatorVillage.objects.all ()})
            
def add_secteur (req, pays):
    '''
    Add new secteur
    '''
    pays  = get_object_or_404(Pays ,
                              name__icontains = pays )
    regions =[]
    # For Guinee Bissau,secteur should have regions as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Secteur.objects.create (parent =parent ,
                                    name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
             "indicator/add_secteur.html",
             {"form" : form ,
              "msg": msg,
              "regions": Secteur.objects.all () 
              })
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
         "indicator/add_secteur.html",
         {"form" : form, 
          "msg": msg,
          "regions": Secteur.objects.all ()})
    
def add_district(req, pays):
    '''
    Add new district
    '''
    pays  = get_object_or_404(Pays ,
                              name__icontains = pays )
    regions =[]
    # For Guinee Bissau,secteur should have regions as parent
    regions= cast_region(pays)
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            District.objects.create (parent =parent ,
                                     name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
            "indicator/add_district.html",
             {"form" : form ,
              "msg": msg,
              "regions": District.objects.all () } )
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_district.html",
         {"form" : form, 
          "msg": msg,
          "regions": District.objects.all () })
    
def add_etat(req, pays):
    '''
    Add new etat
    '''
    pays  = get_object_or_404(Pays ,
                              name__icontains = pays )
    regions =[]
    # For Guinee Bissau,secteur should have regions as parent
    #regions= cast_region(pays)
    regions  = [pays]
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = get_area_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Pays.objects.get (pk =req.POST["region"])
            Etat.objects.create (parent =parent ,
                                 name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
            "indicator/add_etat.html",
             {"form" : form ,
              "msg": msg,
              "regions": Etat.objects.all ()} )
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_etat.html",
         {"form" : form, 
          "msg": msg,
          "regions": Etat.objects.all ()})
    
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
        return {"regions"  : cast_region (pays),
               "prefectures": cast_prefecture (pays),
               "subprefectures":cast_sub_prefecture (pays),
                "villages"  : cast_village(pays , "guinee_konakry")}
    
    def get_bissau_form ():
        return {"regions"   :cast_region(pays) ,
                "secteurs"  :cast_secteur(pays),
                "villages"  :cast_village(pays , "guinee_bissau")}
    
    def get_gambie_form ():
        return {"regions"  :cast_region(pays),
                "districts":cast_district (pays),
                "villages"  : cast_village(pays , "gambie")}
        
    def get_senegal_form ():
        return {"regions" : cast_region (pays),
                "arrondissements" :cast_arrondissement (pays),
                "departements"   :cast_departement (pays),
                "commune_arrondissements" :cast_arrondissement (pays),
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
        return {"regions"  :cast_region (pays),
                "villages" :cast_village (pays , "djibouti")}
    
    def get_mauritanie_form ():
        ''' Regions qui sont partages en departements '''
        return {"regions" :cast_region (pays),
                # The elelements list to be associated to the projects
                "departements" :cast_departement (pays),
                "villages"    :cast_village (pays , "mauritanie")}
    
    name  = pays.name.upper ()
    if name  =="GUINEE_KONAKRY":
        return get_konakry_form () 
    elif name =="GUINEE_BISSAU":
        return get_bissau_form ()
    elif name =="GAMBIE" :
        return get_gambie_form ()
    elif name =="SENEGAL":
        return get_senegal_form ()
    elif name =="SOMALIE":
        return get_somalie_form ()
    elif name =="DJIBOUTI":
        return get_djibouti_form ()
    elif name =="MAURITANIE":
        return get_mauritanie_form ()
    else :
        return []
      
def indicator_form ():
    #The indicator list to be associated to the project
    return {"indicators":Indicator.objects.all ()}

def add_project(req , pays):
    '''
    Each pays should have it own layout 
    Chaque pays doit avoir la liste de ces regions village , etc afin que dans 
    l'edition d'un project qu'on puisse filter et ajouter un village
    '''
    template = 'indicator/add_project.html'
    pays= get_object_or_404(Pays , 
                            name__icontains = pays.lower ())
    #Get the village filter form
    vil_form_data= get_pays_form (pays)
    ind_form_data =indicator_form ()
    #Go to create dynamically a project from based on the vil_from_filter and the indicator_form
    form_village_class   =make_village_form (vil_form_data)
    form_village  =form_village_class ()
    form_indicator_class =make_indicator_form (ind_form_data)
    form_indicator = form_indicator_class ()
    msg  =[]
    if req.method.lower () =="post":
        form_village  = form_village_class (req.POST)
        form_indicator = form_indicator_class (req.POST)
        if form_village.is_valid  ()  and form_indicator.is_valid ():
                try:
                   villages, indicators =[], []
                   for vil_pk in  req.POST.getlist("villages"):
                       villages.append(IndicatorVillage.objects.get (pk =vil_pk)) 
                   for ind_pk in req.POST.getlist ('indicators'):
                       indicators.append(Indicator.objects.get (pk =ind_pk))
                   Project.create_project (villages , indicators ,
                                           ** {"titre": req.POST.get ("titre") , 
                                               "bailleur": req.POST.get ("bailleur"),
                                               "description": req.POST.get ("description")})
                   msg.append (_("OK"))          
                except (KeyError, Exception):
                   raise
                   project.delete ()
                   msg.append(_("Vous devez choisir le dernier element dans le filtre"))
        else:
                msg.append (_("OK"))
    return render_to_response (req , template , 
        { "form_village" : form_village ,
          "form_indicator": form_indicator , 
          "projects" :Project.objects.all (),
          "msg" :msg })

def edit_submission (req , submission_pk):
    '''Edit Submission '''
    dict =[]
    submission = get_object_or_404 (Submission , pk =submission_pk)
    fiche  = submission.fiche
    indicatorvalues  = submission.indicatorvalues.all ()
    form_class  =fiche.form_edit(submission ,indicatorvalues)
    form = form_class ()
    if req.method =="POST":
        if form.is_valid ():
            data = form.cleaned_data         
    template ="indicator/edit_submission.html"
    return render_to_response (req, 
        template  , 
        {"form": form  , "submission": submission})
            
def add_submission (req , fiche_id):
    '''  Get a request '''
    msg  = []
    fiche = get_object_or_404 (Fiche , pk =fiche_id)
    indicators  = fiche.indicators.all ()
    p  = Paginator (indicators , ITEM_PER_PAGE)            
    submission =None
    try:
            page  = int (req.GET.get ("page"))
    except Exception :
            page  = 1
    try:
            indicators  = p.page (page)
            form_class  = fiche.form_save (indicators.object_list)
            form = form_class ()
    except EmptyPage :
            form =None 
            pass
    if req.method =='POST':
        form  = form_class (req.POST)
        if form.is_valid ():
            # Get The primary Key of the indicator 
            submission , created = Submission.objects.get_or_create (fiche= fiche)
            indicator_input_values =[]
            for k , val in form.cleaned_data.items ():
                pk_indicator = k.split ("_")[-1]
                indicator = Indicator.objects.get (pk =pk_indicator)
                if type (val)==list :
                    # This is a indicator list 
                    for v in val:
                        indicator_value = get_object_or_404( IndicatorValue , id =int (v))
                        #submission.indicatorvalues.create (indicator =indicator , user =req.user , value=v)
                        submission.indicatorvalues.add (indicator_value)
                else:
                    submission.indicatorvalues.create (indicator = indicator, value =val)
            msg.append ("Les elements precedents sont bien sauvegarde")
    template = 'indicator/add_submission.html'
    return render_to_response ( req ,template , 
                                {"indicators":indicators ,
                                 "submissions": Submission.objects.all () ,
                                 "form": form  , 
                                 "fiche" : fiche,
                                 "msg" : msg})          
def add_indicator(req):
    '''
    Here we are going to define  our indicator , by adding a basic indicator form and a list .
    Creation des indicateurs ici , en specifiant le type et les valeurs si 'indicateur est de type list
    '''
    form =IndicatorForm ()
    form_value =IndicatorValueForm ()
    template = "indicator/add_indicator.html"
    msg  = []
    if req.method.lower ()=="post":
        form = IndicatorForm (req.POST)
        form_value =IndicatorValueForm (req.POST) 
        if form.is_valid ():
            indicator =form.save ()
            try:
                        value =form_value.data["value"]
                        if value.strip()!=""  and indicator.type !=Indicator.TYPE_LIST:
                            indicator.delete()
                            raise ValidationError (_("La liste des valeurs doit etre saisie si \
                                    l'indicateur est de type list")) 
                        if indicator.type ==Indicator.TYPE_TEXT:
                            IndicatorValue.objects.create(value ="text" , indicator =indicator)
                        elif indicator.type ==Indicator.TYPE_DATE:
                            IndicatorValue.objects.create(value ="date" , indicator =indicator)                    
                        elif indicator.type ==Indicator.TYPE_NUMERIC:
                            IndicatorValue.objects.create(value ="numeric" , indicator =indicator)
                        elif indicator.type ==Indicator.TYPE_LIST:
                            values  = [v for  v  in value.split ('\r\n')  if v.strip() !='' ]
                            if len (values):
                                for value in values:
                                    IndicatorValue.objects.create(value =value, indicator =indicator)
                        else : pass
                        msg.append (_("OK"))
            except ValidationError, err:
                msg.append (err.message)
                print "err :" , dir (err)
        else :
            msg.append(form.errors)
            msg.append (form_value.errors)
            #return HttpResponse (form.errors)
    return render_to_response (
            req, template , {"form":form , "form_value": form_value ,
                             "msg": msg,
                             "indicators" : Indicator.objects.all ()})

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
    return  render_to_response(req,template , {"msg": msg , "indicators": indicators  , 
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

def form_search_project ():
        ''' Form to allow searching  project '''
        fields  = {}
        fields ['name'] = forms.CharField (
                            required  = False ,
                            label =_("Nom du projet") , 
                            widget =forms.TextInput (attrs  = {"size": "50"}))
        fields ['villages']= forms.MultipleChoiceField (
                            required =False ,
                            choices =as_tuple(IndicatorVillage.objects.all ()),
                            label =_("Village dans lequel le projet est present"))
        fields ['indicators']= forms.MultipleChoiceField (
                            required =False,
                            choices =as_tuple(Indicator.objects.all ()),
                            label = _("Chosir un indicateur contenu dans le projet"))
        def clean (self):
            return self.cleaned_data
        return type ("ProjectFormSearch" , (forms.BaseForm ,) , {"base_fields": fields  , "clean": clean})
        
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

def search_project (req,pays):
    '''
    Search a new projet
    '''
    form_class  = form_search_project ()
    form  = form_class ()
    projects  = Project.objects.all ()
    if req.POST :
        form  = form_class (req.POST)
        if form.is_valid ():
            try:
                    project_kwargs  = {}
                    project_kwargs.update({"indicators__in": [Indicator.objects.get (id =int (pk)) 
                                                              for pk in form.cleaned_data["indicators"]]})
                    project_kwargs.update({"villages__in": [IndicatorVillage.objects.get (id =int (pk)) 
                                                            for pk in form.cleaned_data["villages"]]})
                    project_kwargs.update({"name":form.cleaned_data ["name"]}) 
                    projects =Project.objects.filter (**project_kwargs).all ()            
            except Exception  ,e :
                    projects  = []
            if not len(projects): projects  = Project.objects.all ()
    template ='indicator/search_project.html'
    return render_to_response (req , template , 
        {"projects" : projects ,
        "form" : form})
        
def export_project(req ,pays):
    return export (Project.objects.all (), 
                   ["name" , "titre" , "bailleur" , "description", "indicators" , "villages"] )
def export_indicator (req):
    '''
    Export the indicator list
    '''
    return export (Indicator.objects.all ())

def export_user (req):
    '''
    Export the indicator list
    '''
    return export (User.objects.filter (groups__in =['indicator']))
       
def stats (req):
    template ="indicator/index_stats.html"
    return render_to_response (req, template  , {})

def indicator_stats (req):
    '''
    Dashboard stats indicator
    '''
    form =IndicatorStatForm ()
    if req.POST :
        if form.is_valid ():
                pass
    
    template = "indicator/indicator_stats.html"
    return render_to_response (req,
        template ,
        {"form": form})
    
def project_stats (req):
    '''
    Dashorboard project stat
    '''
    form =ProjectStatForm ()
    if req.POST :
        form  = ProjectStatForm(req.POST)
        if form.is_valid (): 
            data = form.cleaned_data
            context ["projet"] = data ["projet"]
    template = "indicator/project_stats.html"
    return render_to_response (req,
        template ,
        {"form": form})
     
def add_user (req):
    '''
    Add new user
    '''
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
      "users" : User.objects.filter (groups__name='indicator_edit'),
     "msg" : msg})
    
    
def edit_user (req , id):
    '''
    Edit new user
    '''
    user  = get_object_or_404(User ,pk =id)
    if ':' in user.username :
            user_names = user.username.split (':')
            initial_args  ={"first_name":  user_names [0] ,
                            'last_name' :user_names[1]}
    else :
            initial_args  ={}
    form  = UserForm(initial = initial_args)
    msg  = []
    if req.POST:
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
      "users" : User.objects.filter (groups__name='indicator_edit'),
     "msg" : msg})