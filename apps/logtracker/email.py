""" 

This exists to provide a utility for email alerts to be sent from runserver
(i.e. where no instance of router is accessible, so no access to email backend)

"""

from django.core.mail import SMTPConnection, EmailMessage
from rapidsms.webui.settings import RAPIDSMS_CONF as conf

class EmailAgent(object):
    """ A simple class for handling email sending """
    
    def __init__(self):
        """ Configure the default connection
        Here we take email settings from the email backend
        """
        self.conn = SMTPConnection(username=conf['email']['username'],
                                   port=conf['email']['port'],
                                   host=conf['email']['host'],
                                   password=conf['email']['password'],
                                   use_tls=True,
                                   fail_silently=False)

    def send_email(self, subject, recipient_addr, msg_payload):
        """ send a basic email message to the group """
        msg = EmailMessage(subject=subject, 
                           body=msg_payload,
                           from_email=conf['email']['username'],
                           to=[recipient_addr],
                           connection=self.conn
                           )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
