#/usr/bin/env python
#-*- encoding =Utf-8 -*-
# Create your webui views here.
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from rapidsms.webui.utils import render_to_response
from django.contrib.auth.decorators import login_required
from apps.rapidsuivi.models import *
from apps.smsforum.models import *
from apps.rapidsuivi.models import Relay as r
from django.http import HttpResponse , HttpResponseRedirect
from .forms import *
import codecs
import csv
import cStringIO


GOOGLE_QTIP_WIDGET="""<ul>\
<li>Message envoye par :%(first_and_last_name)s</li>\
<li>Contact :%(phone)s</li>\
<li>Role :%(role)s</li>\
<li>Cordination Contact : %(cordination)s</li>\
<li>Village Contact : %(village_name)s</li>\
<li>Date :%(date)s</li>\
<li>--</li>\
<li>Message:%(message)s</li>\
<li>\
<li>--</li>\
<li>\
<a href='/rapidsuivi/update_message_status/%(from_page)s/%(message_instance)s/%(message_pk)s'>\
Marquer le message comme lu</a>\
</li>\
<li>\
<a href='/rapidsuivi/update_message/%(from_page)s/%(message_instance)s/%(message_pk)s'>\
Modifier Le Message\
</a>\
</li>\
<li>--</li>\
<a href ='/rapidsuivi/export_village_message/%(village_pk)s'>\
Exporter sous excel les messages de %(village_name)s\
</a>\
</li>\
</ul>\
"""

EMPTY_VILLAGE_MESSAGE ="""<ul>\
<li>Bonjour,il n'a pas encore de messages\
en provenance de ce village</li>\
</ul>\
"""


@login_required
def calendar(req, template="rapidsuivi/calendar.html"):
    '''
    Display data from calendar , display form to filter into the calendar
    Attention Si vous voulez trouver les CMC de Kaolack , il faut choichir
    la coordination de Kaolack et il doit exiter un relay qui a envoyer un CMC depuis Koalack
    Cela veut dire si un relay de Thies envoie un CMC et que dans les fitres vous choisissez*
    Kaolack ,ce CMC ne vas pas apparaitre puis qu'il vient de Thies .
    De Meme comme il y'a pas de  village pour les Radio , Si vous selectionner un village vous
    ne verrai pas les radios.
    '''
    # Conext  dict 
    c =dict()
    all= Relay.objects.all ()
    radios = Radio.objects.all()
    cmcs   = Cmc.objects.all()
    classes = Class.objects.all()
    qtip_datas = []
    if req.POST:
            def handle_form (post):
                    buffer = dict()
                    cordination =post.get("cordination" ,None)
                    project  =post.get("project" ,None)
                    village  = post.get("village" ,None)
                    if  (cordination  and cordination not in ["" ,"all"]):
                        buffer['cordination_id'] =cordination
                        c['cordination_selected']=cordination
                    if  (project   and  project not in ["" ,"all"]):
                        buffer['project_id'] =project
                        c["project_selected"]=project
                    if(village and  village not in ["", "all"]):
                        buffer["village_suivi__village" ]= Village.objects.get (pk = village)
                        buffer["village_selected"]= village
                    return buffer                
            bubber = handle_form (req.POST)
            if all.count ()>0:
                all =all.filter (**buffer)
		if all.count ()>0:
                   radios =radios.filter(relay__in =all)
                   cmcs   =cmcs.filter(relay__in =all)
                   classes=classes.filter(relay__in =all)
                    
            def handle_form_actors(post) :
		'''
		Only exist  to handle  form filter from WeBUI .The page exact is calendar page 
		The method handle the submission form data 
		>>> handle_form_actors (req.POST)
		'''
                actor  = post.get ("actor" ,None)
                if actor is not None  and actor not  in ["", "all"]:
                   return int(actor)
		return None
            actor  =handle_form_actors (req.POST)
            if actor ==1:    
                 qtip_datas.extend (objects_to_qtip (cmcs))
            elif actor==2:
                 qtip_datas.extend (objects_to_qtip (classes))
            elif actor==3 :
                 qtip_datas.extend (objects_to_qtip (radios))
            else :
		for k in [cmcs ,classes , radios]:
		 qtip_datas.extend(objects_to_qtip(k))
    else :
	for  k in [cmcs ,classes ,radios]:
             qtip_datas.extend(objects_to_qtip (k))
    # Get the form and the qtip data for calendar
    # return HttpResponse (datas)
    c.update(_get_form_data())
    c.update ( {"data": qtip_datas})
    return render_to_response (req ,template, c)

def _get_form_data ():
     """ 
     Create data to populated  the form for   filtering data  from 
     the  calendar UI  
     >> _get_form_date  ()
     >>	{'cordiations' :  (1,'kaolack'), ('2','Thies')}
     """
     return {
        "cordination_options": dict (r.COORDINATION_TYPES),\
        "project_options": dict(r.PROJECT_TYPES),\
        "village_options": SuiviVillage.objects.values ("village__pk" , "village__name"),\
        "actor_options":  dict([("1" , "CMC" ) , ("2" , "CLASS") ,("3" ,"RADIO")])
    }
 
