# Create your webui views here.
from rapidsms.webui.utils import render_to_response
from django.contrib.auth.decorators import login_required
from apps.rapidsuivi.models import *
from apps.smsforum.models import *
from apps.rapidsuivi.models import Relay as r
from django.http import HttpResponse , HttpResponseRedirect
from .forms import *

"""
**Note**
The MESSAGE_FOR_UI will be displayed from calendar and  from map
Le MESSAGE_FOR_UI est utilise pour etre affiche dans la amp et dans le calendrier
"""

"""
**Important***
Don't forget to use {{ var|safe }} into your template 
because django does auto-scape for every views .
Also don't forget to do _\_ to avoid unterminated line from JQUERY
"""
MESSAGE_FOR_UI="""<ul>\
<li>Message envoye par :%(first_and_last_name)s</li>\
<li>Contact :%(phone)s</li>\
<li>Role :%(role)s</li>\
<li>Date :%(date)s</li>\
<li>--</li>\
<li>Message:%(message)s</li>\
<li>\
<li>--</li>\
<li><a href='%(update_status_url)s'>[MARQUER LE MESSAGE COMME LU]</a></li>\
<li><a href='%(update_message_url)s'>[MODIFIER LE MESSAGE]</a></li>\
<li>--</li>\
<a href ='/rapidsuivi/export_village_message/%(village_pk)s'>\
Exporter sous excel les messages de %(village_name)s\
</a>\
</li>\
</ul>\
"""

#If there are no message from village yet
EMPTY_VILLAGE_MESSAGE ="""<ul>\
<li>Bonjour,il n'a pas encore de messages\
en provenance de ce village</li>\
</ul>\
"""


@login_required
def calendar(req, template="rapidsuivi/calendar.html"):
    context ={}
    calendar_form (context)
    all_relays  = Relay.objects.all ()
    relay_filtres  = {}
    if req.method =="POST":
        if "cordination" in  req.POST :
                if req.POST.get ("cordination")  not in ("" , "all"):
                    relay_filtres["cordination_id"] = req.POST["cordination"]
                context["cordination_selected"] =req.POST["cordination"]
                
        if "project" in req.POST:
                if req.POST.get("project") not in ("" , "all"):
                    relay_filtres["project_id"] =req.POST["project"]
                context["project_selected"] = req.POST["project"]
        
        if "village" in req.POST:
                if req.POST.get ("village") not in ("" , "all"):
                    relay_filtres["village_suivi__village"] =\
			 Village.objects.get (pk =req.POST["village"])
                context["village_selected"]= req.POST["village"]
                   
        if len (relay_filtres)>0:
            all_relays =all_relays.filter (**relay_filtres)
        
        if "actor" in req.POST:
             if req.POST.get("actor") not in ("", "all"):
                   cmc_or_class_or_radio =req.POST["actor"]
                   if cmc_or_class_or_radio =="1" :
                       context["cmcs"]  =\
		       Cmc.objects.filter (relay__in =all_relays)
                   if cmc_or_class_or_radio =="2" :
                       context["classes"]=\
		       Class.objects.filter(relay__in=all_relays)
		   if cmc_or_class_or_radio =="3":
		       context["radios"]=\
		       Radio.objects.filter(relay__in =all_relays) 
			                   
             else:
                      context["cmcs"]    =\
				Cmc.objects.filter (relay__in=all_relays)
                      context["classes"] =\
				Class.objects.filter (relay__in =all_relays)
		      context["radios"]  =\
				Radio.objects.filter()
             context["actor_selected"] =req.POST["actor"]
                        
    else :
             context  ["cmcs"]   =Cmc.objects.all ()
             context  ["classes"]=Class.objects.all ()
	     context  ["radios"] =Radio.objects.all()
    # Now We have a liste of cmcs  , relays , and  radios we can go to 
    # go to  format data  for calendar UI by providing dict data to fill
    # for exemple into  MESSAGE_FOR_UI , 
    # ***ulr  for calendar ebent ***
    # ***date for caledar event 
    # ***is_read to  determine  class css  for  the calendar event 
    # So if message is already readed the callendar is **RED** else the calendar is *GREEN*
    calendar_events (context)
    return render_to_response (req ,template, context)
	
def calendar_form (context):
     context ["cordination_options"] =\
	dict (r.COORDINATION_TYPES)
     context ["project_options"]     =\
	dict(r.PROJECT_TYPES)
     context ["village_options"]     =\
	SuiviVillage.objects.values ("village__pk" , "village__name")
     context ["actor_options"]       =\
		dict ([
		      ("1" , "CMC" ) , 
		      ("2" , "CLASS") ,
		      ("3" ,"RAD")])
     
