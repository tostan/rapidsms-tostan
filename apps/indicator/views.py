# Create your webui views here.
#from django.shortcuts import render_to_response
from django.http import HttpResponse ,HttpResponseRedirect
from rapidsms.webui.utils import render_to_response
from django.core.urlresolvers import reverse
from apps.indicator.models import *
from django import forms
from .forms import *
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required , permission_required 
from django.http import HttpResponse 
from django.core.exceptions import ValidationError
def index (req):
    return render_to_response (req,"indicator/index.html" , {})
@login_required
def parametrage(req):
    return render_to_response (
     req, "indicator/parametrage.html" , {})
    
@login_required
def parametrage_indicator (req):
    return render_to_response (
    req , "indicator/parametrage_indicator.html"
    )
    
@login_required
def parametrage_project(req):
    return render_to_response (
    req , "indicator/parametrage_project.html"
    )
    

def make_form(qs, field_name):
        fields = {}
        fields["name"]      = forms.CharField (label = _("Nom"),max_length = 160)
        fields["surface"]   = forms.CharField (label = _("Surface"),max_length = 200)
        fields["latitude"]  = forms.CharField (label = _("Latitude"),max_length = 200)
        fields["longitude"] = forms.CharField (label = _("Longitude"),max_length = 200)
        fields[field_name]  = forms.ChoiceField (choices = qs)
        def clean (self):
            print "CLEANED data"
            print self.cleaned_data
            return self.cleaned_data
            
        return type ("FormArea" , (forms.BaseForm,) , {"base_fields":fields  ,"clean" : clean})
    
    
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
    
    
    


def cast_region(top):
    '''
    '''
    regions =[]
    for child in top.children.all ():
        d = child._downcast(klass=Region)
        if type (d)==Region:
            regions.append(d)
    
    return regions

def add_region (req, pays):
    '''
    if senegal , flatten  pays to regions
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions = [pays]
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = make_form (data,"region")
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
          "regions": Region.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_region.html",
         {"form" : form ,
          "msg": msg,
          "regions": Region.objects.all () 
          }                     
        )
    
            
        

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
             "pays" : Pays.objects.all ()}                   
    )
    
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
            template , {}                          
            ) 
    else:
        return render_to_response(req, 
         template , {}
        )
        
        

def as_tuple (qs):
    '''
    Given a list of objets return a tuple
    '''
    l  = [("0" , "--"*20)]
    [ l.append((q.pk , q.__unicode__()) ) for q in qs]
    return l
    

        
def add_commune (req , pays):
    '''
    '''
    pass
def add_communaute_rurale (req):
    '''
    '''
    pass

def add_commune_arrondissement(req, pays):
    '''
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    regions= cast_arrondissement(pays)
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Arrondissement.objects.get (pk =req.POST["region"])
            CommuneArrondissement.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_commune_arrondissement.html",
         {"form" : form, 
          "msg": msg,
          "regions": CommuneArrondissement.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_region.html",
         {"form" : form ,
          "msg": msg,
          "regions": CommuneArrondissement.objects.all () 
          }                     
        )

    
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
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = CommuneArrondissement.objects.get (pk =req.POST["region"])
            Commune.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_commune.html",
         {"form" : form ,
          "msg": msg,
          "regions": Commune.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_commune.html",
         {"form" : form ,
          "msg": msg,
          "regions": Commune.objects.all () 
          }                     
        )



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
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Departement.objects.get (pk =req.POST["region"])
            Arrondissement.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_arrondissement.html",
         {"form" : form ,
          "msg": msg,
          "regions": Arrondissement.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_arrondissement.html",
         {"form" : form,
          "msg": msg,
          "regions": Arrondissement.objects.all() 
          }                     
        )


def cast_departement (top):
    deps = []
    regions = cast_region(top)
    for region in regions:
        for dep in region.children.all():
            d = dep._downcast(klass =Departement)
            if d and type (d)==Departement:
                deps.append (d)

    return deps

def cast_arrondissement(top):
    arrs  = []
    deps = cast_departement(top)
    for dep in deps:
        for arr in dep.children.all ():
            a = arr._downcast(klass =Arrondissement)
            if a and type(a)==Arrondissement:
                arrs.append (a)
                
    return arrs

