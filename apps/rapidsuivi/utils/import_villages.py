#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import sys
import os
import codecs
import csv
from rapidsuivi.models import SuiviVillage
from smsforum.models import Region
from locations.models import Location
import re
import string
import random
def import_villages(file):
    """
    Ce module permet d'importer les donnees des villages , la latitude 
    longitude , departements, regions , arrondissments , communaute rurale, commune
    """
    csvee =codecs.open("/home/alioune/rapidsms-all/rapidsuivi-tostan/apps/rapidsuivi/data/Tostan2.csv",
                      "rU", encoding="ascii", errors="ignore")
    dialect = csv.Sniffer().sniff(csvee.read (1024))
    csvee.seek(0)
    dialect.quotechar='"'
    reader  = csv.DictReader(csvee, quoting= csv.QUOTE_ALL ,dialect=dialect ,delimiter=",")
    for i , row  in enumerate(reader):
        try:
            
            if row.has_key ("X") and row.has_key("Y"):
                  def only_digit(val):
                     val =re.sub ("[0-9\.]" , "" ,val).strip()
                     if  val!="":  
                         #On a des caractere dans cette chaine
                         return False
                     # On a que des nombres dans la chaine , ou (.)
                     # Donc c'est bon on a une bonne latitude et une bonne longitude
                     return True
                 
                  def is_not_empty(row , keys):
                      print  row
                      print keys
                      if hasattr (keys , "__iter__"):
                          has_keys=[row.has_key(key) and row[key] 
                                            is not None for key in keys]
                      else :
                          has_keys =[row.has_key(key) and row[key] is not None]                 
                      
                      if has_keys:
                          print has_keys
                          if False in has_keys:
                              return False
                          
                          else :return True
                      return False
                  
                  def filter(row , keys):
                      for k in row.keys ():
                            if k not in keys:
                                del row[k]
                        
                      return row
                      
                  latitude =only_digit(row["X"])
                  longitude=only_digit(row["Y"])
                  
                  if latitude and longitude :
                        try:
                            code = "".join(random.sample (string.letters, 10))
                            loc =Location.objects.create\
                                    (code =code , latitude =latitude , longitude = longitude)
                            
                            bool=is_not_empty (row, ["departement", "arrondissement", 
                                                "region","commune","coordination" ,"langue"])
                            row = filter (row, ["departement" ,"arrondissment" ,
                                                    "region", "commune" , "coordination", "langue"])
                            if bool:
                                village = SuiviVillage(**row)
                                village.location = loc
                                village.save ()
                                print "Enregistrement  OK"
                                print row
                                print i
                            else :
                                raise Exception ("Des champs sont vides")
                                
                        except Exception ,e:
                            raise 
                            print e
                            print row
                            print i
                             
                  else :
                      
                      print "Latitude or longitude mal forme"
                      print row
                      print i
                      continue
                  
                    
            else :
                continue
        
        
        except Exception  , e :
            raise 
            print row
            print "COUNT :",i 
            break
        
if __name__=="__main__":
    argv  = sys.argv
    f  = argv[1]
    import_villages (f)
    
