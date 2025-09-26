from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from django.conf import settings

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use settings.BASE_DIR to find files
    static_root = settings.STATIC_ROOT
    static_url = settings.STATIC_URL

    if uri.startswith(static_url):
        path = os.path.join(static_root, uri.replace(static_url, ""))
    else:
        # handle relative paths
        path = os.path.join(settings.BASE_DIR, uri)

    # check if file exists
    if not os.path.isfile(path):
        return uri
    return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(
            BytesIO(html.encode("UTF-8")), 
            dest=result,
            link_callback=link_callback)
    if not pdf.err:
        return result.getvalue()
    return None