def cast_commune_arrondissement(top):
    coms  = []
    com_arrs= cast_arrondissement(top)
    for com_arr in com_arrs:
        for com in com_arr.children.all ():
            c= com._downcast(klass =CommuneArrondissement)
            if c and type(c)==CommuneArrondissement:
                coms.append (c)
                
    return coms

def cast_commune(top):
    coms  = []
    com_arrs= cast_commune_arrondissement(top)
    for com_arr in com_arrs:
        for com in com_arr.children.all ():
            c= com._downcast(klass =Commune)
            if c and type(c)==Commune:
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
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Departement.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_departement.html",
         {"form" : form ,
          "msg": msg,
          "regions": Departement.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_region.html",
         {"form" : form ,
          "msg": msg,
          "regions": Departement.objects.all () 
          }                     
        )
    
def add_village (req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    regions= cast_commune(pays)
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Commune.objects.get (pk =req.POST["region"])
            IndicatorVillage.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_village.html",
         {"form" : form ,
          "msg": msg,
          "regions": IndicatorVillage.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_village.html",
         {"form" : form, 
          "msg": msg,
          "regions": IndicatorVillage.objects.all () 
          }                     
        )
    
    
def add_prefecture (req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    
    # For Guinee Konakry the region  should be casted to precture
    regions= cast_region(pays)
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Prefecture.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_prefecture.html",
         {"form" : form ,
          "msg": msg,
          "regions": Prefecture.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_prefecture.html",
         {"form" : form, 
          "msg": msg,
          "regions": Prefecture.objects.all () 
          }                     
        )

def add_special_zone (req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    
    # For Guinee Konakry , for this moment , special zone should have region as parent
    regions= cast_region(pays)
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            SpecialZone.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_special_zone.html",
         {"form" : form ,
          "msg": msg,
          "regions": SpecialZone.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_speciale_zone.html",
         {"form" : form, 
          "msg": msg,
          "regions": SpecialZone.objects.all () 
          }                     
        )

def add_commune_hurbaine (req, pays):
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
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            CommuneHurbaine.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_commune_hurbaine.html",
         {"form" : form ,
          "msg": msg,
          "regions": CommuneHurbaine.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_commune_hurbaine.html",
         {"form" : form, 
          "msg": msg,
          "regions": CommuneHurbaine.objects.all () 
          }                     
        )


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
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            IndicatorVillage.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_village.html",
         {"form" : form ,
          "msg": msg,
          "regions": IndicatorVillage.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_village.html",
         {"form" : form, 
          "msg": msg,
          "regions": IndicatorVillage.objects.all () 
          }                     
        )

            
def add_secteur (req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    
    # For Guinee Bissau,secteur should have regions as parent
    regions= cast_region(pays)
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            Secteur.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
         "indicator/add_secteur.html",
         {"form" : form ,
          "msg": msg,
          "regions": Secteur.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
         "indicator/add_secteur.html",
         {"form" : form, 
          "msg": msg,
          "regions": Secteur.objects.all () 
          }                     
        )
    
    
def add_district(req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    
    # For Guinee Bissau,secteur should have regions as parent
    regions= cast_region(pays)
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Region.objects.get (pk =req.POST["region"])
            District.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_district.html",
         {"form" : form ,
          "msg": msg,
          "regions": District.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_district.html",
         {"form" : form, 
          "msg": msg,
          "regions": District.objects.all () 
          }                     
        )
    
    
def add_etat(req, pays):
    '''
    Add new commune
    '''
    pays  = get_object_or_404(Pays ,name__icontains = pays )
    regions =[]
    
    # For Guinee Bissau,secteur should have regions as parent
    #regions= cast_region(pays)
    regions  = [pays]
    
    msg = []
    #as tuple to fill the form choice fields dynamique 
    data =as_tuple (regions)
    form_class  = make_form (data,"region")
    form   = form_class ()
    if  req.method.lower ()=="post":
        form = form_class (req.POST)
        if form.is_valid ():
            #form.save ()
            parent = Pays.objects.get (pk =req.POST["region"])
            Etat.objects.create (parent =parent , name =req.POST.get ("name"))
            msg.append (_("OK"))
            return render_to_response (req,
        "indicator/add_etat.html",
         {"form" : form ,
          "msg": msg,
          "regions": Etat.objects.all () 
          }                     
        )
    
        else :
            msg.append (_("Not OK"))        
    return render_to_response (req,
        "indicator/add_etat.html",
         {"form" : form, 
          "msg": msg,
          "regions": Etat.objects.all () 
          }                     
        )
    
     
    
    

def get_village (pays , id):
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
        Region.objects.get (pk =id)
        
def filter_village_form (pays):
    def get_konakry_village_form():
        dict ={"villages": None  , 
               "regions":None  ,
               "special_zones":None ,
               "commune_hurbaines":None  ,
               "prefectures":None,
            
        }
        dict ["regions"]     =cast_region ("guinee_konakry")
        dict ["prefectures"] =cast_prefecture ("guinee_konakry")
        dict ["special_zones"]=cast_special_zone ("guinee_konakry")
        dict ["communes_hurbaines"] = cast_commune_hurbaine("guinee_konakry")
        dict ["villages"] = cast_village_guinee ("guinee_konakry")
        return dict
    
     
        
    def get_senegal_village_form ():
        dict ={"villages" :None ,
               "arrondissements" :None ,
               "commune_arrondissements":None,
               "departements" :None , 
               "regions" :None }

        dict ["regions"] = cast_region ("senegal")
        dict ["arrondissements"]=cast_arrondissement ("senegal")
        dict ["departements"]   =cast_departement ("senegal")
        dict ["commune_arrondissements"] =cast_arrondissement ("senegal")
        dict ["villages"] =cast_village ("senegal")
        return dict
    
    def get_somalie_village_form ():
        pass
        
        
        
                
def indicator_form ():
    dict ={}
    dict ["indicator"] =Indicator.objects.all ()

def add_project(req , pays):
    '''
    Each pays should have it own layout 
    Chaque pays doit avoir la liste de ces regions village , etc afin que dans 
    l'edition d'un project qu'on puisse filter et ajouter un village
    '''
    p = get_object_or_404(Project , name__icontains = pays.lower ())
    #Get the village filter form
    vil_form = filter_village_form (pays)
    ind_form =indicator_form ()
    
    #Go to create dynamically a project from based on the vil_from_filter and the indicator_form
    form =make_project_form (vil_form, ind_form)
    errors  =[]
    if req.method.lower () =="post":
        try:
           vil = req.POST.get ("village")
           # For Senegal we shoul fine a village 
           # For Gambie for exemple we should get a district 
           # For mauritanie we should have a region
           vil =  get_village (vil , pays)  
            
        except (KeyError, Exception):
           # The user does not choice a village or region or district
           pass   
           errors.append(_("Vous devez choisir le dernier element dans le filtre"))
           return render_to_response (req,template , {"errors":errors}) 
       
       
        else:
            if form.is_valid ():
                p =Project(name = req.POST.pop("name"))
                p.save (req.POST)
                
                
                
              
                
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
            indicator =form.save (commit =False)
            # If the form is a type list add list values to the indicator
            #print "form_value  :", dir(form_value)
            try:
                        value =form_value.data["value"]
                        print "value :" ,value.strip()
                        print "type :", indicator.type 
                        if value.strip()!=""  and indicator.type !="4":
                            raise ValidationError (_("La liste des valeurs doit etre saisie si \
                                    l'indicateur est de type list")) 
                        values = value.split ('\r\n')
                        indicator.save ()
                        for v in values:
                            indicator.indicatorvalue_set.add (
                                        IndicatorValue(value =str (v)))
                      
                        msg.append (_("OK"))
                        
                        #return HttpResponse ("OK")
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
    indicator = get_objets_or_404 (pk =id)
    template = "indicator/confirm_delete.html"
    if req.method.lower()=="post":
        try:
            req.POST.get ("confirm_delete")
            indicator.delete ()
            return HttpResponseRedirect ("/indicator/add_indicator")
        except KeyError , err:
            pass
        
        else:
          return render_to_reponse (
            req, 
            template , {}                          
            ) 
    return render_to_response(req, 
         template , {}
        )
        
def export_indicator (req):
    '''
    Export the indicator list
    '''
  

def export_project (req, pays ):
    pass

def search_project (req,pays):
    pass
def export_projects(req ,pays):
    pass
              
            