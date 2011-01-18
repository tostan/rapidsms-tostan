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
import  models
import  forms
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
    context =dict()
    all= Relay.objects.all ()
    radios = Radio.objects.all()
    cmcs   = Cmc.objects.all()
    classes = Class.objects.all()
    datas = []
    if req.method =="POST":
            # Pass Handle  from th posted data
            # Will return dict  which we will use to check the  realay   and  git  its  messages
            rel_params  = handle_form (req.POST , context)
            if all.count ()>0:
                all =all.filter (**rel_params)
		if all.count ()>0:
                   radios  = radios.filter(relay__in =all)
                   cmcs    = cmcs.filter(relay__in =all)
                   classes = classes.filter(relay__in =all)
            # Call  the actor Form Handler
            # To handle  form data realed to the actor selected  from UI
            actor_id  =handle_form_actors (req.POST)
            if actor_id  ==1:    
                    datas.extend (objects_to_qtip (cmcs))
            elif actor_id==2:
                    datas.extend (objects_to_qtip (classes))
            elif actor_id ==3 :
                    datas.extend (objects_to_qtip (radios))
            else :
		for k in [cmcs ,classes , radios]:
			datas.extend(objects_to_qtip(k))
    else :
		for  k in [cmcs ,classes ,radios]:
                       datas.extend(objects_to_qtip (k))
            
    # Get the form and the qtip data for calendar
    # return HttpResponse (datas)
    context.update(_get_form_data())
    context.update ( {"data": datas})
    return render_to_response (req ,template, context)

def handle_form (posted_data , context):
        ''' Handle  the form  data  '''
        d = dict()
        cordination_id = posted_data.get("cordination" ,None)
        project_id     = posted_data.get("project" ,None)
        village_id     = posted_data.get("village" ,None)
        # Get all the attribute for the relay 
        if cordination_id  is not None :
		if cordination_id not in  ("" ,"all"):
        		d.update({"cordination_id":cordination_id})
        		context.update({"cordination_selected":cordination_id})
        if project_id  is not None :
		if project_id not in ("" ,"all"):
        		d.update({"project_id":project_id})
           	 	context.update({"project_selected":project_id})
        if village_id  is not None :
		if  village_id not in ("", "all"):
            		d.update({"village_suivi__village":Village.objects.get (pk = village_id) })
            		context.update({"village_selected":village_id })
        return d

def handle_form_actors(posted_data) :
		'''
		Only exist  to handle  form filter from WeBUI .The page exact is calendar page 
		The method handle the submission form data 
		>>> handle_form_actors (req.POST)
		'''
                actor_str  = posted_data.get ("actor" ,None)
                if actor_str is not None  :
			if actor_str not  in ["", "all"]:
                  		 return int(actor_str)
			else :
				return None
		else :
			return None
		
def _get_form_data ():
     """ 
     Create data to populated  the form for   filtering data  from 
     the  calendar UI  
     >> _get_form_date  ()
     >>	{'cordiations' :  (1,'kaolack'), ('2','Thies')}
     """
     return {
        "cordination_options": dict (r.COORDINATION_TYPES),
        "project_options": dict(r.PROJECT_TYPES),
        "village_options": SuiviVillage.objects.values ("village__pk" , "village__name"),
        "actor_options":  dict([("1" , "CMC" ) , ("2" , "CLASS") ,("3" ,"RADIO")])
     }

