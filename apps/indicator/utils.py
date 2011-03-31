from django import forms
from django.utils.translation import  ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
from datetime import datetime , date 
from indicator.models import *
from django.utils.text import capfirst
#def _get_village_form(form_data):
#     '''create a form to get area used into the project'''
#     fields  = {}
#     village_list  = form_data.pop("villages")
#     for item , qs  in form_data.iteritems () :
#             fields [str (item)] = forms.ChoiceField(label =_(str(item)),
#             choices  = as_tuple (qs))
#     fields["villages"] = forms.MultipleChoiceField (
#             label =_("Villages du projet") ,
#             choices = as_tuple (village_list))
#     def clean (self):
#           return self.cleaned_data 
#     return type ("FormArea" , (forms.BaseForm , ) , {"base_fields": fields , "clean": clean})

class VillageForm(forms.Form):
	def __init__(self , data =None , **kwargs):
		fields  =None 
		if "area_of_contry" in kwargs:
			fields  = kwargs.pop ("area_of_contry")
		if data :
			super (VillageForm , self).__init__(data , **kwargs)
		else :
			super (VillageForm , self).__init__(**kwargs)
		if fields:
			for  item ,qs in  fields:
				if item !="villages":
					self.fields [item] =forms.ChoiceField (
						label = capfirst (item [:-1].replace ("_", " ")),
		        			choices = as_tuple(qs))
				else:
					self.fields[item]  =forms.MultipleChoiceField (
					label  ="Villages",
					choices=as_tuple (qs))
		
#def _get_indicator_form(ind_dict):
#     ''' Create form to get some attribute of indicator used to create projet'''
#     fields  = {}
#     fields  ["titre"]  =forms.CharField (label    =_("Titre"), widget   = forms.TextInput (attrs  = {"size": "50"}))
#     fields  ["bailleur"] =forms.CharField (label  =_("Bailleur") , widget  =forms.TextInput (attrs  ={"size" : "50"}))
#     fields  ["description"] =forms.CharField (label  =_("Description du Projet") ,widget = forms.Textarea (attrs  ={"size" : "50"}))
#     fields  ["started"]  = forms.DateField (label =_("Date de demarrage"),widget  = SelectDateWidget ,required =False , initial =date.today)
#     fields ['edited_date'] = forms.CharField  (label =_('Date de demarrage') , help_text = 'YYYY/MM/DD' , required =False)
#     indicator_list=ind_dict.pop ("indicators")  
#     fields ['indicators'] =forms.MultipleChoiceField(label =_("Indicateurs du projet"),widget =forms.CheckboxSelectMultiple ,choices = as_tuple (indicator_list))
     
#     def clean (self):
#          return self.cleaned_data 
#     return type ("FormArea" , (forms.BaseForm , ) , 
#        {"base_fields": fields , "clean": clean})


class IndicatorForm (forms.Form):
	'''
        Create an indicatro form
	'''
	titre  = forms.CharField (label = "Titre du projet")
	bailleur =  forms.CharField (label = "Le bailleur de fonds du projet")
	description  = forms.CharField (label = "La description du projet")
	started      =forms.DateField (label ="Date de Demarrage du projet" , widget =	SelectDateWidget , required =False , initial =date.today)
	def  __init__(self  , data =None  , **kwargs):
		if  "indicators"  in kwargs:
			indicator_list  = kwargs.pop ("indicators")
		if data :
			super (IndicatorForm , self ).__init__(data, **kwargs)
		else :
			super (IndicatorForm , self).__init__(**kwargs)
		if indicator_list :
			 self.fields ["indicators"] = forms.MultipleChoiceField  (label  = "Chosir les indicateurs su projet",
			 widget  = forms.CheckboxSelectMultiple , 
			 choices   = as_tuple (indicator_list))
	

#def _get_submission_form(submission):
#     '''Create a dynamique form to store store submission '''
#     fields  ={}
#     indicatorsubmissions = submission.indicatorsubmissions.all ()
#     for indicator_submission in  indicatorsubmissions:
#             fields ["%s_%s"%(indicator.name,indicator.pk)] =forms.CharField ()



