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
             widget= forms.TextInput())
    class Meta:
        model  =Pays
        fields = ("name")
        
class RegionForm(forms.Form):
    '''
    Region Form
    '''
    name = forms.CharField (
            label =_("Region"),
            widget= forms.TextInput())
    pays = forms.ModelChoiceField (
            queryset = Pays.objects.all () ,
            empty_label = "-" )
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
            widget= forms.Textarea ())
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
    


class IndicatorExportForm (forms.Form):
    '''
    Create form to display statistiques data related of the indicator
    '''
    indicators  = forms.ModelMultipleChoiceField(label = _("Choisir le ou les  indicateurs a exporter"),
                queryset =Indicator.objects.all () ,required =False)

class ProjectForm (forms.ModelForm):
     ''' Create a project-based model form '''
     class Meta :
         model = Project
         
class ProjectStatForm (forms.Form):
    '''
    Create form to display statistiques date related of the  projet
    '''
    project    = forms.ModelChoiceField(queryset =Project.objects.all ())
    indicator  = forms.ModelChoiceField(queryset =Indicator.objects.all ()) 
    village    = forms.ModelChoiceField(queryset =IndicatorVillage.objects.all ())
    date1      = forms.DateField (label ="Le mois de saisie (1)" ,widget =SelectDateWidget , required =False)
    date2      = forms.DateField (label ="Le mois de saisie (2)" ,widget =SelectDateWidget , required =False)

class ProjectExportForm (forms.Form):
    '''
    Create form to display statistiques data related of the indicator
    '''
    projects    = forms.ModelMultipleChoiceField(queryset =Project.objects.all() ,required =False)
  


class VillageExportForm (forms.Form):
    '''
    Create form to display statistiques data related of the indicator
    '''
    villages  = forms.ModelMultipleChoiceField(
                label = _("Choisir le ou les  villages a exporter"),
                queryset =IndicatorVillage.objects.all () , required =False) 

class DataExportForm (forms.Form):
      project = forms.ModelChoiceField (
                label = _("Choisir un projet"),
                required =False,
                queryset=Project.objects.all ())
      villages  = forms.ModelMultipleChoiceField(
                label = _("Les villages"),
                queryset =IndicatorVillage.objects.all () , required =False) 
      date_edit = forms.DateField (label =_('Le mois de saisie') , 
         widget =SelectDateWidget , required =False)
    
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
                queryset=User.objects.all ().filter(groups__name__in =['indicator_edit' ,'indicator_admin']),
                required =False) 
    
class  UserForm (forms.Form):
       '''create a form to create user , update .The user is the editor od the indicator system'''
       first_name  = forms.CharField (
                     label = _("Nom de l'employer pour la saisie") , 
                     widget =forms.TextInput ())
       last_name  = forms.CharField (
                     label = _("Prenom de l'employer pour la saisie") , 
                     widget =forms.TextInput ())
       # to pass to django.contrib.auth.views as login
       username  = forms.CharField (
                     label = _("Le login") , 
                     widget =forms.TextInput ())
       password  =  forms.CharField (
                     label = _("Mot de passe pour la saisie") ,
                      widget =forms.PasswordInput ())
       group     = forms.ModelChoiceField(
                label = _("Choisir le groupe de l'utilsateur"),
                queryset=Group.objects.all ().filter (name__in= ['indicator_edit' , 'indicator_admin'] )) 
       def  save (self):
	   '''
	   Save the user and add to the indicator_editor group'''
           data  = self.cleaned_data
           # Login must be unique
           #update
           perm_list  = [Permission.objects.get(codename = 'can_admin') ,
                         Permission.objects.get(codename = 'can_edit')]
           group_list  = [Group.objects.get(name = 'indicator_edit') ,
                         Group.objects.get(name  = 'indicator_admin')]
           try:
               #Updatting user 
               user = User.objects.get (username = data['username'])
           except:
               # creating user
               user =User.objects.create_user(
                        email = '' ,
                        password =data['password'] ,
                        username = data['username'])
           user.first_name = data ['first_name']
           user.last_name  = data ['last_name']
           # Add permission to admin  to the user if it is into the group admin
           user.save ()
           # IF update remove the existing perimssion 
           for  perm in  perm_list :
                try:
                    user.user_permissions.remove (perm)
                except :
                    pass
           #If update group
           #A user should not to be in two groups in  the same time 
           for group in  group_list :
                try:
                     user.groups.remove(group)
                except :
                    pass
           user.groups.add (data['group'])
           if  'indicator_admin' in data['group'].name:
                 # Add the Admin permission to the user
                 user.user_permissions.add (perm_list [0])
           else: user.user_permissions.add (perm_list [1])
           
           #Set user to be actif
           user.is_active =True          
           user.save ()
           
class  UserSearchForm (forms.Form):
       '''
       create a basic form to allow searchin user 
       '''
       first_name  = forms.CharField (
                     required =False,
                     label = _("Nom de l'employer pour la saisie") , 
                     widget =forms.TextInput ())
       last_name  = forms.CharField (
                     required=False,
                     label = _("Prenom de l'employer pour la saisie") , 
                     widget =forms.TextInput ())

class RegionForm_(forms.ModelForm):
    class Meta:
        model  = Region
        
class DepartementForm(forms.ModelForm):
    class Meta:
        model  = Departement
class ArrondissementForm(forms.ModelForm):
    class Meta:
        model  = Arrondissement
class CommuneArrondissementForm(forms.ModelForm):
    class Meta:
        model  = CommuneArrondissement
        
class CommuneForm(forms.ModelForm):
    class Meta:
        model  = Commune

class  IndicatorVillageForm(forms.ModelForm):
    class Meta:
        model  = IndicatorVillage

class  PrefectureForm(forms.ModelForm):
    class Meta:
        model  = Prefecture
        
class  SuPrefectureForm(forms.ModelForm):
    class Meta:
        model  = SubPrefecture

class  SecteurForm(forms.ModelForm):
    class Meta:
        model  = Secteur
        
class  DistrictForm(forms.ModelForm):
    class Meta:
        model  = District
        