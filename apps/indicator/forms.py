from django import froms

class PaysForm (forms.ModelForms):
    class Meta:
        fields = ("name")
        
class RegionForm(forms.Form ):
    name = forms.CharField (max_length = 100)
    pays = forms.ModelChoiceField (queryset = Pays.objects.all ())
    
    def save (self):
        print  "FIELDS"
        print self.fields
        super (RegionForm , self).save ()
    
    class Meta :
        fields  = ("name" , "pays")
        
        

    