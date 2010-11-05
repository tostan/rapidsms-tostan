
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
<a href='/rapidsuivi/update_message_status/%(from_page)s/%(message_pk)s'>\
[MARQUER LE MESSAGE COMME LU]</a>\
</li>\
<li>\
<a href='/rapidsuivi/update_message/%(from_page)s/%(message_pk)s/%(message_instance)s'>\
[MODIFIER LE MESSAGE]\
</a>\
</li>\
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
    all= Relay.objects.all ()
    relay_args =dict()
    if req.method =="POST":
        p =req.POST
	if ("cordination" in p  and p.get("cordination") not in ["" ,"all"]):
                    relay_args.update({"cordination_id" :p.get("cordination")})
                    context.update({"cordination_selected": p.get("cordination")})
        if ("project" in p  and p.get("project") not in ["" ,"all"]):
                    relay_args.update({"project_id" :p.get("project")})
              	    context.update({"project_selected" :p.get("project")})
        # Ne selectionne pas les villages pour les host radios  car ils n'ont pas de villages
        if ("village" in p  and p.get("village") not  in ["", "all"]):
                    relay_args.update({"village_suivi__village" :\
			 	   Village.objects.get (pk =p.get("village"))})
                    context.update({"village_selected": p.get("village")})
        # Truncate the relay list with the given args dict 
        if all.count ()>0:
            all =all.filter (**relay_args)
	# Get the actor [cmc , class , or radio ] , please dont select village if you need radio host
        if ("actor" in p  and  p.get("actor") not in ["", "all"]):
                   actor  =req.POST["actor"]
                   if actor     =="1" :
                       context.update ({
			"cmcs":Cmc.objects.filter (relay__in =all)
			})
                   elif  actor  =="2" :
                       context.update({
			"classes":Class.objects.filter(relay__in =all)
			})
		   elif  actor   =="3":
		       context.update({
			"radios" :Radio.objects.filter(relay__in =all) 		     
		       })
		   else : pass              
        else :
	     for k , v  in {"cmcs" : Cmc , "classes": Class , "radios":Radio}.items():
             	context.update({k  :v.objects.filter(relay__in  =all)})
    else :
	     for k , v  in {"cmcs" : Cmc , "classes": Class , "radios":Radio}.items():
             	context.update({k  :v.objects.all()})
    # Now We have a liste of cmcs  , relays , and  radios we can go to 
    # go to  format data  for calendar UI by providing dict data to fill
    # for exemple into  MESSAGE_FOR_UI , 
    # ***ulr  for calendar ebent ***
    # ***date for caledar event 
    # ***is_read to  determine  class css  for  the calendar event 
    # So if message is already readed the callendar is **RED** else the calendar is *GREEN*
    # Get calendar event to display into  the map
    
    context.update(_get_form_data())
    context.update ( _get_qtip_data(context))
    return render_to_response (req ,template, context)
	
def _get_form_data ():
     """ Get the data for creating  form """
     return  {
	"cordination_options": dict (r.COORDINATION_TYPES),\
        "project_options":     dict(r.PROJECT_TYPES),\
        "village_options":     SuiviVillage.objects.values ("village__pk" , "village__name"),\
    	"actor_options":       dict([("1" , "CMC" ) ,   ("2" , "CLASS") ,("3" ,"RADIO")])
    }
 
