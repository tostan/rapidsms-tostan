from django import forms
from  .models import *
class CmcForm(forms.ModelForm):
	class Meta:
	   model =Cmc
	   exclude = ("debug_id" , "_children" ,"relay")
class RadioForm(forms.ModelForm):
	class Meta:
	   model=Radio
	   exclude  = ("debug_id" ,"_children" ,"relay")
class ClassForm(forms.ModelForm):
	class Meta:
	   model =Class
	   exclude  =("debug_id" ,"_children" , "relay")
