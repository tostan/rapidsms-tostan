from django import forms
from .models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import Permission
class PaysForm (forms.ModelForm):
    '''
    Pays Form
    >>> form=PaysForm (req.POST)
    >>> form.as_table ()
    '''
    name   =forms.CharField(
             label =_("Pays") ,
             widget= forms.TextInput({"size": "50"}))
    class Meta:
        model  =Pays
        fields = ("name")
        
class RegionForm(forms.Form):
    '''
    Region Form
    '''
    name = forms.CharField (
            label =_("Region"),
            widget= forms.TextInput({"size": "50"}))
    pays = forms.ModelChoiceField (
            queryset = Pays.objects.all () ,
            empty_label = "-"*50 )
    def save (self ,*args , **kwargs):
        super (RegionForm , self).save (*args , **kwargs)
    class Meta :
        fields  = ("name" , "pays")
        
class IndicatorValueForm (forms.ModelForm):
    '''
    Indicator Form 
    '''
    value = forms.CharField(
            label =_("Liste des valeurs de l'indicateur"),
            required =False,
            widget= forms.Textarea (attrs  ={"rows":"10" , "cols": "50"}))
    class Meta:
        model =IndicatorValue
        exclude = ("indicator" , "submission")
        
class IndicatorForm(forms.ModelForm):
    '''
    IndicatorForm 
    '''
    class Meta:
        exclude = ("created", "modified") 
        model = Indicator        

class  SearchIndicatorForm(forms.Form):
    '''
    Search  indicator Form 
    '''
    name = forms.CharField (label =_("Name") , help_text ="Saisir le nom de l'indicateur" , required =False)
    date = forms.DateField (label =_('La date de creation') , help_text =\
        _('La date de creation de cette indicateur dans la base de donnee') ,\
         widget =SelectDateWidget , required =False)
    edited_date  = forms.CharField  (label=_('Saisir une date(Exception!)') ,\
        help_text = 'YYYY/MM/DD' , required =False)
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
class IndicatorStatForm (forms.Form):
    '''
    Create form to display statistiques data related of the indicator
    '''
    indicator = forms.ModelChoiceField (
                label = _("Choisir un seul Indicateur"),
                queryset=Indicator.objects.all ())
    projects  = forms.ModelMultipleChoiceField(
                label = _("CHoisir les projects"),
                queryset =Project.objects.all ())


class IndicatorExportForm (forms.Form):
    '''
    Create form to display statistiques data related of the indicator
    '''
    indicators  = forms.ModelMultipleChoiceField(
                label = _("Choisir le ou les  indicateurs a exporter"),
                queryset =Indicator.objects.all ())

class ProjectForm (forms.ModelForm):
     ''' Create a project-based model form '''
     class Meta :
         model = Project
         
class ProjectStatForm (forms.Form):
    '''
    Create form to display statistiques date related of the  projet
    '''
    project = forms.ModelChoiceField (
                label = _("Choisir un seul projet"),
                queryset=Project.objects.all ())
    indicators  = forms.ModelMultipleChoiceField(
                label = _("Choisir les  indicateurs"),
                queryset =Indicator.objects.all ())

class ProjectExportForm (forms.Form):
    '''
    Create form to display statistiques data related of the indicator
    '''
    projects  = forms.ModelMultipleChoiceField(
                label = _("Choisir le ou les  projets a exporter"),
                queryset =Project.objects.all ()) 

class VillageStatForm (forms.Form):
    '''
    The village list for export not for stat
    '''
    villages = forms.ModelMultipleChoiceField (
                label = _("Choisir les utilisateurs a expoter"),
                #Uniquement les utilsateurs du groupe des indicateurs
                queryset=IndicatorVillage.objects.all ())

class VillageExportForm (forms.Form):
    '''
    Create form to display statistiques data related of the indicator
    '''
    villages  = forms.ModelMultipleChoiceField(
                label = _("Choisir le ou les  villages a exporter"),
                queryset =Village.objects.all ()) 

class UserStatForm (forms.Form):
    '''
    The user list for export not for stat
    '''
    users = forms.ModelMultipleChoiceField (
            label = _("Choisir les utilisateurs a expoter"),
            #Uniquement les utilsateurs du groupe des indicateurs
            queryset=User.objects.all ().filter(groups__name__in =['indicator_edit']))

class UserExportForm (forms.Form):
    '''
    Create form to display statistiques data related of the indicator
    '''
    users  = forms.ModelMultipleChoiceField(
                label = _("Choisir le ou les  utilisateurs a exporter"),
                queryset=User.objects.all ().filter(groups__name__in =['indicator_edit' ,'indicator_admin'])) 
    
class  UserForm (forms.Form):
       '''create a form to create user , update .The user is the editor od the indicator system'''
       first_name  = forms.CharField (
                     label = _("Nom de l'employer pour la saisie") , 
                     widget =forms.TextInput ({"size":"50"}))
       last_name  = forms.CharField (
                     label = _("Prenom de l'employer pour la saisie") , 
                     widget =forms.TextInput ({"size":"50"}))
       # to pass to django.contrib.auth.views as login
       username  = forms.CharField (
                     label = _("Le login") , 
                     widget =forms.TextInput ({"size":"50"}))
       password  =  forms.CharField (
                     label = _("Mot de passe pour la saisie") ,
                      widget =forms.PasswordInput ({"size":"50"}))
       group     = forms.ModelChoiceField(
                label = _("Choisir le groupe de l'utilsateur"),
                queryset=Group.objects.all ().filter (name__in= ['indicator_edit' , 'indicator_admin'] )) 
       def  save (self):
	   '''
	   Save the user and add to the indicator_editor group'''
           data  = self.cleaned_data
           user =User.objects.create (first_name =data["first_name"] ,last_name=data ["last_name"] ,
                 password =data['password'] , username = data['username'])
           user.groups.add (data['group'])
           # Add permission to admin  to the user if it is into the group admin
           user.save ()
           if  'indicator_admin' in data['group'].name:
                # Add the Admin permission to the user
                perm =Permission.objects.get(codename = 'can_admin')
           else:
                # Add the Edit permission to the user
                perm =Permission.objects.get(codename = 'can_edit')
           user.user_permissions.add (perm)
           user.save ()
           
class  UserSearchForm (forms.Form):
       '''
       create a basic form to allow searchin user 
       '''
       first_name  = forms.CharField (
                     required =False,
                     label = _("Nom de l'employer pour la saisie") , 
                     widget =forms.TextInput ({"size":"50"}))
       last_name  = forms.CharField (
                     required=False,
                     label = _("Prenom de l'employer pour la saisie") , 
                     widget =forms.TextInput ({"size":"50"}))
