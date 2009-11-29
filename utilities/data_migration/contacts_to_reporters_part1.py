#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

11/29/09 The following script is used to migrate data 
from the old contacts models into the new reporters model

"""

def run():
    print "starting contacts to reporters part 1"
    create_backends()
    create_reporters()
    remove_channels()
    print "done"                 
            
def create_backends():
    from contacts.models import Contact, CommunicationChannel, ChannelConnection
    from reporters.models import Reporter, PersistantBackend, PersistantConnection
    # create various connection objects
    channels = CommunicationChannel.objects.all()
    for channel in channels:
        backend = PersistantBackend(slug=channel.backend_slug, 
                                    title=channel.title)
        backend.save()
    
    # check
    channel_count = channels.count()
    backend_count = PersistantBackend.objects.all().count()
    if channel_count != backend_count:
        raise Exception("channel count does not match backend count! %s %s" \
                        % (channel_count, backend_count))

def create_reporters():
    from contacts.models import Contact, CommunicationChannel, ChannelConnection
    from reporters.models import Reporter, PersistantBackend, PersistantConnection
    all_contacts = Contacts.objects.all()
    for contact in all_contacts:
        print "processing contact %s" % contact.get_signature()
        
        # NEW reporter models
        rep = Reporter()
        rep.unique_id = contact.unique_id
        rep.first_name = contact.given_name
        rep.last_name = contact.family_name
        rep.language = contact._locale
        rep.save()
        
        # check
        conns = contact.channel_connections.all()
        conns_count = conns.count()
        if conns_count==0:
            print "%s has no connections" % (contact.get_signature())
        elif conns_count>1:
            print "%s has more than one connections" % (contact.get_signature())

        # create various connection objects
        for conn in conns:
            new_conn = PersistantConnection()
            new_conn.identity = conn.user_identifier
            new_conn.backend = PersistantBackend.objects.get(slug=conn.communication_channel.backend_slug)
            new_conn.reporter = Reporter.objects.get(unique_id=conn.contact.unique_id)
            new_conn.save()
            conn.delete()
        
    # check
    contact_count = all_contacts.count()
    reporter_count = Reporter.objects.all().count()
    if contact_count != reporter_count:
        raise Exception("Mismatch between contact and reporter count! %s %s" \
                        % (contact_count, reporter_count))

def remove_channels():
    from contacts.models import Contact, CommunicationChannel, ChannelConnection
    from reporters.models import Reporter, PersistantBackend, PersistantConnection
    # drop old connection objects
    channels = CommunicationChannel.objects.all()
    for channel in channels:
        channel.delete()

"""
Fields that stay in contact: 
        first_seen = models.DateTimeField(auto_now_add=True)
        common_name = models.CharField(max_length=255,blank=True)
        location = models.ForeignKey(Location, null=True, blank=True)
        gender = models.CharField(max_length=1,choices=GENDER_CHOICES,blank=True) 
        age_months = models.IntegerField(null=True,blank=True)
        _permissions = models.PositiveSmallIntegerField(default=__PERM_RECEIVE | __PERM_SEND)
        _quota_send_max = models.PositiveSmallIntegerField(default=0)
        _quota_send_period = models.PositiveSmallIntegerField(default=0) # period in minutes
        _quota_send_period_begin = models.DateTimeField(null=True,blank=True)
        _quota_send_seen = models.PositiveSmallIntegerField(default=0) # num messages seen in current period
        _quota_receive_max = models.PositiveSmallIntegerField(default=0)
        _quota_receive_period = models.PositiveSmallIntegerField(default=0) # period in minutes
        _quota_receive_period_begin = models.DateTimeField(null=True,blank=True)
        _quota_receive_seen = models.PositiveSmallIntegerField(default=0) # num messages seen in current period

"""



        