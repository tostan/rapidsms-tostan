#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import rapidsms
from  rapidsms.parsers.keyworder import *
from contacts.models import Contact
from smsforum.models import Village
from decimal import Decimal as D
from rapidsuivi.exceptions import *
from rapidsuivi.models import *
from rapidsuivi.utils import import_villages 
import os
import gettext
import traceback 
from rapidsms.message import Message
# Mon numero envoie moi un message si il y'a une erreur car  je ne serai pas 
# la ,une fois que le systeme sera installe
alioune ="775526745"
_G = { 
    'SUPPORTED_LANGS': {
        # 'deb':u'Debug',
        'pul':['Pulaar','Pular'],
        'wol':['Wolof'],
        'dyu':['Joola','Dyula','Dioula','Diola'],
        'snk':[u'Sooninke',u'Soninke',u'Soninké',u'Sooninké'],
        'mnk':['Mandinka','Mandingo'],
        'fr':[u'Français',u'Francais'],
        'en':['English'],
        },
    'TRANSLATORS':dict(),
    'DEFAULT_LANG':'fr',
    'ADMIN_CMD_PWD': None
    }

########
# i18n #
########
def _init_translators():
    path = os.path.join(os.path.dirname(__file__),"locale")
    for lang,name in _G['SUPPORTED_LANGS'].items():
        trans = gettext.translation(
                        'django',
                        path,
                        [lang,_G['DEFAULT_LANG']]
                        )
        _G['TRANSLATORS'].update( 
                        {lang:trans}
                         )

def _t(locale, text):
    """translate text with default language"""
    translator=_G['TRANSLATORS'][_G['DEFAULT_LANG']]
    if locale in _G['TRANSLATORS']:
        translator=_G['TRANSLATORS'][locale]
    return translator.ugettext(text)

def _st(relay,text):
    """translate a message for the given sender"""
    # TODO: handle fall back from say eng_US to eng
    # AND mappings from old-stylie two letter ('en') to 
    # new hotness 3-letter codes 'eng'
    #return _t(sender.locale, text)
    return _t (relay.contact.locale , text)

# Bah , il ne sert qu'a permettre d'appeller _(key)
# et de permettre a django-admin makemessages -l fr 
# d'identifier les cles 
_ = lambda s :s 
        
def identify(func):
    """
    EN :This function allow us to check if the sender of message is a relay , ie is saved as a relay
    ==
    FR: Cette fonction nous permet de savoir si le relay s'est authentifier dans notre system
    """
    def  wrapper (sself , message , *args , **kwargs):
            
            rel =exists(Relay,contact =message.sender)
            if not rel:
                    Message(message.connection, "Identification requise!").send ()
                    return True 
            message.relay  = rel 
            return func (sself ,message ,*args , **kwargs)
    return  wrapper
        

