from contacts.models import Contact
from logger.models import IncomingMessage, OutgoingMessage
from utilities.export import Report

class ContactReport(Report):
    def __init__(self):
        # filter and order_by the queryset as you please
        self.queryset = Contact.objects.all().order_by('node_ptr')
        # weird. len(self.queryset) can be different from self.queryset.count().
        # why?
        super(ContactReport, self).__init__()
        self.renamed_fields = {'reporter.connection.identity':'Phone Number',
                               'locale':'Preferred Language'
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