def _get_qtip_data_object(obj,from_page =None):
	qtip_data = {}
	if isinstance (obj , Class):
		_title  ="CLASSE"
		type = "classe"
	elif isinstance(obj, Cmc):
		_title ="CMC"
		type ="cmc"
	elif isinstance (obj , Radio):
		_title ="RADIO"
		type ="radio"
	else :
		_title =""
		type  =""
	
	if hasattr (obj ,"relay"):
		relay = obj.relay
		qtip_data.update({"title":_title})
		qtip_data.update({"start": obj.date})
		qtip_data.update({"is_read": obj.is_read})	
	   	qtip_data.update({
		"first_and_last_name" :relay.first_name + relay.last_name
		})
        	qtip_data.update({
		"phone" :relay.contact.phone_number()
		})
        	qtip_data.update({
		"role" :relay.get_title_id_display()
		})
        	qtip_data.update(
		{"message":obj.__str__()}
		)
        	qtip_data.update(
		{"date": obj.date.strftime ("%d-%m-%Y %H:%M:%S")}
		)
        	qtip_data.update(
		{"village_pk"  : relay.village_suivi.pk}
        	)
		# The radio host does not have village
		if not isinstance (obj ,Radio):
			qtip_data.update(
			{"village_name": relay.village_suivi.village.name}
			)
		else :
			qtip_data.update({"village_name":"Radio host"})
        	qtip_data.update(
		{"message_pk" : str(obj.pk)}
		)
        	qtip_data.update(
		 {"cordination" :relay.get_cordination_id_display()})
        	qtip_data.update(
		{"message_instance" : type})
		qtip_data.update({"from_page" : from_page})
        	google_qtip_widget_data = GOOGLE_QTIP_WIDGET%qtip_data
		qtip_data.update(
		{"current_message" :google_qtip_widget_data})
		return qtip_data


	
def _get_qtip_data(context):
    """
    Parceque  , jFullCalendar attends dans son attributs events le format suivant 
    events =[     
            {"title":"CMC" , "url":"/" , "start":"2010-10-02"},
            {"title":"CLASS" , "url":"/" , "start":"2010-10-02"},
            {"title":"CLASS" , "url":"/" , "start":"2010-10-03"}                       
    ]
    Cette methode parcours les classes et cmcs pour retouner le bon format
    """
    data={"data": []}

    if "classes" in context:
	if len(context.get("classes")):
		classes = context.get("classes")
		for classe in classes:
			d=_get_qtip_data_object(classe)
			data["data"].append (d)
    if "cmcs" in context :
	if len(context.get("cmcs")):
		cmcs = context.get ("cmcs")
		for cmc in cmcs:
			d =_get_qtip_data_object(cmc)
			data["data"].append (d)
    if "radios" in context:
	if len (context.get ("radios")):
		radios = context.get ("radios")
		for  radio in radios:
			d= _get_qtip_data_object(radio)
			data["data"].append(d)
    return data
		
def _get_gmap_data_object(village):
	current_message  = village.current_message_from()
	data = {}
	_icon ="red"
	if current_messsage:
		if current_message.is_read :
			_icon ="green"
	data["message"] =EMPTY_VILLAGE_MESSAGE
	data["icon"] = _icon
	data["gmap_latitude"] = village.village.location.latitude
	data["gmap_longitude"]= village.village.location.longitude
	data["name"]          = village.village.name
	return data	
 
def _get_gmap_data(village):
	data  ={}
	gmap_data_object = _get_gmap_data_object(village)
	if village._get_current_message():
		qtip_data_object =_get_qtip_data_object(village._get_current_message()) 
                #Replace the message empty from  by the current_message from qtip_data
		if "message" in gmap_data_object:
			gmap_data_object.update({"message": qtip_data_object.get("current_message")})	
	if qtip_data_object:
		 data.update (qtip_data_object)
	data.update (gmap_data_object)
	return data

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
	context.update(_get_form_data())
	villages =list()
	gmap_datas =list()
	if req.method =="POST" :
		# The user is tryin to  filter  the map
		village_set =True
		all= Relay.objects.all()
		relay_args=dict()
		p = req.POST
                if ("cordination" in p and  p.get ("cordination")  not in ["" , "all"]):
                  	  relay_args["cordination_id"] = p.get("cordination")
 	                  context["cordination_selected"] =p.get("cordination")
	        if ("village" in p  and  p.get ("village") not in ["" , "all"]):
                	  relay_args["village_suivi__village"] =Village.objects.get (pk =p.get("village"))
              	       	  context["village_selected"]=p.get("village")
		if all.count ()>0:
		  all = all.filter(**relay_args)	
		if all.count()>0:
			villages  =SuiviVillage.objects.filter\
			(pk__in =[ v.pk for  v in  [r.village_suivi  for r in all  if r.village_suivi]])	
	if not  len (villages):	
		villages =  SuiviVillage.objects.all ()
        for suivi_village in villages :
	     gmap_data  = _get_gmap_data (suivi_village)
             gmap_datas.append (gmap_data)
        context ["villages"]  =gmap_data
        return render_to_response (req , template , context)

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

        
            
            
