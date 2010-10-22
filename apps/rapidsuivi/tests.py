from rapidsms.tests.scripted import TestScript
import apps.reporters.app  as  reporter_app
import apps.contacts.app   as  contact_app
from apps.contacts.models import *
from apps.rapidsuivi.models import *
from apps.smsforum.models import *
from apps.locations.models import *
from app import App

class TestApp (TestScript):
    fixtures =["rapidsuivi.json"]
    apps = (reporter_app.App ,contact_app.App, App,)
#        print  "Exceution du test a"
#        script_add_cla_fail = """
#        775526745 > cla 1 2 23 12 7 23 9
#        """
#        
#        self.runScript (script_add_cla_fail)
#        if Contact.objects.count () > 0:
#            print Contact.objects.count ()
#            print Contact.objects.all ()
#            
#            
#        if Relay.objects.count ()>0:
#            self.failt ("Relay is not null")
#            
#            
#        script_reg_success  = """
#        775526745 > 123 3 2 25.1 43.12 1 chekh Ba
#        """
#        
#        self.runScript (script_reg_success)
#        print Contact.objects.all ()
#        for c in  Contact.objects.all ():
#            #Contacts  [c.connection_create_from est disponible que a partir de message.sender]
#            #print c.connection_created_from
#            #print c.connection_created_from.identity
#            #print c.relays.all ()
#            #print c.relays.count()
#            print c.reporter 
#            print c.reporter.connection
#        
#        print Relay.objects.count()
#        if Relay.objects.count() >1:
#            self.fail ("Le relay a ete cree alors que il y'a pas encore de village")
#        
#        loc=  Location (code= "00" , latitude = "25.1" , longitude = "43.12")
#        loc.save ()
#        vil = Village.objects.create (location =loc  , name ="Keur Samba Laobe")
#        svil  =SuiviVillage (village=vil)
#        svil.save ()
#        print "V count"
#        print SuiviVillage.objects.count ()
#        
#        print "V coords"
#        for v in SuiviVillage.objects.all ():
#                print v.village.location.latitude 
#                print v.village.location.longitude
#                
#        if not SuiviVillage.objects.count() >0:
#            self.fail ("A suivi village is not create")
#        
#        
#        
#        
#        script_reg_2 = """
#        775526745 > 123 3 2 25.1 43.12 1 chekh Ba
#        """
#        self.runScript (script_reg_2)
#
#        #print "R count"
#        #print Relay.objects.count ()
#        #for   r in Relay.objects.all ():
#        #       r.contact.reporter 
#        #        r.contact.reporter.connection 
#        #        
#        #nb_rel  = Relay.objects.count ()
#        
#        script_reg_2 = """
#        775526745 >123 3 2 25.1 43.12 1 chekh Ba
#        """
#        self.runScript (script_reg_2)
#        #if Relay.objects.count () > nb_rel:
#        #    self.fail ("Relay a ete duplique ")
#        #
#        
#        #print Class.objects.all ()
#        
#        
#        script_relay_exist  ="""
#        775526745 >123 3 2 25.1 43.12 1 chekh Ba
#        """
#        
#        self.runScript(script_relay_exist)
#        
#        print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#        
#        script_add_class  ="""
#        775526745 >cla  1 2 23 12 7 23 9
#        """
#        self.runScript (script_add_class)
#        #print "class C"
#        #print Class.objects.count ()
#        #for c in Class.objects.all ():
#         #    print c.title_id, c.get_title_id_display() ,c.cohort_id ,c.get_cohort_id_display(),c.title_id
#           #  c.num_session , c.num_women , c.num_men ,c.num_girls ,c.num_boys , c.date ,c.relay.contact.locale
#          #   
#             
#        script_abs_class ="""
#        775526745 > abs 2 4 2 2 1
#        """
#        self.runScript (script_abs_class)
#        print "classabs C"
#        print ClassAbs.objects.count ()
#        print Class.objects.all ()[0].absents.all ()
#        
#        script_add_relay2="""
#        7755257642 > 123 3 2 25.1 43.12 1 Fatou Fall
#        """ 
#        
#        self.runScript (script_add_relay2)
#        print "R count"
#        count= Relay.objects.count ()
#        print count 
#        
#        
#        script_add_relay2_fail="""
#        7755257642 > 123 3 2 25.1 43.12 1 Fatou Fall
#        """
#        self.runScript (script_add_relay2_fail)
#        print "R count2"
#        count2  =Relay.objects.count ()
#        print count2
#        if count2 != count :
#            self.fail ("Relay duplicate ERROR")
#        
#        print "------------------REUNION-----------"
#        script_add_reunion = """
#        775526745 > reu 14 25 1 5
#        """
#        print  "CMC count"
#        print Cmc.objects.count ()
#        self.runScript (script_add_reunion)
#        print "CMC count2"
#        print Cmc.objects.count ()
#        print Cmc.objects.all ()[0].get_type_id_display ()
#        
#        print "------------------FINANCE-----------"
#        script_add_reunion = """
#        775526745 > fin 25000 45000
#        """
#        print  "CMC count"
#        print Cmc.objects.count ()
#        self.runScript (script_add_reunion)
#        print "CMC count2"
#        print Cmc.objects.count ()
#        print Cmc.objects.all ()[0].get_type_id_display ()
#        print Cmc.objects.all ()[1].get_type_id_display ()
#        
#        print "------------------MOBLILIZATION-----------"
#        script_add_reunion = """
#        775526745 > ms 321 8 2 1
#        """
#        print  "CMC count"
#        print Cmc.objects.count ()
#        self.runScript (script_add_reunion)
#        print "CMC count2"
#        print Cmc.objects.count ()
#        print Cmc.objects.all ()[0].get_type_id_display ()
#        print Cmc.objects.all ()[1].get_type_id_display ()
#        print Cmc.objects.all ()[2].get_type_id_display ()
#        
#        
#        print "------------------RADIO-----------"
#        script_add_reunion = """
#        775526745 > rad 1 2 3
#        """
#        print  "CMC count"
#        print Cmc.objects.count ()
#        self.runScript (script_add_reunion)
#        print "CMC count2"
#        print Cmc.objects.count ()
#        print Cmc.objects.all ()[0].get_type_id_display ()
#        print Cmc.objects.all ()[1].get_type_id_display ()
#        print Cmc.objects.all ()[2].get_type_id_display ()
#        print Cmc.objects.all ()[3].get_type_id_display ()
#        print Cmc.objects.all ()[3].get_show_type_id_display()
#        print Cmc.objects.all ()[3].get_show_location_id_display()
#    
#    
#    
#       
#       
#        
#        
#        
#        
#        
#        
#               
              
             
    # define your test scripts here.
    # e.g.:
    #
    # testRegister = """
    #   8005551212 > register as someuser
    #   8005551212 < Registered new user 'someuser' for 8005551212!
    #   8005551212 > tell anotheruser what's up??
    #   8005550000 < someuser said "what's up??"
    # """
    #
    # You can also do normal unittest.TestCase methods:
    #
    # def testMyModel (self):
    #   self.assertEquals(...)

    
    def setUp(self):    
         loc=  Location (code= "00" , latitude = "25.1" , longitude = "43.12")
         loc.save ()
         vil = Village.objects.create (location =loc  , name ="Keur Samba Laobe")
         svil  =SuiviVillage (latitude ="25.1" , longitude ="43.12" , village = vil)
         svil.save ()
         super(TestApp,self).setUp()
        
    testClasseFail ="""
    775526745 > cla 1 2 23 12 7 23 9
    775526745 < Identification requise!
    775526745 > 123 3 2 25.1 43.12 1 chekh Ba 
    775526745 < Merci chekhou Ba.Vous etes bien inscrit a RapidSuivi en tant que Facilitator de Keur Samba Laobe.En cas de probleme,merci de contacter votre Superviseur.Bonne journee!
    775526745 > 123 3 2 25.1 43.12 1 chekh Ba
    775526745 < Vous etes deja enregistre
    775526745 > cla 1 2 23 12 7 23 9
    775526745 < Merci chekh Ba .Vous avez fini la sceance 23 du Kobi2 avec les adult de Keur Samba Laobe .Presents : 12 femmes ,7 hommes ,23 filles et 9 garcons .En cas d'erreur ,merci de contacter votre Superviseur .Bonne journee !
    """
   
     
     
    testAddClasseFail="""
    775526745 > cla 1 2 23 12 7 23 9
    775526745 < Identification requise!  
    """
    
    testUpdateClasse="""
    775526745 > cla 1 2 23 12 7 23 9
    775526745 < Identification requise!
    775526745 > 123 3 2 25.1 43.12 1 chekh Ba
    775526745 < Merci chekh Ba.Vous etes bien inscrit a RapidSuivi en tant que Facilitator de Keur Samba Laobe.En cas de probleme,merci de contacter votre Superviseur.Bonne journee!
    775526745 > cla 1 1 23 12 7 23 9
    775526745 < Merci chekh Ba .Vous avez fini la sceance 23 du Kobi 1 avec les adult de Keur Samba Laobe .Presents : 12 femmes ,7 hommes ,23 filles et 9 garcons .En cas d'erreur ,merci de contacter votre Superviseur .Bonne journee !
    775526745 > abs 2 4 2 2 1
    775526745 < Merci chekh Ba .Durant le Kobi 1 ,4 femmes ,2 hommes ,2 filles et 1 garcons ont abandonne la classe en cours de route .En cas d'erreur ,merci de contacter votre Superviseur
    """
    
    
    
    testAddReunion ="""
    775526748 > 123 3 2 25.1 43.12 1 Fatou Fall
    775526748 < Merci Fatou Fall.Vous etes bien inscrit a RapidSuivi en tant que Facilitator de Keur Samba Laobe.En cas de probleme,merci de contacter votre Superviseur.Bonne journee!
    775526748 > reu 14 25 1 5
    775526748 < Merci Fatou Fall .Le CGC de Keur Samba Laobe s'est reuni aujourd'hui ,14 membres et 25 invites etaient presents et vous avez discute principalement du theme de la Health .Vous avez planifie d'organiser un Sensibilisation Paludisme bientot .En cas d'erreur ,merci de contacter votre Superviseur .Bonne journee
    """
    
        
    testAddFinance="""
    775526748 > 123 3 2 25.1 43.12 1 Fatou Fall
    775526748 < Merci Fatou Fall.Vous etes bien inscrit a RapidSuivi en tant que Facilitator de Keur Samba Laobe.En cas de probleme,merci de contacter votre Superviseur.Bonne journee!
    775526748 > fin 25000 45000
    775526748 < Merci Fatou Fall .Le CGC de Keur Samba Laobe dispose apres une transaction bancaire effectuee aujourd'hui de 25000 CFA dans sa caisse communautaire et de 45000 dans son compte en banque .En cas d'erreur ,merci de contacter votre Superviseur .Bonne journee
    """


    testAddMobilization="""
    775526748 > 123 3 2 25.1 43.12 1 Fatou Fall
    775526748 < Merci Fatou Fall.Vous etes bien inscrit a RapidSuivi en tant que Facilitator de Keur Samba Laobe.En cas de probleme,merci de contacter votre Superviseur.Bonne journee!
    775526748 > ms 321 8 2 1
    775526748 < Merci Fatou Fall .Le CGC de Keur Samba Laobe a organise aujourdhui dans un My Village de Keur Samba Laobe un Environnement qui a touche 321 personnes originaires de 8 villages .En cas d'erreur ,merci de contacter votre supervieur .Bonne journee
    """
    
    
    
    testAddRadio="""
    775526748 > 123 3 2 25.1 43.12 1 Fatou Fall
    775526748 < Merci Fatou Fall.Vous etes bien inscrit a RapidSuivi en tant que Facilitator de Keur Samba Laobe.En cas de probleme,merci de contacter votre Superviseur.Bonne journee!
    775526748 > ms 321 8 2 1
    775526748 < Merci Fatou Fall .Le CGC de Keur Samba Laobe a organise aujourdhui dans un My Village de Keur Samba Laobe un Environnement qui a touche 321 personnes originaires de 8 villages .En cas d'erreur ,merci de contacter votre supervieur .Bonne journee
    """
    
    testAddRadioFail="""
    775526748 > 123 3 2 25.1 43.12 1 Fatou Fall
    775526748 < Merci Fatou Fall.Vous etes bien inscrit a RapidSuivi en tant que Facilitator de Keur Samba Laobe.En cas de probleme,merci de contacter votre Superviseur.Bonne journee!
    775526748 > rad 321 8 2 A
    775526748 < Il y'a une erreur sur le message pour Rapidsuivi,merci de contacter votre superviseur.
    """
    
    
    
    
    