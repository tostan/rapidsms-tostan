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
        trans = gettext.translation('django',path,[lang,_G['DEFAULT_LANG']] )
        _G['TRANSLATORS'].update( {lang:trans} )

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
            rel =exists(Relay,contact =message.sender , status ="C")
            if not rel:
                    message.respond(_t("fr","identification-requise"))
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
        try:
            if hasattr(self, "kw"):
                try:
                    # attempt to match tokens in this message
                    # using the keyworder parser
                    func, captures = self.kw.match(self, message.text) 
                except Exception:
                    traceback.print_exc()
		    # If the user message start with our key, to be sure that message is for us
                    # This message is not for this app
                    # Ce message n'est pas pour RAPID SUIVI
                    # Regarde si le message est bien pour rapidsuivi 
                    # si c'est la cas alors le relay essaie de contacter rapidsuivi avec la mauvaise syntaxe
                    try:
                        for key in ["cla"  ,"abs","reu" ,"ms" , "rad", "fin"]:
                            if message.text.strip ().startswith (key):
                                message.respond (_t("fr" , "help-message"))
                                return True
                    
                    except :
                        traceback.print_exc()
                        pass
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
                    self.error (str(traceback.print_exc()))
                    return True 
            else :
                self.debug("App does not instantiate Keyworder as 'kw'") 
        except Exception, e:    
            # TODO maybe don't log here bc any message not meant
            # for this app will log this error
            # self.error(e) 
            pass


    def outgoing(self, message):
        pass 
    
    def _get_register_relay_args (self,**kwargs):
        """ Get argument dict to fill to the register relay  success response """
        relay   = kwargs.get("relay" , None)    
        return {
                    "first_name":  relay.first_name,
                    "last_name":relay.last_name,
                    "title":  relay.get_title_id_display() ,
                    "village":relay.village_suivi.village.name
    }
    def _get_register_radio_relay_args (self,**kwargs):
        """ Get argument dict to fill to the register relay  success response """
        relay   = kwargs.get("relay" , None)
        return {
                    "first_name":  relay.first_name,
                    "last_name":relay.last_name,
                    "title":  relay.get_title_id_display() ,
        }

    def _get_already_register_args (self,**kwargs):
        """Get arguemnt dict to fill to the already registered succes response """
        relay  = kwargs.get("relay" , None)
        return{
                    "first_name":  relay.first_name,
                    "last_name":relay.last_name,
                    "title": relay.get_title_id_display() ,
                    "village": relay.village_suivi.village.name
        }
    def _get_save_class_args (self,**kwargs):
        """ Get the  arguments dict to  fill save class sucess response """
        cla = kwargs.get("classe",None)
        return { 
                    "first_name": cla.relay.first_name ,
                    "last_name": cla.relay.last_name, 
                    "session": cla.num_session ,
                    "title" :cla.get_title_id_display(),
                    "cohort" : cla.get_cohort_id_display(),
                    "village": cla.relay.village_suivi.village.name, 
                    "women": cla.num_women ,
                    "men":cla.num_men  ,
                    "girls":cla.num_girls ,
                    "boys" : cla.num_boys
        }
         
    def _get_update_class_args (self,**kwargs):
        """Get arguement to fill into the response arg for success update """
        abs_cla  =kwargs.get("classe",None)
        return    {
                    "first_name":abs_cla.relay.first_name, 
                    "last_name":abs_cla.relay.last_name ,
                    "women" : abs_cla.num_women_dropped ,
                    "men": abs_cla.num_men_dropped ,      
                    "girls": abs_cla.num_girls_dropped ,
                    "boys": abs_cla.num_boys_dropped ,
                    "title": abs_cla.get_title_id_display()
         }     
    
    def _get_save_reunion_args (self,**kwargs):
        """ Get argument to fill the reunion add success response"""
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
    def _get_save_finance_args (self ,**kwargs):
        """ Get the arguement dict to fill the save finance response """
        cmc  = kwargs.get ("cmc" ,None)
        return {
                    "first_name":cmc.relay.first_name ,
                    "last_name":cmc.relay.last_name ,
                    "village":cmc.relay.village_suivi.village.name,
                    "balance_com": cmc.balance_com ,
                    "balance_bank":cmc.balance_bank
         }
    def _get_save_mobilization_args (self,**kwargs):
        """ Get the dict arguement response to fill into the save moblilization success response """
        cmc  = kwargs.get("cmc" ,None)
        return {
                    "first_name":   cmc.relay.first_name ,
                    "last_name":    cmc.relay.last_name, 
                    "attendees":    cmc.num_attendees ,
                    "village" :   cmc.relay.village_suivi.village.name,
                    "location":     cmc.get_location_id_display() ,
                    # Ce qui serai mieu c'est de remplacer dans locale/django.po le theme par activity car
		    # pour la mobilization le theme en fait c'est l'activity
		    "theme":        cmc.get_activity_id_display() ,
                    "villages":     cmc.num_villages ,
                    "attendees":cmc.num_attendees
        }
    def _get_save_radio_args (self ,**kwargs):
        """Get args to fill the save radio succes response """
        radio  = kwargs.pop ("radio")
        return {
                    "first_name": radio.relay.first_name ,
                    "last_name":  radio.relay.last_name,
                    "showtype" :  radio.get_type_id_display(),
                    "theme":      radio.get_theme_id_display() ,
                    "showlocation": radio.get_location_id_display()
        }
    
          
    @kw("123 (\d+) (\d+) (\d+\.?\d+?) (\d+\.?\d+?) (\d+) (\S+) (\S+)$")
    def register (self ,message, *args, **kwargs):
            """
            Identification d'un relay.La latitude et la longitude doit correspondre a un village 
            Si l'utilisateur s'est deja identifie , il peut changer ses parametre si il le veut.
            args [0] :coordination_id  ,args [1] :project_id ,args [2] :latitude ,args [3] :longitude ,args [4] :title_id ,
            args [5]: first_nameargs [6] :last_name
            """
            try:
                rel =self.__register_relay(message ,*args)
                print  "** AFTER ** register"
                # Get the response to send to the relay 
                text = _st (rel , "register-relay")%\
                        self._get_register_relay_args (relay=rel)
                message.respond (text)
                return True
            except RelayExistError , e:
                traceback.print_exc()
                # This would never happen because we will always force saving relay
                pass
                
            except VillageNotExistError , e:
                #Check the project args  , village latitude and village longitude
		check_args =[args [1] ,args [2] ,args [3]]
		if  self.__check_radio (*check_args):
			rel =self.__register_relay (message , *args , radio=True)
			text =_st(rel ,"register-relay-radio")%\
			      self._get_register_radio_relay_args(relay=rel)
			message.respond(text)
			return True
		# Else this is not a radio , please raise village not exist 
                traceback.print_exc()
                message.respond(_t("fr","no-village-found"))
                return True
            except Exception, e :
                traceback.print_exc()
                # Raise so handler will  log message and email will be sent to djokko initiative
		raise 
    def __check_radio(self,*args):
	    """ If the village does not exist we should check if the user 
	    is trying to regsiter as a Radio Host .There are no village 
            for the radio host .So  if the project_id =0 an latitude =0
	    and logittude =0 , we should register the user"""
            if len ([ arg for arg in args if int(arg)!=0])>0:
		return  False
	    #It exist an arg wish is different 0 , this  is not a radio
	    return True
                
    def __register_relay (self,message , *args , **kwargs):
            """
            Permettre le relay de s'enregister , ou de modifier ses coordonnees.
            Le village doit etre dans notre base de donnees
            args [0] :coordination_id ,args [1] :project_id ,args [2] :latitude ,args [3] :longitude ,
            args [4] :title_id ,args [5]: first_name args [6] :last_name
            """
            params =["cordination_id" ,"project_id","latitude" ,"longitude","title_id", "first_name" ,"last_name"]
            dict_ = dict (zip (params ,args)) 
	    #It the radio is set , I  add True to bypass checking village existe
            if "radio"  in kwargs and kwargs ["radio"]:
                    dict_["radio"] =bool(kwargs["radio"])
            dict_["message"] = message    
            dict_["contact"] = message.sender
            return  relay_from_message (**dict_)
            
            
            
    @kw("cla (\d+?) (\d+?) (\d+?) (\d+?) (\d+?) (\d+?) (\d+)$")
    @identify 
    def add_new_class (self ,message, *args,**kwargs):
        """Sauvegarde une nouvelle classe [Kobi 1 ,Awade 1, ...] 
        args [0] :cohort_id, args [1] :title_id ,args [2] :num_session ,args [3] :num_women
        args [4] :num_men ,args [5]: num_girls  ,args [6] :num_boys"""
        keys = ["cohort_id" ,"title_id" , "num_session" ,"num_women" ,
		"num_men" , "num_girls" ,"num_boys"]
        kw_args  = dict (zip (keys , args))
        cla  =Class.objects.create (relay =message.relay, **kw_args)
        try:
            text =_st(message.relay,"save-classe")%\
                 self._get_save_class_args (classe =cla)
        except Exception, e:
            traceback.print_exc()
            #Raise  so email will be sent to the djokko developper  group
            raise 
        else:
            message.respond (text)
            cla.message = text
            cla.save ()
            return True
                        
                        
    @kw("abs (\d+?) (\d+?) (\d+?) (\d+?) (\d+?)$")
    @identify
    def add_abs_class(self,message , *args , **kwargs):
        """Envoi un repport detaille sur les absences de la classe precedente  
        [args [0]  :parent_class_id,args [1]  :num_women_dropped ,args [2]: num_men_drpped 
        args [3] : num_girls_drpped  ,args [4] :num_boys_dropped ]"""
        
        # Si le rapport sur le awade ou le  Kobi precedent ne passe 
        # pas alors on envoie un message
        
        #Il semble que tostan n'a pas besion de voir si la classe exite  bien avant de pouvoir enoyer les avsences
        # Pour l'instant on le commente
        
        #prec_class =exists(Class , **{"title_id" :int (args[0])-1})       
        #if not prec_class:
        #  Message(message.connection ,"Je ne peux pas trouver la classe concernee par ces absence").send ()
        #   return True
    
        attrs   =["num_women_dropped" ,"num_men_dropped", "num_girls_dropped" ,   "num_boys_dropped"]
        kw_args =dict (zip (attrs , args[1:]))
        # Because args[0]is the gegining classe
        # we should do args [0]	-1 to get the class refered by the reporting
        kw_args.update({"title_id": str(int(args[0])-1)})
        abs_cla = ClassAbs.objects.create(relay  = message.relay , **kw_args)
        # Get the response with argument to send  to the relay
        try:
            text =_st (message.relay,"update-classe")%\
                    self._get_update_class_args (classe =abs_cla)
       
        except Exception, e:
            traceback.print_exc()
            # Raise so email will be sent to the djokko group
            raise  
            
        else:
            message.respond (text)
            abs_cla.message=text
            abs_cla.save ()
            return True 
    
    
                    
    @kw ("reu (\d+?) (\d+?) (\d+?) (\d+?)$")
    @identify
    def add_reunion (self , message ,*args , **kwargs):  
        """
        Ajouter une nouvelle reunion  au systeme 
        args [0]  :num_members ,args [1]  :num_guests ,args [2]  :subject_id  ,args [3] :activity_id
        """
        attrs    = ["num_members" ,"num_guests" , "subject_id" ,"activity_id"]
        kw_args  = dict (zip (attrs  , args ))
        cmc  = Cmc.objects.create(type_id  ="1", relay = message.relay , **kw_args)
        try:
            text =_st (message.relay, "save-reunion")%\
                 self._get_save_reunion_args (cmc =cmc)
        except Exception, e:
            traceback.print_exc()
            # Raise so email will be sent to the djokko developper group 
            raise 
        else:
            message.respond (text)  
            cmc.message  = text
            cmc.save()
            return True 
    
    
    
    @kw("fin (\d+?) (\d+?)$")
    @identify
    def add_finance (self, message ,  *args ,**kwargs):
        """Ajouter un rapport financier au systeme
        args [0]:balance_com,args [1]:balance_bank"""     
        attrs = ["balance_com" ,"balance_bank"]
        kw_args   =dict (zip (attrs , args))
        cmc =Cmc.objects.create(type_id ="2" ,relay  =message.relay, **kw_args)
        try:
            text = _st(message.relay, "save-finance")%\
                  self._get_save_finance_args (cmc =cmc)
        except Exception, e:
            traceback.print_exc()
            #Raise so email will be sent to the djokko developper group
	    raise
        else:
            message.respond (text)
            cmc.message =text
            cmc.save ()
            return True
        
    
    @kw ("ms (\d+?) (\d+?) (\d+?) (\d+?)$")
    @identify  
    def add_mobilization (self,message , *args , **kwargs):
        """
        Ajouter un rapport su une mobilization
        args [0] : num_attendees ,args [1] :num_villages ,args [2] :activity_id  ,args [3] :location_id
        """
        attrs  = ["num_attendees" , "num_villages" ,"activity_id" ,"location_id"]
        kw_args  = dict (zip (attrs , args))
        cmc  = Cmc.objects.create(type_id ="3" , relay =message.relay ,**kw_args)
        # Get the response with arguement to send to the user 
        try:
            text =_st(message.relay,"save-mobilization")%\
                 self._get_save_mobilization_args(cmc=cmc)
        except Exception, e:
            traceback.print_exc()
      	    raise                     
        else :
             message.respond (text)
             cmc.message =text
             cmc.save ()
             return True 
        
    @kw ("rad (\d+?) (\d+?) (\d+?)$")
    @identify
    def add_radio (self ,message , *args , **kwargs):
        """Ajouter une nouvelle radio 
        args [0] : theme ,args [1] :show_location ,args [2] :show_type """
        attrs    = ["theme_id" , "location_id" , "type_id"]
        kw_args  = dict (zip (attrs , args))
        radio      = Radio.objects.create (relay =message.relay, **kw_args)
        try:
            text = _st (message.relay, "save-radio")%\
                    self._get_save_radio_args(radio= radio)
        except Exception, e:
            traceback.print_exc()
            raise
	else :
            message.respond (text)
            cmc.message =msg
            cmc.save ()
            return True


    @kw ("lang (.{2,3})")
    @identify 
    def change_lang (self , message , *args , **kwargs):
        """
        Cette fonction permet de hanger la langue du relay
        """
        lang = re.sub("[0-9]","" , args [0]).strip()
        if not lang:
                if message.relay.locale  != lang.lower ():
                        message.relay.locale= lang
                        message.relay.save ()

        return True      
    
