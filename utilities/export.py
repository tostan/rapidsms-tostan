import csv
import cStringIO
import codecs
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from django.db.models import Manager

def export(qs, fields=None, format='csv'):
    response = HttpResponse(mimetype='text/csv')
    if len(qs)==0:
        response['Content-Disposition'] = 'attachment; filename=empty.csv'
        return response
    if hasattr(qs,'model'):
        # if we received a query set...
        model = getattr(qs,'model')
    else:
        # if we received a regular list [] object, just infer class from instance
        model = qs[0].__class__
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
    writer = UnicodeWriter(response)
    # Write headers to CSV file
    if fields:
        headers = fields
    else:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
    writer.writerow(headers)
    # Write data to CSV file
    for obj in qs:
        row = []
        for field in headers:
            if field in headers:
                val = getattr(obj, field)
                if isinstance(val,Manager):
                    # support ManyToMany relations here
                    vals = val.all()
                    val = ','.join([str(v) for v in vals])
                else:
                    if callable(val):
                        val = val()
                    if hasattr(obj, "get_" + field + "_display"):
                        val2 = getattr(obj, "get_" + field + "_display")
                        if callable(val2):
                            val = val2()
                row.append(val)
        writer.writerow(row)
    # Return CSV file to browser as download
    return response

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# TODO DRY
def ass_dicts_for_export():
    dicts_for_export = []
    #asses = Assessment.objects.all().select_related()
    patients = Patient.objects.all()
    asses = []
    for patient in patients:
        if patient.latest_assessment() is not None:
            asses.append(patient.latest_assessment())

    for ass in asses:
        ass_dict = {}
        # add desired fields from related models (we want to display the
        # IDs, ect from foreign fields rather than just the unicode() names
        # or all of the fields from related models)
        # TODO is there a better way to do this? adding fields to the queryset???
        ass_dict.update({'interviewer_id'   : ass.healthworker.interviewer_id})
        ass_dict.update({'child_id'         : ass.patient.code})
        ass_dict.update({'household_id'     : ass.patient.household_id})
        ass_dict.update({'cluster_id'       : ass.patient.cluster_id})
        ass_dict.update({'sex'              : ass.patient.gender})
        ass_dict.update({'date_of_birth'    : ass.patient.date_of_birth})
        ass_dict.update({'age_in_months'    : ass.patient.age_in_months})
        ass_dict.update({'human_status'     : ass.get_status_display()})
        ass_dict.update(**instance_to_dict(ass))
        dicts_for_export.append(ass_dict)
    return dicts_for_export

def export_custom(req):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=assessments.csv'

    assessments = ass_dicts_for_export()
    # sort by date, descending
    assessments.sort(lambda x, y: cmp(y['date'], x['date']))

    writer = csv.writer(response)
    # column labels
    writer.writerow(['date', 'interviewer ID', 'cluster ID', 'child ID',\
        'household ID', 'sex', 'date of birth', 'age in months', 'height',\
        'weight', 'oedema', 'muac', 'height for age', 'weight for age',\
        'weight for height', 'survey status'])
    for ass in assessments:
        row = []
        keys = ['date', 'interviewer_id', 'cluster_id', 'child_id',\
            'household_id', 'sex', 'date_of_birth', 'age_in_months',\
            'height', 'weight', 'oedema', 'muac', 'height4age', 'weight4age',\
            'weight4height', 'human_status']
        for key in keys:
            if ass.has_key(key):
                row.append(ass[key])
            else:
                row.append("None")
        writer.writerow(row)

    return response
