from rapidsms.tests.scripted import TestScript
from app import App
from apps.rapidsuivi.models import *
import apps.rapidsuivi  as rapidsuivi_app
from .models import *
class TestApp (TestScript):
    apps = (App,)
    
    def setUp(self):
        super (TestApp, self).setUp ()
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
    
    
    def test(self):
        self._testcreatepays ()
        self._testcreateregion ()
        self._testregionspays ()
        self._testdowncast_children ()
        self._testdowncast_parent ()
    def _testcreatepays (self):
         senegal = Pays.objects.get_or_create (name = "Senegal")
         self.assertTrue(senegal is not None )

    def _testcreateregion (self):
        senegal  = Pays.objects.get(name__icontains = "Senegal")
        kaolack  = Region.objects.create (name = "Kaolack" ,parent = senegal)
        self.assertTrue (kaolack is not None)
        
    def _testregionspays (self):
         senegal  = Pays.objects.get(name__icontains = "Senegal")
         regions =senegal.children.all ()
         for region in regions :
             print region , type (region)
             
             
         self.assertTrue (len (regions) ,1 )
         
         
         
    def _testdowncast_children (self):
       senegal = Pays.objects.get (name__icontains = "Senegal")
       region  = senegal.children.all () [0]
       print region , type (region)
       region = region._downcast (klass =Region)
       print region , type (region)
       
      
    
    def _testdowncast_parent (self):
        kaolack  = Region.objects.get (name__icontains ="kaolack")
        print kaolack.parent , type (kaolack.parent)
        print kaolack.parent._downcast (klass = Pays) ,  type (kaolack.parent._downcast(klass =Pays))
        
        
        
        
        