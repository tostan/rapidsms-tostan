#!/usr/bin/env/python 
# vim :ai ts=4 sts=4 et sw =4 coding =utf-8
from django.db import models
# Create your Django models here, if you need them.
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from rapidsuivi.models import *
from django.contrib.admin.models import User
from django import forms 
from datetime import date 
from django.forms.extras.widgets import SelectDateWidget

class Project(models.Model):
    '''
    Model to store all tostan ,s projects 
    Model pour garder tous les projects de tostan ,ainsi que leur description 
    '''
    name = models.CharField (
		_("Name of the project"),
		 max_length = 160 ,
		 null =True , 
	 	 blank =True)
    titre =models.CharField (
		_("Title of the project") ,
		max_length =160 ,
		null =True ,
		blank =True)
    bailleur =models.CharField (_
		("Bailleur du project"),
		 max_length =160 , 
		null =True , blank =True)
    description = models.CharField (
		_("The description of the project") , 
		max_length =160, 
		null =True , blank =True)
    #List of the indicators of projects
    indicators = models.ManyToManyField ("Indicator", null =True , blank= True)
    # Village of the projects
    villages   = models.ManyToManyField ("Area" , null =True , blank =True)
    created    = models.DateTimeField (auto_now_add =True)

    class Meta:
        permissions = (
            ("can_admin", "Active Member"),
            ("can_edit", "Edit Member"),
        )

    @property
    def submissions(self):
        submission_list  = list ()
        if self.fiches.count ()>0:
            for fiche in self.fiches.all():                 
                 if fiche.submissions.count ()>0:
                     submission_list.extend(fiche.submissions.all())
        return submission_list

    @property
    def indicatorvalues(self):
        values  = {}
        if len (self.submissions):
          for submission in self.submissions:
             for indicatorvalue in  submission.indicatorvalues.all():
                indicator = indicatorvalue.indicator
                #Only the indicator int value will be retreived ,
                # Skip the type string
                try:
                    if indicator in values :
                         values [indicator] =+int(indicatorvalue.value)
                    else:
                        values [indicator] = int(indicatorvalue.value) 
                except   Exception  as e:
                    #Sure it is not a int or float value
                    pass
        return values
                                                              
    @classmethod 
    def create_project (cls, villages , indicators, **kwargs):
          '''
	  create a new project 
	  ''' 
	  try:
            p = Project.objects.create(**kwargs)
            p.villages= villages
            p.indicators= indicators
            Fiche.create_fiche (p, indicators)
            return True
	  except Exception , err:
              import traceback 
              traceback.print_exc()
      	      return False
    def __unicode__(self):
        return u"%s -%s -%s"%(self.name , self.titre , self.bailleur)

