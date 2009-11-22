from rapidsms.webui.utils import render_to_response
from rapidsms.webui.utils import paginated
from smsforum.models import Village

def smscommands(request, template_name="tostan/smscommands.html"):
    return render_to_response(request, template_name)

def dashboard(request, template_name="tostan/dashboard.html"):
    return render_to_response(request, template_name)

def export(request, template="tostan/export.html"):
    context = {}
    context['villages'] = Village.objects.all()
    return render_to_response(request, template, context)