def calendar_events (context):
    """
    Parceque  , jFullCalendar attends dans son attributs events le format suivant 
    events =[     
            {"title":"CMC" , "url":"/" , "start":"2010-10-02"},
            {"title":"CLASS" , "url":"/" , "start":"2010-10-02"},
            {"title":"CLASS" , "url":"/" , "start":"2010-10-03"}                       
    ]
    Cette methode parcours les classes et cmcs pour retouner le bon format
    """
    calendar_event =[]
    # Get classes for the calendar UI
    if "classes" in context :
        classes  =context["classes"]
        for cls in classes :
            values ={"title" :"CLASS"}
            #values ["url"] =\
	    #	"/update_message_status/%s"%cls.pk
            #values ["update_message"] =\
	    #	"/update_message/%s/classe"%cls.pk
            values ["start"] = "%s"%cls.date
            values ['is_read']=cls.is_read
	    values ["current_message"] =\
		MESSAGE_FOR_UI%message_ui_from_class(cls)
            calendar_event.append (values)
    # Get cmc/CGC for the calendar UI
    if "cmcs" in context:
        cmcs =context["cmcs"]
        for cmc in cmcs :
            values ={"title" :"CMC"}
            #values ["url"] =\
	    #	"/update_message_status/%s"%cmc.pk
	    #values ["update_message"]=\
	    #	"/update_message/%s/cmc"%cmc.pk
            values ["start"] = "%s"%cmc.date
            values ["is_read"] =cmc.is_read 
            values ["current_message"]=\
		MESSAGE_FOR_UI%message_ui_from_cmc(cmc)
            calendar_event.append (values)


    # Get Radio Messages for the calendar UI
    if "radios" in context:
	radios = context["radios"]
	for radio in radios:
	    values = {"title": "RAD"}
            #values ["url"]=\
	    #	"/update_message_status/%s"%radio.pk
            #values["update_message"]=\
	    #	"/update_message/%s/radio"%radio.pk
	    values["start"] ="%s"%radio.date
	    values["is_read"]=radio.is_read
	    values["current_message"]=\
		MESSAGE_FOR_UI%message_ui_from_radio(radio)
	    calendar_event.append(values)

    if len (calendar_event):
        context ["data"]  = calendar_event 
    
            
def map (req , template = "rapidsuivi/gmap.html"):
        context  = {}
        villages =  SuiviVillage.objects.all ()
        gmap_data  =[]
        for suivi_village in villages :
             dict ={}
	     icon = "red"
	     # Le dernier message recu par le village ou bien 
	     # le dernier message qui n'est pas encore ete lu
	     cur_msg  =suivi_village.current_message_from ()
	     if cur_msg:
		if not cur_msg.is_read:
			icon = 'green'
		dict["message"] =MESSAGE_FOR_UI%message_ui_from_village(cur_msg)
		#dict["url"]     ="/update_message_status/%s"%cur_msg.pk
		# Get the url to  update message 
		# if message is instance of CMC  ==> url =/update_message/pk/cmc
		# if message is inatance if Classe  ==> url = /update_message/pk/classe
		#if isintance (cur_msg , Cmc):
		#	dict["update_message"] =\
		#	 "/update_message/%s/cmc"%cur_msg.pk
		#if isinstance(cur_message , Class):
		#	dict["update_message"]=\
		#	 "/update_message/%s/classe"%cur_msg.pk
		#if isinstance (cur_message ,Radio):
		#	dict["update_message"]=\
		#	 "/update_message/%s/radio"%cur_msg.pk
	     else :
		dict["message"]=EMPTY_VILLAGE_MESSAGE
	     dict.update ({"gmap_latitude": suivi_village.village.location.latitude})
             dict.update ({"gmap_longitude":suivi_village.village.location.longitude})
	     # Quel icon pour goolemap (rouge  ou vert 
	     dict["icon"]=icon
	     gmap_data.append (dict)

        #return HttpResponse (gmap_data)
        context ["villages"]  =gmap_data
        return render_to_response (req , template , context)


def message_ui_from_class(classe):
	"""Return un dict of data to fill into the MESSAGE_FOR_UI text"""
	dict = {}
	dict["first_and_last_name"] =\
		classe.relay.first_name + classe.relay.last_name
	dict["phone"]=\
		classe.relay.contact.phone_number()
	dict["role"]=\
		classe.relay.get_title_id_display()
	dict["message"] =classe.message 
        dict["date"] = classe.date.strftime ("%d-%m-%Y %H:%M:%S")
	dict["village_pk"] =classe.relay.village_suivi.pk
	dict["village_name"]=classe.relay.village_suivi.village.name
	dict["update_status_url"] = "update_message_status/%s"%classe.pk
	dict['update_message_url']= "update_message/%s/classe"%classe.pk
	return dict

