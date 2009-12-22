#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.tests.scripted import TestScript
import apps.smsforum.app as smsforum_app
import apps.logger.app as logger_app
import apps.contacts.app as contacts_app
import apps.reporters.app as reporters_app
import apps.smsforum.app as smsforum_app
 
class TestSMSCommands (TestScript):
    apps = (smsforum_app.App, contacts_app.App, logger_app.App, reporters_app.App, smsforum_app.App )

    def setUp(self):
        TestScript.setUp(self)
        #should setup default village in here
        
    testMsgTooLongEnglish = """
        8005551210 > .create village20
        8005551210 < Community 'village20' was created
        8005551210 > .join village20
        8005551210 < Thank you for joining the village20 community - welcome!
        8005551210 > very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast
        8005551210 < Message length (258) is too long. Please limit to 60
        """
           
    testMsgTooLongFrench = """
        8005551210 > .creer village20
        8005551210 < La communauté village20 a été créée
        8005551210 > .entrer village20
        8005551210 < Merci d'avoir adhere le village20 - soyez le bienvenu!
        8005551210 > tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,
        8005551210 < Votre message doit contenir moins de 140 caracteres
        """
    testMsgToLongWolof = u"""
        8005551220 > .lang wol
        8005551220 < Làkk wi nga tànn moo kàllaama Wolof
        8005551220 > .duggu village7
        8005551220 < Jerejef ci dugg bi nga dugg ci 'village7 ' dalal ak jamm
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Messasse  bi  goudouna  lolo ,  wgni ko ba mou  tolou  ci  140 araf
        """
    testMsgToLongPulaar = u"""
        8005551220 > .lang wol
        8005551220 < Làkk wi nga tànn moo kàllaama Wolof
        8005551220 > .duggu village7
        8005551220 < Jerejef ci dugg bi nga dugg ci 'village7 ' dalal ak jamm
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Messasse  bi  goudouna  lolo ,  wgni ko ba mou  tolou  ci  140 ara 
        """
    testMsgToLongDjoola = u"""
        8005551220 > .lang wol
        8005551220 < Làkk wi nga tànn moo kàllaama Wolof
        8005551220 > .duggu village7
        8005551220 < Jerejef ci dugg bi nga dugg ci 'village7 ' dalal ak jamm
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Messasse  bi  goudouna  lolo ,  wgni ko ba mou  tolou  ci  140 araf 
        """
    testMsgToLongSoninke = u"""
        8005551220 > .lang wol
        8005551220 < Làkk wi nga tànn moo kàllaama Wolof
        8005551220 > .duggu village7
        8005551220 < Jerejef ci dugg bi nga dugg ci 'village7 ' dalal ak jamm
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Messasse  bi  goudouna  lolo ,  wgni ko ba mou  tolou  ci  140 araf 
        """
    testMsgToLongMandingo = u"""
        8005551220 > .lang wol
        8005551220 < Làkk wi nga tànn moo kàllaama Wolof
        8005551220 > .duggu village7
        8005551220 < Jerejef org.eclipse.uici dugg bi nga dugg ci 'village7 ' dalal ak jamm
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Messasse  bi  goudouna  lolo ,  wgni ko ba mou  tolou  ci  140 araf 
        """

