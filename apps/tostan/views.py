from django.contrib.auth.decorators import login_required
from rapidsms.webui.utils import render_to_response
from rapidsms.webui.utils import paginated
from smsforum.models import Village
from tostan.reports import ContactReport

@login_required
def export(request, template="tostan/export.html"):
    context = {}
    context['villages'] = Village.objects.all()
    return render_to_response(request, template, context)

def export_contacts(request):
    c = ContactReport()
    return c.get_csv_response(request)