def message_ui_from_cmc(cmc):
	"""Return a dict of data to fill into the MESSAGE_FOR_UI text"""
	dict ={}
	dict["first_and_last_name"]=\
		cmc.relay.first_name + cmc.relay.last_name
	dict["phone"]=\
		cmc.relay.contact.phone_number()
	dict["role"]=\
		cmc.relay.get_title_id_display()
	dict["message"] = cmc.message
        dict["date"] = cmc.date.strftime ("%d-%m-%Y %H:%M:%S")
	dict["village_pk"] =cmc.relay.village_suivi.pk
	dict["village_name"]=cmc.relay.village_suivi.village.name
	dict["update_status_url"] = "update_message_status/%s"%cmc.pk
	dict['update_message_url']= "update_message/%s/cmc"%cmc.pk
	
	return dict

def message_ui_from_radio(radio):
	""" Return a dict of data  to fill  into MESSAGE_UI text """
	dict ={}
	dict["first_and_last_name"]=\
		radio.relay.first_name + radio.relay.last_name
	dict["phone"]=\
		radio.relay.contact.phone_number()
        dict["role"]=\
		radio.relay.get_title_id_display()
  	dict["message"]=radio.message
        dict["date"] = radio.date.strftime ("%d-%m-%Y %H:%M:%S")
	dict["village_pk"] =radio.relay.village_suivi.pk
	dict["village_name"]=radio.relay.village_suivi.village.name	
	dict["update_status_url"] = "update_message_status/%s"%radio.pk
	dict['update_message_url']= "update_message/%s/radio"%radio.pk
	return dict 
        
def message_ui_from_village (current_village_message):
	"""Return a dict of data to fill into the MESSAGE_FOR_UI text
 	In Fact this is the current message  from  village 
	Either the latest message not  yet readed from village
	Either the latest message received by the village 
	Also the message can be CMC , CLASS , OR RADIO
	"""
	if isinstance (current_village_message , Cmc):
		return message_ui_from_cmc(current_village_message)
        if isinstance (current_village_message,Class):
		return message_ui_from_class(current_village_message)
	if isinstance(current_village_message ,Radio):
		return message_ui_from_radio(current_village_message)
        return None
 
    
def update_message_status (req , message_pk =None ):
	"""Update message from calendar UI 
	Note ***
	From _template_ param tell us where the req come from 
	Either from calendar ui ,or from map ui .We need to know for redirection
	"""
	# Are you a CMC ?
	errors =[]
	try:
		Class.objects.filter(pk=message_pk).update (is_read=True)
	except Exception,e:
		errors.append (str (e))
		# Are you a Class
		pass
	try:
		Cmc.objects.filter(pk =message_pk).update(is_read=True)
	except Exception ,e:
		errors.append(str(e))
		pass
	try:
	        Radio.objects.filter(pk =message_pk).update(is_read=True)
	except Exception ,e:
		# I dont understant It is impossible
		errors.append (str(e))
		pass
	# Goto To calendar index
	#return  HttpResponse ("*".join(errors))
	return render_to_response(req , "rapidsuivi/success.html" ,
	{"messages":["Votre requete a ete execute avec success"]})
		
     
def update_message (req , message_pk ,message_instance) :
	"""
        message_instance allow us to use the Best Model Form
	if message_instance =cmc ==> use CmcForm
 	if message_instance =radio ==>  use RadioForm
	"""      
        form  =None
	template  ="rapidsuivi/update_message.html"
	errors = []
	context ={}
        if req.method =="POST":
		#Si  le message est un CMC
		if message_instance =="cmc":
		    ins = Cmc.objects.get (pk =int(message_pk))
		    form  = CmcForm (
			data =req.POST  , instance = ins
			)
		    if form.is_valid():
			form.save()
		    else : errors = form.errors
		# If the given message is a  class
		if message_instance =="classe":
		     ins =Class.objects.get (pk =int (message_pk))
		     form = ClassForm(data = req.POST , instance = ins)
		     if form.is_valid():
			form.save()
		     else: errors = form.errors
		#If the given message is radio type message
		if message_instance =="radio":
		     ins = Radio.objects.get (pk =int (message_pk))
		     form = RadioForm (data = req.POST , instance = ins)
		     if  form.is_valid ():
		     	form.save()
		     else : errors = form.errors
		
		if not len(errors):
	        	return render_to_response(req ,
				"rapidsuivi/success.html" ,
				{"messages": ["Requete a ete execute avec succees"]})
		else :
			context ["errors"] =errors
        form =None		 
	if  message_instance =="cmc":
		 ins = Cmc.objects.get (pk =int(message_pk))
		 form = CmcForm (
		 instance = ins)
	if message_instance =="classe":	
		ins  = Class.objects.get (pk =int (message_pk))
		form =ClassForm(
		instance = ins)
	if message_instance =="radio":
			
		ins = Radio.objects.get(pk =int(message_pk))
		form =RadioForm(
		instance =ins)
        context["form"] =form
	return render_to_response (req ,
		 template ,
		 context)
	

        
            
            
