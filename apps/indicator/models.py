#!/usr/bin/env/python 
# vim :ai ts=4 sts=4 et sw =4 coding =utf-8
from django.db import models
# Create your Django models here, if you need them.
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from rapidsuivi.models import *
class Project(models.Model):
    '''
    Model to store all tostan ,s projects 
    Model pour garder tous les projects de tostan ,ainsi que leur description 
    '''
    name = models.CharField (_("Name of the project"), max_length = 160 , null =True , blank =True)
    description = models.CharField (_("The description of the project") , max_length =160, null =True , blank =True)
    #List of the indicators of projects
    indicators = models.ManyToManyField ("Indicator", null =True , blank= True)
    created    = models.DateTimeField (auto_now_add =True)
    
    def __unicode__(self):
        return u"%s"%(self.name)


INDICATOR_CHOICES =(
 ("1" , "text" ),
 ("2" , "numeric"),
 ("3" , "date"),                    
 ("4" , "list")                   
)
class Indicator (models.Model): 
    '''
    Model to store an indicator , it is defined by the name , 
    the type (text , date , list , numeric)
    Model pour garder les indicateurs , chaque indicateur est definit par son type , 
    (text, date , numeric , list)
    
    '''   
    name  =models.CharField (max_length = 20 , null =True , blank =True)
    type  =models.CharField (max_length =2 , null =True , blank =True, choices =INDICATOR_CHOICES)
    #If the indicator is a list store the value here
    # si l'indicateur est une liste de valueurs , nous gardons la liste
    # des valeurs saisies ici
    #values =models.ManyToManyField ("IndicatorValue", null =True , blank=True)
    
    
    
    def validate (self, type , value):
        ''' Given a value and a indicator , test if the value 
        is correct for this inticator'''
        
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
    indicator = models.ForeignKey("Indicator")
    value = models.CharField (max_length = 200 , null =True , blank =True) 
    
    def __unicode__(self):
        
        u"%s"%(self.value)


FICHES_CHOICES =(
("1" , "semestrielle"),
("2" , "mensuelle"),
("3", "trimestrielle"), 
("4" , "anuelle")
)
class ProjectFiche (models.Model):  
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
      project = models.ForeignKey ("Project")
      # L'indicator depend de du type de la fiche      
      indicators = models.ManyToManyField("Indicator", null =True , blank =True)
      created = models.DateTimeField (auto_now_add =True)
      #submissions = models.ManyToManyField("Submissions", null =True , blank =True)
      type = models.CharField (max_length  =1, choices = FICHES_CHOICES)
      
      
      def make_form (self):
          '''Make a dynamique form depending to the indicator list'''
          fields  = {}
          for indicator  in self.indicators.all ():
              if indicator.type =="1":
                  fields [indicator.name] = models.CharField (
                        label = str(indicator.label),
                        max_length = 160
                        
                        )
              elif indicator.type =="2":
                 fields[indicator.name] =models.DateTimeField (
                    label = str (indicator.label),
                    input_formats = str(indicator.date_format,
                    help_text = str ("Merci de taper la date sur cette format :%s "%str(indicator.date_format)))
              )
              elif idicator.type =="3":
                 fields[indicator.name]= models.CharField (
                  label = str (indicator.label),                 
                  choices =list ([str(v) for v in indicator.indicatorvalue_set.all ()])
              )
              else :      
                  raise ValidationError ("Invalidate indicator type :%s"%(indicator.type))
            
          return  type ("FicheForm" , (forms.Form ,) , 
                        {"base_fields" :fields , "clean" :clean } ) 
         
                
      def make_static_form (self):
        pass
          
      def __unicode__(self):
          return "%s , %s"%(self.type, self.project.name)
      
class Submission (models.Model):
    '''
    A submission is or fiche form save 
    Une submission  est un sauvegarde d'un  formulaire
    Une submission contient en general plusieurs submission d'indiateurs
    '''
    date = models.DateTimeField (auto_now_add =True)
    fiche  = models.ForeignKey("ProjectFiche")
    
class IndicatorSubmission (models.Model):
    submission =models.ForeignKey("Submission")
    indicator = models.ForeignKey("Indicator")
    #The value that the user has typed from the web UI
    #La valeurs saisie par l'utlisateur depuis le formulaire
    value = models.CharField (max_length = 300, null =True , blank =True)
    def __unicode__(self):
        return u"%s"%(self.value)
    
    

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
        klass_mro = [c.__name__.lower () for c in klass.__mro__]
        klass_to_cast = [c.lower () 
                         for c in 
                         klass_mro[ : klass_mro.index (self.__class__.__name__.lower())]]
        klass_to_cast.reverse ()
        
        print "*KLASS TO CAST*"
        print klass_to_cast
        
        casted = self
        for  c in klass_to_cast:
            if hasattr (casted, c):
                casted = getattr (casted,c) 
            else :
                return casted 
            
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
    
    
        
         
    def __unicode__(self):
        return "%s"%(self.name)
    
    
   # class Meta:
   #    abstract =True 
    
    
######################################################
# [1]-Guinee
# Region > Prefecture > Zone speciale > Commune Urbaine > Communaute Rurale 
# [2]-Guinee Bissao 
# Region
# [3]-Gambie 
#  Region > districts 
# [4]-Somalie
#  Region
# [7]-DJibouti
# Region
# [8]-Mauritanie
# Region
# [9]-Senegal
#  Region  > Departement > Arrondissement > CommuneArrondissement >
#  Commune > CommunauteRurale
######################################################   
class Pays (Area):
    pass


class Region (Area):
    pass

class Departement (Area):
    pass

class  Arrondissement(Area):
    pass

class CommunauteRurale (Area):
    pass
class Commune(Area):
    pass
class SpecialZone (Area):
    pass
class Region (Area):
    pass
class District (Area):
    pass
class CommuneArrondissement(Area):
    pass
class IndicatorVillage (Area):
    village = models.ForeignKey(SuiviVillage)
