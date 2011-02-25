from django import forms
from django.utils.translation import  ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
from datetime import datetime , date 
from indicator.models import *
def _get_village_form(form_data):
     '''create a form to get area used into the project'''
     fields  = {}
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

def _get_indicator_form(ind_dict):
     ''' Create form to get some attribute of indicator used to create projet'''
     fields  = {}
     fields  ["titre"]  =forms.CharField (label    =_("Titre"), widget   = forms.TextInput (attrs  = {"size": "50"}))
     fields  ["bailleur"] =forms.CharField (label  =_("Bailleur") , widget  =forms.TextInput (attrs  ={"size" : "50"}))
     fields  ["description"] =forms.CharField (label  =_("Description du Projet") ,widget = forms.Textarea (attrs  ={"size" : "50"}))
     fields  ["started"]  = forms.DateField (label =_("Date de demarrage"),widget  = SelectDateWidget ,required =False , initial =date.today)
     fields ['edited_date'] = forms.CharField  (label =_('Date de demarrage') , help_text = 'YYYY/MM/DD' , required =False)
     indicator_list=ind_dict.pop ("indicators")  
     fields ['indicators'] =forms.MultipleChoiceField(label =_("Indicateurs du projet"),widget =forms.CheckboxSelectMultiple ,choices = as_tuple (indicator_list))
     
     def clean (self):
           return self.cleaned_data 
     return type ("FormArea" , (forms.BaseForm , ) , 
        {"base_fields": fields , "clean": clean})

def _get_submission_form(submission):
     '''Create a dynamique form to store store submission '''
     fields  ={}
     indicatorsubmissions = submission.indicatorsubmissions.all ()
     for indicator_submission in  indicatorsubmissions:
             fields ["%s_%s"%(indicator.name,indicator.pk)] =forms.CharField ()

def _get_search_project_form():
     ''' create a dynamique form to store project'''
     fields  = {}
     fields ['name'] = forms.CharField (required  = False ,label =_("Nom du projet") ,widget =forms.TextInput (attrs  = {"size": "50"}))
     fields ['villages']= forms.MultipleChoiceField (required =False , choices =as_tuple(IndicatorVillage.objects.all ()),label =_("Village dans lequel le projet est present"))
     fields ['indicators']= forms.MultipleChoiceField (required =False,choices =as_tuple(Indicator.objects.all ()),label = _("Chosir un indicateur contenu dans le projet"))
     
     def clean (self):
         return self.cleaned_data
     
     return type ("ProjectFormSearch" , (forms.BaseForm ,) ,{"base_fields": fields  , "clean": clean})
      
def _get_area_form(qs, area_parent):
     ''' create a dynamique form to store area'''
     fields = {"name" :None  , "surface" :None , "latitude":None , "longitude":None}
     for k in fields :
         fields [k]  = forms.CharField (label = k , widget =forms.TextInput ({"size":"50"}) )

     # Tres important
     # Le label est generic , cela veut  dire que ce form est tulise quand  nous
     # creons une region , un  departement
     # un arrondissement , ou je ne sais quoi d'aute 
     fields[area_parent]  = forms.ChoiceField (label ='La Zone qui contient la zone a creer' , choices = qs)
     
     def clean (self):
         return self.cleaned_data
     
     return type ("FormArea" , (forms.BaseForm,) , {"base_fields":fields  ,"clean" : clean})

def as_tuple(qs):
    '''Given a list of objets return a tuple'''
    return [ (q.pk , q.__unicode__()) for q in qs]
