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

class Report(object):
    """
    Suggested Usage:
    r = MyReport()
    # r.all_fields = [ 'foo', 'baz', 'bar' ]
    r.fields = ['foo','baz']
    r.renamed_fields = {'foo':'first', 'baz':'second'}
    r.get_csv() #returns the raw excel, csv string
    r.get_csv_response() #returns an http response excel, csv file 
    # Output looks like: 
    # first, second
    # first_val1, first_val2
    # second_val1, second_val2
    # etc.
    """
    
    def __init__(self):
        # select fields you want to be in your report, in the order you want
        # fields should be a subset of all_fields, or they will be ignored
        self.fields = self.all_fields
        # map fields to labels if you don't want to use the default
        self.renamed_fields = {}
    
    @property
    def all_fields(self):
        return []

    def get_csv(self, stream):
        writer = UnicodeWriter(stream)
        # generate the first row of the csv
        field_labels=[]
        for f in self.fields:
            if f in self.renamed_fields:
                field_labels.append(self.renamed_fields[f])
            else:
                field_labels.append(f)
        writer.writerow(field_labels)
        # generate the data
        data = self._get_rows()
        for d in data:
            writer.writerow(d)
        #stream.seek(0)
        return stream
    
    def get_csv_response(self, req):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(mimetype='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=rapidsms.csv'
        self.get_csv(response)
        return response
    
    def _get_rows(self):
        raise NotImplementedError