def  title_and_type (obj) :
        if isinstance (obj , Class):
            return  "CLASSE" , "class"
        elif isinstance(obj, Cmc):
            return  "CMC" ,"cmc"
        elif isinstance (obj , Radio):
            return  "RADIO" ,"radio"
        else :
                    "" , ""
             
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
        qtip_data = {}
        _title , type  = title_and_type  (obj)
        if hasattr (obj ,"relay"):
                relay = obj.relay
                qtip_data.update({"title":              _title})
                qtip_data.update({"start":              obj.date.strftime("%Y-%m-%d")})
                qtip_data.update({"is_read":            obj.is_read})
                qtip_data.update({"first_and_last_name":relay.first_name + relay.last_name})
                qtip_data.update({ "phone":             relay.contact.phone_number()})
                qtip_data.update({"role":               relay.get_title_id_display()})
                qtip_data.update({"message":            obj.__str__()})
                qtip_data.update({"date":               obj.date.strftime ("%d-%m-%Y %H:%M:%S")})
                
		# Parfois le Radio est enyoye par un CGC donc , il a un village 
		# d'autre fois par un radio et dans ce cas il n'as pas de village

		#Si le type est un radio ,meme si on indqique sur Qtip Ui qu'il in n'ya
		#certains personne essayent quand meme d'exporter les  messages
		#Alors nous allons fixer lorsque le village est de type radio

		#Very bad adea to put  'pas de village'  so I replace right now with None 
		
		qtip_data.update({"village_pk" :         relay.village_suivi.pk if relay.village_suivi else None})
                qtip_data.update({"village_name":        relay.village_suivi.village.name if relay.village_suivi else ''})
                qtip_data.update({"message_pk":          str(obj.pk)})
                qtip_data.update({"cordination":         relay.get_cordination_id_display()})
                qtip_data.update({"message_instance":    type})
                qtip_data.update({"from_page":           from_page})
                google_qtip_widget_data = GOOGLE_QTIP_WIDGET%qtip_data
                qtip_data.update({"current_message" :    google_qtip_widget_data})
                return qtip_data

def objects_to_qtip(objects):
    '''
    Parceque , jFullCalendar attends dans son attributs events le format suivants
    Le context est de la forms  context = {"cmcs" :[] ,"classes": [] ,"radios" :[] }
    '''
    list = []
    for object in objects:
          list.append (object_to_qtip(object ,"cal"))
    return list
 
def  object_to_gmap_qtip(village):
        '''
        Return the gmap data for each village
        {"icon" :(red'green) , "gmap_latitude": "12.75555" ,
	"gmap_longitude": "-15.7777555" , "name":"name of the village"}
        '''
        current_message = village.current_message()
        data_dict  = dict()
        icon_color  ="red"
        if current_message:
            if not current_message.is_read :
                icon_color ="green"
        data_dict.update({"message":        EMPTY_VILLAGE_MESSAGE})
        data_dict.update({"icon":          icon_color})
        data_dict.update({"gmap_latitude" : village.village.location.latitude})
        data_dict.update({"gmap_longitude": village.village.location.longitude})
        data_dict.update({"name":           village.village.name})
        return data_dict  
 
def object_to_gmap_qtip_with_qtip(village):
        """
        Fill   data into the dict  to populate the Qtip Widget
	whish are going to be used into Google Map  to display 
	villages' currents messages
        """
        data_dict ={}
        object_gmap_qtip= object_to_gmap_qtip(village)
        object_qtip =None
        if village.current_message():
                    #This function is used into the map  so set from page to map
                    object_qtip =object_to_qtip(village.current_message() ,'map')
                    object_gmap_qtip.update({"message":   object_qtip.get("current_message")})
        if object_qtip:
            data_dict.update (object_qtip)
        data_dict.update (object_gmap_qtip)
        return data_dict 