def object_to_qtip(obj, from_page =None):
        '''
        Nous utilisons Qtip et google Qtip pour afficher les messages sur le
        calendier et sur la Map ,nous avons besions de formatter les
        object class  --> {"title" :"" , "start" :"" , "current_message"}
        pour rendre facile a utiliser dans la map et dans le calendrier.
        ---
        {"title":"CMC" , "url":"/" , "start":"2010-10-02"},
        {"title":"CLASS" , "url":"/" , "start":"2010-10-02"},
        {"title":"CLASS" , "url":"/" , "start":"2010-10-03" , {"village_name" : "" , 'from_page' :'' ....}} ,
        '''
        buffer= dict ()
        if isinstance (obj , Class):
            _title ="CLASSE"
            type = "classe"
        elif isinstance(obj, Cmc):
            _title ="CMC"
            type ="cmc"
        elif isinstance (obj , Radio):
            _title ="RADIO"
            type ="radio"
        else :
            _title =""
            type =""
        if hasattr (obj ,"relay"):
                relay = obj.relay
                buffer["title"]= _title
                buffer["start"]= obj.date.strftime("%Y-%m-%d")
                buffer["is_read"]= obj.is_read
                buffer["first_and_last_name"]= relay.first_name + relay.last_name
                buffer["phone"]= relay.contact.phone_number()
                buffer["role"] = relay.get_title_id_display()
                buffer["message"]= obj.__str__()
           	buffer["date"]= obj.date.strftime ("%d-%m-%Y %H:%M:%S")
		# Parfois le Radio est enyoye par un CGC donc , il a un village 
		# d'autre fois par un radio et dans ce cas il n'as pas de village
		buffer["village_pk" ]=( relay.village_suivi.pk 
				       if relay.village_suivi 
				       else "pas_de_village")
                buffer["village_name"]=(relay.village_suivi.village.name 
				       if relay.village_suivi 
				       else  "pas_de_village")
                buffer["message_pk"] =str(obj.pk)
                buffer["cordination"] =relay.get_cordination_id_display()
                buffer["message_instance"]= type
                buffer["from_page"]=from_page
                html_buffer= GOOGLE_QTIP_WIDGET%buffer
                buffer["current_message"] =html_buffer
                return buffer

def objects_to_qtip(objects):
    '''
    Parceque , jFullCalendar attends dans son attributs events le format suivants
    Le context est de la forms  context = {"cmcs" :[] ,"classes": [] ,"radios" :[] }
    '''
    return [ object_to_qtip (obj , 'cal') 
	     for obj in objects ]
def  object_to_gmap_qtip(village):
        '''
        Return the gmap data for each village
        {"icon" :(red'green) , "gmap_latitude": "12.75555" ,
	"gmap_longitude": "-15.7777555" , "name":"name of the village"}
        '''
        current_message = village.current_message()
        buffer= dict()
        _icon ="red"
        if current_message:
            if not current_message.is_read :
               _icon ="green"
        buffer["message"]= EMPTY_VILLAGE_MESSAGE
        buffer["icon"] =   _icon
        buffer["gmap_latitude"]= village.village.location.latitude
        buffer["gmap_longitude"]= village.village.location.longitude
        buffer["name"]= village.village.name
        return buffer
 
def object_to_gmap_qtip_with_qtip(village):
        """
        Fill   data into the dict  to populate the Qtip Widget
	whish are going to be used into Google Map  to display 
	villages' currents messages
        """
        buffer=dict ()
        object_gmap_qtip= object_to_gmap_qtip(village)
        object_qtip =None
        if village.current_message():
                  #This function is used into the map  so set from page to map
                   object_qtip =object_to_qtip(village.current_message() ,'map')
                   object_gmap_qtip.update({"message":
                                                object_qtip.get("current_message")})
        if object_qtip:
            buffer.update (object_qtip)
        buffer.update (object_gmap_qtip)
        return buffer

def map (req , template = "rapidsuivi/gmap.html"):
        """
	Handle google map data from the form displayed over the map via Qtip 
	"""
        context =dict()
        context.update(_get_form_data())
        villages =list()
        gmap_datas =list()
        if req.method =="POST" :
                all= Relay.objects.all()
                def  handle_form (post):
                        # Get the village et cordination selected  by the user
                        rel_params=dict()
                        coordination =  post.get ("cordination")
                        village =  post.get ("village")
                        if coordination and   coordination  not in ["" , "all"]:
                               rel_params.update({"cordination_id" :
                                                  coordination })
                               context.update({"cordination_selected" :
                                               coordination})
                        if village and village not in ["" , "all"]:
                               rel_params.update({"village_suivi__village" :
                                                  Village.objects.get (pk =village)})
                               context.update({"village_selected" :
                                            village})
                        return rel_params
                rel_params = handle_form (req.POST)
                if all.count ()>0:
                    all = all.filter(**rel_params)
                if all.count()>0:
                    villages =SuiviVillage.objects.filter(pk__in =\
                            [ v.pk for v in [r.village_suivi for r in all if r.village_suivi]])
        if (not villages or not len (villages)):
                villages = SuiviVillage.objects.all ()
        for suivi_village in villages :
                gmap_data =object_to_gmap_qtip_with_qtip(suivi_village)
                gmap_datas.append (gmap_data)
        context.update ( {"villages" : gmap_datas})
        return render_to_response (req , template ,
                                   context)