class Indicator (models.Model): 
    '''
    Model to store an indicator , it is defined by the name , 
    the type (text , date , list , numeric)
    Model pour garder les indicateurs , chaque indicateur est definit par son type , 
    (text, date , numeric , list)    
    '''   
    TYPE_TEXT    = 't'
    TYPE_NUMERIC = 'n'
    TYPE_DATE    = 'd'
    TYPE_LIST    = 'l'
    MENSUEL      = "m"
    SEMESTRIEL   = "s"
    TRIMESTRIEL  = "t"
    ANNUEL       = 'a'
   
    INDICATOR_TYPE_CHOICES =(
     (TYPE_TEXT , "text" ),
     (TYPE_NUMERIC , "numeric"),
     (TYPE_DATE , "date"),                    
     (TYPE_LIST, "list")                   
    )
    
    INDICATOR_PERIOD_CHOICES =(
        (MENSUEL , "Mensuel") ,
        (SEMESTRIEL , "Semestriel"),
        (TRIMESTRIEL, "Trimestriel"),
        (ANNUEL , "Annuel")                           
    )
    name  =models.CharField (max_length = 200, null =True , blank =True)
    type  =models.CharField (max_length =2, choices =INDICATOR_TYPE_CHOICES)
    period   = models.CharField (max_length =2  , null  =True  , choices  =INDICATOR_PERIOD_CHOICES)
    created =models.DateTimeField(auto_now_add =True)
    modified =models.DateTimeField (auto_now =True)
    description =models.CharField (max_length = 200 , null =True , blank =True)

    @property
    def expected_values (self):
        '''The value expected by the indicator , if not type list , return  '' , if
        type is list return the list of value of the indicator'''
        if self.type != Indicator.TYPE_LIST:
            return ''
        values =self.values.filter (submission__isnull =True)
        if values.count ()>0:
            return   '\n\r' .join  (values.values_list ('value', flat = True))
        return ''        

    @property
    def type_str(self):
        return self.get_type_display ()
    
    def validate (self, type , value):   
        if type =="text":
            return validate_text ()
        elif type =="numeric":
            return validate_numeric
        elif type =="list":
            validate_list ()
        elif type =="date":
            validate_date ()
        
    def validate_date (self, value):
        pass
    
    def validate_numeric (self, value):
        try:
            float (value)
        except ValueError,err:
            raise ValidattionError ("Numeric is required , get : %s "%str(value))
    
    def validate_text (self, value):
        try:
            str (value)
        except ValueError ,e :
            raise ValidationError ("Text is reauired")

    def __unicode__(self):
        return  "%s"%(self.name)

class IndicatorValue(models.Model):
    '''
    Each indicator whish is a list will have many values
    Chaque indicator de type list aura plusieurs valeurs
    '''
    indicator = models.ForeignKey("Indicator"  , related_name= "values")
    submission= models.ForeignKey("Submission" , null =True , related_name ="indicatorvalues")
    value = models.CharField (
		_("La valeur de l'indicateur "),
                max_length = 200 , null =True , blank =True,
                help_text =_("Saisir ici la liste des valeurs de l'indicateur si l'indicacteur est une liste de choix")) 
    def __unicode__(self):
        return "%s" %(self.value)

