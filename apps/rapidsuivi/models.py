from django.db import models
from apps.nodegraph.models import NodeSet
from locations.models import Location
from apps.contacts.models import Contact
from smsforum.models import Village
from django.utils.translation import ugettext_lazy as _
# Create your Django models here, if you need them.
import datetime 
from decimal import Decimal as D
import traceback
import re
from apps.rapidsuivi.exceptions import *
class Relay(models.Model):
    # Le code du regional coordication
    COORDINATION_TYPES =(("1", "Kalolack"),
                        ("2", "Thies"),
                        ("3", "Mbour"),
                        ("4" , "TambaCounda"),
                        ("5" , "Kolda"),
                        ("6", "Ziguinchor"),
                        ("7", "Matam"))
    
    # Le projet du relay
    PROJECT_TYPES=( ("1", "UNICEF"), 
                    ("2", "Nike Foundation"),
                    ("3" , "Rapidan"),
                    ("4" , "Blaustein"),
                    ("5" , "AJWS & Weelspring"),
                    ("6" , "Banyan Tree Foundation"),
                    ("7" , "CEPAIM"),
                    ("8" , "Helen Vaverde Charitable Lead Trust"),
                    ("9" , "Johnson & Johnson Corporate Contributions"), 
                    ("10" ,"Just World International"),
                    ("11" , "Norad"),("12" , "Pathfinder"), 
                    ("13" , "Radio Sweden"), 
                    ("14" , "Skoll"),("15" , "UNFPA"), 
                    ("16" , "Wallace Global Fund"))
                
    # Type du Relay               )
    TITLE_TYPES =(("1", "Facilitator"),
                   ("2", "CMC"),
                   ("3", "Radio Host"))
                
    STATUS = (("U" , "Update"),
              ("D" , "Delate"),
              ("C" , "Create"))
    contact               = models.ForeignKey (Contact ,related_name = "relay")
    village_suivi         = models.ForeignKey("SuiviVillage" , related_name ="relay")
    title_id              = models.CharField(max_length=2 ,choices =  TITLE_TYPES)
    cordination_id       = models.CharField(max_length=2  ,choices =  COORDINATION_TYPES)
    project_id            = models.CharField(max_length=2 ,choices =  PROJECT_TYPES)
    date_reg              = models.DateTimeField(default =datetime.datetime.now)
    first_name            = models.CharField (max_length = 200, null =True , blank =True)
    last_name             = models.CharField (max_length =200 , null =True , blank =True)
    status                = models.CharField(max_length =1 ,default ="C" )
    
    def send_to (self, text):
        """
        EN: Send a response to the relay
        ==
        FR :Envoie un message au relay
        """
        self.contact.send_to (text)


    @classmethod
    def from_contact (klass , contact):
        """
        EN : This method allow us to get the relay using contact 
        ==
        FR : Cette methode nous permet de recuperer le relay a partir du contact
        """
        try:
             return klass.objects.get ( contact = contact)
        except  Exception  , e :
            traceback.print_exc()
            return None 

    def __unicode__(self): 
        return """"Relay +++++phone +++%s+++cordination+++%s
                +++projet+++%s+++fisrt_name+++%s+++last_name+++%s+++village+++%s"""%(
                self.contact.phone_number ,
                self.get_cordination_id_display (), 
                self.get_project_id_display (), 
                self.first_name , 
                self.last_name ,
                self.village_suivi
                )  
                
                      
