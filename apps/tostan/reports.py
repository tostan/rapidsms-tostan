from contacts.models import Contact
from logger.models import IncomingMessage, OutgoingMessage
from smsforum.models import Village, MembershipLog
from utilities.export import Report

class ContactReport(Report):
    def __init__(self):
        # filter and order_by the queryset as you please
        self.queryset = Contact.objects.all().order_by('node_ptr')
        # weird. len(self.queryset) can be different from self.queryset.count().
        # why?
        super(ContactReport, self).__init__()
        self.renamed_fields = {'node_ptr':'Unique ID',
                               'reporter.connection.identity':'Phone Number',
                               'locale':'Preferred Language',
                               'common_name':'Name',
                               'messages.sent':'Messages sent to Magic Number',
                               'messages.received':'Messages received from Magic Number'
                               }
    
    @property
    def all_fields(self):
        return ['node_ptr', 'reporter.connection.identity', 'common_name',
                'messages.sent', 'messages.received', 'first_seen', 'locale']
        
    def _get_rows(self):
        rows = []
        for q in self.queryset:
            datum = []
            # we hard code the fields here, because sometimes they can be
            # tricky to get access to. e.g. they might require a 
            # select_related, or strange calculations or whatnot
            for i in self.fields:
                if i == 'node_ptr':
                    datum.append(q.pk)
                elif i == 'reporter.connection.identity':
                    if hasattr(q, 'reporter'):
                        if q.reporter.connection:
                            datum.append(q.reporter.connection.identity)
                        else:
                            datum.append('')
                    else:
                        datum.append('')
                elif i == 'common_name':
                    datum.append(q.common_name)
                elif i == 'messages.sent':
                    if q.phone_number is not None:
                        datum.append(IncomingMessage.objects.filter(\
                                     identity=q.phone_number).count())
                    else:
                        datum.append('')
                elif i == 'messages.received':
                    if q.phone_number is not None:
                        datum.append(OutgoingMessage.objects.filter(\
                                     identity=q.phone_number).count())
                    else:
                        datum.append('')
                elif i == 'first_seen':
                    datum.append(q.first_seen)
                elif i == 'locale':
                    datum.append(q.locale)
            rows.append(datum)
        return rows

class MembershipReport(Report):
    def __init__(self):
        self.queryset = MembershipLog.objects.all().order_by('id')
        self.renamed_fields = {}
        super(MembershipReport, self).__init__()

    @property
    def all_fields(self):
         # viewing contact requires permissions
        return ['id','date','contact','action']
        
    def _get_rows(self):
        rows = []
        for q in self.queryset:
            datum = []
            for i in self.fields:
                if i == 'id':
                    datum.append(q.pk)
                elif i == 'date':
                    datum.append(q.date)
                elif i == 'contact':
                    datum.append(q.contact)
                elif i == 'action':
                    datum.append(q.action)
            rows.append(datum)
        return rows
    
class MessageReport(Report):
    def __init__(self):
        super(MessageReport, self).__init__()

    @property
    def all_fields(self):
        # viewing identity requires permissions
        return ['id','text','identity','date']

class IncomingMessageReport(MessageReport):
    def __init__(self):
        self.queryset = IncomingMessage.objects.all().order_by('id')
        self.renamed_fields = {'identity':'Phone Number'}
        super(IncomingMessageReport, self).__init__()

    def _get_rows(self):
        rows = []
        for q in self.queryset:
            datum = []
            for i in self.fields:
                if i == 'id':
                    datum.append(q.pk)
                elif i == 'text':
                    datum.append(q.text)
                elif i == 'identity':
                    datum.append(q.identity)
                elif i == 'date':
                    datum.append(q.received)
            rows.append(datum)
        return rows

class OutgoingMessageReport(MessageReport):
    def __init__(self):
        self.queryset = OutgoingMessage.objects.all().order_by('id')
        self.renamed_fields = {'identity':'Phone Number'}
        super(OutgoingMessageReport, self).__init__()

    def _get_rows(self):
        rows = []
        for q in self.queryset:
            datum = []
            for i in self.fields:
                if i == 'id':
                    datum.append(q.pk)
                elif i == 'text':
                    datum.append(q.text)
                elif i == 'identity':
                    datum.append(q.identity)
                elif i == 'date':
                    datum.append(q.sent)
            rows.append(datum)
        return rows
