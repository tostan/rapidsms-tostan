
# Create your webui views here.
from django.utils.translation  import ugettext  as _ 
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
** Note**
Because to MESSAGE_FOR_UI work like an html page  displayed from 
map and calendar I need to flag which page the Widget MESSAGE_FOR_UI
is displayed. So I keep a flag named *from_page* into the classe.
"""
MESSAGE_FOR_UI="""<ul>\
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
<li><a href='/rapidsuivi/update_message_status/%(from_page)s/%(message_pk)s'>[MARQUER LE MESSAGE COMME LU]</a></li>\
<li><a href='/rapidsuivi/update_message/%(from_page)s/%(message_pk)s/%(message_instance)s'>[MODIFIER LE MESSAGE]</a></li>\
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
    context =dict()
    _get_calendar_form (context)
    all= Relay.objects.all ()
    relay_args =dict()
    if req.method =="POST":
        if "cordination" in  req.POST and req.POST["cordination"] not in ["" ,"all"] :
                    relay_args["cordination_id"] = req.POST["cordination"]
                    context["cordination_selected"] =req.POST["cordination"]
        if "project" in req.POST and req.POST["project"] not in ["" ,"all"]:
                    relay_args["project_id"] =req.POST["project"]
              	    context["project_selected"] = req.POST["project"]
        # Ne selectionne pas les villages pour les host radios  car ils n'ont pas de villages
        if "village" in req.POST and req.POST["village"]  not  in ["", "all"]:
                    relay_args["village_suivi__village"] =\
			 Village.objects.get (pk =req.POST["village"])
                    context["village_selected"]= req.POST["village"]
        # Truncate the relay list with the given args dict 
        if all.count ()>0:
            all =all.filter (**relay_args)
	# Get the actor [cmc , class , or radio ] , please dont select village if you need radio host
        if "actor" in req.POST and  req.POST.get("actor") not in ["", "all"]:
                   actor  =req.POST["actor"]
                   if actor     =="1" :
                       context["cmcs"]   =Cmc.objects.filter (relay__in =all)
                   if  actor  =="2" :
                       context["classes"]=Class.objects.filter(relay__in =all)
		   if  actor   =="3":
		       context["radios"] = Radio.objects.filter(relay__in =all) 		                   
        else :
             context  ["cmcs"]   =Cmc.objects.filter(relay__in  =all)	
             context  ["classes"]=Class.objects.filter(relay__in =all)
	     context  ["radios"] =Radio.objects.filter(relay__in =all)
    else :
             context  ["classes"]=Class.objects.all ()
             context  ["cmcs"]   =Cmc.objects.all ()
	     context  ["radios"] =Radio.objects.all()
    # Now We have a liste of cmcs  , relays , and  radios we can go to 
    # go to  format data  for calendar UI by providing dict data to fill
    # for exemple into  MESSAGE_FOR_UI , 
    # ***ulr  for calendar ebent ***
    # ***date for caledar event 
    # ***is_read to  determine  class css  for  the calendar event 
    # So if message is already readed the callendar is **RED** else the calendar is *GREEN*
    # Get calendar event to display into  the map
    _get_calendar_events (context)
    return render_to_response (req ,template, context)
	
def _get_calendar_form (context):
     """ Get the data for creating  form """
     context ["cordination_options"] =dict (r.COORDINATION_TYPES)
     context ["project_options"]     =dict(r.PROJECT_TYPES)
     context ["village_options"]     =SuiviVillage.objects.values ("village__pk" , "village__name")
     context ["actor_options"]       =dict([("1" , "CMC" ) ,   ("2" , "CLASS") ,("3" ,"RADIO")])
    
 
def _get_calendar_events (context):
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
            values ={"title" :"CLASSE"}
            values ["start"] = "%s"%cls.date
            values ['is_read']=cls.is_read
	    # We are into the calendar , so get the messag_ui  params and add
	    # the from page as calendar {"from_page" :"calendar"}
	    msg_ui_params= message_ui_from_class(cls)
	    msg_ui_params.update ({"from_page":"calendar"})
	    values ["current_message"] =MESSAGE_FOR_UI%msg_ui_params
            calendar_event.append (values)
    # Get cmc/CGC for the calendar UI
    if "cmcs" in context:
        cmcs =context["cmcs"]
        for cmc in cmcs :
            values ={"title" :"CMC"}
            values ["start"] = "%s"%cmc.date
            values ["is_read"] =cmc.is_read
	    msg_ui_params = message_ui_from_cmc(cmc) 
	    msg_ui_params.update ({"from_page" :"calendar"})
            values ["current_message"]=	MESSAGE_FOR_UI%msg_ui_params
            calendar_event.append (values)
    # Get Radio Messages for the calendar UI
    if "radios" in context:
	radios = context["radios"]
	for radio in radios:
	    values = {"title": "RADIO"}
	    values["start"] ="%s"%radio.date
	    values["is_read"]=radio.is_read
	    msg_ui_params =message_ui_from_radio(radio)
	    msg_ui_params.update({"from_page":"calendar"})
	    values["current_message"]=MESSAGE_FOR_UI%msg_ui_params
	    calendar_event.append(values)
    if len (calendar_event):
        context ["data"]  = calendar_event 
    
            