class Fiche (models.Model):  
      '''
      Each project will have many fiches depending to the indicators  types
      Chaque projet aura plusieurs fiches  (semestrielle , mensuelle ,annuelle , trimestrielle)
      dependant de sa liste des indicateurs.
      les indicateurs mensuelles ===> dans la fiche mensuelle
      les indicateurs trimestrielle ==> dans la fiche trimestrielle
      les indicateurs anuelles ==>dans la fiche annuelle
      
      ===
      Chaque fiche peut avoir plusieurs submissions ie une sauvevegarde de valeurs
      via un formulaire de la fiche , on doit savoir l'utilisateur qui a fait
      cette submission (Django User)
      '''
      
      MENSUEL     = "m"
      SEMESTRIEL  = "s"
      TRIMESTRIEL = "t"
      ANNUEL      = 'a'
      FICHE_PERIOD_CHOICES =(
        (MENSUEL , "Mensuel") ,
        (SEMESTRIEL , "Semestriel"),
        (TRIMESTRIEL, "Trimestriel"),
        (ANNUEL , "Annuel")                           
      )
      project    = models.ForeignKey ("Project" , related_name = "fiches")
      # L'indicator depend de du type de la fiche      
      indicators = models.ManyToManyField("Indicator", null =True , blank =True)
      period     = models.CharField (max_length = 2 , choices  = FICHE_PERIOD_CHOICES)
      created    = models.DateTimeField (auto_now_add =True)

      @classmethod 
      def create_fiche (cls , project , indicators):
            dict  = {"m" : [] , "s" :[] , 't' :[] , 'a':[]}  
            for indicator in indicators :
                if indicator.period ==Fiche.MENSUEL:
                    dict ['m'] .append (indicator)
                elif indicator.period ==Fiche.ANNUEL:
                    dict['a'].append (indicator)
                elif indicator.period  ==Fiche.SEMESTRIEL:
                    dict ['s'].append (indicator)                    
                elif indicator.period==Fiche.TRIMESTRIEL:
                    dict['t'].append (indicator)
                else :
                    pass
            if len (dict['m']):
                f =Fiche.objects.create (
                       project = project ,
                       period = Fiche.MENSUEL)
                f.indicators = (dict['m'])
            if len (dict['s']):
                f= Fiche.objects.create (
                                project = project , 
                                period = Fiche.SEMESTRIEL)
                f.indicators =dict['s']
            if len (dict['t']):
                f=Fiche.objects.create (
                                project = project , 
                                period = Fiche.TRIMESTRIEL)
                f.indicators = dict['t']
            if len (dict['a']):
                f=Fiche.objects.create (
                                project = project ,
                                period = Fiche.ANNUEL)
                f.indicators = dict['a']
    
      def form_save  (self , indicators):
          '''
          Given a list of indicators (10 per page) , we create a dynamique from for them
          '''     
          fields  ={}
          for indicator in indicators:
              if indicator.type in (Indicator.TYPE_TEXT ,Indicator.TYPE_NUMERIC):
                 fields["indicator_%s"%indicator.pk] = forms.CharField (
                                            label =_(indicator.name) ,
                                            widget =forms.TextInput (attrs  ={"size" : "50"}),
                                            )
              elif indicator.type == Indicator.TYPE_DATE:
                  fields['indicator_%s'%indicator.pk] = forms.DateField(
                                            label =_(indicator.name),
                                            widget =SelectDateWidget,
                                            initial= date.today)
              else:            
                fields["indicator_%s"%indicator.pk] = forms.MultipleChoiceField (
                        label = _(indicator.name),
                        widget = forms.CheckboxSelectMultiple() , 
                        choices  = as_tuple(indicator.values.all ())
                )
          def clean (self):
             return self.cleaned_data
          return type ("FormFiche", 
                       (forms.BaseForm ,) ,
                       {"base_fields" : fields , "clean" :clean})
    
      def form_edit (self ,submission ,indicator_values):
          '''
	  Basically different to the first submission form ,only  for edition
	  '''
          fields  ={}   
          for indicator_value in indicator_values:
              if indicator_value.indicator.type in (Indicator.TYPE_TEXT ,Indicator.TYPE_NUMERIC):
                 fields["indicator_%s"%indicator_value.indicator.pk] = forms.CharField (
                                label =_(indicator_value.indicator.name),
                                widget =forms.TextInput (attrs  ={"size" : "50"}),
                                initial =str (indicator_value.value))
              elif indicator_value.indicator.type in (Indicator.TYPE_DATE):
                 fields["indicator_%s"%indicator_value.indicator.pk] = forms.CharField (
                                label =_(indicator_value.indicator.name),
                                widget =SelectDateWidget,
                                initial =str (indicator_value.value))      
              else:
                   fields["indicator_%s"%indicator_value.indicator.pk] = forms.MultipleChoiceField (
                        label  = _(indicator_value.indicator.name),
                        widget = forms.CheckboxSelectMultiple (), 
                        initial= as_ids (IndicatorValue.objects.filter (
				indicator=indicator_value.indicator , 
				submission = submission).all ()),
                        choices= as_tuple(IndicatorValue.objects.filter (
				indicator =indicator_value.indicator).all()))
       
          def clean (self):
             return self.cleaned_data  
          return type ("FormFiche", 
                       (forms.BaseForm ,) ,
                       {"base_fields" : fields , "clean" :clean})
      
      def __unicode__(self):
          return "%s , %s"%(self.pk, self.period)

def as_ids (queryset):
          return  ["%s" %obj.pk for obj in queryset ]
      
