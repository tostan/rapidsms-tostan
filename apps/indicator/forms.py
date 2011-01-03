from django import forms
from .models import *
from django.utils.translation import ugettext_lazy as _
class PaysForm (forms.ModelForm):
    class Meta:
        model  =Pays
        fields = ("name")
        
class RegionForm(forms.Form):
    name = forms.CharField (max_length = 100)
    pays = forms.ModelChoiceField (queryset = Pays.objects.all ())
    
    def save (self):
        print  "FIELDS"
        print self.fields
        super (RegionForm , self).save ()
    
    class Meta :
        fields  = ("name" , "pays")
        
class IndicatorValueForm (forms.ModelForm):
    value = forms.CharField(_("Liste des valeurs de l'indicateur"),
            required =False,
            help_text = _("Saisir les valeurs de si l'indicateur est de type list (Une valeur par ligne)"),
            widget= forms.Textarea ())
    
    
    class Meta:
        model =IndicatorValue
        exclude = ("indicator")
        
        
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
        
    