def map (req , template = "rapidsuivi/gmap.html"):
	"""
	I dont think if this is a good idea to filter the village and regions using the relay 
	I will check later .But Because for this moment there is no link with village an regionnal
	coordination  bu between the relay and  the regionnal coordination and  between the 
	relay and the village.
	"""
	# I a using here the calendar form function again here because it contain all 
	# data to fill  form , regionnals coordinations  , villages list ......
	context =dict()
	# Get the form to filter  the map
	_get_calendar_form(context)
	villages =list()
	if req.method =="POST" and "filter" in  req.POST and req.POST["filter"]:
		# The user is tryin to  filter  the map
		village_set =True
		all= Relay.objects.all()
		relay_args=dict()
                if "cordination" in req.POST and  req.POST.get ("cordination")  not in ["" , "all"]:
                  	  relay_args["cordination_id"] = req.POST["cordination"]
 	                  context["cordination_selected"] =req.POST["cordination"]
	        if "village" in req.POST  and  req.POST.get ("village") not in ["" , "all"]:
                	    relay_args["village_suivi__village"] =Village.objects.get (pk =req.POST["village"])
              	       	    context["village_selected"]= req.POST["village"]
		if all.count ()>0:
		  all = all.filter(**relay_args)	
		if all.count()>0:
			villages  =SuiviVillage.objects.filter\
			(pk__in =[ v.pk for  v in  [r.village_suivi  for r in all  if r.village_suivi]])
	
	if not  len (villages):	villages =  SuiviVillage.objects.all ()
        gmap_data  =[]
        for suivi_village in villages :
             values ={}
	     icon = "red"
	     # Le dernier message recu par le village ou bien 
	     # le dernier message qui n'est pas encore ete lu
	     cur_msg  =suivi_village.current_message_from ()
	     if cur_msg:
		if not cur_msg.is_read:
			icon = 'green'
		# The message from classse can be a message from cmc , or classe  or radio
		# depends of the current message received  by the village 
		msg_ui_from_vil =message_ui_from_village  (cur_msg)
		# Add page param
		msg_ui_from_vil.update({"from_page":"map"})
		values["message"] =MESSAGE_FOR_UI%msg_ui_from_vil
	     else :
		values["message"]=EMPTY_VILLAGE_MESSAGE
	     values["name"] = suivi_village.village.name
	     values.update ({"gmap_latitude": suivi_village.village.location.latitude})
             values.update ({"gmap_longitude":suivi_village.village.location.longitude})
	     # Quel icon pour goolemap (rouge  ou vert 
	     values["icon"]=icon
	     gmap_data.append (values)

        #return HttpResponse (gmap_data)
        context ["villages"]  =gmap_data
        return render_to_response (req , template , context)


def message_ui_from_class(classe):
	"""Return un dict of data to fill into the MESSAGE_FOR_UI text"""
	kw  = dict ()
	kw["first_and_last_name"] =classe.relay.first_name + classe.relay.last_name
	kw["phone"]=classe.relay.contact.phone_number()
	kw["role"]=classe.relay.get_title_id_display()
	kw["message"] =classe.__str__() 
        kw["date"] = classe.date.strftime ("%d-%m-%Y %H:%M:%S")
	kw["village_pk"] =classe.relay.village_suivi.pk
	kw["village_name"]=classe.relay.village_suivi.village.name
 	kw["message_pk"] = str(classe.pk)
	kw["cordination"] = classe.relay.get_cordination_id_display()
	kw["message_instance"] = "classe"
	return kw

def message_ui_from_cmc(cmc):
	"""Return a dict of data to fill into the MESSAGE_FOR_UI text"""
	kw=dict ()
	kw["first_and_last_name"]=cmc.relay.first_name + cmc.relay.last_name
	kw["phone"]=cmc.relay.contact.phone_number()
	kw["role"] =cmc.relay.get_title_id_display()
	kw["message"] = cmc.__str__()
        kw["date"] = cmc.date.strftime ("%d-%m-%Y %H:%M:%S")
	kw["village_pk"] =cmc.relay.village_suivi.pk
	kw["village_name"]=cmc.relay.village_suivi.village.name
	kw["message_pk"] =str(cmc.pk)
	kw["cordination"] = cmc.relay.get_cordination_id_display()
        kw["message_instance"] ="cmc"	
	return kw

