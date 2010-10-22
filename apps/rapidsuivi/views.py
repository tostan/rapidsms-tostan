# Create your webui views here.
from rapidsms.webui.utils import render_to_response
from django.contrib.auth.decorators import login_required
from apps.rapidsuivi.models import *
from apps.smsforum.models import *
from apps.rapidsuivi.models import Relay as r
from django.http import HttpResponse , HttpResponseRedirect


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
			    if cmc_or_class_or_radio ="3":
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
     context ["cordination_options"] =dict (r.COORDINATION_TYPES)
     context ["project_options"]     =dict(r.PROJECT_TYPES)
     context ["village_options"]     =SuiviVillage.objects.values ("village__pk" , "village__name")
     context ["actor_options"]       = dict ((("1" , "CMC" ) , ("2" , "Class")))
     
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
            values ["url"] =\
		"/update_message_status/%s"%cls.pk
            values ["start"] = "%s"%cls.date
            values ["current_message"] =\
		MESSAGE_FOR_UI%message_ui_from_class(cls)
            calendar_event.append (values)
    # Get cmc/CGC for the calendar UI
    if "cmcs" in context:
        cmcs =context["cmcs"]
        for cmc in cmcs :
            values ={"title" :"CMC"}
            values ["url"] =\
		"/update_message_status/%s"%cmc.pk
            values ["start"] = "%s"%cmc.date 
            values ["current_message"]=\
		MESSAGE_FOR_UI%message_ui_from_cmc(cmc)
            calendar_event.append (values)


    # Get Radio Messages for the calendar UI
    if "radios" in context:
	radios = context["radios"]
	for radio in radios:
	    values = {"title": "RAD"}
            values ["url"]=\
		"/update_message_status/%s"%radio.pk
	    values["start"] ="%s"%radio.date
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
             icon = "red"
             pk =""
	     cur_msg  =suivi_village.current_message ()
	     if cur_msg:
	 	display_message = cur_msg.message
		pk =cur_msg.pk
		if not cur_msg.is_read:
			icon = 'green'
	     dict = {
		 "gmap_latitude" : suivi_village.village.location.latitude  ,
                 "gmap_longitude" : suivi_village.village.location.longitude,
                 "name"  :     suivi_village.village.name , 
                 "current_message" :MESSAGE_FOR_UI%message_ui_from_village (suivi_village),
                 "pk":pk
                 }
	     # Quel icon pour goolemap (rouge  ou vert 
	     dict["icon"]=icon
	     gmap_data.append (dict)

        #return HttpResponse (gmap_data)
        context ["villages"]  =gmap_data
        return render_to_response (req , template , context)


def message_ui_from_classe(classe):
	"""Return un dict of data to fill into the MESSAGE_FOR_UI text"""
	dict = {}
	dict["first_and_last_name"] =\
		classe.relay.firt_name + classe.relay.last_name
	dict["contact_phone"]=\
		classe.relay.contact.phone
	dict["type"]=\
		classe.relay.get_title_id_display()
	dict["message"] =classe.message 

def message_ui_from_cmc(cmc):
	"""Return a dict of data to fill into the MESSAGE_FOR_UI text"""
	dict ={}
	dict["first_and_last_name"]=\
		cmc.relay.first_name + cmc.relay.last_name
	dict["contact_phone"]=\
		cmc.relay.contact.phone
	dict["type"]=\
		cmc.relay.get_title_id_dispaly()
	dict["message"] = cmc.message

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

def message_read (req ,pk =None):
	try:
	   Cmc.objects.filter(pk =pk).update (is_read =True)
	except Exception, e:
		print "CE N'EST PAS UN CMC"
	try:
	   Class.objects.filter (pk=pk).update(is_read=True)
	except Exception , e:
	       print "CE N'EST PAS UNE CLASS"
        return HttpResponseRedirect ("/map") 
    
def messages (req , msg_id = None):
    # If we have a urrent message id 
    if msg_id :
        # Are you a  class message 
        try:
            context ["current_cmc "] =Cmc.objects.get(pk = msg_id)    
        except :
            pass
        # Are you a cmc  message
        try:
            context ["current_class"]=Class.objects.get (pk =msg_id)
        except :
            pass
        
    context ["cmcs"]  =Cmc.objects.all ().order("is_read" , "date")
    context ["classes"]=Class.objects.all ().order("is_read ", "date")
    to_message (context)
    return render_to_response (req, template , context)
    
             
def to_message (context):
    messages =[]
    if "cmcs" in context and len (context["cmcs"]) :
            message = { "type" : "CMC"}
            message["content"] = cmc.message_resp
            message["relay"]  = cmc.relay.fisrt_name + cmc.relay.last_name 
            message["date"]   = cmc.date 
            message["village"]=cls.relay.village_suivi.village.name
            messages.append (message)
            
    if "classes" in context and len (context["classes"]) :
            message = { "type" : "CLASS"}
            message["content"] = cls.message_resp
            message["relay"]  = cls.relay.first_name + cls.relay.last_name 
            message["date"]   = cls.date 
            message["village"] =cls.relay.village_suivi.village.name 
            messages.append (message)
    context ["messages"]
 
def update_message_status (req , message_pk):
	return  HttpResponse ("OK")
     
            
                
        
         
            
            