class Submission (models.Model):
    '''
    A submission is or fiche form save 
    Une submission  est un sauvegarde d'un  formulaire
    Une submission contient en general plusieurs submission d'indiateurs
    '''
    # The user who is editing this submission
    # Le secretaire aui saisie la fiche
    user = models.ForeignKey(User , null =True ,blank =True)
    # The month of edition 
    date = models.DateField (auto_now_add =True)
    fiche= models.ForeignKey("Fiche" , related_name = "submissions")
    village =  models.ForeignKey("Area" , null =True , blank =True)
    supervisor = models.CharField(max_length= 200 , blank =True , null =True)
    
    
    
class Area(models.Model):
    '''
    An are can be 
    [1] - Village
    [2] - Rural community
    [3] - Deprtement 
    [4] - Region
    [5] - Pays
    '''   
    name =models.CharField (max_length = 160)
    parent   =   models.ForeignKey("self", related_name ="children" ,blank =True , null =True )
    surface    =models.PositiveIntegerField (null =True , blank =True ,default=0)
    latitude   =models.CharField (max_length = 20 , blank =True , null =True)
    longitude  =models.CharField (max_length = 20 , blank =True , null =True)
    latitude_gmap = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True,
                                        help_text="The physical longitude of this location")
    longitude_gmap =models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, 
                                        help_text="The physical longitude of this location")
    description = models.TextField ()
    created     = models.DateTimeField (auto_now_add =True)
    modified    = models.DateTimeField (auto_now= True)
    
    def _downcast (self, klass):
        klass_name = klass.__name__
        klass_mro = [c.__name__.lower () 
		     for c in klass.__mro__]
        klass_to_cast = [c.lower () 
			 for c in klass_mro[ : klass_mro.index (
			 self.__class__.__name__.lower())]]
        klass_to_cast.reverse ()
        casted = self
        for  c in klass_to_cast:
            if hasattr (casted, c):
                casted = getattr (casted,c) 
            else :
                return casted 
        return casted
    
    def flatten (self , klass = None):
        seen = set ()
        leave = set ()
        def recurse(area):
            if (hasattr (area , "children") 
		and  len(area.children.all())):
                print  area , area.children
                seen.add(area)
                for area in area.children.all() :
                        recurse(area)
            else :
                leave.add (area)
        recurse (self)
        if klass and len (leave):
            casted =  [ area._downcast(klass)  
			for area in leave ]
        else :
            casted= leave
        return casted
        
    def get_ancestors(self):
        seen = set ()
        while self.parent :
            seen.add(self.parent)
            self = self.parent 
        return seen 
    
    def get_ancestor (self, klass_list):
        klass_list.reverse ()
        seen = self ()
        while self.parent and klass_list :
            real_klass = klass_list.pop ()
            seen.append (self.parent._downcast(real_klass))
        return seen

    def get_children(self, klass=None):
        childs = self.children.all()
        if klass is not None:
            return [c._downcast(klass) for c in childs]
        else:
            return childs   
                  
    def __unicode__(self):
        return "%s"%(self.name)
     
def as_tuple (qs):
    '''
    Given a list of objets return a tuple
    '''
    return [ (q.pk , q.__unicode__()) 
      	     for q in qs]

class Pays (Area):
    pass
class Region (Area):
    pass
class Departement (Area):
    pass
class  Arrondissement(Area):
    pass
class  CommuneArrondissement(Area):
    pass
class CommunauteRurale (Area):
    pass
class Commune(Area):
    pass
class SpecialZone (Area):
    pass
class Prefecture (Area):
    pass
class SubPrefecture (Area):
    pass
class Secteur (Area):
    pass
class Etat(Area):
    pass
class Region (Area):
    pass
class District (Area):
    pass
class CommuneArrondissement(Area):
    pass
class CommuneHurbaine (Area):
    pass
class IndicatorVillage (Area):
    '''
    This not be null , but Iam not sure
    '''
    village = models.ForeignKey(SuiviVillage , 
	null =True , blank =True)
