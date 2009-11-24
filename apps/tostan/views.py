from rapidsms.webui.utils import render_to_response
from rapidsms.webui.utils import paginated
from smsforum.models import Village

def export(request, template="tostan/export.html"):
    context = {}
    context['villages'] = Village.objects.all()
    return render_to_response(request, template, context)

