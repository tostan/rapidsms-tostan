from django import forms
from .models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.db.models import Q

class PaysForm (forms.ModelForm):
    name   =forms.CharField(
             label =_("Pays") ,
             widget= forms.TextInput({"size": "50"})                 
            )
    class Meta:
        model  =Pays
        fields = ("name")
        
class RegionForm(forms.Form):
    name = forms.CharField (
            label =_("Region"),
            widget= forms.TextInput({"size": "50"})
            )
    pays = forms.ModelChoiceField (
            queryset = Pays.objects.all () ,
            empty_label = "-"*50 )
    
    def save (self):
        print  "FIELDS"
        print self.fields
        super (RegionForm , self).save ()
    
    class Meta :
        fields  = ("name" , "pays")
        
class IndicatorValueForm (forms.ModelForm):
    value = forms.CharField(
            label =_("Liste des valeurs de l'indicateur"),
            required =False,
            widget= forms.Textarea (attrs  ={"rows":"10" , "cols": "50"}))
    
    
    class Meta:
        model =IndicatorValue
        exclude = ("indicator" , "submission")
        
        
class IndicatorForm(forms.ModelForm):
    
    
    class Meta:
        exclude = ("created", "modified") 
        model = Indicator        

class  SearchIndicatorForm(forms.Form):
    name = forms.CharField (_("Name") , help_text ="Saisir le nom de l'indicateur")
    def clean_name(self) :
        '''
        Le name est valide automatquement par django car required =True , mais 
        je veux appliquer en plus de la validation  de django ma  propre validation
        '''
        cleaned_data  = self.cleaned_data 
        name = cleaned_data["name"]
        if not name or name.strip() =="":
            raise ValidationError (_("Vous devez saisir une valeur pour effectuer une recherche"))
        return  name 
    
def get_area_form(qs, area_parent):
    fields = {"name" :None  , "surface" :None , "latitude":None , "longitude":None}
    for k in fields :
        fields [k]  = forms.CharField (
                     label = k , 
                     widget =forms.TextInput ({"size":"50"})
                    )
    fields[area_parent]  = forms.ChoiceField (
                            label =area_parent , 
                            choices = qs)
    def clean (self):
        print "CLEANED data"
        print self.cleaned_data
        return self.cleaned_data
        
    return type ("FormArea" , (forms.BaseForm,) , {"base_fields":fields  ,"clean" : clean})

class IndicatorStatForm (forms.Form):
    indicator = forms.ModelChoiceField (
                label = _("Choisir un seul Indicateur"),
                queryset=Indicator.objects.all ()
                )
    projects  = forms.ModelMultipleChoiceField(
                label = _("CHoisir les projects"),
                queryset =Project.objects.all ()
                ) 
    
class ProjectStatForm (forms.Form):
    indicator = forms.ModelChoiceField (
                label = _("Choisir un seul projet"),
                queryset=Project.objects.all ()
                )
    projects  = forms.ModelMultipleChoiceField(
                label = _("CHoisir les  indicateurs"),
                queryset =Indicator.objects.all ()
                )
    
class  UserForm (forms.Form):
       first_name  = forms.CharField (
                     label = _("Nom de l'employer pour la saisie") , 
                     widget =forms.TextInput ({"size":"50"}))
       last_name  = forms.CharField (
                     label = _("Prenom de l'employer pour la saisie") , 
                     widget =forms.TextInput ({"size":"50"}))
       password  =  forms.CharField (
                     label = _("Mot de passe pour la saisie") ,
                      widget =forms.PasswordInput ({"size":"50"})) 
       def  save (self):
           data  = self.cleaned_data
           user =User.objects.create (username ="%s :%s"%(data["first_name"] ,data ["last_name"]) ,
                                      password =data['password'])
           indicator_group  , created= Group.objects.get_or_create(name="indicator_edit")
           user.groups.add (indicator_group)
           user.save ()
           
class  UserSearchForm (forms.Form):
       first_name  = forms.CharField (
                     required =False,
                     label = _("Nom de l'employer pour la saisie") , 
                     widget =forms.TextInput ({"size":"50"}))
       last_name  = forms.CharField (
                     required=False,
                     label = _("Prenom de l'employer pour la saisie") , 
                     widget =forms.TextInput ({"size":"50"}))