def handle_map_form  (posted_data , context):
            # Get the village et cordination selected  by the user
            d=dict()
            coordination_id =  posted_data.get ("cordination" , None)
            village_id =  posted_data.get ("village" ,None)
            # Get the cordination id
            if coordination_id :
		if  coordination_id  not in ("" , "all"):
                   d.update({"cordination_id":        coordination_id })
                   context.update({"cordination_selected":     coordination_id})
            # Get the village id 
            if village_id :
		if  village_id not in ("" , "all"):
                   d.update({"village_suivi__village": Village.objects.get (pk =village_id)})
                   context.update({"village_selected":          village_id})
            return d
        
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
                rel_params = handle_map_form (req.POST , context)
                if all.count ()>0:
                    all = all.filter(**rel_params)
                if all.count()>0:
                    villages =SuiviVillage.objects.filter(pk__in =[ v.pk for v in [r.village_suivi for r in all if r.village_suivi]])
        if (not villages or not len (villages)):
                villages = SuiviVillage.objects.all ()
        for suivi_village in villages :
                gmap_data =object_to_gmap_qtip_with_qtip(suivi_village)
                gmap_datas.append (gmap_data)
        context.update ( {"villages": gmap_datas})
        return render_to_response (req , template ,context)

def update_model  ( model , model_pk):
        '''Update the classe '''
        # get the classe id  and update it's status
        model.objects.filter(pk=model_pk).update (is_read=True)
           
def update_message_status (req ,from_page , type ,message_pk):
        '''
	Update message from calendar UI
        Note ***
        From _template_ param tell us where the req come from
        Either from calendar ui ,or from map ui .We need to know for redirection
        '''
        model_class = getattr (models ,  '%s'%type.capitalize())
        update_model (model_class , message_pk)
        return HttpResponseRedirect(reverse("map") if from_page =="map"  else reverse ("calendar"))

def _get_message_form(model_type , model_data  = {} ,model_pk =None ):
        model_class = getattr (models ,'%s'%model_type.capitalize())
        form_class  = getattr (forms ,'%sForm'%model_type.capitalize())
        return   form_class (data  =model_data  , instance  = model_class.objects.get (pk  = int(model_pk)))
    
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
        if req.method =="POST":
            form =_get_message_form (type ,model_data =req.POST ,model_pk= message_pk)
            if form.is_valid ():
                form.save()
                return HttpResponseRedirect(reverse("map") if from_page =="map" else reverse("calendar"))
        else :
               form = _get_message_form (type , model_data =None , model_pk =message_pk)
        return render_to_response (req , template ,{"form" :form})


def _get_all_cmc_radio_class_from_village (village):
	       '''
		Return the data list   for export depending of the given village
		>>>_get_all_cmc_radio_class_from_village (1)
		>>>[cmc1 , radio1 , cmc2 , class3]
	       '''
               all = [ o for o in Cmc.objects.filter  (relay__village_suivi  = village).all()]+\
                     [ o for o in Class.objects.filter(relay__village_suivi = village).all()]+\
                     [ o for o in Radio.objects.filter(relay__village_suivi = village).all()]
               return all
def export_message (req,village_pk =None):
            """
	    Given a village I am going to export all CMC , RADIO , AND CLASS
            activity sent from the given village
	    """

            # For Radio Type We have not village so  village_pk = None
            if 'None' in village_pk  :
                    return  HttpResponseRedirect (reverse ('calendar'))
            village =SuiviVillage.objects.get (pk = int (village_pk))
            
            all_cmc_radio_class = _get_all_cmc_radio_class_from_village (village)
            if not len(all_cmc_radio_class):
                response = HttpResponse (mimetype ="application/vnd.ms-excel")
                response ["Content-Disposition"]  ="attachment; filename =empty.xls"
                return response
            response = HttpResponse (mimetype ="text/csv")
            response ["Content-Disposition"]="attachment; filename =%s.xls"\
            %village.village.name.replace(" " ,"_")
            writer   = UnicodeWriter(response)
            fields   = {"message" : _("Message Recu par Tostan"), "relay": _("Le Relay") ,
                      "date" :_("Date de Reception"), "type_id":_("Type du message")}
            writer.writerow (fields.values ())
            for obj in all_cmc_radio_class :
                row =[]
                for field in fields.keys() :
                    if field    =="relay":
                        val =( obj.relay.first_name + obj.relay.last_name )
                    elif field  =="type_id":
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
