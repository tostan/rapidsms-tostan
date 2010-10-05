# Create your webui views here.
from rapidsms.webui.utils import render_to_response
from django.contrib.auth.decorators import login_required
from apps.rapidsuivi.models import *
from apps.smsforum.models import *
from apps.rapidsuivi.models import Relay as r


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
                    relay_filtres["village_suivi__village"] = Village.objects.get (pk =req.POST["village"])
                context["village_selected"]= req.POST["village"]
                   
        print "relay_filtres++++++++++++++++++++++++++" , relay_filtres
        if len (relay_filtres)>0:
            all_relays =all_relays.filter (**relay_filtres)
        
        print "all_relay++++++++++++++++++++++++++" ,all_relays
        if len (all_relays):
                if "actor" in req.POST:
                        if req.POST.get("actor") not in ("", "all"):
                            cmc_or_class =req.POST["actor"]
                            if cmc_or_class =="1" :
                                context["cmcs"]  =Cmc.objects.filter (relay__in =all_relays)
                            if cmc_or_class =="2" :
                                context["classes"]=Class.objects.filter(relay__in=all_relays)                    
                        else:
                             context["cmcs"]  =Cmc.objects.filter (relay__in=all_relays)
                             context["classes"] =Class.objects.filter (relay__in =all_relays)
                        context["actor_selected"] =req.POST["actor"]
                        
    else :
                        context  ["cmcs"]  =Cmc.objects.all ()
                        context   ["classes"]=Class.objects.all ()
    print "context ++++++++++++++++++++++++" , context 
    calendar_events (context)
    print  "context +++++++++++++++++++++++++",context
    return render_to_response ( req, template, context )                    

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
    if "classes" in context :
        classes  =context["classes"]
        for cls in classes :
            values ={"title" :"[CLASS] ,[Relay]:%s , [Village] :%s  )"%(
                    (cls.relay.first_name + cls.relay.last_name),
                    (cls.relay.village_suivi.village.name)
                    
                    )}
            values ["url"] ="/suivi/messages/%s"%(cls.pk)
            values ["start"] = "%s"%cls.date 
            calendar_event.append (values)
    if "cmcs" in context :
        cmcs =context["cmcs"]
        for cmc in cmcs :
            values ={"title" :"[CMC] , [Relay] : %s , [Village] :%s"%(
                (cmc.relay.first_name +cmc.relay.last_name),
                 cmc.relay.village_suivi.village.name
            )}
            values ["url"] ="/suivi/messages/%s"%(cmc.pk)
            values ["start"] = "%s"%cmc.date 
            calendar_event.append (values)
        
    if len (calendar_event):
        context ["data"]  = calendar_event 
    print "calendar_event++++++++++++++++++++++++++++++",calendar_event
    
            
def map (req , template = "rapidsuivi/gmap.html"):
        context  = {}
        villages =  SuiviVillage.objects.all ()
        gmap_data  =[]
        for suivi_village in villages :
             if Cmc.objects.filter (relay__village_suivi = suivi_village, is_read = False).count ()>0:
                    suivi_village.new_message = True 
             
             elif   Class.objects.filter (relay__village_suivi =suivi_village , is_read =False).count ()>0:
                    suivi_village.new_message  =True 
                    
             else :
                  suivi_village.new_message  =False 
            
             gmap_data.append  (
                {"gmap_latitude" : suivi_village.gmap_latitude  ,
                 "gmap_longitude" : suivi_village.gmap_longitude  ,
                 "name"  :     suivi_village.village.name , 
                 "new_message" :suivi_village.new_message
                 })
        
        print  "data +++++++++++++++++++++++" ,gmap_data
        context ["villages"]  =gmap_data
        return render_to_response (req , template , context)
    
    
    
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
    

     
            
                
        
         
            
            