class Cmc(NodeSet):
        """
        Rapport d'activites sur les CMC , les meetings organises
        les operations de transferts banquaires,  les mobilizations 
        les radios  communautaires.
        """
        CMC_TYPES = (("1" ,_("Meetings")), 
                    ("2" ,_("Account Operation")),
                    ("3" , _("Social Mobilisation")),
                    ("4" , _("Radio")))
        
        #Village Location type
        LOCATION_TYPES=(( "1" , _("My Village")),
                        ( "2" , _("Village adopte")),
                        ( "3" , _("Other Village")))
        
        #Show location type
        SHOW_LOCATION_TYPES=(("1" , _("Live")),
                             ("2" , _("Tape Delayed")))
        
        SHOW_TYPES =(("1" ,_("With guests")),
                     ("2", _("Debate")), 
                     ("3", _("Reportage")))
        
        SUBJECT_TYPES =(("1" ,_("Health")), 
                        ("2" ,_("Environnement")),
                        ("3" ,_("Education")),
                        ("4" ,_("Income Generating Activity")),
                        ("5" ,_("Youth protection")),
                        ("6" ,_("Social Activity")),
                        ("7" ,_("Conflit Resolution")),
                        ("8" ,_("Microcredit")),
                        ("9" ,_("External RElation")),
                        ("10" ,_("Others")))
        ACTIVITY_TYPES =( ("1"  , _("Assainissement-Set Settal")),
                        ("2"  , _("Sensibilisation etat Civil")),
                        ("3"  , _("Sensibilisation inscriptiondes enfants a l'ecole")),
                        ("4"  , _("Sensibilisation Paludisme")),
                        ("5"  , _("Sensibilisation Paludisme")),
                        ("6"  , _("Sensibilisation sur la sante de la femme et de la fille")),
                        ("7" , _("Vente produit divers")),
                        ("8"  , _("Apui Structure de Sante")),
                        ("9"  , _("Reception de delegation")),
                        ("10" , _("Other")))
            
        THEME_TYPES = ( ("1" , _("Health"))  , 
                        ("2" , _("Environnement")),
                        ("3" , _("Education")) , 
                        ("4" , _("Income Generating Activity")) ,
                        ("5" , _("Youth protection")),
                        ("6" , _("Social Activity")),
                        ("7" , _("Conflict Resolution")),
                        ("8" , _("Microcredit")),
                        ("9" , _("External Relation")),
                        ("10" ,_("Other")))
        # Metting 
        type_id      = models.CharField(max_length =2,choices = CMC_TYPES , null =True , blank =True)
        num_members  = models.PositiveIntegerField(default =0)
        num_guests   = models.PositiveIntegerField(default =0)
        subject_id   = models.CharField(max_length=2,null =True , blank=True,choices = SUBJECT_TYPES)
        activity_id  = models.CharField(max_length=2,null =True ,blank=True ,choices = ACTIVITY_TYPES)
        #Account Operation
        balance_com   = models.PositiveIntegerField(default =0)
        balance_bank  = models.PositiveIntegerField(default =0)
        #Social Mobilzation
        num_attendees = models.PositiveIntegerField (default =0)
        num_villages  = models.PositiveIntegerField (default =0)
        theme_id      = models.CharField(max_length =2,null=True , blank =True ,choices =THEME_TYPES)
        location_id   = models.CharField(max_length =2,null=True ,blank =True,choices = LOCATION_TYPES)
        #Radio
        show_location_id = models.CharField(max_length =2,null =True ,blank =True ,choices  = SHOW_LOCATION_TYPES)
        show_type_id    = models.CharField(max_length  =2,null =True ,blank =True ,choices = SHOW_TYPES)
        
        #Relay
        relay     = models.ForeignKey ("Relay" , related_name ="cmcs")
        date = models.DateTimeField (default =datetime.datetime.now())
        is_read = models.BooleanField (default =False)
        
        def __unicode__(self):
                return  u"CMC +++relay +++%s"%(
                        self.relay
                        ) 
            
         
class Class(NodeSet):
        """
        Les rapports d'activites sur les classes , nous essayons ici 
        d'avoir des rapports sur les activites de la classes.
        """
        COHORT_TYPES  =(("1", _("adult")),
                        ("2" ,_("adolescent")))
        
        TITLE_TYPES = (("1", _("Kobi 1")),
                       ("2" ,_("Kobi2")),
                       ("3" ,_("Awade1")), 
                       ("4" ,_( "Awade2")))
        
        cohort_id    = models.CharField(max_length =2 ,null=True , blank =True ,choices  =COHORT_TYPES)
        title_id     = models.CharField (max_length =2 ,null =True ,blank=True ,choices  =TITLE_TYPES)
        num_session  = models.PositiveIntegerField(default =0)
        num_women    = models.PositiveIntegerField(default =0)
        num_men      = models.PositiveIntegerField(default =0)
        num_girls    = models.PositiveIntegerField(default =0)
        num_boys     = models.PositiveIntegerField(default =0)
        relay        = models.ForeignKey ("Relay" , related_name="classes")
        date         = models.DateTimeField(default = datetime.datetime.now ())
        is_read      = models.BooleanField (default =False)
        
        def __unicode__(self):
                return u"Class +++ cohort_id +++%s , cohort_id_display ++++%s"%(
                                self.cohort_id  , 
                                self.get_cohort_id_display ()) 
class  ClassAbs(NodeSet):
        """ 
        This classe exite only to allow reporting classe absences .Before each begining classe
        the relay sent us a message to report the liste of men , women , grils , boys which dropped
        this classe
        """
        classe            =models.ForeignKey ("Class" , related_name = "absents")
        relay             =models.ForeignKey ("Relay", related_name   = "classabsents")
        num_women_dropped =models.IntegerField (default =0)
        num_men_dropped   =models.IntegerField (default =0)
        num_girls_dropped =models.IntegerField (default =0)
        num_boys_dropped  =models.IntegerField (default =0)
        date              =models.DateTimeField(default =datetime.datetime.now ())
             
        def __unicode__(self):
            return u"AbsClass +++ women +++%s  , men +++ %s"%\
                (
                 self.num_women_dropped ,
                 self.num_men_dropped
                 )

