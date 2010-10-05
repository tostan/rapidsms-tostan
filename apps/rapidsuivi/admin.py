from django.contrib import admin
from rapidsuivi.models import *
class SuiviVillageAdmin(admin.ModelAdmin):
    def suivi_data (self , vil):
        abs  =vil.absents.all ()
        data
        for a in abs :
            data.append ("".join (["Date :%s ,M:%s ,G:%s, B:%s" %(
                                   a.num_women_dropped  , a.num_men_dropped ,a.num_boys_dropped ,a.num_girls_dropped)
                                  ]))
            
        return "".join (data)
    list_display = ("village",)

admin.site.register(SuiviVillage , SuiviVillageAdmin)
admin.site.register(Cmc)
admin.site.register(Class)
admin.site.register(Relay)