class App (rapidsms.app.App):
    _init_translators ()
    kw = Keyworder()
    
    def start (self):
        """ Some data need to be loaded when the application start , like the village name ,coords , latitude 
        , ... where rapidsuivi is deployed """
        self.__loadFixtures ()
    
    
    def __loadFixtures (self):
        """ This method allow us to import tostan 's village from xsl file into the data base"""
        #import_villages ("centresTostan.xls")
        
    
    def parse(self, message):
        """ Parse some incoming messages before handling message , so """
        self.handled = False     
    
    def handle(self, message):
        self.backend  =message.connection.backend 
        try:
            if hasattr(self, "kw"):
                try:
                    # attempt to match tokens in this message
                    # using the keyworder parser
                    func, captures = self.kw.match(self, message.text) 
                except Exception:
                    #traceback.print_exc()
                    # If the user message start with our key, to be sure that message is for us
                    for start in ("reu", "cla" , "abs" , "ms" , "rad"):
                        if message.text.strip().startswith (start):
                            Message(
                                    message.connection,
                                    "Il y'a une erreur sur le message ,contacter le superviseur").send()
                            return True
                    # This message is not for this app
                    return False
                try:
                    handle = func(self, message, *captures) 
                    # short-circuit handler calls because 
                    # we are responding to this message
                    return handle
                except Exception , e:
                    # This is a internal message , so send sms to alioune , 
                    # and send a sms to the user , so he will understant that he sent us a good message , but 
                    # our app is now  safe
                    traceback.print_exc()
                    #self.error (str (e))
                    Message(
                                message.connection,
                                "Errueur"
                                ).send ()
                    
            else :
                self.debug("App does not instantiate Keyworder as 'kw'") 
        except Exception, e:    
            # TODO maybe don't log here bc any message not meant
            # for this app will log this error
            # self.error(e) 
            pass


    def outgoing(self, message):
        pass 
    
    
    def send_response(self,**kwargs):
        """
        
        Envoie une message a un relay
        """
        
        def _get_param_values(**kwargs):
            
            """
            Etant donnee une clef on retourne le bon message 
            ie : "reunion"  ==>{first_name: relay.first_name}
            """
            
            key = kwargs["key"]
            if key =="register-relay":
                relay  = kwargs.get("relay" , None)
                return{"first_name":  relay.first_name,
                       "last_name":relay.last_name,
                       "title": relay.get_title_id_display() ,
                       "village":relay.village_suivi.village.name}
                
            elif key =="already-registered":
                relay  = kwargs.get("relay" , None)
                return{"first_name":  relay.first_name,
                       "last_name":relay.last_name,
                       "title": relay.get_title_id_display() ,
                       "village":relay.village_suivi.village.name}
                       
            elif  key =="save-classe": 
                 cla = kwargs.get("classe",None)
                 return {
                         "first_name": cla.relay.first_name ,
                         "last_name": cla.relay.last_name,
                        "session":   cla.num_session ,
                        "title":     cla.get_title_id_display(),
                        "cohort": cla.get_cohort_id_display() ,
                        "village": cla.relay.village_suivi.village.name ,
                        "women": cla.num_women ,
                        "men":cla.num_men ,
                        "girls":cla.num_girls ,
                        "boys" : cla.num_boys
                }
                     
            elif key =="update-classe":
              abs_cla  =kwargs.get("classe",None)
              return    {
                         "first_name":abs_cla.relay.first_name,
                         "last_name":abs_cla.relay.last_name ,
                         "women" : abs_cla.num_women_dropped ,
                         "men": abs_cla.num_men_dropped ,
                         "girls": abs_cla.num_girls_dropped ,
                         "boys": abs_cla.num_boys_dropped ,
                         "title": abs_cla.classe.get_title_id_display()
                    }     
            elif key =="save-reunion":
              cmc  = kwargs.get("cmc",None)
              return {
                      "first_name":cmc.relay.first_name ,
                      "last_name":cmc.relay.last_name ,
                      "members":cmc.num_members ,
                      "guests":cmc.num_guests ,
                      "activity":cmc.get_activity_id_display(),
                      "village":cmc.relay.village_suivi.village.name,
                     "subject":cmc.get_subject_id_display()
             }
        
            elif key =="save-finance":
                cmc  = kwargs.get ("cmc" ,None)
                return {
                        "first_name":cmc.relay.first_name ,
                        "last_name":cmc.relay.last_name ,
                        "village":cmc.relay.village_suivi.village.name,
                        "balance_com": cmc.balance_com ,
                        "balance_bank":cmc.balance_bank
                }
            elif key =="save-mobilization":
                cmc  = kwargs.get("cmc" ,None)
                return {
                        "first_name":   cmc.relay.first_name ,
                        "last_name":    cmc.relay.last_name,
                        "attendees":    cmc.num_attendees ,
                        "village" :     cmc.relay.village_suivi.village.name,
                        "location":     cmc.get_location_id_display() ,
                        "theme":        cmc.get_theme_id_display() ,
                        "villages":     cmc.num_villages , 
                        "attendees":    cmc.num_attendees
                }
                
            elif key=="save-radio":
                cmc  = kwargs.pop ("cmc")
                return {"first_name": cmc.relay.first_name ,
                         "last_name":  cmc.relay.last_name,
                         "showtype" :  cmc.get_show_type_id_display(),
                         "theme":      cmc.get_theme_id_display() ,
                        "showlocation": cmc.get_show_location_id_display()
                }
        
        
        # Check the relay  
        if "key" in kwargs: 
            key  = kwargs ["key"]
            params =_get_param_values(**kwargs)
        

        def _get_relay (**kwargs):
                """
                Recherche le relay dans la liste des argumenst , soit  dans kwargs  , ou dans kwargs.pop("cmc")
                """
                # Check the relay
                if "relay" in kwargs :
                    return  kwargs.pop("relay")
                    
                elif "cmc" in kwargs   :
                    cmc =kwargs.pop("cmc") 
                    if cmc.relay : 
                            return cmc.relay
                elif "classe" in kwargs:
                    classe =kwargs.pop ("classe")
                    if classe.relay:
                            return classe.relay
                        
                
        relay  =_get_relay (**kwargs)           
        # Esce  que nous sommes sure que le relay  n 'est pas  null 
        assert (relay is not None)    
        if relay:
            try:
                
                key =_st (relay, key)
            except: 
                pass
            
            msg = key % params
            print "SEND_RESPONSES"
            print msg
            #Envoi un message au relay
            relay.send_to(msg)
        
        
    
    @kw("321 (\d+) (\d+) (\d+\.?\d+?) (\d+\.?\d+?) (\d+)\s+(\S+) (\S+)")
    def update (self , message , *args , **kwargs):
            try:
                relay= self.__register_relay(
                                    message ,
                                    *args , 
                                    force =True)
            
                self.send_response(
                                relay ,
                                "register-relay")
                return True 
            
            except VillageNotExistError , err:
                traceback.print_exc()
                Message(
                    message.connection, 
                    "Desole mais il ya pas de village sur cette latitude").send ()
                return True
                
                
            except Exception, e :               
                traceback.print_exc()
                message.forward(
                            alioune, 
                            str(e))
            
          
    @kw("123 (\d+) (\d+) (\d+\.?\d+?) (\d+\.?\d+?) (\d+) (\S+) (\S+)$")
    def register (self ,message, *args, **kwargs):
            """
            Identification d'un relay.La latitude et la longitude doit correspondre a un village 
            Si l'utilisateur s'est deja identifie , il peut changer ses parametre si il le veut.
            args [0] :coordination_id  ,args [1] :project_id ,args [2] :latitude ,args [3] :longitude ,args [4] :title_id ,
            args [5]: first_nameargs [6] :last_name
            """
            try:
                rel =self.__register_relay(
                            message ,
                            *args , 
                            force =False)
            
                return  self.send_response(          
                        relay =rel,
                        key="register-relay"                  
                        )
            except RelayExistError , e:
                traceback.print_exc()
                Message(
                        message.connection,
                        "Vous etes deja enregistre").send()
                
                
                
            except VillageNotExistError , e:
                traceback.print_exc()
                Message(
                         message.connection ,
                        "Desole mais il ya pas de village sur cette latitude"
                        ).send()
                return True
                   
            except Exception, e :
                traceback.print_exc()
                message.forward(
                     alioune ,
                    "Erreur dans rapidsms :%s"%str (e))
                    
                
                
    def __register_relay (self,message , *args , **kwargs):
            """
            Permettre le relay de s'enregister , ou de modifier ses coordonnees.
            Le village doit etre dans notre base de donnees
            args [0] :coordination_id ,args [1] :project_id ,args [2] :latitude ,args [3] :longitude ,
            args [4] :title_id ,args [5]: first_name args [6] :last_name
            """
            #print "Message" , message
            #print "Args" , args
            params =[
                    "cordination_id" ,
                    "project_id",
                    "latitude" , 
                    "longitude",
                    "title_id", 
                    "first_name" ,
                    "last_name" 
            ]
            kw = dict (zip (params ,args)) 
            if "force"  in kwargs :
                    kw["force"] =kwargs.pop ("force")
            
            kw["message"] =message    
            kw["contact"] = message.sender
            #print "__register__relay +++",kw
            return  relay_from_message (**kw)
            
            
            
    @kw("cla (\d+?) (\d+?) (\d+?) (\d+?) (\d+?) (\d+?) (\d+)$")
    @identify 
    def add_new_class (self ,message, *args,**kwargs):
        """Sauvegarde une nouvelle classe [Kobi 1 ,Awade 1, ...] 
        args [0] :cohort_id, args [1] :title_id ,args [2] :num_session ,args [3] :num_women
        args [4] :num_men ,args [5]: num_girls  ,args [6] :num_boys"""
    
        keys = ["cohort_id" , 
                "title_id" , 
                "num_session" ,
                "num_women" ,
                "num_men" , 
                "num_girls" , 
                "num_boys"]
        kw_args  = dict (zip (keys , args))
        cla  =Class.objects.create (
                        relay =message.relay, 
                        **kw_args
                        )
        self.send_response (
                        classe =cla , 
                        key ="save-classe"
                )
        
        return True
                        
                        
    @kw("abs (\d+?) (\d+?) (\d+?) (\d+?) (\d+?)$")
    @identify
    def add_abs_class(self,message , *args , **kwargs):
        """Envoi un repport detaille sur les absences de la classe precedente  
        [args [0]  :parent_class_id,args [1]  :num_women_dropped ,args [2]: num_men_drpped 
        args [3] : num_girls_drpped  ,args [4] :num_boys_dropped ]"""
        # Si le rapport sur le awade ou le  Kobi precedent ne passe 
        # pas alors on envoie un message
        
        prec_class =exists(
                    Class , 
                    **{"title_id" :int (args[0])-1})
        if not prec_class:
            Message(
                    message.connection ,
                    "Je ne peux pas trouver la classe concernee par ces absence"
            ).send ()
            return True
        
        attrs   =[
                  "num_women_dropped" ,
                  "num_men_dropped" ,
                   "num_girls_dropped" ,   
                   "num_boys_dropped"]
        kw_args =dict (zip (attrs , args[1:]))
        abs_cla = ClassAbs.objects.create(
                     relay  = message.relay,
                     classe =prec_class ,
                     **kw_args)
      
        self.send_response(
                classe = abs_cla ,           
                key ="update-classe"
                )
        return True 
    
    
                    
    @kw ("reu\s+(\d+?)\s+(\d+?)\s+(\d+?)\s+(\d+?)$")
    @identify
    def add_reunion (self , message ,*args , **kwargs):  
        """
        Ajouter une nouvelle reunion  au systeme 
        args [0]  :num_members ,args [1]  :num_guests ,args [2]  :subject_id  ,args [3] :activity_id
        """
        attrs    = ["num_members" ,
                    "num_guests" , 
                    "subject_id" ,
                    "activity_id"]
        kw_args  = dict (zip (attrs  , args ))
        cmc  = Cmc.objects.create(
                            type_id  =1 ,
                            relay = message.relay , 
                            **kw_args
                            )
        self.send_response (
                        cmc  = cmc,
                        key  ="save-reunion"           
                        )  
        return True 
    
    
    
    @kw("fin\s+(\d+?)\s+(\d+?)$")
    @identify
    def add_finance (self, message ,  *args ,**kwargs):
        """Ajouter un rapport financier au systeme
        args [0]:balance_com,args [1]:balance_bank"""
        
        attrs = ["balance_com" ,
                 "balance_bank"]
        kw_args   =dict (zip (attrs , args))
        cmc =Cmc.objects.create(
                type_id =2 ,
                relay  =message.relay, 
                **kw_args)
        
        return self.send_response (
                    cmc   = cmc,
                    key   = "save-finance"                
                    )
        return True
    
    
    @kw ("ms (\d+?) (\d+?) (\d+?) (\d+?)$")
    @identify  
    def add_mobilization (self,message , *args , **kwargs):
        """
        Ajouter un rapport su une mobilization
        args [0] : num_attendees ,args [1] :num_villages ,args [2] :theme_id  ,args [3] :location_id
        """
        
        attrs  = ["num_attendees" ,
                   "num_villages" ,
                   "theme_id" ,
                   "location_id" ,
                   ]
        kw_args  = dict (zip (attrs , args))
        cmc  = Cmc.objects.create(
                        type_id =3 , 
                        relay =message.relay,
                        **kw_args
                        )
        
        self.send_response (
                    key ="save-mobilization",
                    cmc = cmc
                    )
        return True 
        
    @kw ("rad (\d+?) (\d+?) (\d+?)$")
    @identify
    def add_radio (self ,message , *args , **kwargs):
        """Ajouter une nouvelle radio 
        args [0] : theme ,args [1] :show_location ,args [2] :show_type """
        attrs    = ["theme_id" , "show_location_id" , "show_type_id"]
        kw_args  = dict (zip (attrs , args))
        cmc      = Cmc.objects.create (
                            type_id = 4,
                            relay =message.relay, 
                            **kw_args
                    )
        self.send_response (
                cmc  = cmc,
                key = "save-radio"
                )
    
    
        return True
    @kw ("lang (.{2,3})")
    @identify 
    def change_lang (self , message , *args , **kwargs):
        """
        Cette fonction permet de hanger la langue du relay
        """
        lang = re.sub("[0-9]","" , args [0]).strip()
        if not lang:
                if message.relay.contact.lang.lower ()  != lang.lower ():
                        message.relay.contact.locale  = lang
                        message.relay.contact.save ()
                        message.relay.save ()
        return True      
    