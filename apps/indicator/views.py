# Create your webui views here.
#from django.shortcuts import render_to_response
from django.http import HttpResponse ,HttpResponseRedirect
from rapidsms.webui.utils import render_to_response
from django.core.urlresolvers import reverse
from apps.indicator.models import *
from django import forms
from django.utils.translation import ugettext_lazy as _
def index (req):
    return render_to_response (req,"indicator/index.html" , {})

def parametrage(req):
    return render_to_response (
     req, "indicator/parametrage.html" , {})
def make_form(qs, klass):
        fields = {}
        fields["name"] = forms.CharField (label = _("Nom"),max_length = 160)
        #fields[str (klass.__name__.lower ())]=forms.ModelChoiceField ( queryset = qs)
        fields[str (klass.__name__.lower ())]=forms.ChoiceField ( choices = (("--" , ("--") , ("1" , "un"))))
        
        def clean (self):
            print "CLEANED data"
            print self.cleaned_data
            return self.cleaned_data
            
        return type ("FormArea" , (forms.BaseForm,) , {"base_fields":fields  ,"clean" : clean})
    
def add_area (req, pays , type):
    if(pays and pays.lower ().strip() =="senegal"):
        if (type and type =="region"):
            
            form_class  = make_form (Region.objects.all (), Region)
            print "******"
            print form_class ()
            form = form_class ()
    

    print form
    template = "indicator/add_area.html"
    return render_to_response (req, template , {"form": form })

            