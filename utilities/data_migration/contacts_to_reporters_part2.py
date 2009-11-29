#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

11/29/09 The following script is used to trim redundant fields
from contacts and to link it to reporters properly

"""
from django.db import connection

def run():
    cursor = connection.cursor()
    print "starting contacts to reporters part 2"
    from reporters.models import Reporter, PersistantBackend, PersistantConnection
    
    # add reporter_id, allowing null values fo rnow
    cursor.execute("ALTER TABLE `contacts_contact` ADD COLUMN `reporter_id` INT(11) DEFAULT NULL AFTER `node_ptr_id`;")
    cursor.execute("ALTER TABLE `contacts_contact` ADD CONSTRAINT `reporter_id_refs_id_32f59ca5` FOREIGN KEY (`reporter_id`) REFERENCES `reporters_reporter` (`id`);")
    cursor.execute("ALTER TABLE `contacts_contact` ADD CONSTRAINT UNIQUE `reporter_id`;")
    
    contact_count = 0
    reps = Reporters.objects.all()
    for rep in reps:
        c = Contact.objects.get(unique_id=rep.unique_id)
        c.reporter = rep
        c.save()
        contact_count = contact_count + 1

    #check
    rep_count = reps.count()
    if rep_count != contact_count:
        print "Mismatch between rep and contacts! %s %s" \
              % (rep_count, contact_count)    
               
    # check
    unassociated_contacts = Contact.objects.filter(reporter=None)
    if len(unassociated_contacts)>0:
        print "PROBLEMS WITH GENERATING REPORTERS!"
        print "UNASSOCIATED: "
        for con in unassociated_contacts:
            print " contact id: %s\n" % con.id 
            
    # set reporter_id to be required
    cursor.execute("ALTER TABLE `contacts_contact` MODIFY COLUMN `reporter_id` INT(11) NOT NULL AFTER `node_ptr_id`;")

    # manually trim old db tables
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `given_name`;")
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `family_name`;")
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `unique_id`;")
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `location`;")
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `_locale`;")

    print "done"