def message_ui_from_radio(radio):
	""" Return a dict of data  to fill  into MESSAGE_UI text """
	kw=dict()
	kw["first_and_last_name"]=radio.relay.first_name + radio.relay.last_name
	kw["phone"]=radio.relay.contact.phone_number()
        kw["role"]=radio.relay.get_title_id_display()
  	kw["message"]=radio.__str__()
        kw["date"] = radio.date.strftime ("%d-%m-%Y %H:%M:%S")
	kw["village_pk"] =radio.relay.village_suivi.pk
	kw["village_name"]=radio.relay.village_suivi.village.name	
	kw["message_pk"] = str(radio.pk)
	kw["cordination"] = ""
        kw["message_instance"] = "radio"
	return kw 
        
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
 
    
def update_message_status (req ,from_page , message_pk ):
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
	return HttpResponseRedirect(reverse("map") if  from_page =="map" else reverse ("calendar"))
		
     
def update_message (req , from_page ,message_pk ,message_instance) :
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
		    form  = CmcForm (data =req.POST  , instance =Cmc.objects.get (pk =int (message_pk)))
		    if form.is_valid():
			form.save()
		    else : errors = form.errors
		# If the given message is a  class
		if message_instance =="classe":
		     form = ClassForm(data = req.POST , instance = Class.objects.get (pk =int (message_pk)))
		     if form.is_valid():
			form.save()
		     else: errors = form.errors
		#If the given message is radio type message
		if message_instance =="radio":
		     form = RadioForm (data = req.POST , instance = Radio.objects.get(pk = int (message_pk)))
		     if  form.is_valid ():
		     	form.save()
		     else : errors = form.errors	
		if not len(errors):
	        	return HttpResponseRedirect(reverse("map") if from_page =="map" else reverse("calendar"))
		else :
			context ["errors"] =errors
        form =None		 
	if  message_instance =="cmc":
		 form = CmcForm ( instance = Cmc.objects.get (pk =int(message_pk)))
	if message_instance =="classe":	
		form =ClassForm(instance  = Class.objects.get (pk =int (message_pk)))
	if message_instance =="radio":	
		form =RadioForm(instance = Radio.objects.get(pk =int(message_pk)))
        context["form"] =form
	return render_to_response (req , template ,context)
	
def export_message (req,village_pk):
	"""Given a village I am going  to export all CMC , RADIO , AND CLASS
	activity sent  from  the given village """
	village =SuiviVillage.objects.get (pk = int (village_pk))
        data =  [ o for o in Cmc.objects.filter (relay__village_suivi = village).all()]+\
		[ o for o in Class.objects.filter (relay__village_suivi =village).all()]+\
		[ o for o in Radio.objects.filter(relay__village_suivi =village).all()]

	if not len(data):
		response  = HttpResponse (mimetype ="application/vnd.ms-excel")
		response ["Content-Disposition"]="attachment; filename =empty.xls"
		return response
	response  = HttpResponse (mimetype ="text/csv")
	response ["Content-Disposition"]="attachment; filename =%s.xls"\
		%village.village.name.replace(" " ,"_")
	writer  = UnicodeWriter(response)
	# I dont think if the is the best place to put this
	# Rowena should check
	fields = {"message" : _("Message Recu par Tostan"),   "relay": _("Le Relay") ,
		  "date" :_("Date  de Reception"), 	      "type_id":_("Type du message")
	}			
        writer.writerow (fields.values ())
	for obj  in  data :
		row =[]
		for field  in fields.keys() :
		        if field =="relay":
				val = obj.relay.first_name + obj.relay.last_name
			elif field =="type_id":
			        if isinstance(obj,Cmc):
				 	val = "CMC"
				elif isinstance(obj, Class):
					val ="CLASS"
				else : val  = "RADIO"
			# Certainly e message attribute
			else :
				val  = getattr (obj ,field)
			row.append(val)
		writer.writerow(row)
        return response
class UnicodeWriter(object):
	""" A unicode Writer helper that allow us to write
	any given encoding  , default is utf-8
	"""
	def __init__ (self,stream , dialect ="excel-tab" , encoding= "Utf-8",**kw):
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer (self.queue ,dialect =dialect)
		self.encoder  = codecs.getincrementalencoder (encoding)()
		self.stream  =stream

	def writerow(self, row):
		self.writer.writerow([unicode (s).encode('utf-8') for s in row])
		# Get data from queue 
		data  = self.queue.getvalue ()
		# Decode to unicode 
		data  = data.decode ("Utf-8")
		# Reencode  from given encoding 
		self.encoder.encode (data)
		# write into  stram
		self.stream.write (data)
		self.queue.truncate (0)

        
            
            
