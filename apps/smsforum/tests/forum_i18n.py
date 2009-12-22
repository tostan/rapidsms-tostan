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
        8005551210 < Your message must be less than 140 characterss
        """