class SuiviVillage(models.Model):
    """
    Liste of rapidsuivi villages , We made a foreign key to the village to allow settings the location and 
    to link rapidsuivillage to tostan's village used in sms forum
    """
    village           =models.ForeignKey (Village , related_name ="village_suivi")
    coordination      =models.CharField (max_length =160 , null =True, blank=True)
    region            =models.CharField(max_length=160, null =True , blank =True)
    departement       =models.CharField (max_length =160 , null =True , blank =True)
    arrondissement    =models.CharField(max_length=160, null =True , blank =True)
    communaute_rurale =models.CharField (max_length=160, null =True , blank =True)
    commune           =models.CharField(max_length =160, null =True , blank =True)
    langue            =models.CharField(max_length =160, null =True, blank =True)
    
    # Je stock ici  les latitudes et mongitudes de tostan , les latitudes 
    # et les longitudes utilises par google map sont dans location.latitude
    # et dans location.longitude
    # Ceci nous par exemple lorque Cheikh Ba  s'enregistre de passer 
    # Les latitudes et longitudes de arc gis ou bien ceux de google map
    # qui sont dans  location
    # Nous mettons ici le type char au lieu de Decimal car pour le systeme 
    # de coordonnees de arc gis de tostan je ne maitrise pas le max_digit 
    # et le decimal places
    latitude     =models.CharField(max_length=20 , blank=True, null=True)
    longitude    =models.CharField(max_length=20,  blank=True, null=True)
    
    def current_message (self):
	"""Le plus rescent message non lu ou le plus rescent message lu """
	cmc_to_read=Cmc.objects.filter (relay__village__suivi ==self, is_read=False)
	if cmc_to_read.count ()==0:
		class_to_read =Class.objects.filter (relay__village_suivi=self, is_read=False)
		if class_to_read.count()>0:
			return class_to_read.order_by("-date") [0]
		else :
		     cmc_readed = Class.objects.filter (relay__village_suivi=self)
		     if cmc_reader.count ()==0:
			   class_readed =Class.objects.filter (relay__village_suivi=self)
			   if class_reader.count()>0:
				return class_readed.order_by("-date")[0]
			   else :return None 
		     else :
			        return cmc_readed.order_by("-date")[0]
	else : return  cmc_to_read .oder_by("-date")[0]
    
    def __unicode__(self):
        return u"SuiviVilllage +++village_pk+++%s +++village__name++%s"%(self.pk ,self.village.name)


def relay_from_message (**kwargs):
    """
    L'attribut force deninit si on doit creer le relay  meme si il existe deja
    dans ce cas on met l'ancien relay a status  = 'D', pour sigifier que  ce relay
    vient d'etre supprimer :)
    Si force ==False , si le relay existe deja alors on doir envoyer l'execption 
    que le relay exite deja
    """
    vil= vil_from_la_vil(kwargs.get('latitude') ,kwargs.get('longitude'))
    kwargs["village_suivi" ] =vil
    rel = exists(Relay ,contact =kwargs.get ("message").sender)
    # Si le relay existe , qu'est ce que nous devons faire 
    # mettre son etat  a delete ou bien  envoyer une erreur ,je ne sais a tostan de definir
    # par defaut on force en mettant l'ancien a statut delete    
    #if rel:
    #    if   not "force" in kwargs or not  kwargs["force"]: 
    #           # Le relay ne doit pas etre cree  deux fois
    #           raise RelayExistError 
    if rel :           
        rel.statut  = "D"
        rel.save ()
    # Nous enelevons ici les paramettre  qui ne font pas parti  des parametres pour le relay
    # comme le message , force
    try:
        kwargs.pop("message")
    except KeyError, err:
        pass
    try:
        
        kwargs.pop ("force")
    except KeyError,err:
        pass
    try:
        kwargs.pop("latitude")
    except KeyError ,e: 
        pass
    try:
        kwargs.pop("longitude")
    except KeyError , e:
        pass
    # Ok on doit creer le relay ou bien force sa creation
    rel = Relay.objects.create (**kwarg)
    return rel


def vil_from_la_lo(latitude , longitude):
    try:
        return SuiviVillage.objects.get (village__location__latitude =latitude ,village__location__longitude =longitude)
    except Exception , e:
        traceback.print_exc()
        raise VillageNotExistError
        pass
    
def exists (klass , **kwargs ):
    try:
       return  klass.objects.get (**kwargs)
    except Exception, e:
        #traceback.print_exc()
        return None
    
