from apps.rapidsuivi.models import Relay  as r
from apps.rapidsuivi.models import *
from django import template

register  =template.Library ()


@register.inclusion_tag ("rapidsuivi/partials/calendar_form.html")
def calendar_forms():
   return {
           "cordination_options":  dict (r.COORDINATION_TYPES),
           "project_options":dict(r.PROJECT_TYPES),
           "village_options": dict (SuiviVillage.objects.values ("pk" , "village__name")),
           "actor_options"  : dict ([("1" , "CMC" ) , ("2" , "Class")])
   } 
   
   
    
            