def update_message_status (req ,from_page , type ,message_pk):
        '''
	Update message from calendar UI
        Note ***
        From _template_ param tell us where the req come from
        Either from calendar ui ,or from map ui .We need to know for redirection
        '''
        def update(pk , type):
                # Update the message with pk and type 
                if type =='classe':
                    Class.objects.filter(pk=message_pk).update (is_read=True)
                elif type =='cmc':
                    Cmc.objects.filter(pk =message_pk).update(is_read=True)
                elif type =='radio':
                    Radio.objects.filter(pk =message_pk).update(is_read=True)
        update(message_pk , type)
        return HttpResponseRedirect(reverse("map") if from_page =="map" \
               else reverse ("calendar"))

def update_message (req , from_page ,type ,message_pk) :
        '''
        message_instance allow us to use the Best Model Form
        if message_instance =cmc ==> use CmcForm
        if message_instance =radio ==> use RadioForm
        '''
        form =None
        template ="rapidsuivi/update_message.html"
        errors = []
        context ={}
        def _get_message_form (type , data ={} ,pk=None  ):
                '''
		Return the message Form depending  to the given type
		>>>_get_message_form(cmc)
		>>>CmcForm()
		'''
                if  type =='cmc':
                    return CmcForm ( data = data  ,instance  = Cmc.objects.get(pk =int(pk)))
                if  type =='classe':
                    return ClassForm ( data = data ,instance = Class.objects.get(pk =int(pk)))
                if  type =='radio':
                    return RadioForm ( data = data , instance = Radio.objects.get(pk =int(pk)))                    
        if req.method =="POST":
            form =_get_message_form (type ,data =req.POST ,pk = message_pk)
            if form.is_valid ():
                form.save()
                return HttpResponseRedirect(reverse("map") if from_page =="map" \
                      else reverse("calendar"))
        else :
               form = _get_message_form (type  , data =None ,pk  =message_pk)
        return render_to_response (req , template ,{"form" :form})

def export_message (req,village_pk):
            """
	    Given a village I am going to export all CMC , RADIO , AND CLASS
            activity sent from the given village
	    """
            village =SuiviVillage.objects.get (pk = int (village_pk))
            def _get_all_cmc_radio_class_from_village (village):
	       '''
		Return the data list   for export depending of the given village
		>>>_get_all_cmc_radio_class_from_village (1)
		>>>[cmc1 , radio1 , cmc2 , class3]
	       '''
               all = [ o for o in Cmc.objects.filter\
                          (relay__village_suivi = village).all()]+\
                     [ o for o in Class.objects.filter\
                          (relay__village_suivi =village).all()]+\
                     [ o for o in Radio.objects.filter\
                          (relay__village_suivi =village).all()]
               return all
            all_cmc_radio_class = _get_all_cmc_radio_class_from_village (village)
            if not len(all_cmc_radio_class):
                response = HttpResponse (mimetype ="application/vnd.ms-excel")
                response ["Content-Disposition"]="attachment; filename =empty.xls"
                return response
            response = HttpResponse (mimetype ="text/csv")
            response ["Content-Disposition"]="attachment; filename =%s.xls"\
            %village.village.name.replace(" " ,"_")
            writer = UnicodeWriter(response)
            fields = {"message" : _("Message Recu par Tostan"), "relay": _("Le Relay") ,
                      "date" :_("Date de Reception"), "type_id":_("Type du message")}
            writer.writerow (fields.values ())
            for obj in all_cmc_radio_class :
                row =[]
                for field in fields.keys() :
                    if field =="relay":
                        val =( obj.relay.first_name + obj.relay.last_name )
                    elif field =="type_id":
                        if isinstance(obj,Cmc):
                            val = "CMC"
                        elif isinstance(obj, Class):
                            val ="CLASS"
                        else : val = "RADIO"
                    else :
                        val = getattr (obj ,field)
                    row.append(val)
                writer.writerow(row)
            return response

class UnicodeWriter(object):
        """ 
	A unicode Writer helper that allow us to write
        any given encoding , default is utf-8
        """
        def __init__ (self,stream , dialect ="excel-tab" , encoding= "Utf-8",**kw):   
          self.queue = cStringIO.StringIO()
          self.writer = csv.writer (self.queue ,dialect =dialect)
          self.encoder = codecs.getincrementalencoder (encoding)()
          self.stream =stream

        def writerow(self, row):
       	   self.writer.writerow([unicode (s).encode('utf-8') for s in row])
           # Get data from queue
           data = self.queue.getvalue ()
           # Decode to unicode
           data = data.decode ("Utf-8")
           # Reencode from given encoding
           self.encoder.encode (data)
           # write into stram
           self.stream.write (data)
           self.queue.truncate (0)