#def _get_search_project_form():
#     ''' create a dynamique form to store project'''
#     fields  = {}
#     fields ['name'] = forms.CharField (required  = False ,label =_("Nom du projet") ,widget =forms.TextInput (attrs  = {"size": "50"}))
#     fields ['villages']= forms.MultipleChoiceField (required =False , choices =as_tuple(IndicatorVillage.objects.all ()),label =_("Village dans lequel le projet est present"))
#     fields ['indicators']= forms.MultipleChoiceField (required =False,choices =as_tuple(Indicator.objects.all ()),label = _("Chosir un indicateur contenu dans le projet"))
     
#     def clean (self):
#         return self.cleaned_data
#     
#     return type ("ProjectFormSearch" , (forms.BaseForm ,) ,{"base_fields": fields  , "clean": clean})
      
class  SearchProjectForm (forms.Form):
	name  = forms.CharField(label ="Nom", required =False)
	villages   = forms.MultipleChoiceField (required =False ,label ="Villages" , choices = as_tuple (IndicatorVillage.objects.all ()))
        indicators = forms.MultipleChoiceField (required =False , label ="Inicateurs" , choices = as_tuple (Indicator.objects.all ()))

#def _get_area_form(qs, area_parent):
#     ''' create a dynamique form to store area'''
#     fields = {"name" :None  , "surface" :None , "latitude":None , "longitude":None}
#     for k in fields :
#         fields [k]  = forms.CharField (label = k , widget =forms.TextInput ({"size":"50"}) )

#    # Tres important
#     # Le label est generic , cela veut  dire que ce form est tulise quand  nous
#     # creons une region , un  departement
#     # un arrondissement , ou je ne sais quoi d'aute 
#     fields[area_parent]  = forms.ChoiceField (label ='La Zone qui contient la zone a creer' , choices = qs)
#     
#     def clean (self):
#         return self.cleaned_data
#     
#     return type ("FormArea" , (forms.BaseForm,) , {"base_fields":fields  ,"clean" : clean})


class  AreaForm(forms.Form):
	'''
	Create a dynamique  form to strore area ,and create them if necessary
	'''
	name      = forms.CharField (label ="Nom")
	#surface   = forms.CharField (label ="Superficie")
	#latitude  = forms.CharField (label = "Latitude")
	#longitude = forms.CharField (label ="LOngitude")

	def __init__(self , data =None , **kwargs):
		# The list of parents objects  , for exemple if we are going to  create village
		# data is set to the list of parents  that is list of departemenents
		parent_item = parent_objs  =None
		# The list of parent objects ,for exemple if we are creating village 
		# `parents` is a list of parent village , ie list of rurale communities
		if  "parents" in  kwargs :
			parent_item , parent_objs  = kwargs.pop ('parents')
		# The list of parent of the parent's villages 
		# For exemple if we are creating a village  , this  content dict  of list 
		# of parent of rural communities
		# {'departements' : ""} , {"regions"}
		kwargs_ = kwargs.copy ()
		kwargs  ={}
		if data :
		    super (AreaForm , self).__init__(data , **kwargs)
		else :
		    super (AreaForm ,self).__init__(**kwargs)
		
		# A dict of list of regions , deparetements arrondissement , commune arrondissement ,commune
		# in case we are creating  village 
		if len (kwargs_) and "parents_rest" in kwargs_ and kwargs_.get("parents_rest"):
			# Get parents_rest list of objects
			kwargs_ = kwargs_.get ("parents_rest")
			for attr_name, values in  kwargs_:
				self.fields [attr_name] = forms.ChoiceField(
					 label    = capfirst(attr_name),
				         required = False,
					 widget   = forms.Select (attrs ={'onchange':'this.form.submit();'}) ,  
					 choices  = as_tuple(values))
				#del kwargs_[attr_name]
		# A rural communities list for exemple in case we are creating village
		if parent_item and parent_objs:
		    self.fields [parent_item] = forms.ChoiceField (
			label =capfirst (parent_item) , choices = as_tuple (parent_objs))
		
class  AreaFormForVillage (AreaForm):
	latitude  = forms.CharField (label ="Latitude")
	longitude = forms.CharField (label ="Longitude")
	def __init__(self , data  =None , **kwargs):
		super (AreaFormForVillage,self).__init__(data =data, **kwargs)
	
def as_tuple(qs):
    '''Given a list of objets return a tuple'''
    return [("" , "--")]+[ (q.pk , q.__unicode__()) for q in qs]
