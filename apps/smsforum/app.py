#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
import rapidsms
from rapidsms.parsers import Matcher
from rapidsms.message import Message
from models import *
from apps.locations.models import *
import gettext

from apps.contacts.models import *

_ = gettext.gettext

DEFAULT_VILLAGE="unassociated"

class App(rapidsms.app.App):
    MSG = {
        "en": {
            "period": ". ",
            "denied": "Please join a village by texting us: #join villagename",
            "first-login": "Thank you for joining the village %(village)s",
            "blast-fail": "Sorry, I couldn't send that message.",
            "register-fail": "Sorry, I couldn't register you.",
            "leave-success": "Good-bye from village %(village)s",
            "leave-fail": "'Leave' failed due to some unknown error.",
            "lang-set":    "I will now speak to you in English, where possible." },
            
        # TODO: move to an i18n app!
        "fr": {
            "period": ". ",
            "denied": "Svp join a village by texting us: #join villagename",
            "first-login": "Merci for joining the village %(village)s",
            "register-fail": "Je m'excuse, I couldn't register you.",
            "blast-fail": "Je m'excuse, I couldn't send that message.",
            "leave-success": "Au revoir from village %(village)s",
            "leave-fail": "'Partez' failed due to some unknown error.",
            "lang-set":    "I will now speak to you in French, where possible." },
        }
    
    
    def __str(self, key, contact=None, lang=None):
        
        # if no language was explicitly requested,
        # inherit it from the reporter, or fall
        # back to english. because everyone in the
        # world speaks english... right?
        if lang is None:
            if contact is not None:
                lang = contact.locale
            
            # fall back
            if lang is None:
                lang = "en"

        # look for an exact match, in the language
        # that the reporter has chosen as preferred
        if lang is not None:
            if lang in self.MSG:
                if key in self.MSG[lang]:
                    return self.MSG[lang][key]
        
        # not found in localized language. try again in english
        # TODO: allow the default to be set in rapidsms.ini
        return self.__str(key, lang="en") if lang != "en" else None
    
    
    def start(self):
        # since the functionality of this app depends on a default group
        # make sure that this group is created explicitly in this app 
        # (instead of depending on a fixture)
        Village.objects.get_or_create(name=DEFAULT_VILLAGE)

        # fetch a list of all the backends
        # that we already have objects for
        known_backends = PersistantBackend.objects.values_list("slug", flat=True)
        
        # find any running backends which currently
        # don't have objects, and fill in the gaps
        for be in self.router.backends:
            if not be.slug in known_backends:
                self.info("Creating PersistantBackend object for %s (%s)" % (be.slug, be.title))
                PersistantBackend(slug=be.slug, title=be.title).save()
    
    
    def parse(self, msg):
        print "REPORTER:PARSE"
        # fetch the persistantconnection object
        # for this message's sender (or create
        # one if this is the first time we've
        # seen the sender), and stuff the meta-
        # dta into the message for other apps
        msg.persistent_channel= CommunicationChannelFromMessage(msg)
        msg.persistant_connection = ChannelConnectionFromMessage(msg)
        msg.contact = ContactFromMessage(msg)
        
        # store a handy dictionary, containing the most useful persistance
        # information that we have. this is useful when creating an object
        # linked to _something_, like so:
        # 
        #   class SomeObject(models.Model):
        #     reporter   = models.ForeignKey(Reporter, null=True)
        #     connection = models.ForeignKey(PersistantConnection, null=True)
        #     stuff      = models.CharField()
        #
        #   # this object will be linked to a reporter,
        #   # if one exists - otherwise, a connection
        #   SomeObject(stuff="hello", **msg.persistance_dict)
        if msg.contact: msg.persistance_dict = { "reporter": msg.contact }
        else:            msg.persistance_dict = { "connection": msg.persistant_connection }
        
        # log, whether we know who the sender is or not
        if msg.contact: self.info("Identified: %s as %r" % (msg.persistant_connection.user_identifier, msg.contact))
        else:            self.info("Unidentified: %s" % (msg.persistant_connection.user_identifier))
    
    def handle(self, msg):
        print "REPORTER:HANDLE"
        matcher = Matcher(msg)
        
        # TODO: this is sort of a lightweight implementation
        # of the keyworder. it wasn't supposed to be. maybe
        # replace it *with* the keyworder, or extract it
        # into a parser of its own
        
        # swap in and out based on translations
        # but perhaps we want to accept commands in all known languages?
        map = [ #search algorithm should be ordered
            ("join",  ["#join (whatever)"]), # optionally: join village name m/f age
            ("join",  ["\*join (whatever)"]),
            ("createvillage",  ["###create (whatever)"]),
            #"#name":  ["add_name (whatever)"],
            #"*name":  ["add_name (whatever)"],
            #"#stats":  ["stats (letters) (numbers)"],
            #"*stats":  ["stats (letters) (numbers)"],
            ("leave",  ["#leave"]),
            ("leave",  ["\*leave"]),            
            ("lang",  ["#lang (slug)"]),
            ("lang",  ["\*lang (slug)"]),
            ("blast",  ["(whatever)"])
        ]
        
        # search the map for a match, dispatch
        # the message to it, and return/stop
        for method, patterns in map:
            if matcher(*patterns) and hasattr(self, method):  
                getattr(self, method)(msg, *matcher.groups)
                return True
        
        # no matches, so this message is not
        # for us; allow processing to continue
        return False
      
    # admin utility!
    def createvillage(self, msg, village=DEFAULT_VILLAGE):
        #try:
            # TODO: add administrator authentication
            print "REPORTER:CREATEVILLAGE"
            
            
            ville = Village.objects.get_or_create(name=village)
            
            msg.respond( ("village %s created") % (village) )
            return
            # TODO: remove this for production
            """except:
                msg.respond(
                    self.__str("register-fail", rep) 
                )
            """
            
    def join(self, msg, village=DEFAULT_VILLAGE):
    #try:
        # parse the name, and create a reporter
        # TODO: check for valid village/group/etc.
        print "REPORTER:JOIN"
        #loc = Locations.objects.all().filter(name=village)

        villes = Village.objects.all().filter(name=village)
        if len(villes)==0:
            msg.respond( _("village does not exist") )
            #default join
            rep = self.join(msg,DEFAULT_VILLAGE)
            return rep

        ville = villes[0]
        sender = Contact()
        #create new Contact
        sender.save()
        #create new membership
        sender.add_to_group(ville)
        #create new channelconnection
        ChannelConnection(user_identifier=msg.persistant_connection.user_identifier, \
                          communication_channel=msg.persistent_channel, contact=sender)
        
        # attach the reporter to the current connection
        msg.contact = sender
        
        msg.respond( self.__str("first-login", sender) % {"village": village } )
        return sender
        # TODO: remove this for production
        """except:
            msg.respond(
                self.__str("register-fail", rep) 
            )
        """
 
    def blast(self, msg, txt):
        sender = msg.contact
        if sender is None:
            #join default village and send to default village
            sender = self.join(msg)
        #try:
        # parse the name, and create a reporter
        # TODO: check for valid village/group/etc.
        print "REPORTER:BLAST"
        #find all reporters from the same location
        villages = sender.my_villages
        if len(villages)==0:
            msg.respond( _("You must join a village before sending messages") )
            return
        for ville in villages:
            recipients = ville.subleaves()
            
            # it makes sense to complete all of the sending
            # before sending the confirmation sms
            # iterate every member of the group we are broadcasting
            # to, and queue up the same message to each of them
            for recipient in recipients:
                #add signature
                anouncement = _("%s:to [%s] %s") % ( txt, ville.name, sender.signature() )
                #todo: limit chars to 1 txt message?
                conns = ChannelConnection.objects.all().filter(contact=recipient)
                for conn in conns:
                    be = self.router.get_backend(conn.channel_connection,)
                    be.message(conn.unique_identifier, announcement).send()
                    
        msg.respond( _("success! %s recvd msg: %s" % (sender.location.name,txt) ) )
        return sender
        # TODO: remove this for production
        """except:
            msg.respond(
                self.__str("blast-fail", rep) 
            )
        """

    def leave(self, msg):
        #try:
            print "REPORTER:LEAVE"
            lang = ''
            if msg.contact is not None:
                if len(msg.contact.my_villages)>0:
                    #default to deleting all persistent connections with the same identity
                    #we can always come back later and make sure we are deleting the right backend
                    for ville in msg.contact.my_villages:
                        if len(msg.contact.language) > 0:
                            lang = msg.reporter.language
                        msg.contact.delete()
                        msg.respond(
                            self.__str("leave-success", lang=lang) % {
                             "village": ville })
                    return
            msg.respond( _("nothing to leave") )
            return
        # something went wrong - at the
        # moment, we don't care what
            """except:
                msg.respond(
                    self.__str("leave-fail", rep) 
                )
                """   
    

                    
    def lang(self, msg, code):
        # TODO: make this a decorator to be used in all functions
        # so that users don't have to register in order to get going
        print "REPORTER:LANG"
        err = None
        if msg.contact is None:
            err = "denied"
            msg.contact = self.join(msg)
        
        # if the language code was valid, save it
        # TODO: obviously, this is not cross-app
        if code in self.MSG:
            msg.contact.language = code
            msg.contact.save()
            resp = "lang-set"
        
        # invalid language code. don't do
        # anything, just send an error message
        else: resp = "bad-lang"
        
        # always send *some*
        # kind of response
        
        response = self.__str(resp, msg.contact)
        if err is not None:
            response = response + self.__str(err, msg.contact) + self.__str("period", msg.contact)       
        msg.respond( response )
        
