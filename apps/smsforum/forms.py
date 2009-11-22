from django import forms
from django.forms import ModelForm
from apps.smsforum.models import *
from apps.contacts.models import * 

# On this page, users can upload an xsd file from their laptop
# Then they get redirected to a page where they can download the xsd

class VillageForm(ModelForm):
    latitude  = forms.DecimalField(max_digits=8, decimal_places=6, required=False)
    longitude = forms.DecimalField(max_digits=8, decimal_places=6, required=False)

    class Meta:
        model = Village
        fields = ('name', 'notes')

    def __init__(self, data=None, instance=None):
        super(VillageForm, self).__init__(data=data, instance=instance)
        if instance is not None and instance.location is not None:
            self.fields['latitude'].initial = instance.location.latitude
            self.fields['longitude'].initial = instance.location.longitude

"""    
class AddCommunityForm(forms.Form):
    name = forms.CharField(label=u'Name of Community')
    members = forms.ModelMultipleChoiceField(Village.objects, label=u'Add Villages')
"""
